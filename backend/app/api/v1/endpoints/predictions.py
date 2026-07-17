from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from typing import List, Optional
import uuid
from datetime import datetime

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.prediction import Prediction
from app.models.recommendation import Recommendation
from app.models.disease import Disease
from app.models.pesticide import Pesticide
from app.models.fertilizer import Fertilizer
from app.models.report import Report
from app.schemas.prediction import (
    PredictionResponse, 
    AnalyzeRequest, 
    AnalyzeResponse,
    RecommendationItem
)
from app.services.ml_inference import ml_service
from app.services.recommendation import recommendation_engine
from app.services.storage import storage_client
from app.services.pdf_report import pdf_generator

router = APIRouter()

@router.post("/upload")
async def upload_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload images to R2 storage and return URLs"""
    if len(files) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 images allowed per batch"
        )
    
    uploaded_urls = []
    
    for file in files:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.filename}. Only images allowed."
            )
        
        # Read file data
        file_data = await file.read()
        
        # Validate file size (15MB max)
        if len(file_data) > 15 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} exceeds 15MB limit"
            )
        
        # Upload to storage (local or R2)
        url = await storage_client.upload_file(
            file_data, 
            file.filename, 
            file.content_type
        )
        uploaded_urls.append(url)
    
    return {
        "uploaded_urls": uploaded_urls,
        "count": len(uploaded_urls),
        "message": "Images uploaded successfully"
    }

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_images(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze uploaded images using ML inference service
    and generate treatment recommendations
    """
    if not request.image_urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image URLs provided"
        )
    
    # Call ML inference service
    ml_predictions = await ml_service.predict_disease(request.image_urls)
    
    predictions_response = []
    
    for ml_pred in ml_predictions:
        # Create prediction record
        prediction = Prediction(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            image_url=ml_pred["image_url"],
            disease_id=ml_pred.get("disease_id"),
            confidence_score=ml_pred["confidence_score"]
        )
        db.add(prediction)
        await db.flush()
        
        # Get disease info
        disease_name = None
        if prediction.disease_id:
            disease_result = await db.execute(
                select(Disease).filter(Disease.id == prediction.disease_id)
            )
            disease = disease_result.scalars().first()
            if disease:
                disease_name = disease.name
        
        # Generate recommendations if disease detected
        recommendations_list = []
        if prediction.disease_id:
            recs = await recommendation_engine.get_recommendations(
                prediction.disease_id, 
                db
            )
            
            # Save pesticide recommendations
            for pest_rec in recs["pesticides"]:
                rec = Recommendation(
                    prediction_id=prediction.id,
                    pesticide_id=pest_rec["pesticide_id"],
                    similarity_score=pest_rec["similarity_score"]
                )
                db.add(rec)
                recommendations_list.append(RecommendationItem(
                    id=0,  # Will be set after commit
                    pesticide_id=pest_rec["pesticide_id"],
                    pesticide_name=pest_rec["pesticide_name"],
                    similarity_score=pest_rec["similarity_score"]
                ))
            
            # Save fertilizer recommendations
            for fert_rec in recs["fertilizers"]:
                rec = Recommendation(
                    prediction_id=prediction.id,
                    fertilizer_id=fert_rec["fertilizer_id"],
                    similarity_score=fert_rec["similarity_score"]
                )
                db.add(rec)
                recommendations_list.append(RecommendationItem(
                    id=0,  # Will be set after commit
                    fertilizer_id=fert_rec["fertilizer_id"],
                    fertilizer_name=fert_rec["fertilizer_name"],
                    similarity_score=fert_rec["similarity_score"]
                ))
        
        predictions_response.append(PredictionResponse(
            id=prediction.id,
            user_id=prediction.user_id,
            image_url=prediction.image_url,
            disease_id=prediction.disease_id,
            disease_name=disease_name,
            confidence_score=prediction.confidence_score,
            created_at=prediction.created_at,
            recommendations=recommendations_list
        ))
    
    await db.commit()
    
    return AnalyzeResponse(
        predictions=predictions_response,
        message=f"Successfully analyzed {len(predictions_response)} images"
    )

