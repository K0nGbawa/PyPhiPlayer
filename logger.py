from datetime import datetime
from const import GREEN, YELLOW, RED, RESET

_LEVELS = ["INFO", "WARN", "ERROR"]
_LEVEL_COLORS = [GREEN, YELLOW, RED]

def _to_str(*args):
    return map(str, args)

def _build_log_text(content: str, level=0):
    return f"{_LEVEL_COLORS[level]}[{_LEVELS[level]}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {content}{RESET}"

def info(*args, separator: str=" "):
    print(_build_log_text(separator.join(_to_str(*args)), level=0))

def warn(*args, separator: str=" "):
    print(_build_log_text(separator.join(_to_str(*args)), level=1))

def error(*args, separator: str=" "):
    print(_build_log_text(separator.join(_to_str(*args)), level=2))