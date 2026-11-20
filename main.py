import asyncio
import sqlite3
import os
import re
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
import config
import database

# Database initialize
database.init_db()

# Bot client setup
bot = TelegramClient('bot_session', config.API_ID, config.API_HASH)

# Temporary storage for latest buyer (Automation trigger matching-kaga)
latest_buyer = {}

# --- 1. START & MAIN MENU ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    count = database.get_stock_count()
    welcome_msg = (
        "🚀 **WELCOME TO PREMIUM ID STORE**\n\n"
        f"📊 **Current Stock:** `{count} IDs Available`\n"
        "⚡ **Status:** `Online & Instant OTP`"
    )
    buttons = [
        [Button.inline("🛒 Buy Account (₹50)", data="buy_info")],
        [Button.inline("🛡️ Device Control", data="device_help")],
        [Button.url("💬 Contact Admin", url="https://t.me/your_admin_username")]
    ]
    await event.respond(welcome_msg, buttons=buttons)

# --- 2. ADMIN: ADD STOCK & CHECK STOCK ---
@bot.on(events.NewMessage(pattern=r'/add\s+(.+)\s+(.+)\s+(.+)'))
async def add_stock_handler(event):
    if event.sender_id == config.ADMIN_ID:
        try:
            session = event.pattern_match.group(1).strip()
            phone = event.pattern_match.group(2).strip()
            password = event.pattern_match.group(3).strip()
            
            database.add_stock(session, phone, password)
            await event.respond(f"✅ **Stock Added Successfully!**\n\n📞 Number: `{phone}`")
        except Exception as e:
            await event.respond(f"❌ Error: {str(e)}\nFormat: `/add [session] [phone] [password]`")

@bot.on(events.NewMessage(pattern='/stock'))
async def check_stock(event):
    if event.sender_id == config.ADMIN_ID:
        conn = sqlite3.connect('stock.db')
        cursor = conn.cursor()
        cursor.execute("SELECT phone FROM session_stock WHERE status = 0")
        rows = cursor.fetchall()
        conn.close()

        count = len(rows)
        if count > 0:
            number_list = "\n".join([f"🔹 `{r[0]}`" for r in rows])
            response = (
                "📊 **CURRENT STOCK DETAILS**\n\n"
                f"✅ **Total Available:** `{count}`\n\n"
                "📞 **Numbers List:**\n"
                f"{number_list}"
            )
        else:
            response = "❌ **Stock Empty!**"
        
        await event.respond(response)

# --- 3. PURCHASE & AUTOMATION TRACKING ---
@bot.on(events.CallbackQuery(data="buy_info"))
async def buy_info(event):
    # Store buyer ID locally so automation knows who paid
    latest_buyer['id'] = event.sender_id
    await event.edit(
        "**Payment Method:**\n\nUPI ID: `yourname@upi` \nAmount: ₹50\n\nPay panni notification vandha udanae **Automatic Approval** aagum!",
        buttons=[Button.inline("🔙 Back", data="back")]
    )

# --- 4. FAM PAY AUTOMATION (FULL AUTO) ---
@bot.on(events.NewMessage(incoming=True))
async def fam_pay_automation(event):
    # MacroDroid anuppura text 'Payment_Received' nu irukanum
    if "Payment_Received" in event.text:
        user_id = latest_buyer.get('id')
        
        if user_id:
            acc = database.get_available_account() 
            if acc:
                acc_id, session, phone, password = acc
                database.mark_as_sold(acc_id)
                
                msg = (
                    "✅ **Payment Verified Automatically!**\n\n"
                    f"📞 **Number:** `{phone}`\n"
                    f"🔑 **Password:** `{password}`\n\n"
                    "OTP edukkavum, login control pannaum keela ulla buttons use pannunga."
                )
                buttons = [
                    [Button.inline("📩 Get OTP", data=f"otp_{acc_id}")],
                    [Button.inline("🛡️ Logout Others", data=f"logout_{acc_id}")]
                ]
                
                await bot.send_message(user_id, msg, buttons=buttons)
                # Admin confirmation
                await bot.send_message(config.ADMIN_ID, f"⚡ **Auto-Delivered to {user_id}!**\n📞 Number: `{phone}`")
                # Clear for next user
                latest_buyer.clear()
            else:
                await bot.send_message(config.ADMIN_ID, "❌ Payment vandhuchi, aana Stock Empty!")
        else:
            await bot.send_message(config.ADMIN_ID, "⚠️ Payment detected, aana Buyer ID therila (User /buy click panni irukanum).")

# --- 5. OTP & DEVICE LOGIC ---
@bot.on(events.CallbackQuery(pattern=r"otp_(\d+)"))
async def otp_handler(event):
    acc_id = event.data.decode().split('_')[1]
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    cursor.execute("SELECT session_text FROM session_stock WHERE id = ?", (acc_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        await event.answer("Connecting...", alert=False)
        try:
            # strip() adds stability to string session
            async with TelegramClient(StringSession(row[0].strip()), config.API_ID, config.API_HASH) as client:
                async for msg in client.iter_messages(777000, limit=1):
                    await event.respond(f"📩 **Latest OTP Message:**\n\n`{msg.text}`")
        except Exception as e:
            await event.respond(f"❌ Session Error: {str(e)}")

@bot.on(events.CallbackQuery(pattern=r"logout_(\d+)"))
async def logout_others(event):
    acc_id = event.data.decode().split('_')[1]
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    cursor.execute("SELECT session_text FROM session_stock WHERE id = ?", (acc_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            async with TelegramClient(StringSession(row[0].strip()), config.API_ID, config.API_HASH) as client:
                from telethon.tl.functions.auth import TerminateAllSessionsRequest
                await client(TerminateAllSessionsRequest())
                await event.respond("✅ Success! Other devices logged out.")
        except:
            await event.respond("❌ Error during termination.")

# --- EXECUTION ---
async def main():
    await bot.start(bot_token=config.BOT_TOKEN)
    print("Bot is LIVE with Full-Auto Delivery!")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

