from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class GenerateDocumentRequest(BaseModel):
    type: Literal["invoice"] = "invoice"
    entity_id: int
    format: Literal["html"] = "html"


class DocumentOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    doc_type: str
    file_path: str
    created_at: datetime

    model_config = {"from_attributes": True}

