import math

# Major airports with ICAO, IATA, Name, Country, Lat, Lon, Radio Frequencies and LiveATC streaming config
AIRPORTS = [
    {
        "icao": "EPGD",
        "iata": "GDN",
        "name": "Gdańsk Lech Wałęsa",
        "country": "Польша 🇵🇱",
        "lat": 54.3776,
        "lon": 18.4662,
        "frequencies": {
            "twr": "118.105 MHz (Gdańsk Tower)",
            "app": "127.280 MHz (Gdańsk Approach / Radar)",
            "gnd": "131.330 MHz (Gdańsk Ground)",
            "atis": "129.630 MHz (Gdańsk ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В Гданьске нет волонтёра с приёмником LiveATC. Для прослушивания у полосы используйте радиосканер Airband на 118.105 MHz.",
            "web_url": "https://www.liveatc.net/search/?icao=EPGD",
            "streams": []
        }
    },
    {
        "icao": "EPWA",
        "iata": "WAW",
        "name": "Warsaw Chopin",
        "country": "Польша 🇵🇱",
        "lat": 52.1672,
        "lon": 20.9679,
        "frequencies": {
            "twr": "118.305 MHz (Warszawa Tower)",
            "app": "128.805 MHz (Warszawa Radar / Approach)",
            "gnd": "121.605 MHz (Warszawa Ground)",
            "atis": "120.455 MHz (Warszawa ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=EPWA",
            "streams": [
                {
                    "title": "EPWA Warsaw Tower",
                    "freq": "118.305 MHz",
                    "mount": "epwa2",
                    "url": "https://s1-bos.liveatc.net/epwa2"
                },
                {
                    "title": "EPWA Warsaw Approach",
                    "freq": "128.805 MHz",
                    "mount": "epwa_app",
                    "url": "https://s1-fmt2.liveatc.net/epwa_app"
                }
            ]
        }
    },
    {
        "icao": "EPMO",
        "iata": "WMI",
        "name": "Warsaw Modlin",
        "country": "Польша 🇵🇱",
        "lat": 52.4511,
        "lon": 20.6517,
        "frequencies": {
            "twr": "125.005 MHz (Modlin Tower)",
            "gnd": "121.980 MHz (Modlin Ground)",
            "atis": "134.580 MHz (Modlin ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В Модлине нет постоянного стрима на LiveATC. Рабочая частота вышки: 125.005 MHz.",
            "web_url": "https://www.liveatc.net/search/?icao=EPMO",
            "streams": []
        }
    },
    {
        "icao": "EPKK",
        "iata": "KRK",
        "name": "Kraków John Paul II",
        "country": "Польша 🇵🇱",
        "lat": 50.0777,
        "lon": 19.7848,
        "frequencies": {
            "twr": "123.255 MHz (Kraków Tower)",
            "app": "121.080 MHz (Kraków Approach)",
            "atis": "126.130 MHz (Kraków ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В Кракове в данный момент нет активного онлайн-стрима. Рабочая частота вышки: 123.255 MHz.",
            "web_url": "https://www.liveatc.net/search/?icao=EPKK",
            "streams": []
        }
    },
    {
        "icao": "EPKT",
        "iata": "KTW",
        "name": "Katowice Airport",
        "country": "Польша 🇵🇱",
        "lat": 50.4743,
        "lon": 19.0800,
        "frequencies": {
            "twr": "129.255 MHz (Katowice Tower)",
            "app": "124.280 MHz (Katowice Approach)",
            "atis": "120.230 MHz (Katowice ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=EPKT",
            "streams": [
                {
                    "title": "EPKT Katowice Tower",
                    "freq": "129.255 MHz",
                    "mount": "epkt",
                    "url": "https://s1-bos.liveatc.net/epkt"
                }
            ]
        }
    },
    {
        "icao": "EPWR",
        "iata": "WRO",
        "name": "Wrocław Copernicus",
        "country": "Польша 🇵🇱",
        "lat": 51.1028,
        "lon": 16.8858,
        "frequencies": {
            "twr": "120.680 MHz (Wrocław Tower)",
            "app": "127.230 MHz (Wrocław Approach)",
            "atis": "124.330 MHz (Wrocław ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В данный момент стрим оффлайн. Вышка Wrocław Tower: 120.680 MHz.",
            "web_url": "https://www.liveatc.net/search/?icao=EPWR",
            "streams": []
        }
    },
    {
        "icao": "EPPO",
        "iata": "POZ",
        "name": "Poznań–Ławica",
        "country": "Польша 🇵🇱",
        "lat": 52.4211,
        "lon": 16.8261,
        "frequencies": {
            "twr": "119.980 MHz (Poznań Tower)",
            "app": "134.630 MHz (Poznań Approach)",
            "atis": "124.705 MHz (Poznań ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=EPPO",
            "streams": [
                {
                    "title": "EPPO Poznań Tower",
                    "freq": "119.980 MHz",
                    "mount": "eppo_twr",
                    "url": "http://d.liveatc.net/eppo_twr"
                }
            ]
        }
    },
    {
        "icao": "EVRA",
        "iata": "RIX",
        "name": "Riga International",
        "country": "Латвия 🇱🇻",
        "lat": 56.9236,
        "lon": 23.9711,
        "frequencies": {
            "twr": "118.105 MHz (Riga Tower)",
            "app": "129.930 MHz (Riga Approach)",
            "atis": "130.130 MHz (Riga ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=EVRA",
            "streams": [
                {
                    "title": "EVRA Riga Tower/Approach",
                    "freq": "118.105 MHz",
                    "mount": "evra2",
                    "url": "http://d.liveatc.net/evra2"
                }
            ]
        }
    },
    {
        "icao": "EYVI",
        "iata": "VNO",
        "name": "Vilnius International",
        "country": "Литва 🇱🇹",
        "lat": 54.6341,
        "lon": 25.2858,
        "frequencies": {
            "twr": "118.205 MHz (Vilnius Tower)",
            "app": "120.405 MHz (Vilnius Approach)",
            "atis": "125.805 MHz (Vilnius ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=EYVI",
            "streams": [
                {
                    "title": "EYVI Vilnius Tower",
                    "freq": "118.205 MHz",
                    "mount": "eyvi_twr",
                    "url": "http://d.liveatc.net/eyvi_twr"
                }
            ]
        }
    },
    {
        "icao": "EETN",
        "iata": "TLL",
        "name": "Tallinn Lennart Meri",
        "country": "Эстония 🇪🇪",
        "lat": 59.4133,
        "lon": 24.8328,
        "frequencies": {
            "twr": "120.605 MHz (Tallinn Tower)",
            "app": "127.905 MHz (Tallinn Approach)",
            "atis": "124.880 MHz (Tallinn ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=EETN",
            "streams": [
                {
                    "title": "EETN Tallinn Tower",
                    "freq": "120.605 MHz",
                    "mount": "eetn_twr",
                    "url": "http://d.liveatc.net/eetn_twr"
                }
            ]
        }
    },
    {
        "icao": "EHAM",
        "iata": "AMS",
        "name": "Amsterdam Schiphol",
        "country": "Нидерланды 🇳🇱",
        "lat": 52.3105,
        "lon": 4.7683,
        "frequencies": {
            "twr": "119.225 MHz / 118.275 MHz (Tower)",
            "app": "121.205 MHz / 131.155 MHz (Approach)",
            "atis": "122.205 MHz (ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=EHAM",
            "streams": [
                {
                    "title": "EHAM Schiphol Tower",
                    "freq": "119.225 MHz",
                    "mount": "eham_twr",
                    "url": "http://d.liveatc.net/eham_twr"
                },
                {
                    "title": "EHAM Schiphol Approach",
                    "freq": "121.205 MHz",
                    "mount": "eham_app",
                    "url": "http://d.liveatc.net/eham_app"
                }
            ]
        }
    },
    {
        "icao": "EDDB",
        "iata": "BER",
        "name": "Berlin Brandenburg",
        "country": "Германия 🇩🇪",
        "lat": 52.3667,
        "lon": 13.5033,
        "frequencies": {
            "twr": "120.030 MHz / 118.805 MHz (Tower)",
            "app": "121.130 MHz (Approach)",
            "atis": "123.780 MHz (ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В Германии публичный интернет-стриминг радиопереговоров запрещен законом (§ 89 TKG). Используйте приёмник у полосы.",
            "web_url": "https://www.liveatc.net",
            "streams": []
        }
    },
    {
        "icao": "EDDF",
        "iata": "FRA",
        "name": "Frankfurt Airport",
        "country": "Германия 🇩🇪",
        "lat": 50.0379,
        "lon": 8.5622,
        "frequencies": {
            "twr": "119.900 MHz / 124.850 MHz (Tower)",
            "app": "120.150 MHz (Approach)",
            "atis": "118.025 MHz (ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В Германии интернет-стриминг ATC запрещен законом (§ 89 TKG).",
            "web_url": "https://www.liveatc.net",
            "streams": []
        }
    },
    {
        "icao": "EDDM",
        "iata": "MUC",
        "name": "Munich Airport",
        "country": "Германия 🇩🇪",
        "lat": 48.3537,
        "lon": 11.7860,
        "frequencies": {
            "twr": "120.500 MHz / 118.700 MHz (Tower)",
            "app": "123.900 MHz (Approach)",
            "atis": "123.125 MHz (ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В Германии интернет-стриминг ATC запрещен законом (§ 89 TKG).",
            "web_url": "https://www.liveatc.net",
            "streams": []
        }
    },
    {
        "icao": "LOWW",
        "iata": "VIE",
        "name": "Vienna International",
        "country": "Австрия 🇦🇹",
        "lat": 48.1103,
        "lon": 16.5697,
        "frequencies": {
            "twr": "119.400 MHz (Wien Tower)",
            "app": "118.780 MHz (Wien Director)",
            "atis": "122.955 MHz (Wien ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В Австрии вещание ATC запрещено законом о связи (TKG).",
            "web_url": "https://www.liveatc.net",
            "streams": []
        }
    },
    {
        "icao": "LKPR",
        "iata": "PRG",
        "name": "Václav Havel Airport Prague",
        "country": "Чехия 🇨🇿",
        "lat": 50.1008,
        "lon": 14.2600,
        "frequencies": {
            "twr": "118.105 MHz / 134.560 MHz (Prague Tower)",
            "app": "127.130 MHz (Prague Approach)",
            "atis": "122.155 MHz (Prague ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=LKPR",
            "streams": [
                {
                    "title": "LKPR Prague Tower/Radar",
                    "freq": "118.105 MHz",
                    "mount": "lkpr_twr",
                    "url": "http://d.liveatc.net/lkpr_twr"
                }
            ]
        }
    },
    {
        "icao": "EGLL",
        "iata": "LHR",
        "name": "London Heathrow",
        "country": "Великобритания 🇬🇧",
        "lat": 51.4700,
        "lon": -0.4543,
        "frequencies": {
            "twr": "118.500 MHz / 118.700 MHz (Heathrow Tower)",
            "app": "119.730 MHz / 120.400 MHz (Heathrow Director)",
            "atis": "128.080 MHz (Heathrow ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "В Великобритании интернет-вещание ATC запрещено Wireless Telegraphy Act 2006.",
            "web_url": "https://www.liveatc.net",
            "streams": []
        }
    },
    {
        "icao": "LFPG",
        "iata": "CDG",
        "name": "Paris Charles de Gaulle",
        "country": "Франция 🇫🇷",
        "lat": 49.0097,
        "lon": 2.5479,
        "frequencies": {
            "twr": "118.150 MHz / 120.900 MHz (De Gaulle Tower)",
            "app": "121.150 MHz (De Gaulle Approach)",
            "atis": "127.130 MHz (ATIS)"
        },
        "liveatc": {
            "available": False,
            "note": "Во Франции интернет-стриминг радиопереговоров запрещен законом.",
            "web_url": "https://www.liveatc.net",
            "streams": []
        }
    },
    {
        "icao": "OMDB",
        "iata": "DXB",
        "name": "Dubai International",
        "country": "ОАЭ 🇦🇪",
        "lat": 25.2532,
        "lon": 55.3657,
        "frequencies": {
            "twr": "118.750 MHz / 118.400 MHz (Dubai Tower)",
            "app": "124.900 MHz (Dubai Approach)",
            "atis": "131.700 MHz (Dubai ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=OMDB",
            "streams": [
                {
                    "title": "OMDB Dubai Tower",
                    "freq": "118.750 MHz",
                    "mount": "omdb_twr",
                    "url": "http://d.liveatc.net/omdb_twr"
                }
            ]
        }
    },
    {
        "icao": "OTHH",
        "iata": "DOH",
        "name": "Hamad International",
        "country": "Катар 🇶🇦",
        "lat": 25.2731,
        "lon": 51.6081,
        "frequencies": {
            "twr": "118.050 MHz (Doha Tower)",
            "app": "121.100 MHz (Doha Approach)",
            "atis": "126.850 MHz (Doha ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=OTHH",
            "streams": [
                {
                    "title": "OTHH Hamad Tower",
                    "freq": "118.050 MHz",
                    "mount": "othh_twr",
                    "url": "http://d.liveatc.net/othh_twr"
                }
            ]
        }
    },
    {
        "icao": "LTFM",
        "iata": "IST",
        "name": "Istanbul Airport",
        "country": "Турция 🇹🇷",
        "lat": 41.2753,
        "lon": 28.7519,
        "frequencies": {
            "twr": "118.075 MHz / 118.175 MHz (Istanbul Tower)",
            "app": "121.100 MHz (Istanbul Approach)",
            "atis": "128.200 MHz (Istanbul ATIS)"
        },
        "liveatc": {
            "available": True,
            "web_url": "https://www.liveatc.net/search/?icao=LTFM",
            "streams": [
                {
                    "title": "LTFM Istanbul Tower",
                    "freq": "118.075 MHz",
                    "mount": "ltfm_twr",
                    "url": "http://d.liveatc.net/ltfm_twr"
                }
            ]
        }
    }
,
    {
        "icao": "EPRZ",
        "iata": "RZE",
        "name": "Rzeszów-Jasionka",
        "country": "Польша 🇵🇱",
        "lat": 50.1100,
        "lon": 22.0190,
        "frequencies": {"twr": "129.530 MHz", "atis": "124.955 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EPRZ", "streams": []}
    },
    {
        "icao": "EDFH",
        "iata": "HHN",
        "name": "Frankfurt-Hahn",
        "country": "Германия 🇩🇪",
        "lat": 49.9487,
        "lon": 7.2639,
        "frequencies": {"twr": "119.650 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EDFH", "streams": []}
    },
    {
        "icao": "EDDH",
        "iata": "HAM",
        "name": "Hamburg Airport",
        "country": "Германия 🇩🇪",
        "lat": 53.6304,
        "lon": 9.9882,
        "frequencies": {"twr": "126.850 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EDDH", "streams": []}
    },
    {
        "icao": "EDDL",
        "iata": "DUS",
        "name": "Düsseldorf Airport",
        "country": "Германия 🇩🇪",
        "lat": 51.2895,
        "lon": 6.7668,
        "frequencies": {"twr": "118.300 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EDDL", "streams": []}
    },
    {
        "icao": "EGKK",
        "iata": "LGW",
        "name": "London Gatwick",
        "country": "Великобритания 🇬🇧",
        "lat": 51.1537,
        "lon": -0.1821,
        "frequencies": {"twr": "124.225 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EGKK", "streams": []}
    },
    {
        "icao": "EGSS",
        "iata": "STN",
        "name": "London Stansted",
        "country": "Великобритания 🇬🇧",
        "lat": 51.8860,
        "lon": 0.2389,
        "frequencies": {"twr": "123.800 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EGSS", "streams": []}
    },
    {
        "icao": "EGGW",
        "iata": "LTN",
        "name": "London Luton",
        "country": "Великобритания 🇬🇧",
        "lat": 51.8747,
        "lon": -0.3683,
        "frequencies": {"twr": "132.550 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EGGW", "streams": []}
    },
    {
        "icao": "EGCC",
        "iata": "MAN",
        "name": "Manchester Airport",
        "country": "Великобритания 🇬🇧",
        "lat": 53.3537,
        "lon": -2.2750,
        "frequencies": {"twr": "118.625 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EGCC", "streams": []}
    },
    {
        "icao": "EGPH",
        "iata": "EDI",
        "name": "Edinburgh Airport",
        "country": "Великобритания 🇬🇧",
        "lat": 55.9500,
        "lon": -3.3725,
        "frequencies": {"twr": "118.700 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EGPH", "streams": []}
    },
    {
        "icao": "LFPO",
        "iata": "ORY",
        "name": "Paris Orly",
        "country": "Франция 🇫🇷",
        "lat": 48.7262,
        "lon": 2.3652,
        "frequencies": {"twr": "118.700 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LFPO", "streams": []}
    },
    {
        "icao": "LFMN",
        "iata": "NCE",
        "name": "Nice Côte d'Azur",
        "country": "Франция 🇫🇷",
        "lat": 43.6584,
        "lon": 7.2159,
        "frequencies": {"twr": "118.700 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LFMN", "streams": []}
    },
    {
        "icao": "LEMD",
        "iata": "MAD",
        "name": "Madrid-Barajas",
        "country": "Испания 🇪🇸",
        "lat": 40.4839,
        "lon": -3.5680,
        "frequencies": {"twr": "118.150 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LEMD", "streams": []}
    },
    {
        "icao": "LEBL",
        "iata": "BCN",
        "name": "Barcelona El Prat",
        "country": "Испания 🇪🇸",
        "lat": 41.2974,
        "lon": 2.0833,
        "frequencies": {"twr": "118.100 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LEBL", "streams": []}
    },
    {
        "icao": "LEPA",
        "iata": "PMI",
        "name": "Palma de Mallorca",
        "country": "Испания 🇪🇸",
        "lat": 39.5517,
        "lon": 2.7388,
        "frequencies": {"twr": "118.300 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LEPA", "streams": []}
    },
    {
        "icao": "LIRF",
        "iata": "FCO",
        "name": "Rome Fiumicino",
        "country": "Италия 🇮🇹",
        "lat": 41.8003,
        "lon": 12.2389,
        "frequencies": {"twr": "118.700 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LIRF", "streams": []}
    },
    {
        "icao": "LIMC",
        "iata": "MXP",
        "name": "Milan Malpensa",
        "country": "Италия 🇮🇹",
        "lat": 45.6301,
        "lon": 8.7255,
        "frequencies": {"twr": "119.000 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LIMC", "streams": []}
    },
    {
        "icao": "LIME",
        "iata": "BGY",
        "name": "Milan Bergamo",
        "country": "Италия 🇮🇹",
        "lat": 45.6739,
        "lon": 9.7042,
        "frequencies": {"twr": "120.500 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LIME", "streams": []}
    },
    {
        "icao": "EHEH",
        "iata": "EIN",
        "name": "Eindhoven Airport",
        "country": "Нидерланды 🇳🇱",
        "lat": 51.4501,
        "lon": 5.3745,
        "frequencies": {"twr": "131.000 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EHEH", "streams": []}
    },
    {
        "icao": "LSZH",
        "iata": "ZRH",
        "name": "Zurich Airport",
        "country": "Швейцария 🇨🇭",
        "lat": 47.4582,
        "lon": 8.5555,
        "frequencies": {"twr": "118.100 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LSZH", "streams": []}
    },
    {
        "icao": "LSGG",
        "iata": "GVA",
        "name": "Geneva Airport",
        "country": "Швейцария 🇨🇭",
        "lat": 46.2370,
        "lon": 6.1092,
        "frequencies": {"twr": "118.700 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LSGG", "streams": []}
    },
    {
        "icao": "ESSA",
        "iata": "ARN",
        "name": "Stockholm Arlanda",
        "country": "Швеция 🇸🇪",
        "lat": 59.6498,
        "lon": 17.9238,
        "frequencies": {"twr": "118.500 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=ESSA", "streams": []}
    },
    {
        "icao": "EKCH",
        "iata": "CPH",
        "name": "Copenhagen Kastrup",
        "country": "Дания 🇩🇰",
        "lat": 55.6180,
        "lon": 12.6508,
        "frequencies": {"twr": "118.100 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EKCH", "streams": []}
    },
    {
        "icao": "ENGM",
        "iata": "OSL",
        "name": "Oslo Gardermoen",
        "country": "Норвегия 🇳🇴",
        "lat": 60.1976,
        "lon": 11.1004,
        "frequencies": {"twr": "118.300 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=ENGM", "streams": []}
    },
    {
        "icao": "EFHK",
        "iata": "HEL",
        "name": "Helsinki-Vantaa",
        "country": "Финляндия 🇫🇮",
        "lat": 60.3172,
        "lon": 24.9633,
        "frequencies": {"twr": "118.600 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=EFHK", "streams": []}
    },
    {
        "icao": "LTFJ",
        "iata": "SAW",
        "name": "Istanbul Sabiha Gökçen",
        "country": "Турция 🇹🇷",
        "lat": 40.8986,
        "lon": 29.3092,
        "frequencies": {"twr": "118.800 MHz"},
        "liveatc": {"available": False, "web_url": "https://www.liveatc.net/search/?icao=LTFJ", "streams": []}
    }
]
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_nearest_airport(lat: float, lon: float):
    best_ap = None
    min_dist = float("inf")
    for ap in AIRPORTS:
        dist = haversine(lat, lon, ap["lat"], ap["lon"])
        if dist < min_dist:
            min_dist = dist
            best_ap = ap
    return best_ap, min_dist

