"""Simple SMTP email service for sending OTP verification emails."""
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger("clfms")


def send_otp_email(user_email: str, user_name: str, otp: str) -> None:
    """Send a 6-digit OTP verification email to the user."""
    subject = "Your CLFMS verification code"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; max-width: 560px; margin: 0 auto; padding: 20px;">
        <div style="background: #1e293b; padding: 24px; border-radius: 12px; margin-bottom: 24px; text-align: center;">
            <h2 style="color: #fff; margin: 0; font-size: 22px;">CLFMS — Verify Your Email</h2>
        </div>
        <p>Hi {user_name or "there"},</p>
        <p>Use the code below to verify your email address. It expires in <strong>10 minutes</strong>.</p>
        <div style="background: #f1f5f9; border-radius: 12px; padding: 32px; text-align: center; margin: 24px 0;">
            <p style="font-size: 42px; font-weight: bold; letter-spacing: 10px; color: #2563eb; margin: 0;">{otp}</p>
        </div>
        <p style="color: #64748b; font-size: 13px;">
            If you didn't create a CLFMS account, you can safely ignore this email.
        </p>
    </body>
    </html>
    """

    text_body = (
        f"Your CLFMS verification code is: {otp}\n\n"
        f"It expires in 10 minutes.\n\n"
        f"If you did not sign up, ignore this email."
    )

    _send_email(to=user_email, subject=subject, html_body=html_body, text_body=text_body)


def _send_email(to: str, subject: str, html_body: str, text_body: str) -> None:
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials not configured — skipping email to %s", to)
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
        logger.info("OTP email sent to %s", to)
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
