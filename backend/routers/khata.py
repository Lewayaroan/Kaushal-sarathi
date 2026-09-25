from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

try:
    from ..database import get_db
    from .. import models, schemas
except (ImportError, ValueError):
    from database import get_db
    import models, schemas

router = APIRouter(
    prefix="/api/khata",
    tags=["khata"]
)

@router.post("", response_model=schemas.KhataResponse)
def create_transaction(transaction: schemas.KhataCreate, db: Session = Depends(get_db)):
    artisan = db.query(models.Artisan).filter(models.Artisan.id == transaction.artisan_id).first()
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan profile not found")
        
    db_transaction = models.KhataTransaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/artisan/{artisan_id}", response_model=List[schemas.KhataResponse])
def get_artisan_ledger(artisan_id: int, db: Session = Depends(get_db)):
    return db.query(models.KhataTransaction).filter(
        models.KhataTransaction.artisan_id == artisan_id
    ).order_by(models.KhataTransaction.timestamp.desc()).all()


@router.post("/sync", response_model=List[schemas.KhataResponse])
def sync_offline_transactions(transactions: List[schemas.KhataCreate], db: Session = Depends(get_db)):
    synced_items = []
    for tx in transactions:
        # Check if artisan exists
        artisan = db.query(models.Artisan).filter(models.Artisan.id == tx.artisan_id).first()
        if not artisan:
            continue # Skip invalid ones, or we could error out
            
        # Create synced entry
        db_tx = models.KhataTransaction(
            type=tx.type,
            amount=tx.amount,
            details=tx.details,
            sync_status="Synced",
            artisan_id=tx.artisan_id
        )
        db.add(db_tx)
        synced_items.append(db_tx)
        
    db.commit()
    for item in synced_items:
        db.refresh(item)
    return synced_items


@router.get("/summary/{artisan_id}")
def get_ledger_summary(artisan_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.KhataTransaction).filter(
        models.KhataTransaction.artisan_id == artisan_id
    ).all()
    
    total_sales = sum(tx.amount for tx in transactions if tx.type.upper() == "SALE")
    total_expenses = sum(tx.amount for tx in transactions if tx.type.upper() == "EXPENSE")
    net_profit = total_sales - total_expenses
    
    return {
        "artisan_id": artisan_id,
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "transaction_count": len(transactions)
    }