def get_airport_by_code(code: str):
    if not code:
        return None
    c = code.upper().strip()
    for ap in AIRPORTS:
        if ap.get("iata") == c or ap.get("icao") == c:
            return ap
    return get_world_airport(c)

def generate_atc_m3u(airport: dict) -> str:
    liveatc = airport.get("liveatc", {})
    streams = liveatc.get("streams", [])
    if not streams:
        return ""
    lines = ["#EXTM3U"]
    for s in streams:
        lines.append(f"#EXTINF:-1,{s.get('title')} ({s.get('freq')})")
        lines.append(s.get("url"))
    return "\n".join(lines) + "\n"

COUNTRY_TRANSLATIONS = {
    "Польша 🇵🇱": {"ru": "Польша 🇵🇱", "en": "Poland 🇵🇱", "pl": "Polska 🇵🇱"},
    "Германия 🇩🇪": {"ru": "Германия 🇩🇪", "en": "Germany 🇩🇪", "pl": "Niemcy 🇩🇪"},
    "Великобритания 🇬🇧": {"ru": "Великобритания 🇬🇧", "en": "United Kingdom 🇬🇧", "pl": "Wielka Brytania 🇬🇧"},
    "Франция 🇫🇷": {"ru": "Франция 🇫🇷", "en": "France 🇫🇷", "pl": "Francja 🇫🇷"},
    "Нидерланды 🇳🇱": {"ru": "Нидерланды 🇳🇱", "en": "Netherlands 🇳🇱", "pl": "Holandia 🇳🇱"},
    "Австрия 🇦🇹": {"ru": "Австрия 🇦🇹", "en": "Austria 🇦🇹", "pl": "Austria 🇦🇹"},
    "Чехия 🇨🇿": {"ru": "Чехия 🇨🇿", "en": "Czechia 🇨🇿", "pl": "Czechy 🇨🇿"},
    "Латвия 🇱🇻": {"ru": "Латвия 🇱🇻", "en": "Latvia 🇱🇻", "pl": "Łotwa 🇱🇻"},
    "Литва 🇱🇹": {"ru": "Литва 🇱🇹", "en": "Lithuania 🇱🇹", "pl": "Litwa 🇱🇹"},
    "Эстония 🇪🇪": {"ru": "Эстония 🇪🇪", "en": "Estonia 🇪🇪", "pl": "Estonia 🇪🇪"},
    "Турция 🇹🇷": {"ru": "Турция 🇹🇷", "en": "Turkey 🇹🇷", "pl": "Turcja 🇹🇷"},
    "ОАЭ 🇦🇪": {"ru": "ОАЭ 🇦🇪", "en": "UAE 🇦🇪", "pl": "ZEA 🇦🇪"},
    "Катар 🇶🇦": {"ru": "Катар 🇶🇦", "en": "Qatar 🇶🇦", "pl": "Katar 🇶🇦"},
}

