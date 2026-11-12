import sys
import os
import re
from unittest.mock import MagicMock

# Mock boto3 before importing aws_lambda modules
sys.modules["boto3"] = MagicMock()
sys.path.insert(0, os.path.abspath("aws_lambda"))

import i18n
import lambda_webhook
from bot import SpotterBot

CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")

class MockTelegramAPI:
    def __init__(self):
        self.sent_messages = []
        self.sent_photos = []
        self.sent_documents = []
        self.answered_callbacks = []

    def send_message(self, chat_id, text, parse_mode="HTML", reply_markup=None, disable_preview=True, photo_preview=None):
        self.sent_messages.append({
            "chat_id": chat_id,
            "text": text,
            "reply_markup": reply_markup,
            "photo_preview": photo_preview
        })
        return {"ok": True, "result": {"message_id": 999}}

    def send_photo(self, chat_id, photo, caption, reply_markup=None):
        self.sent_photos.append({
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
            "reply_markup": reply_markup
        })
        return {"ok": True, "result": {"message_id": 999}}

    def send_document(self, chat_id, file_bytes, filename, caption=None, reply_markup=None):
        self.sent_documents.append({
            "chat_id": chat_id,
            "filename": filename,
            "caption": caption,
            "reply_markup": reply_markup
        })
        return {"ok": True, "result": {"message_id": 999}}

    def answer_callback_query(self, cb_id, text=None):
        self.answered_callbacks.append({"cb_id": cb_id, "text": text})
        return {"ok": True}


def assert_no_cyrillic(content, context=""):
    """
    Recursively inspect strings, dicts, lists and assert NO Cyrillic characters are present.
    """
    if isinstance(content, str):
        match = CYRILLIC_RE.search(content)
        assert not match, f"Found Cyrillic character '{match.group(0)}' in [{context}]:\n{content}"
    elif isinstance(content, dict):
        for k, v in content.items():
            assert_no_cyrillic(v, context=f"{context} -> {k}")
    elif isinstance(content, (list, tuple)):
        for idx, item in enumerate(content):
            assert_no_cyrillic(item, context=f"{context}[{idx}]")


def test_i18n_keys_zero_cyrillic():
    """Verify that all spotting & radar keys in i18n have valid EN and PL translations with 0 Cyrillic."""
    keys_to_check = [
        "spotting_menu_msg", "btn_stop_active_radar", "btn_buy_premium_inline",
        "plan_header", "plan_mode_dep_label", "plan_mode_arr_label", "plan_sub_schedule",
        "plan_filter_prefix", "plan_this_hour", "plan_no_flights_msg", "plan_badge_new",
        "plan_badge_in_db", "plan_badge_divert", "plan_fr24_hint", "plan_fetch_error",
        "btn_plan_all_flights", "btn_plan_departures", "btn_plan_arrivals",
        "btn_plan_reset_filter", "btn_plan_prev", "btn_plan_page", "btn_plan_next",
        "btn_spotterguide_spots", "btn_atc_radio_inline", "btn_radar_30", "btn_radar_240",
        "radar_stopped_msg", "radar_not_active_msg", "atc_menu_title", "atc_menu_body",
        "atc_btn_scanner", "radar_alert_emergency", "radar_alert_divert",
        "radar_alert_unspotted_arr", "radar_alert_unspotted_dep", "radar_alert_unspotted_gnd",
        "radar_alert_unspotted_air", "radar_not_in_collection", "radar_btn_fr24", "radar_btn_jp",
        "location_not_found", "radar_prem_limit_warning", "radar_activated_msg",
        "atc_card_title", "atc_not_found", "atc_official_freqs", "atc_freq_twr",
        "atc_freq_app", "atc_freq_gnd", "atc_freq_atis", "atc_stream_active",
        "atc_stream_channels", "atc_stream_hint", "atc_stream_unavailable",
        "atc_stream_unavail_note", "atc_airband_hint", "atc_btn_listen_tg",
        "atc_btn_download_m3u", "atc_btn_liveatc_web", "atc_btn_back_plan",
        "atc_btn_open_scanner_tg", "atc_btn_check_liveatc", "atc_btn_back_freqs",
        "atc_playlist_not_found", "atc_playlist_caption", "facts_msg"
    ]
    for k in keys_to_check:
        assert k in i18n.MESSAGES, f"Missing key '{k}' in i18n.MESSAGES"
        entry = i18n.MESSAGES[k]
        assert "pl" in entry, f"Missing Polish ('pl') translation for '{k}'"
        assert "en" in entry, f"Missing English ('en') translation for '{k}'"
        assert_no_cyrillic(entry["pl"], context=f"i18n.MESSAGES['{k}']['pl']")
        assert_no_cyrillic(entry["en"], context=f"i18n.MESSAGES['{k}']['en']")
    print("✓ Test 1: All spotting i18n translation keys have 0 Cyrillic in EN & PL passed")


