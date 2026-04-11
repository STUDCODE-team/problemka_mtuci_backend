from email.mime.text import MIMEText

import aiosmtplib
from aiosmtplib.errors import SMTPException, SMTPRecipientsRefused
from fastapi import HTTPException, status

from common_lib.config.settings import settings


async def send_otp_email(to_email: str, otp: str) -> None:
    msg = MIMEText(f"Ваш код подтверждения: {otp}\n\nКод действителен {settings.OTP_TTL_SEC // 60} минут.")
    msg["Subject"] = "Код подтверждения"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
    except SMTPRecipientsRefused:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SMTP refused recipient email",
        )
    except SMTPException:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SMTP error while sending email",
        )
    except OSError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SMTP connection error",
        )
