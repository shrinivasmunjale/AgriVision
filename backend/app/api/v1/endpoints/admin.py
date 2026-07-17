from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.api.deps import RoleChecker, get_current_user
from app.models.user import User
from app.models.disease import Disease
from app.models.pesticide import Pesticide
from app.models.fertilizer import Fertilizer
from app.models.audit_log import AuditLog
from app.models.prediction import Prediction
from app.schemas.disease import DiseaseCreate, DiseaseUpdate, DiseaseResponse
from app.schemas.pesticide import PesticideCreate, PesticideUpdate, PesticideResponse
from app.schemas.fertilizer import FertilizerCreate, FertilizerUpdate, FertilizerResponse

router = APIRouter()
require_admin = RoleChecker(["admin"])

# ==================== DISEASE CRUD ====================

@router.get("/diseases", response_model=List[DiseaseResponse])
async def get_diseases(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all diseases"""
    result = await db.execute(
        select(Disease).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/diseases", response_model=DiseaseResponse, status_code=status.HTTP_201_CREATED)
async def create_disease(
    disease_in: DiseaseCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new disease"""
    disease = Disease(**disease_in.model_dump())
    db.add(disease)
    await db.commit()
    await db.refresh(disease)
    
    # Log audit
    audit = AuditLog(
        admin_id=current_user.id,
        action="CREATE",
        entity="disease",
        entity_id=str(disease.id)
    )
    db.add(audit)
    await db.commit()
    
    return disease

@router.put("/diseases/{disease_id}", response_model=DiseaseResponse)
async def update_disease(
    disease_id: int,
    disease_in: DiseaseUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a disease"""
    result = await db.execute(select(Disease).filter(Disease.id == disease_id))
    disease = result.scalars().first()
    
    if not disease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease not found"
        )
    
    # Update fields
    update_data = disease_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(disease, field, value)
    
    await db.commit()
    await db.refresh(disease)
    
    # Log audit
    audit = AuditLog(
        admin_id=current_user.id,
        action="UPDATE",
        entity="disease",
        entity_id=str(disease.id)
    )
    db.add(audit)
    await db.commit()
    
    return disease

@router.delete("/diseases/{disease_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_disease(
    disease_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a disease"""
    result = await db.execute(select(Disease).filter(Disease.id == disease_id))
    disease = result.scalars().first()
    
    if not disease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease not found"
        )
    
    # Log audit before delete
    audit = AuditLog(
        admin_id=current_user.id,
        action="DELETE",
        entity="disease",
        entity_id=str(disease.id)
    )
    db.add(audit)
    
    await db.delete(disease)
    await db.commit()

# ==================== PESTICIDE CRUD ====================

@router.get("/pesticides", response_model=List[PesticideResponse])
async def get_pesticides(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all pesticides"""
    result = await db.execute(
        select(Pesticide).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/pesticides", response_model=PesticideResponse, status_code=status.HTTP_201_CREATED)
async def create_pesticide(
    pesticide_in: PesticideCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new pesticide"""
    pesticide = Pesticide(**pesticide_in.model_dump())
    db.add(pesticide)
    await db.commit()
    await db.refresh(pesticide)
    
    # Log audit
    audit = AuditLog(
        admin_id=current_user.id,
        action="CREATE",
        entity="pesticide",
        entity_id=str(pesticide.id)
    )
    db.add(audit)
    await db.commit()
    
    return pesticide

@router.put("/pesticides/{pesticide_id}", response_model=PesticideResponse)
async def update_pesticide(
    pesticide_id: int,
    pesticide_in: PesticideUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a pesticide"""
    result = await db.execute(select(Pesticide).filter(Pesticide.id == pesticide_id))
    pesticide = result.scalars().first()
    
    if not pesticide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pesticide not found"
        )
    
    # Update fields
    update_data = pesticide_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pesticide, field, value)
    
    await db.commit()
    await db.refresh(pesticide)
    
    # Log audit
    audit = AuditLog(
        admin_id=current_user.id,
        action="UPDATE",
        entity="pesticide",
        entity_id=str(pesticide.id)
    )
    db.add(audit)
    await db.commit()
    
    return pesticide

@router.delete("/pesticides/{pesticide_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pesticide(
    pesticide_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a pesticide"""
    result = await db.execute(select(Pesticide).filter(Pesticide.id == pesticide_id))
    pesticide = result.scalars().first()
    
    if not pesticide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pesticide not found"
        )
    
    # Log audit before delete
    audit = AuditLog(
        admin_id=current_user.id,
        action="DELETE",
        entity="pesticide",
        entity_id=str(pesticide.id)
    )
    db.add(audit)
    
    await db.delete(pesticide)
    await db.commit()

# ==================== FERTILIZER CRUD ====================

@router.get("/fertilizers", response_model=List[FertilizerResponse])
async def get_fertilizers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all fertilizers"""
    result = await db.execute(
        select(Fertilizer).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/fertilizers", response_model=FertilizerResponse, status_code=status.HTTP_201_CREATED)
async def create_fertilizer(
    fertilizer_in: FertilizerCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new fertilizer"""
    fertilizer = Fertilizer(**fertilizer_in.model_dump())
    db.add(fertilizer)
    await db.commit()
    await db.refresh(fertilizer)
    
    # Log audit
    audit = AuditLog(
        admin_id=current_user.id,
        action="CREATE",
        entity="fertilizer",
        entity_id=str(fertilizer.id)
    )
    db.add(audit)
    await db.commit()
    
    return fertilizer

@router.put("/fertilizers/{fertilizer_id}", response_model=FertilizerResponse)
async def update_fertilizer(
    fertilizer_id: int,
    fertilizer_in: FertilizerUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a fertilizer"""
    result = await db.execute(select(Fertilizer).filter(Fertilizer.id == fertilizer_id))
    fertilizer = result.scalars().first()
    
    if not fertilizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fertilizer not found"
        )
    
    # Update fields
    update_data = fertilizer_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fertilizer, field, value)
    
    await db.commit()
    await db.refresh(fertilizer)
    
    # Log audit
    audit = AuditLog(
        admin_id=current_user.id,
        action="UPDATE",
        entity="fertilizer",
        entity_id=str(fertilizer.id)
    )
    db.add(audit)
    await db.commit()
    
    return fertilizer

@router.delete("/fertilizers/{fertilizer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fertilizer(
    fertilizer_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a fertilizer"""
    result = await db.execute(select(Fertilizer).filter(Fertilizer.id == fertilizer_id))
    fertilizer = result.scalars().first()
    
    if not fertilizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fertilizer not found"
        )
    
    # Log audit before delete
    audit = AuditLog(
        admin_id=current_user.id,
        action="DELETE",
        entity="fertilizer",
        entity_id=str(fertilizer.id)
    )
    db.add(audit)
    
    await db.delete(fertilizer)
    await db.commit()

# ==================== ANALYTICS ====================

@router.get("/analytics")
async def get_analytics(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get platform analytics"""
    
    # Total users
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar()
    
    # Total predictions
    predictions_result = await db.execute(select(func.count(Prediction.id)))
    total_predictions = predictions_result.scalar()
    
    # Disease distribution
    disease_dist_result = await db.execute(
        select(Disease.name, func.count(Prediction.id))
        .join(Prediction, Disease.id == Prediction.disease_id, isouter=True)
        .group_by(Disease.id, Disease.name)
    )
    disease_distribution = [
        {"disease": row[0], "count": row[1]} 
        for row in disease_dist_result.all()
    ]
    
    # Average confidence
    avg_confidence_result = await db.execute(
        select(func.avg(Prediction.confidence_score))
    )
    avg_confidence = avg_confidence_result.scalar() or 0.0
    
    # Recent audit logs
    audit_result = await db.execute(
        select(AuditLog)
        .order_by(desc(AuditLog.timestamp))
        .limit(10)
    )
    recent_audits = audit_result.scalars().all()
    
    return {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "average_confidence": round(avg_confidence, 2),
        "disease_distribution": disease_distribution,
        "recent_audits": [
            {
                "admin_id": audit.admin_id,
                "action": audit.action,
                "entity": audit.entity,
                "entity_id": audit.entity_id,
                "timestamp": audit.timestamp
            }
            for audit in recent_audits
        ]
    }
