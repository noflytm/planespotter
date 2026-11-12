"""
Internationalization (i18n) and Timezone utilities for PlaneSpotter Bot.
Supported Languages:
- ru: Russian (Русский)
- en: English (English)
- pl: Polish (Polski)
"""

import os

# Base URL of the Mini App (the web page opened from the bot). Override with the HUB_BASE_URL environment variable.
HUB_BASE_URL = os.environ.get("HUB_BASE_URL", "https://jetphotos-api.ai-planespotter-bot.workers.dev").rstrip("/")


SUPPORTED_LANGUAGES = ["ru", "en", "pl"]
DEFAULT_LANGUAGE = "ru"

LANG_FLAGS = {
    "ru": "🇷🇺",
    "en": "🇬🇧",
    "pl": "🇵🇱",
}

LANG_NAMES = {
    "ru": "Русский",
    "en": "English",
    "pl": "Polski",
}

# Common timezones with display labels in RU, EN, PL and approximate UTC offset
COMMON_TIMEZONES = [
    {
        "id": "UTC",
        "offset": 0,
        "labels": {"ru": "🌐 UTC (Время по Гринвичу)", "en": "🌐 UTC (Greenwich Mean Time)", "pl": "🌐 UTC (Czas uniwersalny)"}
    },
    {
        "id": "Europe/London",
        "offset": 1,
        "labels": {"ru": "🇬🇧 Лондон (UTC+1/0)", "en": "🇬🇧 London (UTC+1/0)", "pl": "🇬🇧 Londyn (UTC+1/0)"}
    },
    {
        "id": "Europe/Warsaw",
        "offset": 2,
        "labels": {"ru": "🇵🇱 Варшава, Берлин (UTC+2/1)", "en": "🇵🇱 Warsaw, Berlin (UTC+2/1)", "pl": "🇵🇱 Warszawa, Berlin (UTC+2/1)"}
    },
    {
        "id": "Europe/Kyiv",
        "offset": 3,
        "labels": {"ru": "🇺🇦 Киев, Хельсинки (UTC+3/2)", "en": "🇺🇦 Kyiv, Helsinki (UTC+3/2)", "pl": "🇺🇦 Kijów, Helsinki (UTC+3/2)"}
    },
    {
        "id": "Europe/Moscow",
        "offset": 3,
        "labels": {"ru": "🇷🇺 Москва, Стамбул (UTC+3)", "en": "🇷🇺 Moscow, Istanbul (UTC+3)", "pl": "🇷🇺 Moskwa, Stambuł (UTC+3)"}
    },
    {
        "id": "Asia/Dubai",
        "offset": 4,
        "labels": {"ru": "🇦🇪 Дубай (UTC+4)", "en": "🇦🇪 Dubai (UTC+4)", "pl": "🇦🇪 Dubaj (UTC+4)"}
    },
    {
        "id": "Asia/Tokyo",
        "offset": 9,
        "labels": {"ru": "🇯🇵 Токио (UTC+9)", "en": "🇯🇵 Tokyo (UTC+9)", "pl": "🇯🇵 Tokio (UTC+9)"}
    },
    {
        "id": "America/New_York",
        "offset": -4,
        "labels": {"ru": "🇺🇸 Нью-Йорк, Майами (UTC-4/5)", "en": "🇺🇸 New York, Miami (UTC-4/5)", "pl": "🇺🇸 Nowy Jork, Miami (UTC-4/5)"}
    },
    {
        "id": "America/Chicago",
        "offset": -5,
        "labels": {"ru": "🇺🇸 Чикаго (UTC-5/6)", "en": "🇺🇸 Chicago (UTC-5/6)", "pl": "🇺🇸 Chicago (UTC-5/6)"}
    },
    {
        "id": "America/Los_Angeles",
        "offset": -7,
        "labels": {"ru": "🇺🇸 Лос-Анджелес (UTC-7/8)", "en": "🇺🇸 Los Angeles (UTC-7/8)", "pl": "🇺🇸 Los Angeles (UTC-7/8)"}
    },
]

# Airport ICAO prefix to Timezone mapping
AIRPORT_TIMEZONES = {
    "EP": {"tz": "Europe/Warsaw", "offset": 2, "name": "Польша (UTC+2)"},
    "ED": {"tz": "Europe/Berlin", "offset": 2, "name": "Германия (UTC+2)"},
    "EG": {"tz": "Europe/London", "offset": 1, "name": "Великобритания (UTC+1)"},
    "LF": {"tz": "Europe/Paris", "offset": 2, "name": "Франция (UTC+2)"},
    "EH": {"tz": "Europe/Amsterdam", "offset": 2, "name": "Нидерланды (UTC+2)"},
    "EV": {"tz": "Europe/Riga", "offset": 3, "name": "Латвия (UTC+3)"},
    "EE": {"tz": "Europe/Tallinn", "offset": 3, "name": "Эстония (UTC+3)"},
    "EY": {"tz": "Europe/Vilnius", "offset": 3, "name": "Литва (UTC+3)"},
    "LK": {"tz": "Europe/Prague", "offset": 2, "name": "Чехия (UTC+2)"},
    "LO": {"tz": "Europe/Vienna", "offset": 2, "name": "Австрия (UTC+2)"},
    "LE": {"tz": "Europe/Madrid", "offset": 2, "name": "Испания (UTC+2)"},
    "LT": {"tz": "Europe/Istanbul", "offset": 3, "name": "Турция (UTC+3)"},
    "OM": {"tz": "Asia/Dubai", "offset": 4, "name": "ОАЭ (UTC+4)"},
    "OT": {"tz": "Asia/Qatar", "offset": 3, "name": "Катар (UTC+3)"},
    "RJ": {"tz": "Asia/Tokyo", "offset": 9, "name": "Япония (UTC+9)"},
    "KJ": {"tz": "America/New_York", "offset": -4, "name": "США Восток (UTC-4)"},
    "KL": {"tz": "America/Los_Angeles", "offset": -7, "name": "США Запад (UTC-7)"},
    "KM": {"tz": "America/Chicago", "offset": -5, "name": "США Центр (UTC-5)"},
}

def get_timezone_for_airport(icao: str):
    if not icao:
        return {"tz": "Europe/Warsaw", "offset": 2, "name": "Europe/Warsaw"}
    prefix = icao[:2].upper()
    return AIRPORT_TIMEZONES.get(prefix, {"tz": "UTC", "offset": 0, "name": "UTC"})


