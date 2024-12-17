import sys
import traceback
from tkinter.messagebox import showerror
from os.path import isdir, join, dirname
from datetime import datetime
from os import mkdir
from random import randint

def except_hook(exc_type, exc_value, exc_traceback):
    track = traceback.format_exception(exc_value)
    log_dir = join(dirname(__file__), "log")
    if not isdir(log_dir):
        mkdir(log_dir)
    log_path = join(log_dir, f"{datetime.now().strftime("%Y-%m-%d %H-%M-%S")} {randint(10000,99999)}.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(track))
    showerror("错误", f"模拟器发生错误，错误信息如下：\n\n{'\n'.join(track)}\n\n错误信息已保存至{log_path}")

sys.excepthook = except_hook