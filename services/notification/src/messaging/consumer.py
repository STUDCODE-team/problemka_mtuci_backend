import json
import logging
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractRobustConnection

from infrastructure.db import AsyncSessionLocal
from data.repositories.push_subscription_repository import PushSubscriptionRepository
from services.email_service import send_otp_email
from services.push_service import PushService

logger = logging.getLogger(__name__)

NOTIFICATIONS_QUEUE = "notifications"

_connection: AbstractRobustConnection | None = None


async def start_consumer(url: str) -> None:
    global _connection
    _connection = await aio_pika.connect_robust(url)
    channel = await _connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)
    await queue.consume(_on_message)
    logger.info("Notification consumer started, listening on queue '%s'", NOTIFICATIONS_QUEUE)


async def stop_consumer() -> None:
    global _connection
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None
    logger.info("Notification consumer connection closed")


async def _on_message(message: aio_pika.IncomingMessage) -> None:
    try:
        body = json.loads(message.body)
        await _handle(body)
        await message.ack()
    except Exception:
        logger.exception("Failed to process notification message, dropping")
        await message.nack(requeue=False)


async def _handle(body: dict) -> None:
    msg_type = body.get("type")

    if msg_type == "otp_email":
        await send_otp_email(to_email=body["to_email"], otp=body["otp"])

    elif msg_type == "push":
        async with AsyncSessionLocal() as session:
            repo = PushSubscriptionRepository(session)
            push_service = PushService(repo)
            await push_service.send_push_to_user(
                user_id=UUID(body["user_id"]),
                title=body["title"],
                body=body["body"],
                data=body.get("data"),
            )

    else:
        logger.warning("Unknown notification message type: %s", msg_type)
