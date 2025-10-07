from dataclasses import dataclass
from uuid import UUID

@dataclass
class Company:
    id: UUID
    name: str
    email: str
