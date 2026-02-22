from telegram import Update, InlineQueryResultPhoto, InlineQueryResultsButton
from telegram.ext import ContextTypes
import uuid
import aiohttp
from io import BytesIO

from core.utils import has_active_private_chat, check_user
from core.config_loader import TEXTS

### --- waifu argument parser --- ###
def parse_waifu_args_from_text(text: str):
    text = text.lower()
    args = text.split()

    orientation = None
    is_nsfw = False

    if "nsfw" in text:
        is_nsfw = True
    if "portrait" in args or "vertical" in args or "v" in args:
        orientation = "Portrait"
    elif "landscape" in args or "horizontal" in args or "h" in args:
        orientation = "Landscape"
    elif "random" in args:
        orientation = "All"

    return orientation, is_nsfw


### --- fetch image helper --- ###
async def fetch_waifu_image(orientation=None, is_nsfw=None, min_height=None, limit=1, download=False):
    url = "https://api.waifu.im/images"
    params = {}

    if orientation:
        params["Orientation"] = orientation
    if is_nsfw is not None:
        params["IsNsfw"] = str(is_nsfw)
    if min_height:
        params["Height"] = f">={min_height}"
    if limit > 1:
        params["PageSize"] = str(int(limit))

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            if not data.get("items"):
                return None

            results = []
            for image_data in data["items"]:
                image_url = image_data["url"]
                tags = ", ".join([t["name"] for t in image_data.get("tags", [])])

                img_bytes = None
                if download:
                    async with session.get(image_url) as img_resp:
                        if img_resp.status != 200:
                            continue
                        img_bytes = BytesIO(await img_resp.read())
                        img_bytes.name = "waifu" + (".png" if image_url.endswith(".png") else ".jpg")

                results.append((img_bytes, tags, image_url))

    return results

### --- random character inline --- ###
async def random_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    check = await check_user(update, context)

    # user is banned
    if check == -1:
        await context.bot.answer_inline_query(
            update.inline_query.id,
            results=[],
            cache_time=0,
            is_personal=True,
            button=InlineQueryResultsButton(
                text=TEXTS["errors"]["banned"],
                start_parameter="ban"
            )
        )
        return

    # check active pv or require channels/groups
    pv_active = await has_active_private_chat(context.bot, user_id=update.effective_user.id)
    if not pv_active or check == -2:
        await context.bot.answer_inline_query(
            update.inline_query.id,
            results=[],
            cache_time=0,
            is_personal=True,
            button=InlineQueryResultsButton(
                text="برای استفاده از ربات کلیک کنید 🤖",
                start_parameter="inline"
            )
        )
        return

    query = update.inline_query.query.strip()
    orientation, is_nsfw = parse_waifu_args_from_text(query)

    images = await fetch_waifu_image(
        orientation=orientation,
        is_nsfw=is_nsfw,
        limit=10,
        download=False
    )

    if not images:
        await update.inline_query.answer([], cache_time=0, is_personal=True)
        return

    results = []
    for img_bytes, tags, image_url in images:
        results.append(
            InlineQueryResultPhoto(
                id=str(uuid.uuid4()),
                photo_url=image_url,
                thumbnail_url=image_url,
                caption=TEXTS["animebot"]["message"].format(tags=tags),
                parse_mode="HTML",
            )
        )

    await update.inline_query.answer(
        results,
        cache_time=0,
        is_personal=True
    )