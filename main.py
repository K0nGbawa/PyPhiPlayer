import cProfile
import os
import random
import subprocess
import sys
import time
from ctypes import windll

from PIL import Image
from pygame import NOFRAME, HWSURFACE
from pygame.locals import OPENGL, DOUBLEBUF

import io
import numpy as np

from tqdm import tqdm

import dxsmixer
import hitsound
import pgr_ui
from func import draw_image_left_top, get_texture_id, to_BG, phi_time2second, draw_image_center_ex, get_text_texture_id, \
    get_audio_length, get_argv, rpe_beat_to_second, rpe_beat_to_beat, beat_to_second
import err_hook
import parse_chart
from tkinter.filedialog import askopenfilename
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from const import *
from logger import *

class Phi:
    def __init__(self):
        self.game_time = offset
        self.fps_time = 0
        self.combo = 0
        self.lst_cb = 0
        self.lst_pf = 0
        self.lst_gd = 0
        self.judge_line_color = PERFECT
    def update(self, delta: float):
        pf = 0
        gd = 0
        glClear(GL_COLOR_BUFFER_BIT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                windll.kernel32.ExitProcess(0)
        if config["render"]:
            self.game_time += delta
        else:
            game_time = music.get_pos()
            self.game_time = game_time if game_time > 0 else self.game_time + delta
            self.fps_time += delta
            if self.fps_time >= 1:
                info(f"FPS: {clock.get_fps()}")
                self.fps_time = 0

        draw_image_left_top(0, 0, *chart_info["BG"])

        if self.lst_gd > 0:
            self.judge_line_color = GOOD

        for line in lines:
            line.calc(self.game_time, delta)
            line.draw(self.judge_line_color)
        for line in lines:
            line.draw_holds(self.game_time)
        for line in lines:
            line.draw_notes(self.game_time)
        for line in lines:
            line.draw_HE(self.game_time)
            self.combo += line.get_combo()
            pf += line.perfect
            gd += line.good
        if self.combo != self.lst_cb:
            ui.set_combo(self.combo)
        if self.lst_pf != pf or self.lst_gd != gd:
            ui.set_score(pf * note_score + gd * note_score * 0.685)
        ui.draw_ui(self.game_time)
        self.lst_pf = pf
        self.lst_gd = gd
        self.lst_cb = self.combo

        pygame.display.flip()

class RPE:
    def __init__(self):
        self.game_time = -offset
        self.fps_time = 0
        self.combo = 0
        self.lst_cb = 0
        self.lst_pf = 0
        self.bpm_list = []
        for bpm in chart_info["Chart"]["BPMList"]:
            self.bpm_list.append({"time":beat_to_second(bpm["startTime"], chart_info["Chart"]["BPMList"]), "bpm": bpm["bpm"]})

    def update(self, delta: float):
        glClear(GL_COLOR_BUFFER_BIT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                windll.kernel32.ExitProcess(0)
        if "-render" not in sys.argv:
            self.game_time = music.get_pos()+offset
            self.fps_time += delta
            if self.fps_time >= 1:
                info(f"FPS: {clock.get_fps()}")
                self.fps_time = 0
        else:
            game_time = music.get_pos()
            self.game_time = game_time if game_time > 0 else self.game_time + delta
            self.fps_time += delta
            if self.fps_time >= 1:
                info(f"FPS: {clock.get_fps()}")
                self.fps_time = 0
        bpm = self.get_bpm()
        draw_image_left_top(0, 0, *chart_info["BG"])
        for line in lines:
            line.calc(self.game_time)
            line.draw()
        for line in lines:
            line.draw_holds(self.game_time, delta, bpm)
        for line in lines:
            line.draw_notes(self.game_time)
        for line in lines:
            line.draw_he(self.game_time)
        pygame.display.flip()

    def get_bpm(self):
        if len(self.bpm_list) > 1:
            l = 0
            r = len(self.bpm_list)
            while l > r:
                m = (l+r)//2
                if self.bpm_list[m]["time"] > self.game_time:
                    r = m-1
                elif self.bpm_list[m]["time"] < self.game_time:
                    l = m+1
                else:
                    return self.bpm_list[m]["bpm"]
        return self.bpm_list[0]["bpm"]

pygame.init()
pygame.mixer.init()
pygame.font.init()
if config["no_frame"]:
    window = pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL | NOFRAME)
else:
    window = pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL)
tmp = f"k0ngbawa{random.randint(0, 100000)}"
pygame.display.set_caption(tmp)
hwnd = windll.user32.FindWindowW(None, tmp)
if config["render"] and not config["show_window"]:
    windll.user32.ShowWindow(hwnd, 0)
if config["parent"] is not None:
    parent_hwnd = windll.user32.FindWindowW(None, config["parent"])
    windll.user32.SetParent(hwnd, parent_hwnd)
    windll.user32.SetWindowPos(hwnd, 0, 0, 0, *WINDOW_SIZE)
pygame.display.set_caption("PyPhiPlayer")
if not config["r"]:
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
else:
    gluOrtho2D(-WINDOW_WIDTH, WINDOW_WIDTH*2, -WINDOW_HEIGHT, WINDOW_HEIGHT*2)
glClearColor(0., 0., 0., 1.)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

import phigros_obj
import rpe_obj

