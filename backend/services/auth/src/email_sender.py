# email_sender.py
from email.message import EmailMessage

import aiosmtplib
from fastapi import BackgroundTasks

from common_lib.config.settings import settings


async def send_email_async(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = settings.FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
    )


def send_email_bg(background: BackgroundTasks, to_email: str, subject: str, body: str):
    background.add_task(send_email_async, to_email, subject, body)
