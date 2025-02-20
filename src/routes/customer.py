from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..models.models import Customer
from ..schemas.schemas import CustomerCreate, Customer as CustomerSchema, CustomerWithAppointments

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=CustomerSchema)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = Customer(
        email=customer.email,
        full_name=customer.full_name,
        phone_number=customer.phone_number
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=List[CustomerSchema])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=CustomerWithAppointments)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerSchema)
def update_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    for field, value in customer.dict().items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"} 