MESSAGES = {
    "jp_already_linked_warning": {
        "ru": "⚠️ <b>Внимание:</b> У вас уже привязан аккаунт JetPhotos ID: <code>{jp_id}</code> ({name}).\nПо соображениям безопасности и ограничения затрат, к 1 Telegram-аккаунту разрешено привязывать только 1 профиль споттера.",
        "en": "⚠️ <b>Warning:</b> You already have a linked JetPhotos account ID: <code>{jp_id}</code> ({name}).\nFor security and data integrity reasons, only 1 spotter profile is allowed per Telegram account.",
        "pl": "⚠️ <b>Uwaga:</b> Masz już połączone konto JetPhotos ID: <code>{jp_id}</code> ({name}).\nZe względów bezpieczeństwa do 1 konta Telegram można przypisać tylko 1 profil spottera.",
    },
    "jp_import_starting": {
        "ru": "⏳ <b>Начинаю импорт твоей галереи JetPhotos (ID: {jp_id})...</b>\n\nФормирую персональную изолированную базу в DynamoDB. Это займет несколько секунд.\nЯ сразу же пришлю уведомление, как только база будет готова!",
        "en": "⏳ <b>Starting import of your JetPhotos gallery (ID: {jp_id})...</b>\n\nBuilding your isolated personal database in DynamoDB. This will take a few seconds.\nI will notify you as soon as the database is ready!",
        "pl": "⏳ <b>Rozpoczynam import Twojej galerii JetPhotos (ID: {jp_id})...</b>\n\nTworzę Twoją osobistą bazę w DynamoDB. To zajmie kilka sekund.\nPowiadomię Cię natychmiast, gdy baza będzie gotowa!",
    },
    "stats_no_base_msg": {
        "ru": "⚠️ У вас ещё не привязана база JetPhotos. Отправьте свой JetPhotos ID (например, <code>123456</code>).",
        "en": "⚠️ You haven't linked your JetPhotos database yet. Send your JetPhotos ID (e.g. <code>123456</code>).",
        "pl": "⚠️ Nie masz jeszcze połączonej bazy JetPhotos. Wyślij swój JetPhotos ID (np. <code>123456</code>).",
    },
    "card_collection_found_title": {
        "ru": "📸 <b>БОРТ НАЙДЕН В ВАШЕЙ КОЛЛЕКЦИИ!</b>",
        "en": "📸 <b>AIRCRAFT FOUND IN YOUR COLLECTION!</b>",
        "pl": "📸 <b>SAMOLOT ZNALEZIONY W TWOJEJ KOLEKCJI!</b>",
    },
    "card_label_model": {
        "ru": "✈️ <b>Модель:</b>",
        "en": "✈️ <b>Model:</b>",
        "pl": "✈️ <b>Model:</b>",
    },
    "card_label_msn": {
        "ru": "🔢 <b>MSN (серийник):</b>",
        "en": "🔢 <b>MSN (serial):</b>",
        "pl": "🔢 <b>MSN (numer seryjny):</b>",
    },
    "card_label_reg": {
        "ru": "🔹 <b>Бортовой номер:</b>",
        "en": "🔹 <b>Registration:</b>",
        "pl": "🔹 <b>Rejestracja:</b>",
    },
    "card_label_airline": {
        "ru": "🔹 <b>Авиакомпания:</b>",
        "en": "🔹 <b>Airline:</b>",
        "pl": "🔹 <b>Linia lotnicza:</b>",
    },
    "card_label_latest_photo": {
        "ru": "📅 <b>Ваше крайнее фото:</b>",
        "en": "📅 <b>Your latest photo:</b>",
        "pl": "📅 <b>Twoje ostatnie zdjęcie:</b>",
    },
    "card_label_in_collection": {
        "ru": "🖼 <b>В вашей коллекции:</b> {cnt} шт.",
        "en": "🖼 <b>In your collection:</b> {cnt} photos",
        "pl": "🖼 <b>W Twojej kolekcji:</b> {cnt} szt.",
    },
    "card_label_all_photos": {
        "ru": "🌐 <b>Все фото борта:</b> <a href=\'https://www.jetphotos.com/registration/{reg}\'>Галерея JetPhotos ↗</a>",
        "en": "🌐 <b>All aircraft photos:</b> <a href=\'https://www.jetphotos.com/registration/{reg}\'>JetPhotos Gallery ↗</a>",
        "pl": "🌐 <b>Wszystkie zdjęcia samolotu:</b> <a href=\'https://www.jetphotos.com/registration/{reg}\'>Galeria JetPhotos ↗</a>",
    },
    "card_hint_livery": {
        "ru": "💡 <i>Сверьте миниатюру: если ливрея обновилась — это отличный повод поймать Hot Photo!</i> 🔥",
        "en": "💡 <i>Check the thumbnail: if the livery changed — a great chance to catch a Hot Photo!</i> 🔥",
        "pl": "💡 <i>Sprawdź miniaturkę: jeśli malowanie się zmieniło — to świetna okazja na Hot Photo!</i> 🔥",
    },
    "card_btn_all_photos_jp": {
        "ru": "🌐 Все фото борта на JetPhotos",
        "en": "🌐 All aircraft photos on JetPhotos",
        "pl": "🌐 Wszystkie zdjęcia na JetPhotos",
    },
    "card_btn_photo_source": {
        "ru": "📷 Фото на {source}",
        "en": "📷 Photo on {source}",
        "pl": "📷 Zdjęcie na {source}",
    },
    "card_new_for_collection_title": {
        "ru": "🔴 <b>НОВЫЙ БОРТ ДЛЯ КОЛЛЕКЦИИ (ЕЩЁ НЕ СНЯТ)!</b>",
        "en": "🔴 <b>NEW AIRCRAFT FOR COLLECTION (UNSPOTTED)!</b>",
        "pl": "🔴 <b>NOWY SAMOLOT DO KOLEKCJI (NIEZFOTOGRAFOWANY)!</b>",
    },
    "card_new_for_collection_hint": {
        "ru": "🎯 <i>Этого борта ещё нет в вашей галерее! Ловите его у взлётной полосы!</i>",
        "en": "🎯 <i>This aircraft is not in your gallery yet! Catch it by the runway!</i>",
        "pl": "🎯 <i>Tego samolotu jeszcze nie masz w galerii! Złap go przy pasie!</i>",
    },
    "card_global_info_title": {
        "ru": "✈️ <b>ИНФОРМАЦИЯ О БОРТЕ ({source} GLOBAL):</b>",
        "en": "✈️ <b>AIRCRAFT INFORMATION ({source} GLOBAL):</b>",
        "pl": "✈️ <b>INFORMACJE O SAMOLOCIE ({source} GLOBAL):</b>",
    },
    "card_global_info_hint": {
        "ru": "💡 <i>Отправьте /start чтобы привязать свой JetPhotos ID и вести персональный учёт!</i>",
        "en": "💡 <i>Send /start to link your JetPhotos ID and track your personal collection!</i>",
        "pl": "💡 <i>Wyślij /start aby powiązać swój JetPhotos ID i prowadzić statystyki!</i>",
    },
    "card_label_photo_date": {
        "ru": "📸 <b>Крайнее фото:</b>",
        "en": "📸 <b>Latest photo:</b>",
        "pl": "📸 <b>Ostatnie zdjęcie:</b>",
    },
    "card_label_author": {
        "ru": "👤 <b>Автор снимка:</b>",
        "en": "👤 <b>Photographer:</b>",
        "pl": "👤 <b>Autor zdjęcia:</b>",
    },
    "card_rare_title": {
        "ru": "🎯 <b>РЕДКИЙ БОРТ: НЕТ НА JETPHOTOS!</b>",
        "en": "🎯 <b>RARE AIRCRAFT: NOT ON JETPHOTOS!</b>",
        "pl": "🎯 <b>RZADKI SAMOLOT: BRAK NA JETPHOTOS!</b>",
    },
    "card_rare_body": {
        "ru": "Бортовой номер: <b>{reg}</b>\nСтрана: <b>{country}</b>\n\n🔥 <i>На JetPhotos пока нет свежих фотографий этого борта!</i>\nУ вас есть уникальный шанс сделать исторический кадр: <b>First Registration</b> или <b>Hot Photo</b>!\n\nПроверьте актуальный статус полётов на Flightradar24:",
        "en": "Tail number: <b>{reg}</b>\nCountry: <b>{country}</b>\n\n🔥 <i>No recent photos of this aircraft on JetPhotos yet!</i>\nYou have a rare chance to capture a historic shot: <b>First Registration</b> or <b>Hot Photo</b>!\n\nCheck current flight status on Flightradar24:",
        "pl": "Numer rejestracyjny: <b>{reg}</b>\nKraj: <b>{country}</b>\n\n🔥 <i>Brak aktualnych zdjęć tego samolotu na JetPhotos!</i>\nMasz wyjątkową szansę na zrobienie historycznego zdjęcia: <b>First Registration</b> lub <b>Hot Photo</b>!\n\nSprawdź aktualny status lotów na Flightradar24:",
    },
    "card_not_specified": {
        "ru": "Не указана",
        "en": "Not specified",
        "pl": "Nie podano",
    },
    "card_recently": {
        "ru": "Недавно",
        "en": "Recently",
        "pl": "Niedawno",
    },
    "card_aircraft_fallback": {
        "ru": "Самолёт",
        "en": "Aircraft",
        "pl": "Samolot",
    },
    "admin_only_msg": {
        "ru": "⛔️ Доступно только владельцу бота.",
        "en": "⛔️ Available only to the bot owner.",
        "pl": "⛔️ Dostępne tylko dla właściciela bota.",
    },
    "main_menu_title": {
        "ru": "✈️ Главное меню:",
        "en": "✈️ Main Menu:",
        "pl": "✈️ Menu główne:",
    },
    "sync_completed_title": {
        "ru": "🎉 <b>Синхронизация успешно завершена!</b>",
        "en": "🎉 <b>Sync completed successfully!</b>",
        "pl": "🎉 <b>Synchronizacja zakończona sukcesem!</b>",
    },
    "sync_photographer": {
        "ru": "👤 <b>Фотограф:</b>",
        "en": "👤 <b>Photographer:</b>",
        "pl": "👤 <b>Fotograf:</b>",
    },
    "sync_total_photos": {
        "ru": "📸 <b>Всего фото в базе:</b>",
        "en": "📸 <b>Total photos in database:</b>",
        "pl": "📸 <b>Łącznie zdjęć w bazie:</b>",
    },
    "sync_photos_unit": {
        "ru": "шт.",
        "en": "photos",
        "pl": "szt.",
    },
    "sync_unique_aircraft": {
        "ru": "✈️ <b>Уникальных самолётов:</b>",
        "en": "✈️ <b>Unique aircraft:</b>",
        "pl": "✈️ <b>Unikalnych samolotów:</b>",
    },
    "sync_aircraft_unit": {
        "ru": "бортов",
        "en": "aircraft",
        "pl": "samolotów",
    },
    "sync_ready_hint": {
        "ru": "Теперь твоя база готова! Отправь мне номер любого борта (например, <code>A6-EOY</code> или <code>SP-RZS</code>), чтобы проверить его наличие.",
        "en": "Your database is ready! Send me any registration number (e.g. <code>A6-EOY</code> or <code>SP-RZS</code>) to check if it's in your collection.",
        "pl": "Twoja baza jest gotowa! Wyślij mi dowolną rejestrację (np. <code>A6-EOY</code> lub <code>SP-RZS</code>), aby sprawdzić jej obecność w kolekcji.",
    },
    "btn_demo_base": {
        "ru": "🚀 Демо-база (606 бортов)",
        "en": "🚀 Demo Database (606 aircraft)",
        "pl": "🚀 Baza demo (606 samolotów)",
    },
    "status_on": {
        "ru": "Вкл",
        "en": "On",
        "pl": "Wł",
    },
    "status_off": {
        "ru": "Выкл",
        "en": "Off",
        "pl": "Wył",
    },
    "stars_payment_success_msg": {
        "ru": "🎉 <b>Оплата успешно получена ({amount} {currency})!</b>\n\n⭐ <b>Ваш статус повышен до PREMIUM на 30 дней!</b>\n\nВам открыты все профессиональные инструменты споттинга:\n• ⏰ <b>Безлимитные радар-сессии</b> у взлётной полосы (до 4 часов)\n• 🚨 <b>Экстренные алерты:</b> Squawk 7700 (бедствие) и диверты (уход на запасной)\n• 🎯 <b>Споттинг-план на 1 час:</b> список рейсов с разметкой «Кого ловить»\n• 🔔 <b>Push-уведомления на глиссаде</b> с фото-миниатюрой и MSN\n• 🔥 <b>Livery Hunter:</b> выявление самолётов со сменой ливреи для Hot Photos!",
        "en": "🎉 <b>Payment received successfully ({amount} {currency})!</b>\n\n⭐ <b>Your account has been upgraded to PREMIUM for 30 days!</b>\n\nYou now have access to all professional spotting tools:\n• ⏰ <b>Unlimited radar sessions</b> at runway (up to 4 hours)\n• 🚨 <b>Emergency alerts:</b> Squawk 7700 (distress) and diverts\n• 🎯 <b>1-hour spotting plan:</b> flight list tagged with who to catch\n• 🔔 <b>Glideslope push alerts</b> with photo preview & MSN\n• 🔥 <b>Livery Hunter:</b> detect aircraft with special/new liveries!",
        "pl": "🎉 <b>Płatność przyjęta pomyślnie ({amount} {currency})!</b>\n\n⭐ <b>Twój status został podniesiony do PREMIUM na 30 dni!</b>\n\nMasz dostęp do wszystkich profesjonalnych narzędzi spotterskich:\n• ⏰ <b>Nielimitowane sesje radaru</b> przy pasie (do 4 godzin)\n• 🚨 <b>Alerty awaryjne:</b> Squawk 7700 i diverty\n• 🎯 <b>Plan spottingu na 1 godzinę:</b> lista lotów z oznaczeniem celów\n• 🔔 <b>Powiadomienia na prostej (glideslope)</b> ze zdjęciem i MSN\n• 🔥 <b>Livery Hunter:</b> wyszukiwanie specjalnych malowań!",
    },
    "stats_summary_msg": {
        "ru": "📊 <b>Ваша статистика коллекции:</b>\n\n👤 <b>Фотограф:</b> {name}\n📸 <b>Всего фото в галерее:</b> {photos}\n✈️ <b>Уникальных бортов:</b> {aircraft}\n📡 <b>Радар споттинга:</b> {radar}\n⭐ <b>Тариф:</b> {tier}\n\n<i>База синхронизирована с JetPhotos.com</i>",
        "en": "📊 <b>Your Collection Statistics:</b>\n\n👤 <b>Photographer:</b> {name}\n📸 <b>Total photos in gallery:</b> {photos}\n✈️ <b>Unique aircraft:</b> {aircraft}\n📡 <b>Spotting radar:</b> {radar}\n⭐ <b>Plan:</b> {tier}\n\n<i>Database synced with JetPhotos.com</i>",
        "pl": "📊 <b>Statystyki Twojej kolekcji:</b>\n\n👤 <b>Fotograf:</b> {name}\n📸 <b>Zdjęcia w galerii:</b> {photos}\n✈️ <b>Unikalne samoloty:</b> {aircraft}\n📡 <b>Radar spottingu:</b> {radar}\n⭐ <b>Plan:</b> {tier}\n\n<i>Baza zsynchronizowana z JetPhotos.com</i>",
    },
    "prem_info_msg": {
        "ru": "⭐ <b>ПОДПИСКА PLANESPOTTER PREMIUM</b>\n\n<b>Зачем споттеру Premium?</b>\n• ⏰ <b>Безлимитный радар:</b> сессии до 4 часов непрерывно вместо 30 минут.\n• 🚨 <b>Алерты Squawk 7700 и Диверты:</b> мгновенное оповещение об аварийных бортах и посадках на запасной.\n• 🎯 <b>Споттинг-план на 1 час:</b> расписание прилётов/вылетов с фильтрацией «Кого ловить (новые борта)».\n• 🔔 <b>Push-уведомления на глиссаде:</b> предупреждение за 5–10 мин до касания полосы с фото-миниатюрой.\n• 🔥 <b>Livery Hunter:</b> выявление самолётов со сменой ливреи для Hot Photos.\n\n💳 <b>Стоимость: 50 Звёзд Telegram (⭐️ 50 XTR) в месяц</b> (~$0.99).\n<i>Оплата в 1 клик прямо в Telegram!</i>",
        "en": "⭐ <b>PLANESPOTTER PREMIUM SUBSCRIPTION</b>\n\n<b>Why choose Premium?</b>\n• ⏰ <b>Unlimited radar:</b> up to 4-hour continuous runway sessions instead of 30 mins.\n• 🚨 <b>Squawk 7700 & Divert alerts:</b> instant alerts for emergencies and diverted flights.\n• 🎯 <b>1-hour spotting plan:</b> flight schedule with tags for new & unphotographed aircraft.\n• 🔔 <b>Glideslope push alerts:</b> notification 5-10 min before touchdown with photo preview.\n• 🔥 <b>Livery Hunter:</b> detect aircraft with livery changes for Hot Photos.\n\n💳 <b>Price: 50 Telegram Stars (⭐️ 50 XTR) per month</b> (~$0.99).\n<i>1-click payment directly in Telegram!</i>",
        "pl": "⭐ <b>SUBSKRYPCJA PLANESPOTTER PREMIUM</b>\n\n<b>Dlaczego warto wybrać Premium?</b>\n• ⏰ <b>Nielimitowany radar:</b> sesje do 4 godzin ciągłej pracy przy pasie zamiast 30 minut.\n• 🚨 <b>Alerty Squawk 7700 i Diverty:</b> natychmiastowe powiadomienia o sytuacjach awaryjnych.\n• 🎯 <b>Plan spottingu na 1 godzinę:</b> rozkład z filtrem «Kogo łapać (nowe maszyny)».\n• 🔔 <b>Powiadomienia na prostej:</b> alert 5-10 minut przed lądowaniem z miniaturką zdjęcia.\n• 🔥 <b>Livery Hunter:</b> wykrywanie zmian malowania dla Hot Photos.\n\n💳 <b>Koszt: 50 Gwiazdek Telegram (⭐️ 50 XTR) na miesiąc</b> (~$0.99).\n<i>Płatność jednym kliknięciem w Telegramie!</i>",
    },
    "prem_btn_pay": {
        "ru": "⭐️ Оплатить 50 Звёзд Telegram",
        "en": "⭐️ Pay 50 Telegram Stars",
        "pl": "⭐️ Zapłać 50 Gwiazdek Telegram",
    },
    "invoice_title": {
        "ru": "⭐ PlaneSpotter Premium (30 дней)",
        "en": "⭐ PlaneSpotter Premium (30 days)",
        "pl": "⭐ PlaneSpotter Premium (30 dni)",
    },
    "invoice_desc": {
        "ru": "Режим Споттинга: расписание рейсов на 1 час с разметкой «Кого ловить», радар до 4 часов, Squawk 7700 и пуши на глиссаде.",
        "en": "Spotting Mode: 1-hour flight schedule with smart tags, radar up to 4h, Squawk 7700 & glideslope push.",
        "pl": "Tryb Spottingu: 1-godzinny rozkład lotów z oznaczeniem celów, radar do 4h, Squawk 7700 i powiadomienia na prostej.",
    },
    "invoice_price_label": {
        "ru": "⭐ 50 Звёзд Telegram",
        "en": "⭐ 50 Telegram Stars",
        "pl": "⭐ 50 Gwiazdek Telegram",
    },
    "demo_connecting_msg": {
        "ru": "⏳ <b>Готовлю демо-логбук (несколько примерных бортов)...</b>\n\nЭто займёт несколько секунд!",
        "en": "⏳ <b>Setting up a demo logbook (a few sample aircraft)...</b>\n\nThis takes a few seconds!",
        "pl": "⏳ <b>Przygotowuję demonstracyjny logbook (kilka przykładowych maszyn)...</b>\n\nTo potrwa kilka sekund!",
    },
    "radar_status_active": {
        "ru": "Активен ({airport}) 🟢",
        "en": "Active ({airport}) 🟢",
        "pl": "Aktywny ({airport}) 🟢",
    },
    "radar_status_off": {
        "ru": "Выключен ⚪",
        "en": "Disabled ⚪",
        "pl": "Wyłączony ⚪",
    },
    # Main reply buttons
    "btn_spotting_mode": {
        "ru": "🎯 Режим Споттинга",
        "en": "🎯 Spotting Mode",
        "pl": "🎯 Tryb Spottingu",
    },
    "btn_stop_radar": {
        "ru": "🛑 Остановить радар",
        "en": "🛑 Stop Radar",
        "pl": "🛑 Zatrzymaj radar",
    },
    "btn_atc_radio": {
        "ru": "📻 Радио ATC",
        "en": "📻 ATC Radio",
        "pl": "📻 Radio ATC",
    },
    "btn_spotter_hub": {
        "ru": "🛰 Spotter Hub",
        "en": "🛰 Spotter Hub",
        "pl": "🛰 Spotter Hub",
    },
    "btn_check_reg": {
        "ru": "🔎 Проверить борт",
        "en": "🔎 Check tail",
        "pl": "🔎 Sprawdź rejestrację",
    },
    "check_reg_prompt": {
        "ru": "🔎 <b>Проверка борта по базе</b>\n\nОтправьте регистрацию (например, <code>SP-LVD</code> или <code>A6-EOY</code>) — я скажу, есть ли этот борт в вашей базе JetPhotos.",
        "en": "🔎 <b>Tail number check</b>\n\nSend a registration (e.g. <code>SP-LVD</code> or <code>A6-EOY</code>) and I'll tell you whether it is in your JetPhotos database.",
        "pl": "🔎 <b>Sprawdzanie rejestracji</b>\n\nWyślij rejestrację (np. <code>SP-LVD</code> lub <code>A6-EOY</code>), a sprawdzę, czy jest w Twojej bazie JetPhotos.",
    },
    "airport_input_hint": {
        "ru": "✍️ Можно просто написать <b>код</b> (<code>KLU</code>, <code>LOWK</code>) или <b>название города</b> в чат — или выбрать из списка ниже.",
        "en": "✍️ You can simply type an airport <b>code</b> (<code>KLU</code>, <code>LOWK</code>) or a <b>city name</b> in chat — or pick from the list below.",
        "pl": "✍️ Możesz wpisać <b>kod</b> lotniska (<code>KLU</code>, <code>LOWK</code>) lub <b>nazwę miasta</b> — albo wybrać z listy poniżej.",
    },
    "search_results_title": {
        "ru": "🔎 <b>Найдено аэропортов: {n}</b>\nВыберите нужный:",
        "en": "🔎 <b>Airports found: {n}</b>\nChoose one:",
        "pl": "🔎 <b>Znalezione lotniska: {n}</b>\nWybierz:",
    },
    "not_recognized": {
        "ru": "🤔 Не понял запрос. Отправьте <b>номер борта</b> (<code>SP-LVD</code>), <b>код аэропорта</b> (<code>WAW</code>, <code>EPWA</code>) или <b>название города</b> (<code>Klagenfurt</code>).",
        "en": "🤔 I didn't get that. Send an <b>aircraft registration</b> (<code>SP-LVD</code>), an <b>airport code</b> (<code>WAW</code>, <code>EPWA</code>) or a <b>city name</b> (<code>Klagenfurt</code>).",
        "pl": "🤔 Nie rozumiem. Wyślij <b>rejestrację</b> (<code>SP-LVD</code>), <b>kod lotniska</b> (<code>WAW</code>, <code>EPWA</code>) lub <b>nazwę miasta</b> (<code>Klagenfurt</code>).",
    },
    "btn_location": {
        "ru": "📍 Моя локация",
        "en": "📍 My Location",
        "pl": "📍 Moja lokalizacja",
    },
    "btn_stats": {
        "ru": "📊 Моя статистика",
        "en": "📊 My Stats",
        "pl": "📊 Moje statystyki",
    },
    "btn_premium": {
        "ru": "⭐ Premium (Звёзды)",
        "en": "⭐ Premium (Stars)",
        "pl": "⭐ Premium (Gwiazdki)",
    },
    "btn_settings": {
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings",
        "pl": "⚙️ Ustawienia",
    },
    "btn_help": {
        "ru": "❓ Помощь",
        "en": "❓ Help",
        "pl": "❓ Pomoc",
    },

    # Onboarding & Start
    "start_lang_prompt": {
        "multi": (
            "✈️ <b>PlaneSpotter Bot & Hub 3.5</b>\n\n"
            "🇷🇺 <b>Добро пожаловать!</b> Персональный радар у полосы, расписание рейсов, радиосканер ATC и споттинг-блокнот.\n\n"
            "🇬🇧 <b>Welcome!</b> Runway radar, flight schedule, live ATC radio and aircraft logbook.\n\n"
            "🇵🇱 <b>Witaj!</b> Radar pod pasem startowym, rozkład lotów, nasłuch ATC i notatnik spottera.\n\n"
            "🌐 <b>Выберите язык / Select language / Wybierz język:</b>"
        ),
        "ru": "🌐 <b>Выберите язык интерфейса:</b>",
        "en": "🌐 <b>Select interface language:</b>",
        "pl": "🌐 <b>Wybierz preferowany język:</b>"
    },
    "welcome_title": {
        "ru": "👋 <b>Привет, споттер! Добро пожаловать в PlaneSpotter Bot!</b>",
        "en": "👋 <b>Hello, spotter! Welcome to PlaneSpotter Bot!</b>",
        "pl": "👋 <b>Cześć, spotterze! Witaj w PlaneSpotter Bot!</b>",
    },
    "welcome_body": {
        "ru": (
            "Ваш персональный ассистент для авиаспоттинга у взлётно-посадочной полосы:\n\n"
            "✈️ <b>Проверка бортов:</b> отправьте бортовой номер (например, <code>A6-EOY</code>, <code>SP-LVD</code>, <code>F-WWOW</code>).\n"
            "📡 <b>Умный радар:</b> алерты о заходах на посадку прямо на глиссаде.\n"
            "📻 <b>Радиосканер:</b> живой эфир вышки (TWR) и круга (APP).\n"
            "🎯 <b>Spotting Hub (Mini App):</b> расписание, точки съёмки и блокнот бортов.\n"
        ),
        "en": (
            "Your ultimate aviation spotting companion right by the runway:\n\n"
            "✈️ <b>Tail Check:</b> send any registration (e.g. <code>A6-EOY</code>, <code>SP-LVD</code>, <code>N12345</code>).\n"
            "📡 <b>Smart Radar:</b> real-time alerts as aircraft line up on final approach.\n"
            "📻 <b>Airband Radio:</b> live ATC communications (Tower & Approach).\n"
            "🎯 <b>Spotter Hub (Mini App):</b> hourly schedule, spotting guides & personal logbook.\n"
        ),
        "pl": (
            "Twój profesjonalny asystent do plane spottingu pod pasem startowym:\n\n"
            "✈️ <b>Sprawdzanie samolotu:</b> wyślij numer rejestracyjny (np. <code>SP-LVD</code>, <code>A6-EOY</code>, <code>SP-RZS</code>).\n"
            "📡 <b>Inteligentny radar:</b> alerty o samolotach na prostej do lądowania.\n"
            "📻 <b>Radio ATC:</b> nasłuch wieży (TWR) i zbliżania (APP) na żywo.\n"
            "🎯 <b>Spotter Hub (Mini App):</b> rozkład lotów, punkty spottingowe i osobisty logbook.\n"
        ),
    },
    "onboarding_tz_prompt": {
        "ru": (
            "📍 <b>Быстрая настройка:</b>\n"
            "Поделитесь геопозицией, чтобы автоматически определить <b>домашний аэропорт</b> и <b>часовой пояс</b>, либо выберите пояс вручную ⬇️"
        ),
        "en": (
            "📍 <b>Quick Setup:</b>\n"
            "Share your location to automatically configure your <b>home airport</b> and <b>timezone</b>, or choose manually below ⬇️"
        ),
        "pl": (
            "📍 <b>Szybka konfiguracja:</b>\n"
            "Udostępnij lokalizację, aby automatycznie ustalić <b>lotnisko domowe</b> i <b>strefę czasową</b>, lub wybierz ręcznie poniżej ⬇️"
        ),
    },
    "btn_share_location": {
        "ru": "📍 Поделиться локацией (авто-настройка)",
        "en": "📍 Share Location (Auto-setup)",
        "pl": "📍 Udostępnij lokalizację (auto)",
    },
    "btn_open_hub_cta": {
        "ru": "🛰 Открыть Spotter Hub (Mini App)",
        "en": "🛰 Launch Spotter Hub (Mini App)",
        "pl": "🛰 Otwórz Spotter Hub (Mini App)",
    },
    "btn_tz_manual": {
        "ru": "🕒 Выбрать пояс вручную",
        "en": "🕒 Choose Timezone",
        "pl": "🕒 Wybierz strefę",
    },
    "btn_tz_device": {
        "ru": "📱 Считать с устройства",
        "en": "📱 Sync from Device",
        "pl": "📱 Pobierz z urządzenia",
    },

    # Settings Menu
    "settings_title": {
        "ru": "⚙️ <b>НАСТРОЙКИ ПРОФИЛЯ СПОТТЕРА</b>",
        "en": "⚙️ <b>SPOTTER PROFILE SETTINGS</b>",
        "pl": "⚙️ <b>USTAWIENIA PROFILU SPOTTERA</b>",
    },
    "settings_body": {
        "ru": (
            "Здесь вы можете изменить язык интерфейса, часовой пояс для споттинг-плана и аэропорт по умолчанию:\n\n"
            "🌐 <b>Язык интерфейса:</b> {lang_display}\n"
            "🕒 <b>Часовой пояс:</b> <code>{timezone}</code> ({utc_offset})\n"
            "📍 <b>Домашний аэропорт:</b> <b>{airport}</b>\n"
            "🔔 <b>Споттинг-радар:</b> {notifications_status}\n"
        ),
        "en": (
            "Manage your interface language, spotting schedule timezone, and default airport:\n\n"
            "🌐 <b>Language:</b> {lang_display}\n"
            "🕒 <b>Timezone:</b> <code>{timezone}</code> ({utc_offset})\n"
            "📍 <b>Home Airport:</b> <b>{airport}</b>\n"
            "🔔 <b>Spotting Radar:</b> {notifications_status}\n"
        ),
        "pl": (
            "Zarządzaj językiem interfejsu, strefą czasową rozkładu i domyślnym lotniskiem:\n\n"
            "🌐 <b>Język:</b> {lang_display}\n"
            "🕒 <b>Strefa czasowa:</b> <code>{timezone}</code> ({utc_offset})\n"
            "📍 <b>Lotnisko domowe:</b> <b>{airport}</b>\n"
            "🔔 <b>Radar spottingowy:</b> {notifications_status}\n"
        ),
    },
    "settings_btn_lang": {
        "ru": "🌐 Сменить язык",
        "en": "🌐 Change Language",
        "pl": "🌐 Zmień język",
    },
    "settings_btn_tz": {
        "ru": "🕒 Часовой пояс",
        "en": "🕒 Timezone",
        "pl": "🕒 Strefa czasowa",
    },
    "settings_btn_airport": {
        "ru": "📍 Любимый аэропорт",
        "en": "📍 Favorite Airport",
        "pl": "📍 Ulubione lotnisko",
    },
    "settings_btn_notify": {
        "ru": "🔔 Уведомления радара",
        "en": "🔔 Radar Alerts",
        "pl": "🔔 Alerty radaru",
    },
    "settings_btn_back": {
        "ru": "🔙 Назад в настройки",
        "en": "🔙 Back to Settings",
        "pl": "🔙 Wróć do ustawień",
    },

    # Language submenu
    "lang_select_prompt": {
        "ru": "🌐 <b>Выберите язык интерфейса:</b>",
        "en": "🌐 <b>Select interface language:</b>",
        "pl": "🌐 <b>Wybierz język interfejsu:</b>",
    },
    "lang_changed": {
        "ru": "✅ Язык успешно изменён на <b>Русский 🇷🇺</b>!",
        "en": "✅ Language successfully changed to <b>English 🇬🇧</b>!",
        "pl": "✅ Język pomyślnie zmieniony na <b>Polski 🇵🇱</b>!",
    },

    # Timezone submenu
    "tz_select_prompt": {
        "ru": (
            "🕒 <b>Настройка часового пояса:</b>\n\n"
            "Текущий пояс: <code>{tz}</code> ({offset})\n\n"
            "Выберите способ установки:"
        ),
        "en": (
            "🕒 <b>Timezone Configuration:</b>\n\n"
            "Current timezone: <code>{tz}</code> ({offset})\n\n"
            "Choose a setup method:"
        ),
        "pl": (
            "🕒 <b>Konfiguracja strefy czasowej:</b>\n\n"
            "Aktualna strefa: <code>{tz}</code> ({offset})\n\n"
            "Wybierz metodę ustawienia:"
        ),
    },
    "tz_changed": {
        "ru": "✅ Часовой пояс установлен: <b>{tz}</b> ({offset})",
        "en": "✅ Timezone updated: <b>{tz}</b> ({offset})",
        "pl": "✅ Strefa czasowa zaktualizowana: <b>{tz}</b> ({offset})",
    },

    # Location shared
    "location_detected": {
        "ru": (
            "📍 <b>Геопозиция определена!</b>\n\n"
            "Ближайший аэропорт: <b>{name} ({icao} / {iata})</b>\n"
            "Страна: {country}\n"
            "Расстояние до полосы: <b>{dist:.1f} км</b>\n"
            "Установлен часовой пояс: <code>{tz}</code> ({offset})\n\n"
            "🎯 <b>Что сделать:</b>"
        ),
        "en": (
            "📍 <b>Location detected!</b>\n\n"
            "Nearest Airport: <b>{name} ({icao} / {iata})</b>\n"
            "Country: {country}\n"
            "Distance to runway: <b>{dist:.1f} km</b>\n"
            "Configured timezone: <code>{tz}</code> ({offset})\n\n"
            "🎯 <b>Choose an action:</b>"
        ),
        "pl": (
            "📍 <b>Lokalizacja wykryta!</b>\n\n"
            "Najbliższe lotnisko: <b>{name} ({icao} / {iata})</b>\n"
            "Kraj: {country}\n"
            "Odległość do pasa: <b>{dist:.1f} km</b>\n"
            "Ustawiono strefę czasową: <code>{tz}</code> ({offset})\n\n"
            "🎯 <b>Wybierz działanie:</b>"
        ),
    },

    # Aircraft lookup
    "aircraft_not_found": {
        "ru": "🔍 Самолёт с бортовым <b>{reg}</b> не найден в активном эфире. Попробуйте проверить в Spotter Hub:",
        "en": "🔍 Aircraft with tail <b>{reg}</b> was not found in active traffic. Try searching in Spotter Hub:",
        "pl": "🔍 Samolot o rejestracji <b>{reg}</b> nie został znaleziony w aktywnym ruchu. Sprawdź w Spotter Hub:",
    },
    "btn_view_photos": {
        "ru": "🌐 Все фото борта на JetPhotos",
        "en": "🌐 All Photos on JetPhotos",
        "pl": "🌐 Wszystkie zdjęcia na JetPhotos",
    },
    "btn_fr24": {
        "ru": "✈️ Flightradar24",
        "en": "✈️ Flightradar24",
        "pl": "✈️ Flightradar24",
    },
    "btn_open_in_hub": {
        "ru": "🛰 Открыть в Spotter Hub",
        "en": "🛰 Open in Spotter Hub",
        "pl": "🛰 Otwórz w Spotter Hub",
    },
    "btn_aircraft_facts": {
        "ru": "🔍 Факты и история борта",
        "en": "🔍 Aircraft Facts & History",
        "pl": "🔍 Fakty i historia samolotu",
    },

    # Radar
    "radar_running": {
        "ru": "📡 <b>РАДАР АКТИВИРОВАН: {iata} ({icao})</b>\nРадиус: 50 км вокруг глиссады.\nПри появлении интересных бортов вы сразу получите алерт!",
        "en": "📡 <b>RADAR ACTIVATED: {iata} ({icao})</b>\nRadius: 50 km around glidepath.\nYou will receive alerts when aircraft line up!",
        "pl": "📡 <b>RADAR AKTYWNY: {iata} ({icao})</b>\nPromień: 50 km wokół ścieżki schodzenia.\nOtrzymasz alert, gdy samolot wejdzie na prostą!",
    },
    "radar_stopped": {
        "ru": "🛑 <b>Споттинг-радар остановлен.</b> Вы больше не получаете уведомления о заходах.",
        "en": "🛑 <b>Spotting radar stopped.</b> You will no longer receive approach alerts.",
        "pl": "🛑 <b>Radar spottingowy zatrzymany.</b> Powiadomienia zostały wyłączone.",
    },

    # Help
    "help_text": {
        "ru": (
            "📖 <b>КАК ПОЛЬЗОВАТЬСЯ PLANESPOTTER BOT & HUB:</b>\n\n"
            "1. <b>Бортовые номера:</b> отправьте боту регистрацию самолёта (например, <code>SP-LVD</code> или <code>A6-EOY</code>).\n"
            "2. <b>Режим Споттинга:</b> запустите радар для вашего аэропорта и получайте push-уведомления.\n"
            "3. <b>Радио ATC:</b> слушайте переговоры пилотов и диспетчеров (TWR/APP).\n"
            "4. <b>Spotter Hub:</b> полноэкранный мини-апп с интерактивным расписанием, точками на карте и логбуком.\n"
            "5. <b>Настройки:</b> переключайте язык (RU/EN/PL), домашний аэропорт и часовой пояс в меню ⚙️ Настройки."
        ),
        "en": (
            "📖 <b>HOW TO USE PLANESPOTTER BOT & HUB:</b>\n\n"
            "1. <b>Tail Numbers:</b> send any aircraft registration (e.g. <code>SP-LVD</code> or <code>A6-EOY</code>).\n"
            "2. <b>Spotting Mode:</b> start radar for your airport to get instant arrival alerts.\n"
            "3. <b>ATC Radio:</b> tune in to live Tower and Approach tower communications.\n"
            "4. <b>Spotter Hub:</b> rich Mini App with flight schedules, spotting guides & personal logbook.\n"
            "5. <b>Settings:</b> switch language (RU/EN/PL), home airport, and timezone in ⚙️ Settings."
        ),
        "pl": (
            "📖 <b>JAK KORZYSTAĆ Z PLANESPOTTER BOT & HUB:</b>\n\n"
            "1. <b>Numery rejestracyjne:</b> wyślij rejestrację samolotu (np. <code>SP-LVD</code> lub <code>A6-EOY</code>).\n"
            "2. <b>Tryb Spottingu:</b> włącz radar lotniska i otrzymuj powiadomienia o lądowaniach.\n"
            "3. <b>Radio ATC:</b> słuchaj na żywo rozmów wieży (TWR) i zbliżania (APP).\n"
            "4. <b>Spotter Hub:</b> pełnoekranowy Mini App z rozkładem lotów, punktami foto i logbookiem.\n"
            "5. <b>Ustawienia:</b> zmień język (RU/EN/PL), domowe lotnisko i strefę czasową w ⚙️ Ustawieniach."
        ),
    },

    # CardBox Menu Button title
    "menu_button_title": {
        "ru": "🛰 Spotter Hub",
        "en": "🛰 Spotter Hub",
        "pl": "🛰 Spotter Hub",
    },

    # Spotting Mode & Schedule Menu
    "spotting_menu_msg": {
        "ru": (
            "🎯 <b>РЕЖИМ СПОТТИНГА: ВЫБОР АЭРОПОРТА</b>\n\n"
            "Выберите удобный вариант:\n\n"
            "1️⃣ <b>Поделиться геопозицией 📍</b> — нажмите кнопку «📍 Моя локация» внизу.\n"
            "2️⃣ <b>Выбрать аэропорт из списка</b> ниже или просто <b>написать код в чат</b> (например: <code>GDN</code>, <code>EPGD</code>, <code>WAW</code>)."
        ),
        "en": (
            "🎯 <b>SPOTTING MODE: SELECT AIRPORT</b>\n\n"
            "Choose an option:\n\n"
            "1️⃣ <b>Share location 📍</b> — tap '📍 My Location' below.\n"
            "2️⃣ <b>Select an airport from the list</b> below or <b>type the code in chat</b> (e.g. <code>WAW</code>, <code>GDN</code>, <code>LHR</code>)."
        ),
        "pl": (
            "🎯 <b>TRYB SPOTTINGU: WYBIERZ LOTNISKO</b>\n\n"
            "Wybierz dogodną opcję:\n\n"
            "1️⃣ <b>Udostępnij lokalizację 📍</b> — kliknij przycisk „📍 Moja lokalizacja” na dole.\n"
            "2️⃣ <b>Wybierz lotnisko z listy</b> poniżej lub <b>wpisz kod na czacie</b> (np. <code>WAW</code>, <code>GDN</code>, <code>KRK</code>)."
        ),
    },
    "btn_stop_active_radar": {
        "ru": "🛑 Остановить активный радар",
        "en": "🛑 Stop Active Radar",
        "pl": "🛑 Zatrzymaj aktywny radar",
    },
    "btn_browse_geo": {
        "ru": "🌍 Выбрать по странам и городам ↗",
        "en": "🌍 Browse by Country & City ↗",
        "pl": "🌍 Wybierz wg kraju i miasta ↗",
    },
    "geo_countries_title": {
        "ru": "🌍 <b>ВЫБОР АЭРОПОРТА: СТРАНЫ</b>\n\nВыберите страну:\n\n✍️ Или просто напишите код аэропорта / город в чат (KLU, LOWK, Klagenfurt).",
        "en": "🌍 <b>SELECT AIRPORT: COUNTRIES</b>\n\nChoose a country:\n\n✍️ Or just type an airport code / city in chat (KLU, LOWK, Klagenfurt).",
        "pl": "🌍 <b>WYBÓR LOTNISKA: KRAJE</b>\n\nWybierz kraj:\n\n✍️ Albo wpisz kod lotniska / miasto (KLU, LOWK, Klagenfurt).",
    },
    "geo_cities_title": {
        "ru": "📍 <b>{country} — ВЫБОР ГОРОДА</b>\n\nВыберите город или аэропорт:",
        "en": "📍 <b>{country} — SELECT CITY</b>\n\nChoose a city or airport:",
        "pl": "📍 <b>{country} — WYBÓR MIASTA</b>\n\nWybierz miasto lub lotnisko:",
    },
    "geo_airports_title": {
        "ru": "✈️ <b>{city} — АЭРОПОРТЫ</b>\n\nВыберите нужный аэропорт:",
        "en": "✈️ <b>{city} — AIRPORTS</b>\n\nChoose an airport:",
        "pl": "✈️ <b>{city} — LOTNISKA</b>\n\nWybierz lotnisko:",
    },
    "btn_back_to_countries": {
        "ru": "« Назад к странам",
        "en": "« Back to Countries",
        "pl": "« Wróć do krajów",
    },
    "btn_back_to_cities": {
        "ru": "« Назад к городам",
        "en": "« Back to Cities",
        "pl": "« Wróć do miast",
    },
    "btn_back_to_spotting": {
        "ru": "« Назад в меню споттинга",
        "en": "« Back to Spotting Menu",
        "pl": "« Wróć do menu spottingu",
    },
    "btn_buy_premium_inline": {
        "ru": "⭐ Оформить Premium за 50 ⭐️",
        "en": "⭐ Get Premium (50 ⭐️)",
        "pl": "⭐ Kup Premium (50 ⭐️)",
    },

    # Spotting Plan / Schedule
    "plan_header": {
        "ru": "🎯 <b>СПОТТИНГ-ПЛАН: {icao} ({iata}){mode_label}</b>",
        "en": "🎯 <b>SPOTTING PLAN: {icao} ({iata}){mode_label}</b>",
        "pl": "🎯 <b>PLAN SPOTTINGU: {icao} ({iata}){mode_label}</b>",
    },
    "plan_mode_dep_label": {
        "ru": " [🛫 ТОЛЬКО ВЗЛЁТЫ]",
        "en": " [🛫 DEPARTURES ONLY]",
        "pl": " [🛫 TYLKO ODLOTY]",
    },
    "plan_mode_arr_label": {
        "ru": " [🛬 ТОЛЬКО ПОСАДКИ]",
        "en": " [🛬 ARRIVALS ONLY]",
        "pl": " [🛬 TYLKO PRZYLOTY]",
    },
    "plan_sub_schedule": {
        "ru": "<i>Расписание на 1 час: {count} рейсов{airline_filter} | Стр. {page}/{total_pages}</i>\n",
        "en": "<i>1-hour schedule: {count} flights{airline_filter} | Page {page}/{total_pages}</i>\n",
        "pl": "<i>Rozkład na 1 godzinę: {count} lotów{airline_filter} | Str. {page}/{total_pages}</i>\n",
    },
    "plan_filter_prefix": {
        "ru": " • Фильтр: <b>{filter}</b>",
        "en": " • Filter: <b>{filter}</b>",
        "pl": " • Filtr: <b>{filter}</b>",
    },
    "plan_this_hour": {
        "ru": "✈️ <b>В этот час:</b> ",
        "en": "✈️ <b>This hour:</b> ",
        "pl": "✈️ <b>W tej godzinie:</b> ",
    },
    "plan_no_flights_msg": {
        "ru": "<i>Рейсов по выбранным критериям не найдено.</i>\n",
        "en": "<i>No flights found matching selected criteria.</i>\n",
        "pl": "<i>Nie znaleziono lotów spełniających wybrane kryteria.</i>\n",
    },
    "plan_badge_new": {
        "ru": "🔴 <b>НОВЫЙ</b>",
        "en": "🔴 <b>NEW</b>",
        "pl": "🔴 <b>NOWY</b>",
    },
    "plan_badge_in_db": {
        "ru": "🟢 В базе ({cnt} фото)",
        "en": "🟢 In DB ({cnt} photos)",
        "pl": "🟢 W bazie ({cnt} zdjęć)",
    },
    "plan_badge_divert": {
        "ru": " [⚠️ ДИВЕРТ!]",
        "en": " [⚠️ DIVERT!]",
        "pl": " [⚠️ DYWERSJA!]",
    },
    "plan_fr24_hint": {
        "ru": "💡 <i>Кликайте на номер борта или рейса для перехода во Flightradar24!</i>",
        "en": "💡 <i>Tap tail or flight number to open in Flightradar24!</i>",
        "pl": "💡 <i>Kliknij rejestrację lub numer lotu, aby przejść do Flightradar24!</i>",
    },
    "plan_fetch_error": {
        "ru": "⚠️ Не удалось получить текущее расписание для аэропорта {iata}. Попробуйте позже.",
        "en": "⚠️ Could not fetch current schedule for airport {iata}. Please try again later.",
        "pl": "⚠️ Nie udało się pobrać aktualnego rozkładu dla lotniska {iata}. Spróbuj ponownie później.",
    },

    # Spotting Plan Buttons
    "btn_plan_all_flights": {
        "ru": "🔄 Все рейсы",
        "en": "🔄 All Flights",
        "pl": "🔄 Wszystkie loty",
    },
    "btn_plan_departures": {
        "ru": "🛫 Взлёты",
        "en": "🛫 Departures",
        "pl": "🛫 Odloty",
    },
    "btn_plan_arrivals": {
        "ru": "🛬 Посадки",
        "en": "🛬 Arrivals",
        "pl": "🛬 Przyloty",
    },
    "btn_plan_reset_filter": {
        "ru": "✖️ Сбросить фильтр",
        "en": "✖️ Reset Filter",
        "pl": "✖️ Wyczyść filtr",
    },
    "btn_plan_prev": {
        "ru": "◀️ Назад",
        "en": "◀️ Back",
        "pl": "◀️ Wstecz",
    },
    "btn_plan_page": {
        "ru": "Стр. {page}/{total_pages}",
        "en": "Page {page}/{total_pages}",
        "pl": "Str. {page}/{total_pages}",
    },
    "btn_plan_next": {
        "ru": "Вперёд ▶️",
        "en": "Next ▶️",
        "pl": "Dalej ▶️",
    },
    "btn_spotterguide_spots": {
        "ru": "📍 Точки SpotterGuide ({iata})",
        "en": "📍 SpotterGuide Spots ({iata})",
        "pl": "📍 Miejscówki SpotterGuide ({iata})",
    },
    "btn_atc_radio_inline": {
        "ru": "📻 Радиопереговоры ATC и частоты",
        "en": "📻 ATC Radio & Frequencies",
        "pl": "📻 Radio ATC i częstotliwości",
    },
    "btn_radar_30": {
        "ru": "⏱ Радар 30 мин (Free)",
        "en": "⏱ Radar 30 min (Free)",
        "pl": "⏱ Radar 30 min (Free)",
    },
    "btn_radar_240": {
        "ru": "⭐ Радар 4ч (Premium)",
        "en": "⭐ Radar 4h (Premium)",
        "pl": "⭐ Radar 4h (Premium)",
    },

    # Radar status messages
    "radar_stopped_msg": {
        "ru": (
            "🛑 <b>Радар споттинга ОСТАНОВЛЕН.</b>\n\n"
            "Фоновый мониторинг воздушного пространства отключён. Уведомления о подлётах больше не будут приходить.\n"
            "Отличного отдыха после споттинга! 📸"
        ),
        "en": (
            "🛑 <b>Spotting radar STOPPED.</b>\n\n"
            "Airspace monitoring deactivated. Approach notifications will no longer be sent.\n"
            "Great spotting session! 📸"
        ),
        "pl": (
            "🛑 <b>Radar spottingowy ZATRZYMANY.</b>\n\n"
            "Monitorowanie przestrzeni powietrznej wyłączone. Powiadomienia o podejściach nie będą już wysyłane.\n"
            "Udanego odpoczynku po spottingu! 📸"
        ),
    },
    "radar_not_active_msg": {
        "ru": (
            "ℹ️ <b>Радар в данный момент не был активен.</b>\n\n"
            "Чтобы запустить мониторинг, нажмите <b>🎯 Режим Споттинга</b> или отправьте локацию 📍!"
        ),
        "en": (
            "ℹ️ <b>Radar is not currently active.</b>\n\n"
            "To start monitoring, tap <b>🎯 Spotting Mode</b> or share location 📍!"
        ),
        "pl": (
            "ℹ️ <b>Radar nie był w tej chwili aktywny.</b>\n\n"
            "Aby włączyć monitorowanie, kliknij <b>🎯 Tryb Spottingu</b> lub udostępnij lokalizację 📍!"
        ),
    },

    # ATC Radio Menu
    "atc_menu_title": {
        "ru": "📻 <b>РАДИОПЕРЕГОВОРЫ ATC И ЧАСТОТЫ АЭРОПОРТОВ</b>",
        "en": "📻 <b>ATC AIRBAND RADIO & AIRPORT FREQUENCIES</b>",
        "pl": "📻 <b>ROZMOWY LOTNICZE ATC I CZĘSTOTLIWOŚCI LOTNISK</b>",
    },
    "atc_menu_body": {
        "ru": (
            "📍 Выбранный аэропорт: <b>{iata} ({icao})</b>\n\n"
            "Выберите аэропорт, чтобы узнать частоты вышки (TWR), круга (APP), руления (GND) и погодного информера (ATIS), а также слушать живой эфир:\n"
        ),
        "en": (
            "📍 Selected Airport: <b>{iata} ({icao})</b>\n\n"
            "Choose an airport to check Tower (TWR), Approach (APP), Ground (GND), and ATIS weather frequencies, or stream live audio:\n"
        ),
        "pl": (
            "📍 Wybrane lotnisko: <b>{iata} ({icao})</b>\n\n"
            "Wybierz lotnisko, aby sprawdzić częstotliwości wieży (TWR), zbliżania (APP), płyty (GND) oraz ATIS, lub słuchać transmisji na żywo:\n"
        ),
    },
    "atc_btn_scanner": {
        "ru": "📻 Запустить радио-сканер ({iata})",
        "en": "📻 Launch Radio Scanner ({iata})",
        "pl": "📻 Uruchom skaner radiowy ({iata})",
    },

    # Radar Live Push Alerts
    "radar_alert_emergency": {
        "ru": "🚨🚨 <b>ЧРЕЗВЫЧАЙНАЯ СИТУАЦИЯ В ЭФИРЕ: SQUAWK {squawk}!</b> 🚨🚨",
        "en": "🚨🚨 <b>AIRSPACE EMERGENCY: SQUAWK {squawk}!</b> 🚨🚨",
        "pl": "🚨🚨 <b>SYTUACJA AWARYJNA: SQUAWK {squawk}!</b> 🚨🚨",
    },
    "radar_alert_divert": {
        "ru": "🔄 <b>ВНИМАНИЕ: УХОД НА ЗАПАСНОЙ (ДИВЕРТ В {icao})!</b>",
        "en": "🔄 <b>ATTENTION: DIVERT TO {icao}!</b>",
        "pl": "🔄 <b>UWAGA: PRZEKIEROWANIE / DYWERSJA DO {icao}!</b>",
    },
    "radar_alert_unspotted_arr": {
        "ru": "🛬 <b>СПОТТИНГ-РАДАР: ПОСАДКА В АЭРОПОРТ {icao}!</b>",
        "en": "🛬 <b>SPOTTING RADAR: ARRIVAL AT {icao}!</b>",
        "pl": "🛬 <b>RADAR SPOTTINGOWY: LĄDOWANIE NA {icao}!</b>",
    },
    "radar_alert_unspotted_dep": {
        "ru": "🛫 <b>СПОТТИНГ-РАДАР: ВЗЛЁТ ИЗ АЭРОПОРТА {icao}!</b>",
        "en": "🛫 <b>SPOTTING RADAR: DEPARTURE FROM {icao}!</b>",
        "pl": "🛫 <b>RADAR SPOTTINGOWY: ODLOT Z {icao}!</b>",
    },
    "radar_alert_unspotted_gnd": {
        "ru": "🛫 <b>СПОТТИНГ-РАДАР: ВЫРУЛИВАНИЕ НА ВПП ({icao})!</b>",
        "en": "🛫 <b>SPOTTING RADAR: TAXI TO RUNWAY ({icao})!</b>",
        "pl": "🛫 <b>RADAR SPOTTINGOWY: KOŁOWANIE NA PAS ({icao})!</b>",
    },
    "radar_alert_unspotted_air": {
        "ru": "✈️ <b>СПОТТИНГ-РАДАР: БОРТ В НЕБЕ НАД {icao}!</b>",
        "en": "✈️ <b>SPOTTING RADAR: AIRCRAFT OVER {icao}!</b>",
        "pl": "✈️ <b>RADAR SPOTTINGOWY: SAMOLOT NAD {icao}!</b>",
    },
    "radar_not_in_collection": {
        "ru": "🎯 <b>Этого борта ещё НЕТ в вашей коллекции!</b>",
        "en": "🎯 <b>This aircraft is NOT YET in your collection!</b>",
        "pl": "🎯 <b>Tego samolotu NIE MA jeszcze w Twojej kolekcji!</b>",
    },
    "radar_btn_fr24": {
        "ru": "✈️ Смотреть на Flightradar24",
        "en": "✈️ Open in Flightradar24",
        "pl": "✈️ Zobacz na Flightradar24",
    },
    "radar_btn_jp": {
        "ru": "📷 JetPhotos борта",
        "en": "📷 JetPhotos tail photos",
        "pl": "📷 Zdjęcia na JetPhotos",
    },

    # Location messages
    "location_not_found": {
        "ru": "📍 Локация получена, но поблизости не найдено известных международных аэропортов.",
        "en": "📍 Location received, but no known international airports were found nearby.",
        "pl": "📍 Lokalizacja odebrana, lecz w pobliżu nie znaleziono znanych lotnisk międzynarodowych.",
    },

    # Radar session activation
    "radar_prem_limit_warning": {
        "ru": "⚠️ Сессии радара свыше 30 минут доступны в подписке <b>Premium</b>. Активирую бесплатную сессию на <b>30 минут</b>!",
        "en": "⚠️ Radar sessions over 30 minutes require a <b>Premium</b> subscription. Activating free <b>30-minute</b> session!",
        "pl": "⚠️ Sesje radaru powyżej 30 minut wymagają subskrypcji <b>Premium</b>. Aktywuję darmową sesję na <b>30 minut</b>!",
    },
    "radar_activated_msg": {
        "ru": (
            "✅ <b>Радар аэропорта {icao} АКТИВИРОВАН на {minutes} мин!</b>\n\n"
            "🎯 <b>Что отслеживается:</b>\n"
            "• Самолёты на посадку и взлёт в {icao} (эшелоны выше 1 800м отфильтрованы)\n"
            "• 🚨 Экстренные ситуации: Squawk 7700 и уходы на запасной (диверты)\n"
            "• 🔔 Push-уведомление при заходе борта, которого нет в вашей коллекции\n\n"
            "<i>Спокойно снимайте у полосы — бот предупредит о редких бортах вовремя! 📸</i>"
        ),
        "en": (
            "✅ <b>Airport radar for {icao} ACTIVATED for {minutes} min!</b>\n\n"
            "🎯 <b>What is tracked:</b>\n"
            "• Aircraft arrivals and departures at {icao} (cruising traffic above 1,800m filtered)\n"
            "• 🚨 Emergency squawks: Squawk 7700 and diversions\n"
            "• 🔔 Push notification when an unspotted aircraft lines up\n\n"
            "<i>Spot in peace by the runway — the bot will alert you on time! 📸</i>"
        ),
        "pl": (
            "✅ <b>Radar dla lotniska {icao} AKTYWOWANY na {minutes} min!</b>\n\n"
            "🎯 <b>Zakres monitorowania:</b>\n"
            "• Samoloty lądujące i startujące z {icao} (pułap powyżej 1 800m odfiltrowany)\n"
            "• 🚨 Sytuacje awaryjne: Squawk 7700 oraz lądowania zapasowe (dywersje)\n"
            "• 🔔 Powiadomienie push, gdy podchodzi samolot, którego nie ma w Twojej kolekcji\n\n"
            "<i>Spokojnie fotografuj przy pasie — bot ostrzeże Cię o ciekawych maszynach! 📸</i>"
        ),
    },

    # ATC Card details & playback
    "atc_card_title": {
        "ru": "📻 <b>РАДИОПЕРЕГОВОРЫ И ЧАСТОТЫ ATC: {icao} ({iata})</b>",
        "en": "📻 <b>ATC RADIO & FREQUENCIES: {icao} ({iata})</b>",
        "pl": "📻 <b>ROZMOWY I CZĘSTOTLIWOŚCI ATC: {icao} ({iata})</b>",
    },
    "atc_not_found": {
        "ru": "⚠️ Частоты для {iata}/{icao} пока не найдены в базе.",
        "en": "⚠️ Frequencies for {iata}/{icao} not found in database yet.",
        "pl": "⚠️ Częstotliwości dla {iata}/{icao} nie zostały jeszcze znalezione w bazie.",
    },
    "atc_official_freqs": {
        "ru": "📡 <b>Официальные рабочие частоты:</b>",
        "en": "📡 <b>Official operating frequencies:</b>",
        "pl": "📡 <b>Oficjalne częstotliwości operacyjne:</b>",
    },
    "atc_freq_twr": {
        "ru": "• 🏢 <b>Вышка (TWR / Взлёт-Посадка):</b> <code>{freq}</code>",
        "en": "• 🏢 <b>Tower (TWR / Takeoff-Landing):</b> <code>{freq}</code>",
        "pl": "• 🏢 <b>Wieża (TWR / Starty-Lądowania):</b> <code>{freq}</code>",
    },
    "atc_freq_app": {
        "ru": "• 🛰 <b>Подход (APP / Круг / Радар):</b> <code>{freq}</code>",
        "en": "• 🛰 <b>Approach (APP / Radar):</b> <code>{freq}</code>",
        "pl": "• 🛰 <b>Zbliżanie (APP / Radar):</b> <code>{freq}</code>",
    },
    "atc_freq_gnd": {
        "ru": "• 🚜 <b>Руление (GND / Перрон):</b> <code>{freq}</code>",
        "en": "• 🚜 <b>Ground (GND / Apron):</b> <code>{freq}</code>",
        "pl": "• 🚜 <b>Płyta (GND / Kołowanie):</b> <code>{freq}</code>",
    },
    "atc_freq_atis": {
        "ru": "• 🌦 <b>Метеосводка (ATIS):</b> <code>{freq}</code>",
        "en": "• 🌦 <b>Weather (ATIS):</b> <code>{freq}</code>",
        "pl": "• 🌦 <b>Pogoda (ATIS):</b> <code>{freq}</code>",
    },
    "atc_stream_active": {
        "ru": "🟢 <b>Онлайн-стрим LiveATC: АКТИВЕН</b>",
        "en": "🟢 <b>LiveATC Online Stream: ACTIVE</b>",
        "pl": "🟢 <b>Transmisja LiveATC: AKTYWNA</b>",
    },
    "atc_stream_channels": {
        "ru": "<i>Каналы: {titles}</i>\n",
        "en": "<i>Channels: {titles}</i>\n",
        "pl": "<i>Kanały: {titles}</i>\n",
    },
    "atc_stream_hint": {
        "ru": "💡 <i>Слушайте прямо в Telegram через встроенный плеер или скачайте .m3u плейлист для фонового прослушивания:</i>",
        "en": "💡 <i>Listen right in Telegram via built-in player or download .m3u playlist for background playback:</i>",
        "pl": "💡 <i>Słuchaj bezpośrednio w Telegramie przez odtwarzacz lub pobierz playlistę .m3u do odtwarzania w tle:</i>",
    },
    "atc_stream_unavailable": {
        "ru": "🔴 <b>Онлайн-стрим LiveATC: НЕДОСТУПЕН</b>",
        "en": "🔴 <b>LiveATC Online Stream: UNAVAILABLE</b>",
        "pl": "🔴 <b>Transmisja LiveATC: NIEDOSTĘPNA</b>",
    },
    "atc_stream_unavail_note": {
        "ru": "В данном аэропорту нет постоянного интернет-стрима LiveATC.",
        "en": "This airport does not have an active 24/7 LiveATC internet stream.",
        "pl": "To lotnisko nie posiada całodobowej transmisji internetowej LiveATC.",
    },
    "atc_airband_hint": {
        "ru": "💡 <i>Если вы находитесь рядом с аэропортом — настройте портативный радиосканер (Airband 118-136 MHz) на указанную вышку (TWR).</i>",
        "en": "💡 <i>If you are near the airport, tune your handheld radio scanner (Airband 118-136 MHz) to the Tower (TWR) frequency.</i>",
        "pl": "💡 <i>Jeśli jesteś w pobliżu lotniska, nastaw skaner nasłuchowy (Airband 118-136 MHz) na częstotliwość wieży (TWR).</i>",
    },
    "atc_btn_listen_tg": {
        "ru": "📻 Слушать прямо в Telegram (Плеер)",
        "en": "📻 Listen in Telegram (Player)",
        "pl": "📻 Słuchaj w Telegramie (Odtwarzacz)",
    },
    "atc_btn_download_m3u": {
        "ru": "📥 Скачать .m3u плейлист",
        "en": "📥 Download .m3u Playlist",
        "pl": "📥 Pobierz playlistę .m3u",
    },
    "atc_btn_liveatc_web": {
        "ru": "🌐 Веб-плеер LiveATC",
        "en": "🌐 LiveATC Web Player",
        "pl": "🌐 LiveATC Web Player",
    },
    "atc_btn_back_plan": {
        "ru": "🔙 Назад к споттинг-плану",
        "en": "🔙 Back to Spotting Plan",
        "pl": "🔙 Wróć do planu spottingu",
    },
    "atc_btn_open_scanner_tg": {
        "ru": "📻 Открыть сканер частот в Telegram",
        "en": "📻 Open Frequency Scanner in Telegram",
        "pl": "📻 Otwórz skaner częstotliwości w Telegramie",
    },
    "atc_btn_check_liveatc": {
        "ru": "🌐 Проверить LiveATC.net",
        "en": "🌐 Check LiveATC.net",
        "pl": "🌐 Sprawdź LiveATC.net",
    },
    "atc_btn_back_freqs": {
        "ru": "🔙 К частотам аэропорта",
        "en": "🔙 Back to Airport Frequencies",
        "pl": "🔙 Wróć do częstotliwości lotniska",
    },
    "atc_playlist_not_found": {
        "ru": "⚠️ Для аэропорта {icao} нет активных прямых потоков в LiveATC.",
        "en": "⚠️ No active direct streams found on LiveATC for {icao}.",
        "pl": "⚠️ Brak aktywnych transmisji na żywo w LiveATC dla {icao}.",
    },
    "atc_playlist_caption": {
        "ru": (
            "🎧 <b>Аудио-плейлист радиопереговоров ATC: {icao} ({iata})</b>\n\n"
            "▶️ <b>Как слушать прямо сейчас:</b>\n"
            "1. Нажмите на прикреплённый файл <code>{filename}</code> прямо в Telegram.\n"
            "2. Откройте его через VLC, системный медиаплеер iOS/Android или QuickTime.\n"
            "3. Наслаждайтесь живым радиоэфиром диспетчеров и пилотов во время споттинга!"
        ),
        "en": (
            "🎧 <b>ATC Airband Audio Playlist: {icao} ({iata})</b>\n\n"
            "▶️ <b>How to listen:</b>\n"
            "1. Tap the attached <code>{filename}</code> file in Telegram.\n"
            "2. Open it in VLC, iOS/Android media player, or QuickTime.\n"
            "3. Enjoy live air traffic control audio during your spotting session!"
        ),
        "pl": (
            "🎧 <b>Playlista audio rozmów ATC: {icao} ({iata})</b>\n\n"
            "▶️ <b>Jak słuchać teraz:</b>\n"
            "1. Kliknij załączony plik <code>{filename}</code> bezpośrednio w Telegramie.\n"
            "2. Otwórz go w VLC, domyślnym odtwarzaczu iOS/Android lub QuickTime.\n"
            "3. Ciesz się nasłuchem wieży i pilotów na żywo podczas spottingu!"
        ),
    },

    # Facts lookup
    "facts_msg": {
        "ru": (
            "🔍 <b>Полезные ссылки и история по борту {reg}:</b>\n\n"
            "• <b>Флаг регистрации:</b> {country}\n\n"
            "• <a href='https://www.jetphotos.com/registration/{reg}'>JetPhotos (все фото борта и предыдущие ливреи)</a>\n"
            "• <a href='https://www.flightradar24.com/data/aircraft/{reg_lower}'>Flightradar24 (история и расписание полётов)</a>\n"
            "• <a href='https://www.planespotters.net/search?q={reg}'>Planespotters (возраст, история операторов и MSN)</a>\n"
            "• <a href='https://aviation-safety.net/wikibase/dblist.php?Registration={reg}'>Aviation Safety Network (история инцидентов)</a>"
        ),
        "en": (
            "🔍 <b>Useful links and history for tail {reg}:</b>\n\n"
            "• <b>Registration Country:</b> {country}\n\n"
            "• <a href='https://www.jetphotos.com/registration/{reg}'>JetPhotos (all aircraft photos & previous liveries)</a>\n"
            "• <a href='https://www.flightradar24.com/data/aircraft/{reg_lower}'>Flightradar24 (flight history & schedule)</a>\n"
            "• <a href='https://www.planespotters.net/search?q={reg}'>Planespotters (age, operator history & MSN)</a>\n"
            "• <a href='https://aviation-safety.net/wikibase/dblist.php?Registration={reg}'>Aviation Safety Network (incident history)</a>"
        ),
        "pl": (
            "🔍 <b>Przydatne linki i historia dla samolotu {reg}:</b>\n\n"
            "• <b>Kraj rejestracji:</b> {country}\n\n"
            "• <a href='https://www.jetphotos.com/registration/{reg}'>JetPhotos (wszystkie zdjęcia i poprzednie malowania)</a>\n"
            "• <a href='https://www.flightradar24.com/data/aircraft/{reg_lower}'>Flightradar24 (historia lotów i rozkład)</a>\n"
            "• <a href='https://www.planespotters.net/search?q={reg}'>Planespotters (wiek, historia linii lotniczych i MSN)</a>\n"
            "• <a href='https://aviation-safety.net/wikibase/dblist.php?Registration={reg}'>Aviation Safety Network (rejestr incydentów)</a>"
        ),
    }
}


