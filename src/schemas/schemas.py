from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from ..models.models import AppointmentStatus

class CustomerBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    appointment_date: datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    customer_id: int

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None

class Appointment(AppointmentBase):
    id: int
    customer_id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AppointmentWithCustomer(Appointment):
    customer: Customer

class CustomerWithAppointments(Customer):
    appointments: List[Appointment]

class SuggestDateRequest(BaseModel):
    preferred_date: datetime
    customer_id: int

class SuggestDateResponse(BaseModel):
    suggested_dates: List[datetime] 