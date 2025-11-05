# email_sender.py
from email.message import EmailMessage

import aiosmtplib
from fastapi import BackgroundTasks

from libs.common.config.settings import settings

SMTP_HOST = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "your_email@example.com"
SMTP_PASSWORD = "your_password"
FROM_EMAIL = "your_email@example.com"


async def send_email_async(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = settings.from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=True,
        username=settings.smtp_user,
        password=settings.smtp_password,
    )


def send_email_bg(background: BackgroundTasks, to_email: str, subject: str, body: str):
    background.add_task(send_email_async, to_email, subject, body)
