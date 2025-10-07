from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from company.infrastructure.postgres.database import SessionLocal
from company.infrastructure.repositories.company_repository import SQLAlchemyCompanyRepository
from company.application.company_service import CompanyService
from company.infrastructure.schemas.company_schema import CompanyResponse

app = FastAPI(title="Companies API")

# Dependencia DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/companies", response_model=list[CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    repo = SQLAlchemyCompanyRepository(db)
    service = CompanyService(repo)
    return service.list_companies()

@app.get("/companies/{company_id}", response_model=CompanyResponse)
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    repo = SQLAlchemyCompanyRepository(db)
    service = CompanyService(repo)
    company = service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
