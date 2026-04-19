from app.core.config import settings


def calculate_gst(*, subtotal: float, client_state: str | None) -> dict[str, float]:
    """
    Simple GST engine for intra-state vs inter-state calculation.
    """
    client_state_norm = (client_state or "").strip().upper()
    company_state_norm = (settings.company_state or "").strip().upper()

    subtotal = float(subtotal or 0.0)

    if client_state_norm and company_state_norm and client_state_norm == company_state_norm:
        cgst = subtotal * settings.gst_cgst_rate
        sgst = subtotal * settings.gst_sgst_rate
        igst = 0.0
    else:
        cgst = 0.0
        sgst = 0.0
        igst = subtotal * settings.gst_igst_rate

    total = subtotal + cgst + sgst + igst
    return {"cgst": cgst, "sgst": sgst, "igst": igst, "total": total}
