import uuid
import logging

from py3xui import AsyncApi, Client

from config import settings

logger = logging.getLogger(__name__)


async def ensure_client_exists(name: str, tg_id: int) -> None:
    """Check if a client exists for the given tg_id in each inbound; if not, create one per inbound."""
    api = AsyncApi(
        host=settings.XUI_HOST,
        username=settings.XUI_USERNAME,
        password=settings.XUI_PASSWORD,
        use_tls_verify=False,
    )
    await api.login()

    for inbound_id in settings.XUI_INBOUND_IDS:
        email = f"{name} {settings.XUI_INBOUND_IDS.index(inbound_id) + 1}"
        try:
            existing: Client | None = await api.client.get_by_email(email)
        except Exception:
            existing = None

        if existing is not None:
            logger.info("Client already exists in inbound %s for tg_id=%s", inbound_id, tg_id)
            continue

        logger.info("Creating client in inbound %s for tg_id=%s", inbound_id, tg_id)
        client = Client(
            id=str(uuid.uuid4()),
            email=email,
            sub_id=str(tg_id),
            enable=True,
            tg_id=str(tg_id),
            limit_ip=0,
            total_gb=0,
            expiry_time=0,
        )
        await api.client.add(inbound_id, [client])
