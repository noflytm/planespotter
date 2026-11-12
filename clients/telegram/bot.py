import sys
import time
import json
import logging
import random
import urllib.request
import urllib.parse
from config import get_token
from spotter_db import SpotterDB, detect_country, normalize_reg
from aircraft_facts import get_aircraft_facts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SpotterBot")

class TelegramAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    def request(self, method: str, data: dict = None, timeout: int = 30):
        url = f"{self.base_url}/{method}"
        headers = {"Content-Type": "application/json"}
        req_data = json.dumps(data).encode("utf-8") if data else None
        
        req = urllib.request.Request(url, data=req_data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            logger.error(f"HTTPError {e.code} on {method}: {err_body}")
            try:
                return json.loads(err_body)
            except Exception:
                return {"ok": False, "description": err_body}
        except Exception as e:
            logger.error(f"Request error on {method}: {e}")
            return {"ok": False, "description": str(e)}

    def get_me(self):
        return self.request("getMe")

    def get_updates(self, offset: int = 0, timeout: int = 25):
        payload = {
            "offset": offset,
            "timeout": timeout,
            "allowed_updates": ["message", "callback_query"]
        }
        return self.request("getUpdates", payload, timeout=timeout + 10)

    def send_photo(self, chat_id: int, photo_url: str, caption: str, reply_markup: dict = None):
        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "HTML"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        res = self.request("sendPhoto", payload)
        if not res.get("ok"):
            logger.warning(f"sendPhoto failed: {res.get('description')}, fallback to sendMessage")
            return self.send_message(chat_id, caption, reply_markup=reply_markup, photo_preview=photo_url)
        return res

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict = None, disable_preview: bool = True, photo_preview: str = None):
        full_text = text
        if photo_preview and photo_preview not in text:
            full_text = f'<a href="{photo_preview}">&#8205;</a>' + text
            disable_preview = False

        payload = {
            "chat_id": chat_id,
            "text": full_text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_preview
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.request("sendMessage", payload)

    def answer_callback_query(self, callback_query_id: str, text: str = None):
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        return self.request("answerCallbackQuery", payload)


import os
sys.path.append(os.path.join(os.path.dirname(__file__), "aws_lambda"))
from i18n import (
    HUB_BASE_URL,
    t, detect_user_lang, build_main_reply_keyboard,
    COMMON_TIMEZONES, SUPPORTED_LANGUAGES, LANG_FLAGS, LANG_NAMES
)

class SpotterBot:
    def __init__(self, token: str):
        self.api = TelegramAPI(token)
        self.user_prefs = {} # chat_id -> dict
        logger.info("Bot initialized as Web App Gateway with i18n support.")

    def handle_message(self, message: dict):
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        if not text:
            return

        from_user = message.get("from", {})
        prefs = self.user_prefs.setdefault(chat_id, {})
        user_lang = detect_user_lang(from_user, prefs.get("lang"))
        user_tz = prefs.get("timezone", "Europe/Warsaw")
        user_airport = prefs.get("nearest_airport", "WAW")

        hub_url = f"{HUB_BASE_URL}/player?lang={user_lang}&tz={user_tz}&icao={user_airport}&v={int(time.time())}"
        reply_kb = build_main_reply_keyboard(user_lang, hub_url)

        if text in ["⚙️ Настройки", "⚙️ Settings", "⚙️ Ustawienia", "/settings", "settings"]:
            msg = f"{t('settings_title', user_lang)}\n\n{t('settings_body', user_lang, lang_display=LANG_NAMES.get(user_lang, user_lang), timezone=user_tz, utc_offset='+02:00', airport=user_airport, notifications_status='🟢')}"
            kb = {
                "inline_keyboard": [
                    [{"text": t("settings_btn_lang", user_lang), "callback_data": "settings:lang"}],
                    [{"text": t("settings_btn_tz", user_lang), "callback_data": "settings:tz"}],
                    [{"text": f"🚀 {t('btn_open_hub_cta', user_lang)}", "web_app": {"url": hub_url}}]
                ]
            }
            self.api.send_message(chat_id, msg, reply_markup=kb)
            return

        if text.startswith("/start"):
            has_lang = prefs.get("lang_chosen")
            if not has_lang or text == "/start reset":
                msg = t("start_lang_prompt", "multi")
                kb = {
                    "inline_keyboard": [
                        [
                            {"text": "🇷🇺 Русский", "callback_data": "start_lang:ru"},
                            {"text": "🇬🇧 English", "callback_data": "start_lang:en"},
                            {"text": "🇵🇱 Polski", "callback_data": "start_lang:pl"}
                        ]
                    ]
                }
                self.api.send_message(chat_id, msg, reply_markup=kb)
                return

        welcome = f"{t('welcome_title', user_lang)}\n\n{t('welcome_body', user_lang)}"
        kb = {
            "inline_keyboard": [
                [{"text": f"🚀 {t('btn_open_hub_cta', user_lang)}", "web_app": {"url": hub_url}}],
                [{"text": t("settings_btn_tz", user_lang), "callback_data": "settings:tz"}, {"text": t("settings_btn_lang", user_lang), "callback_data": "settings:lang"}]
            ]
        }
        self.api.send_message(chat_id, welcome, reply_markup=kb)

    def handle_callback(self, cb: dict):
        cb_id = cb["id"]
        self.api.answer_callback_query(cb_id, text="Эта функция перенесена в Mini App.")

    def run(self):
        logger.info("Starting Telegram Bot long-polling loop...")
        me = self.api.get_me()
        if not me.get("ok"):
            logger.error(f"Failed to connect to Telegram Bot API: {me.get('description')}")
            print("\n" + "="*60)
            print("ОШИБКА: Не удалось подключиться к Telegram API.")
            print(f"Ответ Telegram: {me.get('description')}")
            print("Убедитесь, что в файле .env указан корректный BOT_TOKEN от @BotFather.")
            print("="*60 + "\n")
            return

        bot_username = me["result"]["username"]
        logger.info(f"Connected successfully as @{bot_username} (ID: {me['result']['id']})")
        print(f"\nБот успешно запущен: @{bot_username}")
        print("Ожидание сообщений от пользователей...\n")

        offset = 0
        while True:
            try:
                updates = self.api.get_updates(offset=offset, timeout=20)
                if not updates.get("ok"):
                    time.sleep(3)
                    continue

                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" in update:
                        self.handle_message(update["message"])
                    elif "callback_query" in update:
                        self.handle_callback(update["callback_query"])

            except KeyboardInterrupt:
                logger.info("Bot stopped by user.")
                break
            except Exception as e:
                logger.error(f"Unexpected error in polling loop: {e}")
                time.sleep(3)


def main():
    token = get_token()
    if not token or token == "YOUR_BOT_TOKEN_HERE" or "123456789" in token:
        print("\n" + "="*60)
        print("ВНИМАНИЕ: Не найден BOT_TOKEN!")
        print("Пожалуйста, создайте бота в Telegram через @BotFather,")
        print("скопируйте выданный HTTP API Token и вставьте его в файл .env:")
        print("BOT_TOKEN=ваш_токен_здесь")
        print("="*60 + "\n")
        sys.exit(1)

    bot = SpotterBot(token)
    bot.run()

if __name__ == "__main__":
    main()