def test_spotting_menu_zero_cyrillic():
    """Verify send_spotting_menu outputs 0 Cyrillic in text and inline keyboard for EN and PL."""
    mock_api = MockTelegramAPI()
    lambda_webhook.send_telegram = lambda token, chat_id, text, reply_markup=None: mock_api.send_message(chat_id, text, reply_markup=reply_markup)

    for lang in ["pl", "en"]:
        mock_api.sent_messages.clear()
        lambda_webhook.send_spotting_menu(12345, user_lang=lang)
        assert len(mock_api.sent_messages) == 1
        msg = mock_api.sent_messages[0]
        assert_no_cyrillic(msg["text"], context=f"send_spotting_menu text ({lang})")
        assert_no_cyrillic(msg["reply_markup"], context=f"send_spotting_menu keyboard ({lang})")

    print("✓ Test 2: send_spotting_menu has 0 Cyrillic in EN & PL passed")


def test_spotting_plan_zero_cyrillic():
    """Verify send_spotting_plan outputs 0 Cyrillic in flight cards, badges, and filters for EN and PL."""
    mock_api = MockTelegramAPI()
    lambda_webhook.send_telegram = lambda token, chat_id, text, reply_markup=None: mock_api.send_message(chat_id, text, reply_markup=reply_markup)

    # Mock get_airport_schedule
    mock_schedule = [
        {
            "flight_num": "LO3801",
            "reg": "SP-LVD",
            "mode": "departures",
            "time_str": "14:30 UTC",
            "model": "B38M",
            "airline": "LOT Polish Airlines",
            "orig": "WAW",
            "dest": "GDN",
            "is_diverted": False
        },
        {
            "flight_num": "FR1234",
            "reg": "SP-RZS",
            "mode": "arrivals",
            "time_str": "14:45 UTC",
            "model": "B738",
            "airline": "Ryanair",
            "orig": "STN",
            "dest": "WAW",
            "is_diverted": True
        }
    ]
    lambda_webhook.get_airport_schedule = lambda iata: mock_schedule

    mock_users_table = MagicMock()
    mock_aircraft_table = MagicMock()
    mock_aircraft_table.get_item.return_value = {"Item": {"photo_count": 3}}

    for lang in ["pl", "en"]:
        for mode in ["all", "departures", "arrivals"]:
            mock_api.sent_messages.clear()
            lambda_webhook.send_spotting_plan(
                chat_id=12345,
                telegram_id="test_user",
                iata="WAW",
                icao="EPWA",
                users_table=mock_users_table,
                aircraft_table=mock_aircraft_table,
                user={"language": lang},
                filter_mode=mode,
                page=1,
                selected_airline="all",
                user_lang=lang
            )
            assert len(mock_api.sent_messages) == 1
            msg = mock_api.sent_messages[0]
            assert_no_cyrillic(msg["text"], context=f"send_spotting_plan text ({lang}, mode={mode})")
            assert_no_cyrillic(msg["reply_markup"], context=f"send_spotting_plan keyboard ({lang}, mode={mode})")

    print("✓ Test 3: send_spotting_plan has 0 Cyrillic in EN & PL across all modes passed")


