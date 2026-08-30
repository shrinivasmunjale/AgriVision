from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc
from typing import List, Optional, Dict
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
    IgnoredItem,
    BatchReportRequest,
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
    Analyze uploaded images using ML inference service, track ignored images with
    explicit reasons, group valid results by disease, and return batch summary metrics.
    """
    if not request.image_urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image URLs provided"
        )

    total_uploaded = len(request.image_urls)

    # Call ML inference service -> {valid_predictions, ignored_images}
    ml_result = await ml_service.predict_disease(request.image_urls, request.filenames)
    valid_preds = ml_result.get("valid_predictions") or []
    ignored_preds = ml_result.get("ignored_images") or []

    predictions_response = []

    for ml_pred in valid_preds:
        # Determine life stage based on input age or provided stage
        active_life_stage = recommendation_engine.determine_life_stage(
            crop_age_days=request.crop_age_days,
            life_stage=request.life_stage
        )

        # Create prediction record
        prediction = Prediction(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            image_url=ml_pred.get("image_url", ""),
            disease_id=ml_pred.get("disease_id"),
            confidence_score=ml_pred.get("confidence_score", 0.0),
            bounding_boxes=ml_pred.get("bounding_boxes", []),
            crop_age_days=request.crop_age_days,
            life_stage=active_life_stage
        )
        db.add(prediction)
        await db.flush()

        # Get disease name
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
                db,
                crop_age_days=request.crop_age_days,
                life_stage=request.life_stage
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
            disease_name=disease_name or ml_pred.get("disease_name"),
            confidence_score=prediction.confidence_score,
            bounding_boxes=prediction.bounding_boxes or ml_pred.get("bounding_boxes") or [],
            crop_age_days=prediction.crop_age_days,
            life_stage=prediction.life_stage,
            created_at=prediction.created_at,
            recommendations=recommendations_list,
            disease_details=recommendation_engine.get_disease_knowledge(disease_name or ml_pred.get("disease_name"))
        ))

    await db.commit()

    # Build disease summary + healthy/infected counts from valid predictions
    disease_summary: Dict[str, List[str]] = {}
    healthy = 0
    infected = 0
    for ml_pred, pred_resp in zip(valid_preds, predictions_response):
        name = pred_resp.disease_name or ml_pred.get("disease_name") or "Unknown"
        fname = ml_pred.get("filename") or "image"
        disease_summary.setdefault(name, []).append(fname)
        if pred_resp.disease_id == 1 or ("healthy" in name.lower()):
            healthy += 1
        else:
            infected += 1

    ignored_images = [
        IgnoredItem(
            filename=item.get("filename") or "image",
            reason=item.get("reason") or "Invalid image"
        )
        for item in ignored_preds
    ]

    processed = len(predictions_response)
    ignored = len(ignored_images)

    return AnalyzeResponse(
        predictions=predictions_response,
        valid_predictions=predictions_response,
        ignored_images=ignored_images,
        disease_summary=disease_summary,
        total_uploaded=total_uploaded,
        processed=processed,
        ignored=ignored,
        healthy=healthy,
        infected=infected,
        message=(
            f"Batch analysis complete: {processed} valid, {ignored} ignored, "
            f"{healthy} healthy, {infected} infected out of {total_uploaded} images."
        )
    )

@router.post("/report/batch")
async def generate_batch_report(
    request: BatchReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a batch PDF report covering all detected diseases from a scan batch.
    """
    user_data = {
        "name": current_user.name,
        "email": current_user.email,
        "farm_name": current_user.farm_name or "N/A"
    }

    batch_data = {
        "total_uploaded": request.total_uploaded,
        "processed": request.processed,
        "ignored": request.ignored,
        "healthy": request.healthy,
        "infected": request.infected,
        "disease_summary": request.disease_summary,
        "disease_imgs": list(request.disease_summary.keys()),
        "ignored_images": [
            {"filename": item.filename, "reason": item.reason}
            for item in request.ignored_images
        ],
        "valid_predictions": request.valid_predictions or request.predictions or [],
    }

    pdf_buffer = pdf_generator.generate_batch_report(
        user_data=user_data,
        batch_data=batch_data
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=agrivision_batch_report.pdf"
        }
    )

