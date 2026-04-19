import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.clients.models import Client
from app.modules.documents.models import Document
from app.modules.invoices.models import Invoice, InvoiceItem
from app.modules.projects.models import Project


TEMPLATES_DIR = Path("templates")
UPLOADS_DIR = Path("uploads") / "documents"


def _jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def generate_invoice_html(db: Session, invoice_id: int) -> Document:
    invoice = db.execute(select(Invoice).where(Invoice.id == invoice_id)).scalar_one_or_none()
    if not invoice:
        raise ValueError("Invoice not found")

    project = db.execute(select(Project).where(Project.id == invoice.project_id)).scalar_one_or_none()
    client = None
    if project:
        client = db.execute(select(Client).where(Client.id == project.client_id)).scalar_one_or_none()

    items = db.execute(select(InvoiceItem).where(InvoiceItem.invoice_id == invoice.id)).scalars().all()

    env = _jinja_env()
    tpl = env.get_template("documents/invoice.html")
    html = tpl.render(invoice=invoice, project=project, client=client, items=items)

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"invoice_{invoice.invoice_number}.html".replace("/", "_")
    file_path = UPLOADS_DIR / filename
    file_path.write_text(html, encoding="utf-8")

    doc = Document(entity_type="invoice", entity_id=invoice.id, doc_type="invoice", file_path=str(file_path))
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, doc_id: int) -> Document | None:
    return db.execute(select(Document).where(Document.id == doc_id)).scalar_one_or_none()