def test_atc_menu_and_card_zero_cyrillic():
    """Verify send_atc_menu, send_atc_card, and send_atc_playlist have 0 Cyrillic in EN and PL."""
    mock_api = MockTelegramAPI()
    lambda_webhook.send_telegram = lambda token, chat_id, text, reply_markup=None: mock_api.send_message(chat_id, text, reply_markup=reply_markup)
    lambda_webhook.send_telegram_document = lambda token, chat_id, fb, fn, caption=None, reply_markup=None: mock_api.send_document(chat_id, fb, fn, caption=caption, reply_markup=reply_markup)

    for lang in ["pl", "en"]:
        # 1. ATC Menu
        mock_api.sent_messages.clear()
        lambda_webhook.send_atc_menu(12345, user={"language": lang}, user_lang=lang)
        assert len(mock_api.sent_messages) == 1
        assert_no_cyrillic(mock_api.sent_messages[0]["text"], context=f"send_atc_menu text ({lang})")
        assert_no_cyrillic(mock_api.sent_messages[0]["reply_markup"], context=f"send_atc_menu keyboard ({lang})")

        # 2. ATC Card
        mock_api.sent_messages.clear()
        lambda_webhook.send_atc_card(12345, "WAW", "EPWA", user_lang=lang)
        assert len(mock_api.sent_messages) == 1
        assert_no_cyrillic(mock_api.sent_messages[0]["text"], context=f"send_atc_card text ({lang})")
        assert_no_cyrillic(mock_api.sent_messages[0]["reply_markup"], context=f"send_atc_card keyboard ({lang})")

        # 3. ATC Playlist
        mock_api.sent_documents.clear()
        lambda_webhook.send_atc_playlist(12345, "WAW", "EPWA", user_lang=lang)
        assert len(mock_api.sent_documents) == 1
        assert_no_cyrillic(mock_api.sent_documents[0]["caption"], context=f"send_atc_playlist caption ({lang})")
        assert_no_cyrillic(mock_api.sent_documents[0]["reply_markup"], context=f"send_atc_playlist keyboard ({lang})")

    print("✓ Test 4: ATC Menu, Card, and Playlist have 0 Cyrillic in EN & PL passed")


def test_radar_actions_zero_cyrillic():
    """Verify stop_radar and radar activation callback produce 0 Cyrillic in EN and PL."""
    mock_api = MockTelegramAPI()
    lambda_webhook.send_telegram = lambda token, chat_id, text, reply_markup=None: mock_api.send_message(chat_id, text, reply_markup=reply_markup)
    mock_users_table = MagicMock()

    for lang in ["pl", "en"]:
        # 1. Stop radar (active)
        mock_api.sent_messages.clear()
        mock_users_table.get_item.return_value = {"Item": {"monitoring_until": 9999999999, "language": lang}}
        lambda_webhook.stop_radar(12345, "user1", mock_users_table, user_lang=lang)
        assert len(mock_api.sent_messages) == 1
        assert_no_cyrillic(mock_api.sent_messages[0]["text"], context=f"stop_radar active text ({lang})")

        # 2. Stop radar (inactive)
        mock_api.sent_messages.clear()
        mock_users_table.get_item.return_value = {"Item": {"monitoring_until": 0, "language": lang}}
        lambda_webhook.stop_radar(12345, "user1", mock_users_table, user_lang=lang)
        assert len(mock_api.sent_messages) == 1
        assert_no_cyrillic(mock_api.sent_messages[0]["text"], context=f"stop_radar inactive text ({lang})")

    print("✓ Test 5: stop_radar (active & inactive) has 0 Cyrillic in EN & PL passed")


def test_direct_airport_code_message_zero_cyrillic():
    """Verify typing 'WAW' or 'GDN' directly from a PL or EN user renders a spotting plan with 0 Cyrillic."""
    mock_api = MockTelegramAPI()
    lambda_webhook.send_telegram = lambda token, chat_id, text, reply_markup=None: mock_api.send_message(chat_id, text, reply_markup=reply_markup)
    
    # Mock DynamoDB
    mock_users_table = MagicMock()
    mock_aircraft_table = MagicMock()
    mock_aircraft_table.get_item.return_value = {"Item": None}
    lambda_webhook.get_dynamo_tables = lambda: (mock_users_table, mock_aircraft_table)

    # Mock Schedule
    lambda_webhook.get_airport_schedule = lambda iata: [
        {"flight_num": "LO1", "reg": "SP-LRA", "mode": "arrivals", "time_str": "12:00 UTC", "model": "B788", "airline": "LOT", "orig": "JFK", "dest": "WAW"}
    ]

    for lang, code in [("pl", "WAW"), ("en", "GDN"), ("pl", "EPGD")]:
        mock_users_table.get_item.return_value = {"Item": {"telegram_id": "999", "language": lang, "lang": lang}}
        mock_api.sent_messages.clear()
        
        event = {
            "body": {
                "message": {
                    "message_id": 100,
                    "chat": {"id": 999},
                    "from": {"id": 999, "language_code": lang},
                    "text": code
                }
            }
        }
        lambda_webhook.handler(event, None)
        assert len(mock_api.sent_messages) >= 1
        for m in mock_api.sent_messages:
            assert_no_cyrillic(m["text"], context=f"direct message '{code}' text ({lang})")
            if m.get("reply_markup"):
                assert_no_cyrillic(m["reply_markup"], context=f"direct message '{code}' reply_markup ({lang})")

    print("✓ Test 6: Direct airport code messages (WAW, GDN, EPGD) produce 0 Cyrillic for PL & EN passed")


