import time
from PIL import Image
from pygame.locals import OPENGL, DOUBLEBUF

import io

import pgr_ui
from func import draw_image_left_top, get_texture_id, to_BG, phi_time2second, draw_image_center_ex, get_text_texture_id
import err_hook
import parse_chart
from tkinter.filedialog import askopenfilename
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from const import *
from logger import *


pygame.init()
pygame.mixer.init()
pygame.font.init()
window = pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL)
pygame.display.set_caption("PyPhiPlayer")
gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
glClearColor(0., 0., 0., 1.)
glEnable(GL_BLEND)
glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_FASTEST)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
import phigros_obj
while True:
    chart_path = askopenfilename(filetypes=[("谱面文件", ["*.zip", "*.pez", "*.json"]), ("所有类型", "*.*")])
    chart_info = parse_chart.parse_chart(chart_path)
    if "err" in chart_info:
        error(chart_info["err"])
        continue
    if not chart_info["isZip"]:
        info("读取到JSON文件，还需导入音乐与背景图片")
        info("请选择一个图片当作背景图片")
        chart_info["BG"] = get_texture_id(to_BG(Image.open(askopenfilename(filetypes=[("谱面文件", ["*.png", "*.jpg", "*.jpeg"])]))))
        info("请选择一个音乐")
        audio_path = askopenfilename(filetypes=[("谱面文件", ["*.wav", "*.ogg", "*.mp3"])])
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        chart_info["Audio"] = audio_bytes
    break
if "formatVersion" in chart_info["Chart"]:
    info(f"读取到官谱格式的谱面，formatVersion为{chart_info['Chart']['formatVersion']}")
    HX_time = []
    notes = [note for item in chart_info["Chart"]["judgeLineList"] for note in (item["notesAbove"] + item["notesBelow"])]
    notes_bpm = [item["bpm"] for item in chart_info["Chart"]["judgeLineList"] for note in
             (item["notesAbove"] + item["notesBelow"])]
    note_score = 1_000_000 / len(notes)
    for index, item in enumerate(notes):
        for index2, item2 in enumerate(notes):
            if index != index2:
                if item["time"] == item2["time"] and notes_bpm[index] == notes_bpm[index2] and phi_time2second(item["time"], 1.875/notes_bpm[index]) not in HX_time:
                    HX_time.append(phi_time2second(item["time"], 1.875/notes_bpm[index]))
    for i in chart_info["Chart"]["judgeLineList"]:
        for j in i["notesAbove"]:
            j["HX"] = phi_time2second(j["time"],1.875/i["bpm"]) in HX_time
        for j in i["notesBelow"]:
            j["HX"] = phi_time2second(j["time"],1.875/i["bpm"]) in HX_time
    lines = [phigros_obj.Line(data) for data in chart_info["Chart"]["judgeLineList"]]
    draw_image_center_ex(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, 0, 1, *get_text_texture_id("看看控制台TAT", UI_FONT, 50))
    pygame.display.flip()
    if "Name" not in chart_info:
        name = input(f"{GREEN}请输入曲名\n>_ ")
    else:
        name = chart_info["Name"]
    if "Level" not in chart_info:
        level = input(f"请输入难度\n>_ {RESET}")
    else:
        level = chart_info["Level"]
    ui = pgr_ui.UI(name, level)
elif "META" in chart_info["Chart"]:
    warn(f"读取到RPE格式的谱面，格式版本为{chart_info['Chart']['META']['RPEVersion']}，暂未支持，将在一秒后退出")
    time.sleep(1)
    pygame.quit()
    quit()
else:
    error(f"未知格式，将在一秒后退出")
    time.sleep(1)
    pygame.quit()
    quit()


audio_stream = io.BytesIO(chart_info["Audio"])
pygame.mixer.music.load(audio_stream)
clock = pygame.time.Clock()
combo = 0
game_time = 0
fps_time = 0
lst_pf = 0
lst_cb = 0
pygame.mixer.music.play()
while True:
    pf = 0
    delta = clock.tick() / 1000
    glClear(GL_COLOR_BUFFER_BIT)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    game_time += delta
    fps_time += delta
    if fps_time >= 1:
        info(f"FPS: {clock.get_fps()}")
        fps_time = 0

    draw_image_left_top(0, 0, *chart_info["BG"])

    for line in lines:
        line.calc(game_time, delta)
        line.draw()
    for line in lines:
        line.draw_notes(game_time)
    for line in lines:
        line.draw_HE(game_time)
        combo += line.get_combo()
        pf += line.perfect
    if combo != lst_cb:
        ui.set_combo(combo)
    if lst_pf != pf:
        ui.set_score(pf*note_score)
    ui.draw_ui()
    lst_pf = pf
    lst_cb = combo

    pygame.display.flip()