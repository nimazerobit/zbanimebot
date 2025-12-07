import json
from pathlib import Path
from core.db import DB

# ——— Global state ———
CFG = json.loads(Path("config/config.json").read_text(encoding="utf-8"))
DBH = DB(CFG["DB_PATH"])

def reload_config():
    global CFG
    new_cfg = json.loads(Path("config/config.json").read_text(encoding="utf-8"))
    CFG = new_cfg
    return CFG