def detect_user_lang(tg_user: dict, stored_lang: str = None) -> str:
    """
    Detects language preference:
    1. If user already chose a language in stored_lang -> use it.
    2. Else if Telegram language_code is pl -> 'pl'.
    3. Else if Telegram language_code is ru/be/uk/kk -> 'ru'.
    4. Otherwise fallback to 'en'.
    """
    if stored_lang and stored_lang in SUPPORTED_LANGUAGES:
        return stored_lang
    
    if not tg_user:
        return DEFAULT_LANGUAGE
    
    code = (tg_user.get("language_code") or "").lower().split("-")[0].strip()
    if code == "pl":
        return "pl"
    elif code in ["ru", "be", "uk", "kk"]:
        return "ru"
    elif code == "en":
        return "en"
    
    return "en" if code else DEFAULT_LANGUAGE


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Get localized string with fallback.
    """
    entry = MESSAGES.get(key)
    if not entry:
        return f"[{key}]"

    if lang == "multi" and "multi" in entry:
        return entry["multi"]

    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE

    text = entry.get(lang) or entry.get("en") or entry.get("ru") or f"[{key}]"
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def build_main_reply_keyboard(lang: str = "ru", mini_app_url: str = "") -> dict:
    """
    Builds localized persistent Reply Keyboard.
    """
    hub_url = mini_app_url or f"{HUB_BASE_URL}/player"
    return {
        "keyboard": [
            [{"text": t("btn_spotting_mode", lang)}, {"text": t("btn_stop_radar", lang)}],
            [{"text": t("btn_atc_radio", lang)}, {"text": t("btn_check_reg", lang)}],
            [{"text": t("btn_location", lang), "request_location": True}, {"text": t("btn_stats", lang)}],
            [{"text": t("btn_settings", lang)}, {"text": t("btn_help", lang)}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }
