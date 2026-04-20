"""Simple SMTP email service for sending approval notifications."""
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger("clfms")


def send_approval_request_email(user_email: str, user_name: str, approval_token: str) -> None:
    """Send an approval request email to the admin."""
    approval_url = f"{settings.app_base_url}/api/v1/auth/approve/{approval_token}"

    subject = f"[CLFMS] New user signup awaiting approval: {user_email}"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 24px;">
            <h2 style="color: #fff; margin: 0;">CLFMS — New Signup Request</h2>
        </div>
        <p>A new user has signed up and is awaiting your approval:</p>
        <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
            <tr>
                <td style="padding: 8px; font-weight: bold; color: #555; width: 140px;">Name:</td>
                <td style="padding: 8px;">{user_name or "Not provided"}</td>
            </tr>
            <tr style="background: #f9f9f9;">
                <td style="padding: 8px; font-weight: bold; color: #555;">Email:</td>
                <td style="padding: 8px;">{user_email}</td>
            </tr>
        </table>
        <p>Click the button below to approve this account:</p>
        <a href="{approval_url}"
           style="display: inline-block; background: #2563eb; color: #fff; padding: 12px 28px;
                  border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 15px; margin: 8px 0;">
            Approve Account
        </a>
        <p style="color: #888; font-size: 13px; margin-top: 24px;">
            Or copy and paste this URL into your browser:<br>
            <a href="{approval_url}" style="color: #2563eb;">{approval_url}</a>
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
        <p style="color: #aaa; font-size: 12px;">
            This email was sent by CLFMS. If you did not expect this, you can ignore it.
        </p>
    </body>
    </html>
    """

    text_body = (
        f"New CLFMS signup awaiting approval.\n\n"
        f"Name: {user_name or 'Not provided'}\n"
        f"Email: {user_email}\n\n"
        f"Approve here: {approval_url}\n"
    )

    _send_email(
        to=settings.admin_approval_email,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )


def _send_email(to: str, subject: str, html_body: str, text_body: str) -> None:
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials not configured — skipping approval email to %s", to)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        context = ssl.create_default_context()
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as server:
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_from, to, msg.as_string())
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_from, to, msg.as_string())
        logger.info("Approval email sent to %s", to)
    except Exception as exc:
        logger.error("Failed to send approval email to %s: %s", to, exc)
