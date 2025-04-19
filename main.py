import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Configuration
TELEGRAM_TOKEN = "7812351684:AAE_abX1KAD2R2rW9jGFUC6Gcx7py7iQsv8"  # Replace with your BotFather token
GEMINI_API_KEY = "AIzaSyDqhJ36j9UB05kxOEGusaHl4Zub8TjZGXE"  # Replace with your Gemini API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Track chat state
active_chats = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    active_chats.add(update.message.from_user.id)
    await update.message.reply_text(
        "👋 Hello! I'm your AI assistant powered by Gemini. Just send me a message and I'll respond!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "🤖 I can help you with various tasks using Gemini AI. Just send me any message and I'll respond!"
    )

async def quit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask the user to confirm ending the chat."""
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data="quit_yes"),
            InlineKeyboardButton("No", callback_data="quit_no"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Do you want to end the chat?", reply_markup=reply_markup)

async def quit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the user's response to the quit confirmation."""
    query = update.callback_query
    await query.answer()
    if query.data == "quit_yes":
        active_chats.discard(query.from_user.id)
        await query.edit_message_text("Chat ended. Send /start to begin chatting again.")
    elif query.data == "quit_no":
        await query.edit_message_text("Chat resumed. Feel free to send a message!")

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide support link."""
    keyboard = [
        [InlineKeyboardButton("Contact Support", url="https://t.me/MEHRDAD87ORG")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "If you have a problem, press the button below to contact support.",
        reply_markup=reply_markup
    )

def get_gemini_response(prompt: str) -> str:
    """Get response from Gemini AI API."""
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        
        # Extract the text from the response
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        return "Sorry, I couldn't generate a response."
    except Exception as e:
        return f"Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and respond using Gemini AI."""
    user_id = update.message.from_user.id
    if user_id not in active_chats:
        await update.message.reply_text("Please send /start to begin chatting.")
        return

    user_message = update.message.text.lower()

    # Check for specific queries
    if "who is your creator" in user_message or "who made you" in user_message or "سازنده تو کیست" in user_message or "تو را چه کسی ساخته" in user_message:
        await update.message.reply_text("مهرداد اورنگ")
        return

    # Get response from Gemini
    ai_response = get_gemini_response(user_message)
    
    # Send the response back to the user
    await update.message.reply_text(ai_response)

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quit", quit_command))
    application.add_handler(CommandHandler("support", support_command))
    application.add_handler(CallbackQueryHandler(quit_callback, pattern="^quit_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()