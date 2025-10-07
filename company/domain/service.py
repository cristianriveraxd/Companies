"""
import unicodedata
from uuid import UUID

from sqlalchemy.orm.session import Session

from dao.city.crud import get_city_by_local_codes, get_city_id_by_name
from dao.city_company.crud import create_row, is_company_city
from dao.company.crud import get_company_by_id
from dao.modules.rut import Rut
from dao.rut import crud as rut_crud
from shared.domain.constants import Cities
from shared.infrastructure.slack.sender import send_slack
from tax.infrastructure.tax_from_rut import recognize_taxes_from_rut


class ProcessRutService:
    def __init__(self, db: Session):
        self.db = db

    def run(self, company_id: UUID) -> None:
        company = get_company_by_id(company_id=company_id, database=self.db)

        rut_boxes = rut_crud.get_rut_by_company_id(self.db, company_id)

        box_39 = rut_boxes.data.get("39", None)
        box_40 = rut_boxes.data.get("40", None)
        if box_40 is None:
            err_msg = (
                "no se encontró el campo 40 del RUT en la interpretación humana "
                "que es requerido para obtener la posición fiscal"
            )
            raise Exception(err_msg)

        city_id = Cities.BOGOTA.value

        # Verifica que ambos sean códigos numéricos (no nombres)
        if box_40 and box_39 and box_40.isdigit() and box_39.isdigit():
            city_local_code = box_40[-3:]
            departament_local_code = box_39[:2]
            city_id = get_city_by_local_codes(db=self.db, city_code=city_local_code, dpto_code=departament_local_code)

        # Si no son códigos, intenta con nombre de ciudad y departamento
        elif box_40 and not box_40.isdigit():
            normalized_city = normalize_text(box_40)
            normalize_departament = normalize_text(box_39)

            if "bogota" not in normalized_city and normalize_departament:
                city_id = get_city_id_by_name(
                    db=self.db, city_name=normalized_city, departament_name=normalize_departament
                )
            city_company = is_company_city(self.db, company_id=company_id)

        if not city_company:  # type: ignore
            create_row(self.db, company_id=company_id, city_id=city_id)

        box_70 = rut_boxes.data.get("70", 1)
        box_24 = rut_boxes.data.get("24", None)
        box_53 = rut_boxes.data.get("53", None)

        if box_24 is None:
            err_msg = (
                "no se encontró el campo 24 del RUT en la interpretación humana "
                "que es requerido para obtener la posición fiscal"
            )
            raise Exception(err_msg)

        if box_53 is None:
            err_msg = (
                "no se encontró el campo 53 del RUT en la interpretación humana "
                "que es requerido para obtener la posición fiscal"
            )
            raise Exception(err_msg)

        if not Rut.rut_recognize(self.db, company_id, box_24, box_53, box_70):
            err_msg = "no tiene los campos requeridos para obtener la posición fiscal"
            raise Exception(err_msg)

        recognize_taxes_from_rut(self.db, company_id, rut_boxes.data)

        msg = f"La empresa {company.name} se actualizó con la información disponible del RUT"
        send_slack(msg, "random")


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower().replace(",", "").replace(".", "").replace(" ", "").strip()
"""