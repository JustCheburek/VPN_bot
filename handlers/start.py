import logging

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.exceptions import TelegramBadRequest

from config import settings
from services.xui import ensure_client_exists

logger = logging.getLogger(__name__)
router = Router()

SUBSCRIBED_STATUSES = {"member", "administrator", "creator"}

VPN_MESSAGE = """
🔐 <b>Твой персональный VPN ключ</b>

Ключ предоставляется индивидуально под каждого человека и может конфликтовать при его распространении. В ключе предоставляется 3 соединения. 1 соединение — 1 устройство. Если хотите больше — пишите @JustCheburek.

<b>VPN ключ (ссылка-подписка):</b>
<code>https://sub.m-br.ru/vpn/{tg_id}</code>

<b>Как использовать:</b>
1. Скачай <b>Клиент</b> (кнопка ниже)
2. Открой приложение и нажми <b>«+»</b> или <b>«Добавить»</b>
3. <b>Скопируй</b> VPN ключ
3. Выбери <b>«Вставить из буфера обмена»</b>
5. Подключись — готово!
"""


def build_vpn_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Happ (рекомендуется)", url="https://www.happ.su/main/ru")]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id

    try:
        member = await bot.get_chat_member(settings.CHANNEL_ID, user_id)
        is_subscribed = member.status in SUBSCRIBED_STATUSES
    except TelegramBadRequest as e:
        logger.error("Failed to check channel membership for user %s: %s", user_id, e)
        await message.answer(
            "⚠️ Произошла ошибка при проверке подписки. Попробуйте позже. Админ уже осведомлён."
        )
        await bot.send_message(
            settings.ADMIN_ID,
            f"❌ Ошибка проверки подписки для user <code>{user_id}</code>:\n<code>{e}</code>",
            parse_mode="HTML",
        )
        return

    if not is_subscribed:
        await message.answer(
            "❌ <b>Доступ закрыт</b>\n\n"
            "Для получения VPN ключа необходима подписка на закрытый канал.\n"
            "Напишите <b>@JustCheburek</b>, чтобы получить доступ.",
            parse_mode="HTML",
        )
        return

    try:
        await ensure_client_exists(name=message.from_user.username, tg_id=user_id)
    except Exception as e:
        logger.error("Failed to ensure VPN client for user %s: %s", user_id, e)
        await message.answer(
            "⚠️ Произошла ошибка, попробуйте позже. Админ уже осведомлён."
        )
        await bot.send_message(
            settings.ADMIN_ID,
            f"❌ Ошибка создания VPN клиента для user <code>{user_id}</code>:\n<code>{e}</code>",
            parse_mode="HTML",
        )
        return

    await message.answer(
        VPN_MESSAGE.format(tg_id=user_id),
        parse_mode="HTML",
        reply_markup=build_vpn_keyboard(),
    )
