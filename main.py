import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from watermark_utils import apply_image_watermark, apply_video_watermark
from code_manager import is_channel_claimed, claim_channel
import json

api_id = 12345  # dummy (not used in bot)
api_hash = "abc123"  # dummy (not used in bot)
bot_token = os.environ.get("BOT_TOKEN")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

app = Client("watermark-bot", bot_token=bot_token)

if not os.path.exists("watermarks"):
    os.makedirs("watermarks")

if not os.path.exists("config.json"):
    with open("config.json", "w") as f:
        json.dump({}, f)

with open("config.json") as f:
    config = json.load(f)

def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f)

@app.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    await message.reply("👋 Send a claim code to activate watermarking in this channel.\nUse `/claimcode <code>`")

@app.on_message(filters.command("claimcode"))
async def claim_code(client, message: Message):
    if not message.chat or not message.chat.id < 0:
        return await message.reply("⚠️ Please use this in a **channel**.")
    
    if not message.from_user or message.from_user.id != OWNER_ID:
        return await message.reply("❌ Only owner can claim channels.")

    if len(message.command) < 2:
        return await message.reply("❗Usage: `/claimcode your-code-here`", quote=True)

    code = message.command[1]
    channel_id = str(message.chat.id)

    if is_channel_claimed(channel_id):
        return await message.reply("✅ This channel is already activated.")

    if claim_channel(code, channel_id):
        return await message.reply("🎉 Channel successfully activated using code!")
    else:
        return await message.reply("❌ Invalid or already-used code.")

@app.on_message(filters.command("setwm") & filters.user(OWNER_ID) & filters.reply)
async def set_wm(client, message: Message):
    if not message.reply_to_message.photo and not message.reply_to_message.document:
        return await message.reply("❗Reply to a PNG image to set watermark.")

    file_path = f"watermarks/{message.chat.id}.png"
    file = await message.reply_to_message.download(file_path)
    config[str(message.chat.id)] = {"caption": True}
    save_config()
    await message.reply("✅ Watermark set for this channel.")

@app.on_message(filters.command("showwm"))
async def show_wm(client, message: Message):
    wm_path = f"watermarks/{message.chat.id}.png"
    if os.path.exists(wm_path):
        await message.reply_photo(wm_path, caption="🖼 Current Watermark")
    else:
        await message.reply("❌ No watermark set for this channel.")

@app.on_message(filters.command("dltwm") & filters.user(OWNER_ID))
async def del_wm(client, message: Message):
    wm_path = f"watermarks/{message.chat.id}.png"
    if os.path.exists(wm_path):
        os.remove(wm_path)
        await message.reply("🗑 Watermark removed.")
    else:
        await message.reply("❌ No watermark to delete.")

@app.on_message(filters.command(["caption", "captionoff", "captionon"]))
async def toggle_caption(client, message: Message):
    ch_id = str(message.chat.id)
    if ch_id not in config:
        config[ch_id] = {}
    if "caption" not in config[ch_id]:
        config[ch_id]["caption"] = True

    if "off" in message.text.lower():
        config[ch_id]["caption"] = False
        await message.reply("❌ Caption will NOT be forwarded.")
    elif "on" in message.text.lower():
        config[ch_id]["caption"] = True
        await message.reply("✅ Caption will be forwarded.")
    save_config()

@app.on_message(filters.channel & (filters.photo | filters.video))
async def watermark_media(client, message: Message):
    ch_id = str(message.chat.id)
    if not is_channel_claimed(ch_id):
        return  # skip unclaimed channels

    wm_path = f"watermarks/{ch_id}.png"
    if not os.path.exists(wm_path):
        return

    caption = message.caption if config.get(ch_id, {}).get("caption", True) else None
    downloaded = await message.download()
    
    if message.photo:
        output = await apply_image_watermark(downloaded, wm_path)
    else:
        output = await apply_video_watermark(downloaded, wm_path)

    await client.send_document(
        chat_id=message.chat.id,
        document=output,
        caption=caption
    )
    os.remove(downloaded)
    os.remove(output)

app.run()