def get_airport_country(country_raw: str, user_lang: str = "ru") -> str:
    trans = COUNTRY_TRANSLATIONS.get(country_raw)
    if trans:
        return trans.get(user_lang) or trans.get("en") or country_raw
    return country_raw



# Structured Hierarchy for Airport Selection: Country -> City -> Airport
AIRPORT_HIERARCHY = [
    {
        "code": "PL",
        "flag": "🇵🇱",
        "names": {"ru": "Польша", "en": "Poland", "pl": "Polska"},
        "cities": [
            {
                "slug": "waw",
                "names": {"ru": "Варшава", "en": "Warsaw", "pl": "Warszawa"},
                "airports": [
                    {"iata": "WAW", "icao": "EPWA", "name": "Warsaw Chopin"},
                    {"iata": "WMI", "icao": "EPMO", "name": "Warsaw Modlin"}
                ]
            },
            {
                "slug": "gdn",
                "names": {"ru": "Гданьск", "en": "Gdansk", "pl": "Gdańsk"},
                "airports": [{"iata": "GDN", "icao": "EPGD", "name": "Gdańsk Lech Wałęsa"}]
            },
            {
                "slug": "krk",
                "names": {"ru": "Краков", "en": "Krakow", "pl": "Kraków"},
                "airports": [{"iata": "KRK", "icao": "EPKK", "name": "Kraków John Paul II"}]
            },
            {
                "slug": "ktw",
                "names": {"ru": "Катовице", "en": "Katowice", "pl": "Katowice"},
                "airports": [{"iata": "KTW", "icao": "EPKT", "name": "Katowice Airport"}]
            },
            {
                "slug": "wro",
                "names": {"ru": "Вроцлав", "en": "Wroclaw", "pl": "Wrocław"},
                "airports": [{"iata": "WRO", "icao": "EPWR", "name": "Wrocław Copernicus"}]
            },
            {
                "slug": "poz",
                "names": {"ru": "Познань", "en": "Poznan", "pl": "Poznań"},
                "airports": [{"iata": "POZ", "icao": "EPPO", "name": "Poznań-Ławica"}]
            },
            {
                "slug": "rze",
                "names": {"ru": "Жешув", "en": "Rzeszow", "pl": "Rzeszów-Jasionka"},
                "airports": [{"iata": "RZE", "icao": "EPRZ", "name": "Rzeszów-Jasionka"}]
            }
        ]
    },
    {
        "code": "DE",
        "flag": "🇩🇪",
        "names": {"ru": "Германия", "en": "Germany", "pl": "Niemcy"},
        "cities": [
            {
                "slug": "ber",
                "names": {"ru": "Берлин", "en": "Berlin", "pl": "Berlin"},
                "airports": [{"iata": "BER", "icao": "EDDB", "name": "Berlin Brandenburg"}]
            },
            {
                "slug": "fra",
                "names": {"ru": "Франкфурт", "en": "Frankfurt", "pl": "Frankfurt"},
                "airports": [
                    {"iata": "FRA", "icao": "EDDF", "name": "Frankfurt Main"},
                    {"iata": "HHN", "icao": "EDFH", "name": "Frankfurt-Hahn"}
                ]
            },
            {
                "slug": "muc",
                "names": {"ru": "Мюнхен", "en": "Munich", "pl": "Monachium"},
                "airports": [{"iata": "MUC", "icao": "EDDM", "name": "Munich Airport"}]
            },
            {
                "slug": "ham",
                "names": {"ru": "Гамбург", "en": "Hamburg", "pl": "Hamburg"},
                "airports": [{"iata": "HAM", "icao": "EDDH", "name": "Hamburg Airport"}]
            },
            {
                "slug": "dus",
                "names": {"ru": "Дюссельдорф", "en": "Dusseldorf", "pl": "Düsseldorf"},
                "airports": [{"iata": "DUS", "icao": "EDDL", "name": "Düsseldorf Airport"}]
            }
        ]
    },
    {
        "code": "GB",
        "flag": "🇬🇧",
        "names": {"ru": "Великобритания", "en": "United Kingdom", "pl": "Wielka Brytania"},
        "cities": [
            {
                "slug": "lon",
                "names": {"ru": "Лондон", "en": "London", "pl": "Londyn"},
                "airports": [
                    {"iata": "LHR", "icao": "EGLL", "name": "London Heathrow"},
                    {"iata": "LGW", "icao": "EGKK", "name": "London Gatwick"},
                    {"iata": "STN", "icao": "EGSS", "name": "London Stansted"},
                    {"iata": "LTN", "icao": "EGGW", "name": "London Luton"}
                ]
            },
            {
                "slug": "man",
                "names": {"ru": "Манчестер", "en": "Manchester", "pl": "Manchester"},
                "airports": [{"iata": "MAN", "icao": "EGCC", "name": "Manchester Airport"}]
            },
            {
                "slug": "edi",
                "names": {"ru": "Эдинбург", "en": "Edinburgh", "pl": "Edynburg"},
                "airports": [{"iata": "EDI", "icao": "EGPH", "name": "Edinburgh Airport"}]
            }
        ]
    },
    {
        "code": "FR",
        "flag": "🇫🇷",
        "names": {"ru": "Франция", "en": "France", "pl": "Francja"},
        "cities": [
            {
                "slug": "par",
                "names": {"ru": "Париж", "en": "Paris", "pl": "Paryż"},
                "airports": [
                    {"iata": "CDG", "icao": "LFPG", "name": "Paris Charles de Gaulle"},
                    {"iata": "ORY", "icao": "LFPO", "name": "Paris Orly"}
                ]
            },
            {
                "slug": "nce",
                "names": {"ru": "Ницца", "en": "Nice", "pl": "Nicea"},
                "airports": [{"iata": "NCE", "icao": "LFMN", "name": "Nice Côte d'Azur"}]
            }
        ]
    },
    {
        "code": "ES",
        "flag": "🇪🇸",
        "names": {"ru": "Испания", "en": "Spain", "pl": "Hiszpania"},
        "cities": [
            {
                "slug": "mad",
                "names": {"ru": "Мадрид", "en": "Madrid", "pl": "Madryt"},
                "airports": [{"iata": "MAD", "icao": "LEMD", "name": "Madrid-Barajas"}]
            },
            {
                "slug": "bcn",
                "names": {"ru": "Барселона", "en": "Barcelona", "pl": "Barcelona"},
                "airports": [{"iata": "BCN", "icao": "LEBL", "name": "Barcelona El Prat"}]
            },
            {
                "slug": "pmi",
                "names": {"ru": "Пальма-де-Майорка", "en": "Palma de Mallorca", "pl": "Majorka"},
                "airports": [{"iata": "PMI", "icao": "LEPA", "name": "Palma de Mallorca"}]
            }
        ]
    },
    {
        "code": "IT",
        "flag": "🇮🇹",
        "names": {"ru": "Италия", "en": "Italy", "pl": "Włochy"},
        "cities": [
            {
                "slug": "rom",
                "names": {"ru": "Рим", "en": "Rome", "pl": "Rzym"},
                "airports": [{"iata": "FCO", "icao": "LIRF", "name": "Rome Fiumicino"}]
            },
            {
                "slug": "mil",
                "names": {"ru": "Милан", "en": "Milan", "pl": "Mediolan"},
                "airports": [
                    {"iata": "MXP", "icao": "LIMC", "name": "Milan Malpensa"},
                    {"iata": "BGY", "icao": "LIME", "name": "Milan Bergamo"}
                ]
            }
        ]
    },
    {
        "code": "NL",
        "flag": "🇳🇱",
        "names": {"ru": "Нидерланды", "en": "Netherlands", "pl": "Holandia"},
        "cities": [
            {
                "slug": "ams",
                "names": {"ru": "Амстердам", "en": "Amsterdam", "pl": "Amsterdam"},
                "airports": [{"iata": "AMS", "icao": "EHAM", "name": "Amsterdam Schiphol"}]
            },
            {
                "slug": "ein",
                "names": {"ru": "Эйндховен", "en": "Eindhoven", "pl": "Eindhoven"},
                "airports": [{"iata": "EIN", "icao": "EHEH", "name": "Eindhoven Airport"}]
            }
        ]
    },
    {
        "code": "AT",
        "flag": "🇦🇹",
        "names": {"ru": "Австрия", "en": "Austria", "pl": "Austria"},
        "cities": [
            {
                "slug": "vie",
                "names": {"ru": "Вена", "en": "Vienna", "pl": "Wiedeń"},
                "airports": [{"iata": "VIE", "icao": "LOWW", "name": "Vienna Schwechat"}]
            }
        ]
    },
    {
        "code": "CH",
        "flag": "🇨🇭",
        "names": {"ru": "Швейцария", "en": "Switzerland", "pl": "Szwajcaria"},
        "cities": [
            {
                "slug": "zrh",
                "names": {"ru": "Цюрих", "en": "Zurich", "pl": "Zurych"},
                "airports": [{"iata": "ZRH", "icao": "LSZH", "name": "Zurich Airport"}]
            },
            {
                "slug": "gva",
                "names": {"ru": "Женева", "en": "Geneva", "pl": "Genewa"},
                "airports": [{"iata": "GVA", "icao": "LSGG", "name": "Geneva Airport"}]
            }
        ]
    },
    {
        "code": "CZ",
        "flag": "🇨🇿",
        "names": {"ru": "Чехия", "en": "Czechia", "pl": "Czechy"},
        "cities": [
            {
                "slug": "prg",
                "names": {"ru": "Прага", "en": "Prague", "pl": "Praga"},
                "airports": [{"iata": "PRG", "icao": "LKPR", "name": "Prague Václav Havel"}]
            }
        ]
    },
    {
        "code": "BALT",
        "flag": "🇱🇻",
        "names": {"ru": "Страны Балтии 🇱🇻🇱🇹🇪🇪", "en": "Baltic States 🇱🇻🇱🇹🇪🇪", "pl": "Kraje Bałtyckie 🇱🇻🇱🇹🇪🇪"},
        "cities": [
            {
                "slug": "rix",
                "names": {"ru": "Рига 🇱🇻", "en": "Riga 🇱🇻", "pl": "Ryga 🇱🇻"},
                "airports": [{"iata": "RIX", "icao": "EVRA", "name": "Riga International"}]
            },
            {
                "slug": "vno",
                "names": {"ru": "Вильнюс 🇱🇹", "en": "Vilnius 🇱🇹", "pl": "Wilno 🇱🇹"},
                "airports": [{"iata": "VNO", "icao": "EYVI", "name": "Vilnius International"}]
            },
            {
                "slug": "tll",
                "names": {"ru": "Таллин 🇪🇪", "en": "Tallinn 🇪🇪", "pl": "Tallinn 🇪🇪"},
                "airports": [{"iata": "TLL", "icao": "EETN", "name": "Tallinn Lennart Meri"}]
            }
        ]
    },
    {
        "code": "NORD",
        "flag": "🇸🇪",
        "names": {"ru": "Скандинавия 🇸🇪🇩🇰🇳🇴🇫🇮", "en": "Nordics 🇸🇪🇩🇰🇳🇴🇫🇮", "pl": "Skandynawia 🇸🇪🇩🇰🇳🇴🇫🇮"},
        "cities": [
            {
                "slug": "arn",
                "names": {"ru": "Стокгольм 🇸🇪", "en": "Stockholm 🇸🇪", "pl": "Sztokholm 🇸🇪"},
                "airports": [{"iata": "ARN", "icao": "ESSA", "name": "Stockholm Arlanda"}]
            },
            {
                "slug": "cph",
                "names": {"ru": "Копенгаген 🇩🇰", "en": "Copenhagen 🇩🇰", "pl": "Kopenhaga 🇩🇰"},
                "airports": [{"iata": "CPH", "icao": "EKCH", "name": "Copenhagen Kastrup"}]
            },
            {
                "slug": "osl",
                "names": {"ru": "Осло 🇳🇴", "en": "Oslo 🇳🇴", "pl": "Oslo 🇳🇴"},
                "airports": [{"iata": "OSL", "icao": "ENGM", "name": "Oslo Gardermoen"}]
            },
            {
                "slug": "hel",
                "names": {"ru": "Хельсинки 🇫🇮", "en": "Helsinki 🇫🇮", "pl": "Helsinki 🇫🇮"},
                "airports": [{"iata": "HEL", "icao": "EFHK", "name": "Helsinki-Vantaa"}]
            }
        ]
    },
    {
        "code": "ME",
        "flag": "🇦🇪",
        "names": {"ru": "Ближний Восток & Турция 🇦🇪🇹🇷🇶🇦", "en": "Middle East & Turkey 🇦🇪🇹🇷🇶🇦", "pl": "Bliski Wschód i Turcja 🇦🇪🇹🇷🇶🇦"},
        "cities": [
            {
                "slug": "ist",
                "names": {"ru": "Стамбул 🇹🇷", "en": "Istanbul 🇹🇷", "pl": "Stambuł 🇹🇷"},
                "airports": [
                    {"iata": "IST", "icao": "LTFM", "name": "Istanbul Airport"},
                    {"iata": "SAW", "icao": "LTFJ", "name": "Sabiha Gökçen"}
                ]
            },
            {
                "slug": "dxb",
                "names": {"ru": "Дубай 🇦🇪", "en": "Dubai 🇦🇪", "pl": "Dubaj 🇦🇪"},
                "airports": [{"iata": "DXB", "icao": "OMDB", "name": "Dubai International"}]
            },
            {
                "slug": "doh",
                "names": {"ru": "Доха 🇶🇦", "en": "Doha 🇶🇦", "pl": "Doha 🇶🇦"},
                "airports": [{"iata": "DOH", "icao": "OTHH", "name": "Hamad International"}]
            }
        ]
    }
]

