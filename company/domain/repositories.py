from typing import List, Optional
from uuid import UUID
from .models import Company

class CompanyRepository:
    def get_all(self) -> List[Company]:
        raise NotImplementedError

    def get_by_id(self, company_id: UUID) -> Optional[Company]:
        raise NotImplementedError
