from telethon import TelegramClient, events
from telegram import Bot
import re
import asyncio

# CONFIGURACIÓN
api_id = os.getenv("TELEGRAM_API") # Reemplaza con tu API ID
api_hash = os.getenv("TELEGRAM_API_HASH") # Reemplaza con tu API Hash
bot_token = os.getenv("TELEGRAM_BOT_TOKEN") # Token del bot
user_id = 1343297649  # Tu ID de Telegram

# IDS de canales
WATCHED_CHANNELS = {
    os.getenv("TELEGRAM_CHANNEL_LOGAN"),  # Logan
    os.getenv("TELEGRAM_CHANNEL_PIT") # Trading Pit
}

# Inicializar clientes
telethon_client = TelegramClient('session_tradingbot', api_id, api_hash)
telegram_bot = Bot(token=bot_token)

# Función para detectar y formatear señal tipo FUTUROS
def parse_futuros_signal(text):
    if "Entry price" in text and "Targets" in text:
        try:
            direction = "LONG" if "🟢 Long" in text else "SHORT"
            name = re.search(r'Name:\s*(.+)', text).group(1)
            leverage = re.search(r'Margin mode:\s*(.+)', text).group(1)
            entry_price = re.search(r'Entry price\(USDT\):\s*([\d\.]+)', text).group(1)
            targets = re.findall(r'\d\)\s*([\d\.]+)', text)

            result = f"📊 CRYPTO SIGNAL [{direction}]\n"
            result += f"Pair: {name}\n"
            result += f"Leverage: {leverage}\n"
            result += f"Entry: {entry_price}\n"
            for i, t in enumerate(targets, 1):
                result += f"TP{i}: {t}\n"
            result += "SL: 🔺 UNLIMITED\n" if direction == "LONG" else "SL: 🔻 UNLIMITED"
            return result
        except Exception as e:
            return None
    return None

# Función para detectar y formatear señal tipo FOREX
def parse_forex_signal(text):
    if "NEW SIGNAL" in text and "@" in text and "TP1" in text and "SL" in text:
        try:
            pair_action = re.search(r'([A-Z]{3}/[A-Z]{3})\s+(BUY|SELL)\s+@\s+([\d\.]+)', text)
            tp_matches = re.findall(r'TP\d+\s*[-–]\s*([\d\.]+)', text)
            sl_match = re.search(r'SL\s*[-–]\s*([\d\.]+)', text)

            if pair_action and tp_matches and sl_match:
                pair, action, entry = pair_action.groups()
                result = f"💹 FOREX SIGNAL [{action}]\n"
                result += f"Pair: {pair}\n"
                result += f"Entry: {entry}\n"
                for i, tp in enumerate(tp_matches, 1):
                    result += f"TP{i}: {tp}\n"
                result += f"SL: {sl_match.group(1)}"
                return result
        except Exception as e:
            return None
    return None

# Handler para nuevos mensajes
@telethon_client.on(events.NewMessage(chats=WATCHED_CHANNELS))
async def handler(event):
    text = event.message.message
    parsed = parse_futuros_signal(text) or parse_forex_signal(text)

    if parsed:
        await telegram_bot.send_message(chat_id=user_id, text=parsed)

# Ejecutar cliente
def main():
    print("📡 Bot escuchando señales...")
    with telethon_client:
        telethon_client.run_until_disconnected()

if __name__ == "__main__":
    main()
