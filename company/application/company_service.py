from typing import List, Optional
from uuid import UUID
from company.domain.models import Company
from company.domain.repositories import CompanyRepository

class CompanyService:
    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    def list_companies(self) -> List[Company]:
        return self.repository.get_all()

    def get_company(self, company_id: UUID) -> Optional[Company]:
        return self.repository.get_by_id(company_id)
