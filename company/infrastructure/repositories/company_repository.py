from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from company.domain.models import Company
from company.domain.repositories import CompanyRepository
from company.infrastructure.postgres.database import CompanyORM

class SQLAlchemyCompanyRepository(CompanyRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Company]:
        records = self.db.query(CompanyORM).all()
        return [Company(id=r.id, name=r.name, email=r.email) for r in records]

    def get_by_id(self, company_id: UUID) -> Optional[Company]:
        r = self.db.query(CompanyORM).filter(CompanyORM.id == company_id).first()
        if r:
            return Company(id=r.id, name=r.name, email=r.email)
        return None
