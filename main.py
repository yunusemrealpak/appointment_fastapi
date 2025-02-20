from fastapi import FastAPI
from src.routes import customer, appointment
from src.database.database import engine
from src.models.models import Base

app = FastAPI(title="Randevu Sistemi API")

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# Routerları ekle
app.include_router(customer.router)
app.include_router(appointment.router)

@app.get("/")
def read_root():
    return {
        "message": "Randevu Sistemi API'sine Hoş Geldiniz",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }