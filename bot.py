import os, time, hashlib, base64, pyotp
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image
from pyzbar.pyzbar import decode

from telegram import (
    Update, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# ---------- CONFIG ----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
SESSION_TIMEOUT = 120 

# ---------- MONGODB SETUP ----------
client = MongoClient(MONGO_URI)
db = client['vault_db']
users_col = db['users']
accounts_col = db['accounts']

# ---------- ENCRYPTION ----------
def get_key(pin): return hashlib.sha256(pin.encode()).digest()

def encrypt(txt, pin):
    k = get_key(pin)
    return base64.b64encode(bytes([txt.encode()[i] ^ k[i % len(k)] for i in range(len(txt))])).decode()

def decrypt(enc, pin):
    try:
        k = get_key(pin)
        data = base64.b64decode(enc)
        return bytes([data[i] ^ k[i % len(k)] for i in range(len(data))]).decode()
    except: return None

# ---------- CLEANUP ----------
async def purge_sensitive_history(ctx, update: Update):
    bot = update.get_bot()
    chat_id = update.effective_chat.id
    for mid in ctx.user_data.get("purge_list", []):
        try: await bot.delete_message(chat_id=chat_id, message_id=mid)
        except: pass
    ctx.user_data.update({"is_unlocked": False, "active_pin": None, "purge_list": []})

# ---------- AUTH CORE ----------
async def validate_session(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user = users_col.find_one({"user_id": uid})

    if not user:
        ctx.user_data["state"] = "SET_PIN"
        await update.message.reply_text("👋 Welcome. Set a 4-8 digit numeric PIN:")
        return False

    if user.get("lock_until", 0) > time.time():
        await update.message.reply_text("🚫 Locked.")
        return False

    last_active = ctx.user_data.get("last_activity", 0)
    if not ctx.user_data.get("is_unlocked") or (time.time() - last_active > SESSION_TIMEOUT):
        await purge_sensitive_history(ctx, update)
        ctx.user_data["state"] = "INPUT_PIN"
        await update.message.reply_text("🔑 Session Expired. Enter PIN:", reply_markup=ReplyKeyboardRemove())
        return False

    ctx.user_data["last_activity"] = time.time()
    return True

# ---------- HANDLERS ----------
async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text, uid = update.message.text, update.effective_user.id
    state = ctx.user_data.get("state")

    if state in ["SET_PIN", "INPUT_PIN", "ADD_SECRET"]:
        try: await update.message.delete()
        except: pass

    if state == "SET_PIN":
        if text.isdigit() and 4 <= len(text) <= 8:
            users_col.update_one({"user_id": uid}, {"$set": {"pin_hash": hashlib.sha256(text.encode()).hexdigest(), "attempts": 0}}, upsert=True)
            ctx.user_data["state"] = "INPUT_PIN"
            await update.message.reply_text("✅ PIN saved. Enter it to unlock.")
        return

    if state == "INPUT_PIN":
        user = users_col.find_one({"user_id": uid})
        if hashlib.sha256(text.encode()).hexdigest() == user['pin_hash']:
            ctx.user_data.update({"is_unlocked": True, "active_pin": text, "state": None, "last_activity": time.time(), "purge_list": []})
            users_col.update_one({"user_id": uid}, {"$set": {"attempts": 0}})
            await update.message.reply_text("🔓 Vault Unlocked.", reply_markup=ReplyKeyboardMarkup([["🏠 OTP", "📂 Accounts"], ["🔍 Search", "🔐 Security"]], resize_keyboard=True))
        else:
            new_attempts = user.get("attempts", 0) + 1
            users_col.update_one({"user_id": uid}, {"$set": {"attempts": new_attempts}})
            await update.message.reply_text("❌ Wrong PIN.")
        return

    if not await validate_session(update, ctx): return

    if text == "🏠 OTP":
        accounts = list(accounts_col.find({"user_id": uid}))
        if not accounts: return await update.message.reply_text("No accounts.")
        output = "📝 **Codes**\n\n"
        for acc in accounts:
            sec = decrypt(acc['secret'], ctx.user_data["active_pin"])
            if sec: output += f"`{acc['name']}`: **{pyotp.TOTP(sec).now()}**\n"
        msg = await update.message.reply_text(output, parse_mode="Markdown")
        ctx.user_data.setdefault("purge_list", []).append(msg.message_id)

    elif text == "📂 Accounts":
        await update.message.reply_text("Manager:", reply_markup=ReplyKeyboardMarkup([["➕ Add", "📂 List"], ["✏️ Rename", "🗑 Delete"], ["🔙 Back"]], resize_keyboard=True))

    elif text == "➕ Add":
        ctx.user_data["state"] = "ADD_NAME"
        await update.message.reply_text("Account Name:")

    elif state == "ADD_NAME":
        ctx.user_data.update({"temp_name": text, "state": "ADD_SECRET"})
        await update.message.reply_text("Send Secret Key (Text/QR):")

    elif state == "ADD_SECRET":
        try:
            clean = text.replace(" ", "").upper()
            pyotp.TOTP(clean).now()
            accounts_col.insert_one({"user_id": uid, "name": ctx.user_data["temp_name"], "secret": encrypt(clean, ctx.user_data["active_pin"])})
            ctx.user_data["state"] = None
            await update.message.reply_text("✅ Added.")
        except: await update.message.reply_text("❌ Invalid key.")

    elif text == "🔐 Security":
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Lock", callback_data="lock")], [InlineKeyboardButton("🔄 Reset PIN", callback_data="reset")]])
        await update.message.reply_text("Security Center:", reply_markup=kb)

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data.split("|")
    if data[0] == "lock":
        await purge_sensitive_history(ctx, update)
        return await q.edit_message_text("🔒 Session Locked.")
    if not ctx.user_data.get("is_unlocked"): return await q.answer("Unlock first.")
    await q.answer()
    if data[0] == "otp":
        acc = accounts_col.find_one({"_id": data[1]}) # Requires objectID handling or custom IDs
        # simplified for brevity
        pass

# Start Command
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vault Ready.", reply_markup=ReplyKeyboardMarkup([["🏠 OTP", "📂 Accounts"], ["🔍 Search", "🔐 Security"]], resize_keyboard=True))

# Main Execution
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(on_callback))
app.run_polling()

