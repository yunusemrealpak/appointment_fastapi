from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from ..database.database import get_db
from ..models.models import Appointment, Customer, AppointmentStatus
from ..schemas.schemas import (
    AppointmentCreate,
    Appointment as AppointmentSchema,
    AppointmentUpdate,
    AppointmentWithCustomer,
    SuggestDateRequest,
    SuggestDateResponse
)

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/suggest-date", response_model=SuggestDateResponse)
def suggest_date(request: SuggestDateRequest, db: Session = Depends(get_db)):
    # Müşterinin tercih ettiği tarih etrafında 3 gün içinde boş zaman dilimleri öner
    suggested_dates = []
    start_date = request.preferred_date.date()
    
    for i in range(-1, 2):  # -1, 0, 1 günler için kontrol
        current_date = start_date + timedelta(days=i)
        # Her gün için 09:00-17:00 arası saatleri kontrol et
        for hour in range(9, 17):
            check_time = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
            existing_appointment = db.query(Appointment).filter(
                Appointment.appointment_date == check_time,
                Appointment.status != AppointmentStatus.CANCELLED
            ).first()
            
            if not existing_appointment:
                suggested_dates.append(check_time)
    
    return SuggestDateResponse(suggested_dates=suggested_dates[:5])  # En fazla 5 öneri

@router.post("/book-appointment", response_model=AppointmentWithCustomer)
def book_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    # Müşterinin varlığını kontrol et
    customer = db.query(Customer).filter(Customer.id == appointment.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Seçilen tarihte başka randevu var mı kontrol et
    existing_appointment = db.query(Appointment).filter(
        Appointment.appointment_date == appointment.appointment_date,
        Appointment.status != AppointmentStatus.CANCELLED
    ).first()
    
    if existing_appointment:
        raise HTTPException(status_code=400, detail="This time slot is already booked")
    
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.post("/cancel-appointment/{appointment_id}", response_model=AppointmentSchema)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment

@router.get("/appointment-status/{appointment_id}", response_model=AppointmentWithCustomer)
def get_appointment_status(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.post("/reschedule-appointment/{appointment_id}", response_model=AppointmentSchema)
def reschedule_appointment(
    appointment_id: int,
    new_date: datetime,
    db: Session = Depends(get_db)
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Yeni tarihte başka randevu var mı kontrol et
    existing_appointment = db.query(Appointment).filter(
        Appointment.appointment_date == new_date,
        Appointment.status != AppointmentStatus.CANCELLED
    ).first()
    
    if existing_appointment:
        raise HTTPException(status_code=400, detail="This time slot is already booked")
    
    appointment.appointment_date = new_date
    db.commit()
    db.refresh(appointment)
    return appointment

@router.get("/", response_model=List[AppointmentWithCustomer])
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    status: AppointmentStatus = None,
    db: Session = Depends(get_db)
):
    query = db.query(Appointment)
    if status:
        query = query.filter(Appointment.status == status)
    appointments = query.offset(skip).limit(limit).all()
    return appointments

@router.get("/customer/{customer_id}", response_model=List[AppointmentSchema])
def get_customer_appointments(
    customer_id: int,
    status: AppointmentStatus = None,
    db: Session = Depends(get_db)
):
    query = db.query(Appointment).filter(Appointment.customer_id == customer_id)
    if status:
        query = query.filter(Appointment.status == status)
    return query.all() 