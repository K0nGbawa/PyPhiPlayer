import sys



def get_argv(argv: str):
    if f"-{argv}" in sys.argv:
        value = sys.argv[sys.argv.index(f"-{argv}")+1]
    else:
        value = input(f"{argv}: ")
    return value


RED: str = "\033[91m"
GREEN: str = "\033[92m"
YELLOW: str = "\033[93m"
BLUE: str = "\033[94m"
MAGENTA: str = "\033[95m"
CYAN: str = "\033[96m"
WHITE: str = "\033[97m"
RESET: str = "\033[0m"


UI_FONT = "./resources/fonts/font.ttf"
CMDYSJ_FONT = "./resources/fonts/cmdysj.ttf"


usage = ("python main.py\n"
         "--render\t\t渲染视频\n"
         "--use-filedialog\t使用文件对话框选择文件\n"
         "--chart <chart-path>\t指定谱面\n"
         "--audio <audio-path>\t指定音乐\n"
         "--bg <bg_path>\t\t指定背景\n"
         "--res <w>x<h>\t\t指定分辨率\n"
         "--fps <fps>\t\t指定fps\n"
         "--bitrate <bitrate>\t指定码率\n"
         "--name <name>\t\t指定歌曲名\n"
         "--level <level>\t\t指定难度\n"
         "--output <path>\t\t指定导出位置\n"
         "--noframe\t\t无框窗口")

def hex2rgb(hex_c:str):
    hex_c = hex_c.strip().strip("#")
    result = [int(hex_c[i:i+2], 16)/255 for i in range(0, len(hex_c), 2)]
    return result

def get_argv_default(argv: str, default):
    try:
        if f"--{argv}" in sys.argv:
            return sys.argv[sys.argv.index(f"--{argv}")+1]
        else:
            return default
    except IndexError:
        print(usage)
        exit()
config = {
    "chart_path": get_argv_default("chart", None),
    "audio_path": get_argv_default("audio", None),
    "bg_path": get_argv_default("bg", None),
    "fps": get_argv_default("fps", 60),
    "bitrate": get_argv_default("bitrate", 5000),
    "res": [int(x) for x in get_argv_default("res", "800x600").split("x")],
    "use_filedialog": "--use-filedialog" in sys.argv,
    "render": "--render" in sys.argv,
    "output": get_argv_default("output", "./output.mp4"),
    "name": get_argv_default("name", "UK"),
    "level": get_argv_default("level", "UK  Lv.10"),
    "r": "--r" in sys.argv,
    "show_window": "--show-window" in sys.argv,
    "no_frame": "--noframe" in sys.argv,
    "parent": get_argv_default("parent", None),
    "note_size": float(get_argv_default("note-size", 1)),
    "offset": float(get_argv_default("offset", 0)),
    "good_color": hex2rgb(get_argv_default("good-color", "#aae1ff")),
    "perfect_color": hex2rgb(get_argv_default("perfect-color", "#ffe1aa")),
    "combo_label": get_argv_default("combo", "COMBO")
}
if config["parent"] is not None:
    config["parent"] = config["parent"].replace("\\0", " ")
WINDOW_WIDTH, WINDOW_HEIGHT = config["res"]


PERFECT = config["perfect_color"]
GOOD = config["good_color"]

WINDOW_SIZE: list[int] = [WINDOW_WIDTH, WINDOW_HEIGHT]
LINE_WIDTH = 0.0075*WINDOW_HEIGHT

WINDOW_MID = [WINDOW_WIDTH/2, WINDOW_HEIGHT/2]

X_SCALE = WINDOW_WIDTH/800
Y_SCALE = WINDOW_HEIGHT/600
Y = 0.6*WINDOW_HEIGHT
X = 0.05625*WINDOW_WIDTH

WINDOW_POINTS = [
    (0, 0),
    (WINDOW_WIDTH, 0),
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    (0, WINDOW_HEIGHT)
]