@router.get("", response_model=List[PredictionResponse])
async def get_predictions(
    skip: int = 0,
    limit: int = 20,
    disease_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get prediction history for current user with eager loaded relationships (eliminating N+1 queries)"""
    query = (
        select(Prediction)
        .options(
            selectinload(Prediction.disease),
            selectinload(Prediction.recommendations).selectinload(Recommendation.pesticide),
            selectinload(Prediction.recommendations).selectinload(Recommendation.fertilizer),
        )
        .filter(Prediction.user_id == current_user.id)
    )
    
    if disease_id:
        query = query.filter(Prediction.disease_id == disease_id)
    
    query = query.order_by(desc(Prediction.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    # Build response using pre-fetched eager loaded relationships
    response = []
    for pred in predictions:
        disease_name = pred.disease.name if pred.disease else None
        
        recommendations_list = []
        for rec in pred.recommendations:
            rec_item = RecommendationItem(
                id=rec.id,
                pesticide_id=rec.pesticide_id,
                fertilizer_id=rec.fertilizer_id,
                similarity_score=rec.similarity_score,
                pesticide_name=rec.pesticide.name if rec.pesticide else None,
                fertilizer_name=rec.fertilizer.name if rec.fertilizer else None,
            )
            recommendations_list.append(rec_item)
        
        response.append(PredictionResponse(
            id=pred.id,
            user_id=pred.user_id,
            image_url=pred.image_url,
            disease_id=pred.disease_id,
            disease_name=disease_name,
            confidence_score=pred.confidence_score,
            bounding_boxes=getattr(pred, "bounding_boxes", None) or [],
            crop_age_days=getattr(pred, "crop_age_days", None),
            life_stage=getattr(pred, "life_stage", None),
            created_at=pred.created_at,
            recommendations=recommendations_list,
            disease_details=recommendation_engine.get_disease_knowledge(disease_name)
        ))
    
    return response


@router.delete("/clear")
async def clear_prediction_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete all prediction history for current user"""
    result = await db.execute(
        select(Prediction).filter(Prediction.user_id == current_user.id)
    )
    predictions = result.scalars().all()
    
    count = len(predictions)
    for pred in predictions:
        await db.delete(pred)
        
    await db.commit()
    
    return {
        "message": f"Successfully cleared {count} prediction record(s)",
        "deleted_count": count
    }


@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a single prediction record by ID (Admin can delete any prediction)"""
    if current_user.role == "admin":
        stmt = select(Prediction).filter(Prediction.id == prediction_id)
    else:
        stmt = select(Prediction).filter(
            Prediction.id == prediction_id,
            Prediction.user_id == current_user.id
        )
        
    result = await db.execute(stmt)
    prediction = result.scalars().first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
        
    await db.delete(prediction)
    await db.commit()
    
    return {
        "message": "Prediction deleted successfully",
        "id": prediction_id
    }


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed prediction by ID with eager loaded relationships (Admin can view any prediction)"""
    query = (
        select(Prediction)
        .options(
            selectinload(Prediction.disease),
            selectinload(Prediction.recommendations).selectinload(Recommendation.pesticide),
            selectinload(Prediction.recommendations).selectinload(Recommendation.fertilizer),
        )
    )
    if current_user.role == "admin":
        query = query.filter(Prediction.id == prediction_id)
    else:
        query = query.filter(
            Prediction.id == prediction_id,
            Prediction.user_id == current_user.id
        )
        
    result = await db.execute(query)
    prediction = result.scalars().first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    disease_name = prediction.disease.name if prediction.disease else None
    
    recommendations_list = []
    for rec in prediction.recommendations:
        recommendations_list.append(RecommendationItem(
            id=rec.id,
            pesticide_id=rec.pesticide_id,
            fertilizer_id=rec.fertilizer_id,
            similarity_score=rec.similarity_score,
            pesticide_name=rec.pesticide.name if rec.pesticide else None,
            fertilizer_name=rec.fertilizer.name if rec.fertilizer else None,
        ))
    
    return PredictionResponse(
        id=prediction.id,
        user_id=prediction.user_id,
        image_url=prediction.image_url,
        disease_id=prediction.disease_id,
        disease_name=disease_name,
        confidence_score=prediction.confidence_score,
        bounding_boxes=getattr(prediction, "bounding_boxes", None) or [],
        crop_age_days=getattr(prediction, "crop_age_days", None),
        life_stage=getattr(prediction, "life_stage", None),
        created_at=prediction.created_at,
        recommendations=recommendations_list,
        disease_details=recommendation_engine.get_disease_knowledge(disease_name)
    )

@router.get("/{prediction_id}/report")
async def generate_pdf_report(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate and download PDF report for a prediction with eager loaded relationships (Admin can download for any prediction)"""
    query = (
        select(Prediction)
        .options(
            selectinload(Prediction.disease),
            selectinload(Prediction.recommendations).selectinload(Recommendation.pesticide),
            selectinload(Prediction.recommendations).selectinload(Recommendation.fertilizer),
        )
    )
    if current_user.role == "admin":
        query = query.filter(Prediction.id == prediction_id)
    else:
        query = query.filter(
            Prediction.id == prediction_id,
            Prediction.user_id == current_user.id
        )
        
    pred_result = await db.execute(query)
    prediction = pred_result.scalars().first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    disease_data = {}
    if prediction.disease:
        disease_data = {
            "name": prediction.disease.name,
            "description": prediction.disease.description,
            "symptoms": prediction.disease.symptoms,
            "causes": prediction.disease.causes,
            "severity_level": prediction.disease.severity_level
        }
    
    recommendations_list = []
    for rec in prediction.recommendations:
        rec_data = {
            "similarity_score": rec.similarity_score
        }
        
        if rec.pesticide:
            rec_data.update({
                "pesticide_name": rec.pesticide.name,
                "active_ingredient": rec.pesticide.active_ingredient,
                "dosage": rec.pesticide.dosage,
                "application_method": rec.pesticide.application_method
            })
        
        if rec.fertilizer:
            rec_data.update({
                "fertilizer_name": rec.fertilizer.name,
                "composition": rec.fertilizer.composition,
                "dosage": rec.fertilizer.dosage,
                "application_stage": rec.fertilizer.application_stage
            })
        
        recommendations_list.append(rec_data)
    
    user_data = {
        "name": current_user.name,
        "email": current_user.email,
        "farm_name": current_user.farm_name or "N/A"
    }
    
    prediction_data = {
        "confidence_score": prediction.confidence_score,
        "created_at": prediction.created_at.strftime("%B %d, %Y %I:%M %p"),
        "image_url": getattr(prediction, "image_url", None)
    }
    
    pdf_buffer = pdf_generator.generate_report(
        prediction_data=prediction_data,
        user_data=user_data,
        disease_data=disease_data,
        recommendations=recommendations_list
    )
    
    report = Report(
        prediction_id=prediction.id,
        file_url=f"report_{prediction.id}.pdf"
    )
    db.add(report)
    await db.commit()
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=agrivision_report_{prediction_id}.pdf"
        }
    )