def test_callback_queries_zero_cyrillic():
    """Verify callback queries (pl:, atc:, radar:, stop_radar, facts:) return 0 Cyrillic for PL and EN."""
    mock_api = MockTelegramAPI()
    lambda_webhook.send_telegram = lambda token, chat_id, text, reply_markup=None: mock_api.send_message(chat_id, text, reply_markup=reply_markup)
    mock_users_table = MagicMock()
    mock_aircraft_table = MagicMock()
    mock_aircraft_table.get_item.return_value = {"Item": None}
    lambda_webhook.get_dynamo_tables = lambda: (mock_users_table, mock_aircraft_table)

    callbacks_to_test = [
        "pl:WAW:EPWA:all:1:all",
        "pl:GDN:EPGD:arrivals:1:all",
        "atc:WAW:EPWA",
        "radar:30:EPWA",
        "stop_radar",
        "facts:SP-LVD"
    ]

    for lang in ["pl", "en"]:
        mock_users_table.get_item.return_value = {"Item": {"telegram_id": "999", "language": lang, "lang": lang, "is_premium": False}}
        for cb_data in callbacks_to_test:
            mock_api.sent_messages.clear()
            event = {
                "body": {
                    "callback_query": {
                        "id": "cb123",
                        "from": {"id": 999, "language_code": lang},
                        "message": {"chat": {"id": 999}, "message_id": 200},
                        "data": cb_data
                    }
                }
            }
            lambda_webhook.handler(event, None)
            assert len(mock_api.sent_messages) >= 1, f"No message sent for callback {cb_data} ({lang})"
            for m in mock_api.sent_messages:
                assert_no_cyrillic(m["text"], context=f"callback '{cb_data}' text ({lang})")
                if m.get("reply_markup"):
                    assert_no_cyrillic(m["reply_markup"], context=f"callback '{cb_data}' reply_markup ({lang})")

    print("✓ Test 7: All callback queries (pl, atc, radar, stop_radar, facts) produce 0 Cyrillic for PL & EN passed")


def test_legacy_bot_onboarding():
    """Preserve SpotterBot onboarding tests."""
    bot = SpotterBot("dummy_token")
    bot.api = MockTelegramAPI()

    bot.handle_message({"chat": {"id": 100}, "from": {"language_code": "ru"}, "text": "/start"})
    assert "Выберите язык / Select language / Wybierz język" in bot.api.sent_messages[-1]["text"]

    bot.user_prefs[101] = {"lang": "pl", "lang_chosen": True}
    bot.handle_message({"chat": {"id": 101}, "from": {"language_code": "pl"}, "text": "A6-EOY"})
    assert "Cześć, spotterze!" in bot.api.sent_messages[-1]["text"]

    bot.user_prefs[102] = {"lang": "en", "lang_chosen": True}
    bot.handle_message({"chat": {"id": 102}, "from": {"language_code": "en"}, "text": "A6-EOY"})
    assert "Hello, spotter!" in bot.api.sent_messages[-1]["text"]

    print("✓ Test 8: Legacy SpotterBot onboarding & tail search verified")


def run_all_tests():
    print("=" * 70)
    print("RUNNING STRICT ZERO-CYRILLIC SPOTTER VERIFICATION SUITE")
    print("=" * 70)
    test_i18n_keys_zero_cyrillic()
    test_spotting_menu_zero_cyrillic()
    test_spotting_plan_zero_cyrillic()
    test_atc_menu_and_card_zero_cyrillic()
    test_radar_actions_zero_cyrillic()
    test_direct_airport_code_message_zero_cyrillic()
    test_callback_queries_zero_cyrillic()
    test_legacy_bot_onboarding()
    print("=" * 70)
    print("ALL TESTS PASSED! ZERO CYRILLIC IN EN & PL SPOTTING MODE VERIFIED! 🚀")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
