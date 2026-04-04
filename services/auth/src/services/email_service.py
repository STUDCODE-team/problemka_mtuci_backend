from email.mime.text import MIMEText

import aiosmtplib

from common_lib.config.settings import settings


async def send_otp_email(to_email: str, otp: str) -> None:
    msg = MIMEText(f"Ваш код подтверждения: {otp}\n\nКод действителен {settings.OTP_TTL_SEC // 60} минут.")
    msg["Subject"] = "Код подтверждения"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
