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
from app.ml.yolo_detector import yolo_detector

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
        if prediction.disease_id and disease_name:
            recs = await recommendation_engine.get_recommendations(
                prediction.disease_id, 
                db
            )
            
            # Save and return pesticide recommendations from pesticides.json
            for pest_rec in recs["pesticides"]:
                rec = Recommendation(
                    prediction_id=prediction.id,
                    pesticide_id=pest_rec.get("pesticide_id"),
                    similarity_score=pest_rec.get("similarity_score", 0.95)
                )
                db.add(rec)
                recommendations_list.append(RecommendationItem(
                    id=0,
                    pesticide_id=pest_rec.get("pesticide_id"),
                    pesticide_name=pest_rec.get("pesticide_name"),
                    type=pest_rec.get("type"),
                    active_ingredient=pest_rec.get("active_ingredient"),
                    dosage=pest_rec.get("dosage"),
                    spray_interval=pest_rec.get("spray_interval"),
                    application_method=pest_rec.get("application_method"),
                    effectiveness=pest_rec.get("effectiveness"),
                    waiting_period=pest_rec.get("waiting_period"),
                    precautions=pest_rec.get("precautions", []),
                    priority=pest_rec.get("priority"),
                    crop_stage=pest_rec.get("crop_stage"),
                    recommendation_note=pest_rec.get("recommendation_note"),
                    similarity_score=pest_rec.get("similarity_score", 0.95)
                ))
            
            # Save fertilizer recommendations
            for fert_rec in recs["fertilizers"]:
                rec = Recommendation(
                    prediction_id=prediction.id,
                    fertilizer_id=fert_rec.get("fertilizer_id"),
                    similarity_score=fert_rec.get("similarity_score", 0.90)
                )
                db.add(rec)
                recommendations_list.append(RecommendationItem(
                    id=0,
                    fertilizer_id=fert_rec.get("fertilizer_id"),
                    fertilizer_name=fert_rec.get("fertilizer_name"),
                    composition=fert_rec.get("composition"),
                    dosage=fert_rec.get("dosage"),
                    application_stage=fert_rec.get("application_stage"),
                    similarity_score=fert_rec.get("similarity_score", 0.90)
                ))
        
        # Generate bounding box annotated image using YOLO detector
        annotated_image_url = None
        try:
            annotated_bytes, _ = await yolo_detector.annotate_image(
                image_input=ml_pred["image_url"],
                disease_name=disease_name or ml_pred.get("disease_name", "Infected Area"),
                confidence=ml_pred["confidence_score"]
            )
            annotated_url = await storage_client.upload_file(
                annotated_bytes,
                f"annotated_{uuid.uuid4()}.jpg",
                "image/jpeg"
            )
            annotated_image_url = annotated_url
        except Exception as bbox_err:
            print(f"[WARNING] Bounding box annotation failed: {bbox_err}")
            annotated_image_url = ml_pred["image_url"]

        prediction.annotated_image_url = annotated_image_url

        predictions_response.append(PredictionResponse(
            id=prediction.id,
            user_id=prediction.user_id,
            image_url=prediction.image_url,
            annotated_image_url=prediction.annotated_image_url,
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
        recommendations_list = []
        if disease_name and disease_name != "Healthy":
            pesticide_info = recommendation_engine.get_pesticide_products_by_disease_name(disease_name)
            for prod in pesticide_info.get("products", []):
                recommendations_list.append(RecommendationItem(
                    id=prod.get("pesticide_id", 0),
                    pesticide_id=prod.get("pesticide_id"),
                    pesticide_name=prod.get("pesticide_name"),
                    type=prod.get("type"),
                    active_ingredient=prod.get("active_ingredient"),
                    dosage=prod.get("dosage"),
                    spray_interval=prod.get("spray_interval"),
                    application_method=prod.get("application_method"),
                    effectiveness=prod.get("effectiveness"),
                    waiting_period=prod.get("waiting_period"),
                    precautions=prod.get("precautions", []),
                    priority=prod.get("priority"),
                    crop_stage=prod.get("crop_stage"),
                    recommendation_note=prod.get("recommendation_note"),
                    similarity_score=prod.get("similarity_score", 0.95)
                ))
            
            # Fetch fertilizers
            fert_result = await db.execute(select(Fertilizer))
            fertilizers = fert_result.scalars().all()
            for idx, fert in enumerate(fertilizers[:2], start=1):
                recommendations_list.append(RecommendationItem(
                    id=idx,
                    fertilizer_id=fert.id,
                    fertilizer_name=fert.name,
                    composition=fert.composition,
                    dosage=fert.dosage,
                    application_stage=fert.application_stage,
                    similarity_score=max(0.85, round(0.95 - (idx - 1) * 0.05, 2))
                ))
        
        response.append(PredictionResponse(
            id=pred.id,
            user_id=pred.user_id,
            image_url=pred.image_url,
            annotated_image_url=getattr(pred, 'annotated_image_url', None) or pred.image_url,
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
    
    # Get rich recommendations from pesticides.json
    recommendations_list = []
    if disease_name and disease_name != "Healthy":
        pesticide_info = recommendation_engine.get_pesticide_products_by_disease_name(disease_name)
        for prod in pesticide_info.get("products", []):
            recommendations_list.append(RecommendationItem(
                id=prod.get("pesticide_id", 0),
                pesticide_id=prod.get("pesticide_id"),
                pesticide_name=prod.get("pesticide_name"),
                type=prod.get("type"),
                active_ingredient=prod.get("active_ingredient"),
                dosage=prod.get("dosage"),
                spray_interval=prod.get("spray_interval"),
                application_method=prod.get("application_method"),
                effectiveness=prod.get("effectiveness"),
                waiting_period=prod.get("waiting_period"),
                precautions=prod.get("precautions", []),
                priority=prod.get("priority"),
                crop_stage=prod.get("crop_stage"),
                recommendation_note=prod.get("recommendation_note"),
                similarity_score=prod.get("similarity_score", 0.95)
            ))
        
        # Add fertilizer recommendations
        fert_result = await db.execute(select(Fertilizer))
        fertilizers = fert_result.scalars().all()
        for idx, fert in enumerate(fertilizers[:2], start=1):
            recommendations_list.append(RecommendationItem(
                id=idx,
                fertilizer_id=fert.id,
                fertilizer_name=fert.name,
                composition=fert.composition,
                dosage=fert.dosage,
                application_stage=fert.application_stage,
                similarity_score=max(0.85, round(0.95 - (idx - 1) * 0.05, 2))
            ))
    
    return PredictionResponse(
        id=prediction.id,
        user_id=prediction.user_id,
        image_url=prediction.image_url,
        annotated_image_url=getattr(prediction, 'annotated_image_url', None) or prediction.image_url,
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
    recommendations_list = []
    disease_name = disease_data.get("name")
    if disease_name and disease_name != "Healthy":
        pesticide_info = recommendation_engine.get_pesticide_products_by_disease_name(disease_name)
        for prod in pesticide_info.get("products", []):
            recommendations_list.append({
                "pesticide_name": prod.get("pesticide_name"),
                "type": prod.get("type"),
                "active_ingredient": prod.get("active_ingredient"),
                "dosage": prod.get("dosage"),
                "spray_interval": prod.get("spray_interval"),
                "application_method": prod.get("application_method"),
                "effectiveness": prod.get("effectiveness"),
                "waiting_period": prod.get("waiting_period"),
                "precautions": prod.get("precautions", []),
                "similarity_score": prod.get("similarity_score", 0.95)
            })
        
        # Add fertilizers
        fert_result = await db.execute(select(Fertilizer))
        fertilizers = fert_result.scalars().all()
        for idx, fert in enumerate(fertilizers[:2], start=1):
            recommendations_list.append({
                "fertilizer_name": fert.name,
                "composition": fert.composition,
                "dosage": fert.dosage,
                "application_stage": fert.application_stage,
                "similarity_score": max(0.85, round(0.95 - (idx - 1) * 0.05, 2))
            })
    
    # User data
    user_data = {
        "name": current_user.name,
        "email": current_user.email,
        "farm_name": current_user.farm_name or "N/A"
    }
    
    # Prediction data
    prediction_data = {
        "confidence_score": prediction.confidence_score,
        "created_at": prediction.created_at.strftime("%B %d, %Y %I:%M %p"),
        "image_url": prediction.image_url,
        "annotated_image_url": getattr(prediction, 'annotated_image_url', None) or prediction.image_url
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

@router.delete("/{prediction_id}", status_code=status.HTTP_200_OK)
async def delete_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a prediction by ID (User can delete own prediction)"""
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
            detail="Prediction not found or not authorized to delete"
        )
    
    await db.delete(prediction)
    await db.commit()
    
    return {"message": "Prediction deleted successfully", "id": prediction_id}

