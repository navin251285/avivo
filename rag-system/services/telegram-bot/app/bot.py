import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


current_dir = Path(__file__).resolve().parent
service_root = current_dir.parent
rag_system_root = service_root.parent.parent

load_dotenv(rag_system_root / ".env")
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
RAG_API_URL = os.getenv("RAG_API_URL", "")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	del context
	if update.message:
		await update.message.reply_text("Hi 👋 I am your RAG assistant. Ask me anything!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	del context
	if not update.message or not update.message.text:
		return

	user_query = update.message.text
	user_id = update.message.chat_id

	try:
		async with httpx.AsyncClient(timeout=30) as client:
			response = await client.post(
				RAG_API_URL,
				json={"question": user_query, "user_id": user_id},
			)
			response.raise_for_status()

		data = response.json()
		answer = data.get("answer", "No answer found.")
	except Exception as error:
		answer = f"⚠️ Error: {str(error)}"

	await update.message.reply_text(answer)


def main() -> None:
	if not BOT_TOKEN:
		raise ValueError("BOT_TOKEN is not set. Add it in .env or environment variables.")
	if not RAG_API_URL:
		raise ValueError("RAG_API_URL is not set. Add it in .env or environment variables.")

	app = ApplicationBuilder().token(BOT_TOKEN).build()
	app.add_handler(CommandHandler("start", start))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

	print("🚀 Telegram bot running...")
	app.run_polling()


if __name__ == "__main__":
	main()
