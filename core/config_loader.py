import json
from pathlib import Path
from core.db import DB

# Paths
CONFIG_PATH = Path("config/config.json")
TEXTS_PATH = Path("config/texts.json")

# Initial
CFG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
TEXTS = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
DBH = DB(CFG["DB_PATH"])

def reload_config():
    global CFG, DBH
    CFG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    DBH = DB(CFG["DB_PATH"])
    return CFG

def reload_texts():
    global TEXTS
    TEXTS = json.loads(TEXTS_PATH.read_text(encoding="utf-8"))
    return TEXTS