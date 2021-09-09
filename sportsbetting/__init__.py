"""
initialisation du module
"""
import collections
import json
import os
import queue
import re
import sys
import urllib.error

import chromedriver_autoinstaller
import colorama
from fake_useragent import UserAgent
import termcolor

ALL_ODDS_COMBINE = {}
ODDS = {}
TEAMS_NOT_FOUND = []
PROGRESS = 0
SUB_PROGRESS_LIMIT = 1
SITE_PROGRESS = collections.defaultdict(int)
QUEUE_TO_GUI = queue.Queue()
QUEUE_FROM_GUI = queue.Queue()
ODDS_INTERFACE = ""
EXPECTED_TIME = 0
INTERFACE = False
IS_PARSING = False
ABORT = False
SPORTS = ["basketball", "football", "handball", "hockey-sur-glace", "rugby", "tennis"]
PATH_DRIVER = ""
SELENIUM_SITES = {"joa"}
DB_BOOKMAKERS = ["betclic", "betfair", "betway", "bwin", "france_pari", "joa", "netbet", "parionssport",
              "pasinobet", "pinnacle", "pmu", "pokerstars", "unibet", "winamax", "zebet"]
BOOKMAKERS = sorted(DB_BOOKMAKERS + ["barrierebet", "vbet"])
BOOKMAKERS_BOOST = sorted(BOOKMAKERS + ["unibet_boost"])
TEST = False
DB_MANAGEMENT = False
COOKIES_JOA_ACCEPTED = False
TRANSLATION = {}
BETA = False
SUREBETS = {}
MIDDLES = {}
MILES_RATES = {"5€" : 385, "10€" : 770, "20€" : 1510, "50€" : 3700, "100€": 7270, "200€" : 14290, "500€" : 35090, "1000€" : 69000, "2000€":135600, "5000€": 333330}
SEEN_SUREBET = {x:True for x in SPORTS}
FREEBETS_RATES = {bookmaker : 80 for bookmaker in BOOKMAKERS if bookmaker not in ["pinnacle", "betfair"]}


class UnavailableCompetitionException(Exception):
    """
    Exception renvoyée lorsqu'une compétition est introuvable
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class UnavailableSiteException(Exception):
    """
    Exception renvoyée lorsqu'un bookmaker est indisponible
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class AbortException(Exception):
    """
    Exception renvoyée lorsqu'on interropt le parsing
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)



def grp(pat, txt):
    res = re.search(pat, txt)
    return res.group(0) if res else '&'

def find_files(filename, search_path):
    for root, _, files in os.walk(search_path):
        if filename in files:
            return os.path.abspath(os.path.join(root, filename))


chrome_version = ""
colorama.init()
try:
    PATH_DRIVER = chromedriver_autoinstaller.install(True)
    chrome_version = chromedriver_autoinstaller.get_chrome_version()
    print("Chrome version :", chrome_version)
except IndexError:
    PATH_DRIVER = find_files("chromedriver.exe", ".")
    print("Chrome version not found")
    print(termcolor.colored('Chrome version not found{}'
                            .format(colorama.Style.RESET_ALL),
                            'yellow'))

chromedriver_version = ""
if sys.platform.startswith("win"):
    chromedriver_version = PATH_DRIVER.split("\\")[-2]
else:
    chromedriver_version = PATH_DRIVER.split("/")[-2]
if chrome_version.split(".")[0] == chromedriver_version:
    print(termcolor.colored('Matching Chrome and chromedriver versions{}'
                            .format(colorama.Style.RESET_ALL),
                            'green'))
else:
    print(termcolor.colored('Unmatching Chrome and chromedriver versions\nPlease update Chrome{}'
                            .format(colorama.Style.RESET_ALL),
                            'yellow'))
    print(PATH_DRIVER)
colorama.deinit()

PATH_DB = os.path.dirname(__file__) + "/resources/teams.db"

PATH_TOKENS = os.path.dirname(__file__) + "/bookmakers/tokens.txt"

PATH_FREEBETS = os.path.dirname(__file__) + "/freebets.txt"
if not os.path.exists(PATH_FREEBETS):
    with open(PATH_FREEBETS, "a+") as file:
        for bookmaker, rate in FREEBETS_RATES.items():
            if bookmaker in ["pinnacle", "betfair"]:
                continue
            file.write("{} {}\n".format(bookmaker, rate))
else:
    with open(PATH_FREEBETS, "r") as file:
        lines = file.readlines()
        for line in lines:
            bookmaker, rate = line.split()
            FREEBETS_RATES[bookmaker] = float(rate)

PATH_TRANSLATION = os.path.dirname(__file__) + "/resources/translation.json"
with open(PATH_TRANSLATION, encoding='utf-8') as file:
    TRANSLATION = json.load(file)

PATH_FONT = os.path.dirname(__file__) + "/resources/DejaVuSansMono.ttf"