@router.get("", response_model=List[PredictionResponse])
async def get_predictions(
    skip: int = 0,
    limit: int = 20,
    disease_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get prediction history for current user"""
    query = select(Prediction).filter(Prediction.user_id == current_user.id)
    
    if disease_id:
        query = query.filter(Prediction.disease_id == disease_id)
    
    query = query.order_by(desc(Prediction.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    # Build response with recommendations
    response = []
    for pred in predictions:
        # Get disease name
        disease_name = None
        if pred.disease_id:
            disease_result = await db.execute(
                select(Disease).filter(Disease.id == pred.disease_id)
            )
            disease = disease_result.scalars().first()
            if disease:
                disease_name = disease.name
        
        # Get recommendations
        recs_result = await db.execute(
            select(Recommendation).filter(Recommendation.prediction_id == pred.id)
        )
        recommendations = recs_result.scalars().all()
        
        recommendations_list = []
        for rec in recommendations:
            rec_item = RecommendationItem(
                id=rec.id,
                pesticide_id=rec.pesticide_id,
                fertilizer_id=rec.fertilizer_id,
                similarity_score=rec.similarity_score
            )
            
            # Get pesticide/fertilizer names
            if rec.pesticide_id:
                pest_result = await db.execute(
                    select(Pesticide).filter(Pesticide.id == rec.pesticide_id)
                )
                pesticide = pest_result.scalars().first()
                if pesticide:
                    rec_item.pesticide_name = pesticide.name
            
            if rec.fertilizer_id:
                fert_result = await db.execute(
                    select(Fertilizer).filter(Fertilizer.id == rec.fertilizer_id)
                )
                fertilizer = fert_result.scalars().first()
                if fertilizer:
                    rec_item.fertilizer_name = fertilizer.name
            
            recommendations_list.append(rec_item)
        
        response.append(PredictionResponse(
            id=pred.id,
            user_id=pred.user_id,
            image_url=pred.image_url,
            disease_id=pred.disease_id,
            disease_name=disease_name,
            confidence_score=pred.confidence_score,
            created_at=pred.created_at,
            recommendations=recommendations_list
        ))
    
    return response

@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed prediction by ID"""
    result = await db.execute(
        select(Prediction).filter(
            Prediction.id == prediction_id,
            Prediction.user_id == current_user.id
        )
    )
    prediction = result.scalars().first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    # Get disease name
    disease_name = None
    if prediction.disease_id:
        disease_result = await db.execute(
            select(Disease).filter(Disease.id == prediction.disease_id)
        )
        disease = disease_result.scalars().first()
        if disease:
            disease_name = disease.name
    
    # Get recommendations with full details
    recs_result = await db.execute(
        select(Recommendation).filter(Recommendation.prediction_id == prediction.id)
    )
    recommendations = recs_result.scalars().all()
    
    recommendations_list = []
    for rec in recommendations:
        rec_item = RecommendationItem(
            id=rec.id,
            pesticide_id=rec.pesticide_id,
            fertilizer_id=rec.fertilizer_id,
            similarity_score=rec.similarity_score
        )
        
        if rec.pesticide_id:
            pest_result = await db.execute(
                select(Pesticide).filter(Pesticide.id == rec.pesticide_id)
            )
            pesticide = pest_result.scalars().first()
            if pesticide:
                rec_item.pesticide_name = pesticide.name
        
        if rec.fertilizer_id:
            fert_result = await db.execute(
                select(Fertilizer).filter(Fertilizer.id == rec.fertilizer_id)
            )
            fertilizer = fert_result.scalars().first()
            if fertilizer:
                rec_item.fertilizer_name = fertilizer.name
        
        recommendations_list.append(rec_item)
    
    return PredictionResponse(
        id=prediction.id,
        user_id=prediction.user_id,
        image_url=prediction.image_url,
        disease_id=prediction.disease_id,
        disease_name=disease_name,
        confidence_score=prediction.confidence_score,
        created_at=prediction.created_at,
        recommendations=recommendations_list
    )

@router.get("/{prediction_id}/report")
async def generate_pdf_report(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate and download PDF report for a prediction"""
    # Get prediction
    pred_result = await db.execute(
        select(Prediction).filter(
            Prediction.id == prediction_id,
            Prediction.user_id == current_user.id
        )
    )
    prediction = pred_result.scalars().first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    # Get disease info
    disease_data = {}
    if prediction.disease_id:
        disease_result = await db.execute(
            select(Disease).filter(Disease.id == prediction.disease_id)
        )
        disease = disease_result.scalars().first()
        if disease:
            disease_data = {
                "name": disease.name,
                "description": disease.description,
                "symptoms": disease.symptoms,
                "causes": disease.causes,
                "severity_level": disease.severity_level
            }
    
    # Get recommendations with full details
    recs_result = await db.execute(
        select(Recommendation).filter(Recommendation.prediction_id == prediction.id)
    )
    recommendations = recs_result.scalars().all()
    
    recommendations_list = []
    for rec in recommendations:
        rec_data = {
            "similarity_score": rec.similarity_score
        }
        
        if rec.pesticide_id:
            pest_result = await db.execute(
                select(Pesticide).filter(Pesticide.id == rec.pesticide_id)
            )
            pesticide = pest_result.scalars().first()
            if pesticide:
                rec_data.update({
                    "pesticide_name": pesticide.name,
                    "active_ingredient": pesticide.active_ingredient,
                    "dosage": pesticide.dosage,
                    "application_method": pesticide.application_method
                })
        
        if rec.fertilizer_id:
            fert_result = await db.execute(
                select(Fertilizer).filter(Fertilizer.id == rec.fertilizer_id)
            )
            fertilizer = fert_result.scalars().first()
            if fertilizer:
                rec_data.update({
                    "fertilizer_name": fertilizer.name,
                    "composition": fertilizer.composition,
                    "dosage": fertilizer.dosage,
                    "application_stage": fertilizer.application_stage
                })
        
        recommendations_list.append(rec_data)
    
    # User data
    user_data = {
        "name": current_user.name,
        "email": current_user.email,
        "farm_name": current_user.farm_name or "N/A"
    }
    
    # Prediction data
    prediction_data = {
        "confidence_score": prediction.confidence_score,
        "created_at": prediction.created_at.strftime("%B %d, %Y %I:%M %p")
    }
    
    # Generate PDF
    pdf_buffer = pdf_generator.generate_report(
        prediction_data=prediction_data,
        user_data=user_data,
        disease_data=disease_data,
        recommendations=recommendations_list
    )
    
    # Save report record
    report = Report(
        prediction_id=prediction.id,
        file_url=f"report_{prediction.id}.pdf"
    )
    db.add(report)
    await db.commit()
    
    # Return PDF as download
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=agrivision_report_{prediction_id}.pdf"
        }
    )