def get_country_by_code(code: str) -> dict:
    for c in AIRPORT_HIERARCHY:
        if c["code"] == code:
            return c
    return None

def get_city_by_slug(country_code: str, city_slug: str) -> dict:
    country = get_country_by_code(country_code)
    if not country:
        return None
    for city in country.get("cities", []):
        if city["slug"] == city_slug:
            return city
    return None


# ---------------------------------------------------------------------------
# Global airport catalogue (OurAirports, scheduled service + IATA code only)
# Structure: {ISO2: {"n": country name, "c": [[city, [[iata, icao, name, lat, lon], ...]], ...]}}
# ---------------------------------------------------------------------------
import json as _json
import os as _os

_WORLD = None
_WORLD_PRIORITY = ["PL", "DE", "AT", "CZ", "SK", "GB", "FR", "ES", "IT", "NL", "CH", "LV", "LT", "EE",
                   "SE", "DK", "NO", "FI", "US", "TR", "AE"]


def _load_world() -> dict:
    global _WORLD
    if _WORLD is None:
        path = _os.path.join(_os.path.dirname(__file__), "airports_world.json")
        try:
            with open(path, encoding="utf-8") as f:
                _WORLD = _json.load(f)
        except Exception as e:
            print(f"Failed to load airports_world.json: {e}")
            _WORLD = {}
    return _WORLD