while True:
    chart_path = askopenfilename(filetypes=[("谱面文件", ["*.zip", "*.pez", "*.json"]), ("所有类型", "*.*")]) if config["use_filedialog"] or config["chart_path"] is None else config["chart_path"]
    chart_info = parse_chart.parse_chart(chart_path)
    if "err" in chart_info:
        error(chart_info["err"])
        continue
    if not chart_info["isZip"] and (config["use_filedialog"] or config["audio_path"] is None or config["bg_path"] is None):
        info("读取到JSON文件，还需导入音乐与背景图片")
        info("请选择一个图片当作背景图片")
        chart_info["BG"] = get_texture_id(to_BG(Image.open(askopenfilename(filetypes=[("图片文件", ["*.png", "*.jpg", "*.jpeg"])]))))
        info("请选择一个音乐")
        audio_path = askopenfilename(filetypes=[("音频文件", ["*.wav", "*.ogg", "*.mp3"])])
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        chart_info["Audio"] = audio_bytes
    elif config["audio_path"] is not None or config["audio_path"] is not None:
        if config["bg_path"] is not None:
            chart_info["BG"] = get_texture_id(to_BG(Image.open(config["bg_path"])))
        if config["audio_path"] is not None:
            audio_path = config["audio_path"]
    break
if "formatVersion" in chart_info["Chart"]:
    info("Init multi-key prompt...")
    HX_time = []
    notes = [note for item in chart_info["Chart"]["judgeLineList"] for note in (item["notesAbove"] + item["notesBelow"])]
    notes_bpm = [item["bpm"] for item in chart_info["Chart"]["judgeLineList"] for note in
             (item["notesAbove"] + item["notesBelow"])]
    note_score = (1_000_000 / len(notes)) if len(notes) != 0 else 1000000
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
    info("Success.")
    info("Init lines...")
    lines = [phigros_obj.Line(data, index) for index, data in enumerate(chart_info["Chart"]["judgeLineList"])]
    info("Success.")
    #draw_image_center_ex(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, 0, 1, *get_text_texture_id("看看控制台TAT", UI_FONT, 50))
    #pygame.display.flip()
    info("Getting chart info...")
    if "Name" not in chart_info:
        name = config["name"]
    else:
        name = chart_info["Name"]
    if "Level" not in chart_info:
        level = config["level"]
    else:
        level = chart_info["Level"]
    m_io = io.BytesIO(chart_info["Audio"])
    ui = pgr_ui.UI(name, level, get_audio_length(m_io))
    m_io.close()
    offset = chart_info["Chart"]["offset"]
    game = Phi()
elif "META" in chart_info["Chart"]:
    info("Getting chart info...")
    if "Name" not in chart_info:
        name = chart_info['Chart']['META']["name"]
    else:
        name = chart_info["Name"]
    if "Level" not in chart_info:
        level = chart_info['Chart']['META']["level"]
    else:
        level = chart_info["Level"]
    offset = -chart_info["Chart"]["META"]["offset"]/1000
    info("Success.")
    info("Init BPMList...")
    for e in chart_info["Chart"]["BPMList"]:
        e["startTime"] = rpe_beat_to_beat(e["startTime"])
    info("Success")
    info("Init lines...")
    lines = [rpe_obj.Line(data, chart_info["JudgeLineTexture"], chart_info["Chart"]["BPMList"], i) for i, data in enumerate(chart_info["Chart"]["judgeLineList"])]
    for line in lines:
        line.set_lines(lines)
    info("Success.")
    info("Sorting Lines")
    lines.sort(key=lambda x: x.z_order)
    info("Success")
    game = RPE()


audio_stream = io.BytesIO(chart_info["Audio"])
#pygame.mixer.music.load(audio_stream)
music = dxsmixer.musicCls()
music.load(audio_stream.read())
clock = pygame.time.Clock()
if not config["render"]:
    #pygame.mixer.music.play()
    music.play()
    while True:
        delta = clock.tick()/1000
        game.update(delta)
else:
    res = config["res"]
    audio_io = io.BytesIO(chart_info["Audio"])
    audio_duration = get_audio_length(audio_io)
    fps = int(config["fps"])
    delta = 1/fps
    frame_count = int(audio_duration/delta)
    bitrate = config["bitrate"]
    with open("tmp", "wb") as f:
        f.write(chart_info["Audio"])
    hitsound.summon(chart_info["Chart"], "./tmp", "./tmp", config["offset"])
    ffmpeg_command = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-s", f"{res[0]}x{res[1]}", "-pix_fmt", "rgb24",
        "-r", str(fps), "-i", "-", "-i", "./tmp", "-c:v", "libx264", "-b:v", f"{bitrate}k", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-strict", "experimental", config["output"]
    ]
    process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    is_r = config["r"]

    game.update(delta)
    for frame in tqdm(range(frame_count), desc="Rendering video", unit="frames"):
        game.update(delta)
        if is_r:
            frame_image = glReadPixels(-WINDOW_WIDTH, WINDOW_WIDTH*2, -WINDOW_HEIGHT, WINDOW_HEIGHT*2)
        else:
            frame_image = glReadPixels(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
        f = np.frombuffer(frame_image, dtype=np.uint8).reshape((WINDOW_HEIGHT, WINDOW_WIDTH, 3))
        f = np.flipud(f)
        process.stdin.write(f.tobytes())

    process.stdin.close()
    process.wait()
    os.remove("tmp")