def country_flag(cc: str) -> str:
    if not cc or len(cc) != 2:
        return "🌍"
    return "".join(chr(0x1F1E6 + ord(ch) - 65) for ch in cc.upper())


def world_countries() -> list:
    """[(iso2, name)] — priority countries first, then alphabetical."""
    w = _load_world()
    prio = [c for c in _WORLD_PRIORITY if c in w]
    rest = sorted((c for c in w if c not in prio), key=lambda c: w[c]["n"])
    return [(c, w[c]["n"]) for c in prio + rest]


def world_cities(cc: str) -> list:
    """[(city, [airport rows])] for a country; stable order (index used in callbacks)."""
    return [(c, a) for c, a in _load_world().get(cc, {}).get("c", [])]


def world_country_name(cc: str) -> str:
    return _load_world().get(cc, {}).get("n", cc)


def get_world_airport(code: str):
    for cc, data in _load_world().items():
        for city, aps in data["c"]:
            for iata, icao, name, lat, lon in aps:
                if code in (iata, icao):
                    return {
                        "iata": iata, "icao": icao, "name": name, "lat": lat, "lon": lon,
                        "country": f"{data['n']} {country_flag(cc)}",
                        "frequencies": {},
                        "liveatc": {"available": False, "streams": [],
                                    "web_url": f"https://www.liveatc.net/search/?icao={icao}"},
                    }
    return None


def _fold(text: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower().strip()


def search_world_airports(query: str, limit: int = 10) -> list:
    """Search airports by city or airport name (accent/case-insensitive). Returns list of airport dicts."""
    q = _fold(query)
    if len(q) < 3:
        return []
    exact, partial = [], []
    for cc, data in _load_world().items():
        for city, aps in data["c"]:
            fc = _fold(city)
            for iata, icao, name, lat, lon in aps:
                row = {"iata": iata, "icao": icao, "name": name, "city": city, "cc": cc}
                if q == fc or q == _fold(name):
                    exact.append(row)
                elif q in fc or q in _fold(name):
                    partial.append(row)
    res = exact or partial
    return res[:limit] if len(res) <= limit else res[:limit]
