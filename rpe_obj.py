import ctypes
import math
from functools import lru_cache
import random

import pygame
from OpenGL.GL import *

from OpenGL.GL import glDeleteTextures
from PIL import Image

import const
from const import LINE_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT, UI_FONT, X_SCALE, CMDYSJ_FONT, WINDOW_MID, WINDOW_POINTS, \
    WINDOW_SIZE
from func import rpe_beat_to_second, tween_execute, draw_line_ex, rpe_y_to_window_y, rpe_x_to_window_x, \
    draw_image_center_ex, draw_image_center_alpha_ex, tween_color, tween_text, get_text_texture_id, lerp, \
    get_texture_id, draw_image_top_ex, draw_image_bottom_ex, draw_quad_center_ex
from logger import info
from playsound import open_audio
from logger import error as err

try:
    NOTE_TEXTURES: tuple = (get_texture_id(Image.open("./resources/textures/Tap.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_Head.png")),
                            get_texture_id(Image.open("./resources/textures/Flick.png")),
                            get_texture_id(Image.open("./resources/textures/Drag.png")),
                            get_texture_id(Image.open("./resources/textures/Hold.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_End.png")),
                            get_texture_id(Image.open("./resources/textures/TapHL.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_HeadHL.png")),
                            get_texture_id(Image.open("./resources/textures/FlickHL.png")),
                            get_texture_id(Image.open("./resources/textures/DragHL.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_Body_HL.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_End_HL.png")),
                            )
    NOTE_SOUNDS: tuple = (
        open_audio("./resources/sounds/tap.wav"),
        open_audio("./resources/sounds/tap.wav"),
        open_audio("./resources/sounds/flick.wav"),
        open_audio("./resources/sounds/drag.wav")
    )
    HE_TEXTURES: tuple = tuple([get_texture_id(Image.open(f"./resources/textures/HX/{i+1}.png")) for i in range(30)])
    NOTE_TEXTURES = tuple([(i[0], i[1]*X_SCALE, i[2] if index == 4 or index == 10 else i[2]*X_SCALE) for index, i in enumerate(NOTE_TEXTURES)])
    HE_TEXTURES = tuple([(i[0], i[1]*X_SCALE, i[2]*X_SCALE) for index, i in enumerate(HE_TEXTURES)])
except (TypeError, FileNotFoundError) as e:
    err(f"资源缺失：{e}")
    __import__("time").sleep(1)
    pygame.quit()
    quit()

def find_event(es: list, t: float):
    if not es: return 0.0
    l, r = 0, len(es) - 1
    
    while l <= r:
        m = (l + r) // 2
        e = es[m]
        st, et = e["startTime"], e["endTime"]
        if st <= t <= et: return e
        elif st > t: r = m - 1
        else: l = m + 1
    
    return es[-1] if es[-1]["endTime"] >= t else es[0]

def init_move_x_events(e:dict, bpm_list: list[dict], i, f):
    e = init_events(e, bpm_list)
    e["start"] = rpe_x_to_window_x(e["start"], i, f)
    e["end"] = rpe_x_to_window_x(e["end"], i, f)
    return e

def init_move_y_events(e:dict, bpm_list: list[dict], i, f):
    e = init_events(e, bpm_list)
    e["start"] = rpe_y_to_window_y(e["start"], i, f)
    e["end"] = rpe_y_to_window_y(e["end"], i, f)
    return e

def init_events(e: dict, bpm_list: list[dict]):
    e["startTime"] = rpe_beat_to_second(e["startTime"], bpm_list)
    e["endTime"] = rpe_beat_to_second(e["endTime"], bpm_list)
    return e

def fill_events(es: list, default: float|list[float]|str|None = 0.0, is_speed=False):
    aes = []
    for i, e in enumerate(es):
        if i != len(es) - 1:
            ne = es[i + 1]
            if e["endTime"] < ne["startTime"]:
                aes.append({"startTime": e["endTime"], "endTime": ne["startTime"], "start": e["end"], "end": e["end"], "easingType": 1})
    es.extend(aes)
    es.sort(key = lambda x: x["startTime"])
    if es:
        es.append({"startTime": es[-1]["endTime"], "endTime": 31250000, "start": es[-1]["end"], "end": es[-1]["end"], "easingType": 1})
        if es[0]['startTime'] > -999 and not is_speed:
            es.insert(0, {"startTime": 0, "endTime": es[0]["startTime"], "start": es[0]["start"], "end": es[0]["start"], "easingType": 1})
    else: es.append({"startTime": 0, "endTime": 31250000, "start": default, "end": default, "easingType": 1})
    return es


def get_event_value(e: list, t:float):
    e_ = find_event(e, t)
    return tween_execute(e_["startTime"], e_["endTime"], t, e_["start"], e_["end"], e_["easingType"])

def get_event_layer_value(e: list, t: float):
    e_ = [find_event(i, t) for i in e]
    return sum([tween_execute(i["startTime"], i["endTime"], t, i["start"], i["end"], i["easingType"]) for i in e_])

def rotate_point(x, y, θ, r) -> tuple[float, float]:
    xo = r * math.cos(math.radians(θ))
    yo = r * math.sin(math.radians(θ))
    return x + xo, y + yo

def get_color(e, t) -> list[float]:
    e_ = find_event(e, t)
    return tween_color(e_["startTime"], e_["endTime"], t, e_["start"], e_["end"], e_["easingType"])

def get_text(e, t) -> str:
    e_ = find_event(e, t)
    return tween_text(e_["startTime"], e_["endTime"], t, e_["start"], e_["end"], e_["easingType"])

def getLineLength(x0: float, y0: float, x1: float, y1: float):
    return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

def init_color_events(e, bpm_list: list[dict]):
    e = init_events(e, bpm_list)
    e["start"] = [c/255 for c in e["start"]]
    e["end"] = [c/255 for c in e["end"]]
    return e

def to_sx(x_scale):
    return 1/1350*WINDOW_WIDTH*x_scale

def to_sy(y_scale):
    return 1/900*WINDOW_HEIGHT*y_scale

def convert_speed_unit(e):
    e["start"] = e["start"]/ 900 * WINDOW_HEIGHT*120
    e["end"] = e["end"]/ 900 * WINDOW_HEIGHT*120
    return e

def init_speed_event(es):
    es = list(map(convert_speed_unit, es))
    fp = 0
    for i, e in enumerate(es):
        e["fp"] = fp
        fp += (e["end"]+e["start"])*(e["endTime"]-e["startTime"])/2
    return es


def init_note(se: list, data: dict, bpm_list: list[dict]):
    data["startTime"] = rpe_beat_to_second(data["startTime"], bpm_list)
    data["endTime"] = rpe_beat_to_second(data["endTime"], bpm_list)
    data["positionX"] = data["positionX"] / 1350 * WINDOW_WIDTH
    data["alpha"] /= 255
    data["fp"] = get_fp(se, data["startTime"])
    data["end_fp"] = get_fp(se, data["endTime"]) if data["type"] == 2 else data["fp"]
    return data


def get_fp(events: list[dict], time: float):
    e = find_event(events, time)
    return e["fp"] + (lerp(e["start"], e["end"], (time-e["startTime"])/(e["endTime"]-e["startTime"])) + e["start"])*(time-e["startTime"])/2

def calc_line_equation(x, y, r) -> tuple[float, float, float]:
    slope = math.tan(math.radians(r))
    return -slope, 1, slope*x-y

def exe_notes(notes_):
    grouped_note = {}
    for note in notes_:
        speed = str(note.speed)
        if speed not in grouped_note:
            grouped_note[speed] = []
        grouped_note[speed].append(note)
    notes_ = list(grouped_note.values())
    for notes in notes_:
        notes.sort(key=lambda x: x.time)
    return notes_

class Line:
    def __init__(self, data, texture_id, bpm_list, index):
        info(f"Init lines {index}...")
        self.floor_position = 0
        self.cache = [-999, (0, 0)]
        self.index = index
        self.z_order = data["zOrder"] if "zOrder" in data else 0
        self.father_line: Line | None = None
        self.father = data["father"] if "zOrder" in data else -1
        if data["Texture"] != "line.png":
            self.texture = texture_id[data["Texture"]]
        else:
            self.texture = None
        data["eventLayers"] = list(filter(lambda x: x is not None, data["eventLayers"]))

        self.speed_events = [layer["speedEvents"] for layer in data["eventLayers"] if "speedEvents" in layer]
        self.x_events = [layer["moveXEvents"] for layer in data["eventLayers"] if "moveXEvents" in layer]
        self.y_events = [layer["moveYEvents"] for layer in data["eventLayers"] if "moveYEvents" in layer]
        self.x_scale_events = (data["extended"]["scaleXEvents"] if "scaleXEvents" in data["extended"] else []) if "extended" in data else []
        self.y_scale_events = (data["extended"]["scaleYEvents"] if "scaleYEvents" in data["extended"] else []) if "extended" in data else []
        self.text_events = (data["extended"]["textEvents"] if "textEvents" in data["extended"] else []) if "extended" in data else []
        self.color_events = (data["extended"]["colorEvents"] if "colorEvents" in data["extended"] else []) if "extended" in data else []
        self.rotate_events = [layer["rotateEvents"] for layer in data["eventLayers"] if "rotateEvents" in layer]
        self.alpha_events = [layer["alphaEvents"] for layer in data["eventLayers"] if "alphaEvents" in layer]

        self.x_events = [list(map(lambda x: init_move_x_events(x, bpm_list, i, self.father), l)) for i, l in enumerate(self.x_events)]
        self.y_events = [list(map(lambda x: init_move_y_events(x, bpm_list, i, self.father), l)) for i, l in enumerate(self.y_events)]
        self.rotate_events = [list(map(lambda x: init_events(x, bpm_list), l)) for l in self.rotate_events]
        self.alpha_events = [list(map(lambda x: init_events(x, bpm_list), l)) for l in self.alpha_events]
        self.x_scale_events = list(map(lambda x: init_events(x, bpm_list), self.x_scale_events))
        self.y_scale_events = list(map(lambda x: init_events(x, bpm_list), self.y_scale_events))
        self.color_events = list(map(lambda x: init_color_events(x, bpm_list), self.color_events))
        self.text_events = list(map(lambda x: init_events(x, bpm_list), self.text_events))

        self.speed_events = [list(map(lambda x: init_events(x, bpm_list), l)) for l in self.speed_events]
        self.x_events = [fill_events(e, default=e[0]["start"]) for e in self.x_events]
        self.y_events = [fill_events(e, default=e[0]["start"]) for e in self.y_events]
        self.rotate_events = [fill_events(e) for e in self.rotate_events]
        self.alpha_events = [fill_events(e) for e in self.alpha_events]
        self.speed_events = [fill_events(e, is_speed=True) for e in self.speed_events][0] if self.speed_events else []
        self.speed_events = init_speed_event(self.speed_events)
        self.x_scale_events = fill_events(self.x_scale_events, default=1)
        self.y_scale_events = fill_events(self.y_scale_events, default=1)
        self.color_events = fill_events(self.color_events, default=[-1, -1, -1])
        self.text_events = fill_events(self.text_events, default=None)

        note_datas = [init_note(self.speed_events, n, bpm_list) for n in data["notes"]] if "notes" in data else []
        hold_datas = list(filter(lambda x: x["type"] == 2, note_datas))
        note_datas = list(filter(lambda x: x["type"] != 2, note_datas))

        self.above_notes = [Note(n) for n in list(filter(lambda x: not x["above"]-1, note_datas))]
        self.below_notes = [Note(n) for n in list(filter(lambda x: x["above"]-1, note_datas))]

        self.above_holds = [Note(n) for n in list(filter(lambda x: not x["above"]-1, hold_datas))]
        self.below_holds = [Note(n) for n in list(filter(lambda x: x["above"]-1, hold_datas))]

        self.above_notes = exe_notes(self.above_notes)
        self.below_notes = exe_notes(self.below_notes)
        self.above_holds = exe_notes(self.above_holds)
        self.below_holds = exe_notes(self.below_holds)

        self.x = sum([l[0]["start"] for l in self.x_events if l])
        self.y = sum([l[0]["start"] for l in self.y_events if l])
        self.r = -sum([l[0]["start"] for l in self.rotate_events if l])
        self.a = sum([l[0]["start"] for l in self.alpha_events if l])/255
        self.x_scale = self.x_scale_events[0]["start"]
        self.y_scale = self.y_scale_events[0]["start"]
        self.text = self.text_events[0]["start"]
        self.last_text = self.text_events[0]["start"]
        self.text_texture, self.text_w, self.text_h = get_text_texture_id(self.text, UI_FONT, 52) if self.text is not None else [None for _ in range(3)]
        self.color = self.color_events[0]["start"]
        self.ui = data["attachUI"] if "attachUI" in data else ""
        self.hx_list = []


    def get_pos(self, time):
        if time == self.cache[0]:
            return self.cache[1]
        else:
            pos = (get_event_layer_value(self.x_events, time), get_event_layer_value(self.y_events, time))
            if self.father_line is not None:
                father_pos = self.father_line.get_pos(time)
                father_rotate = get_event_layer_value(self.father_line.rotate_events, time)
                posabsValue = getLineLength(*pos, 0.0, 0.0)
                possitaValue = math.degrees(math.atan2(*pos)) + father_rotate
                pos = list(map(lambda v1, v2: v1 + v2, father_pos, rotate_point(0.0, 0.0, 90 - possitaValue, posabsValue)))
            self.cache = [time, pos]
            return pos


    def calc(self, time):
        self.a = get_event_layer_value(self.alpha_events, time) / 255
        if self.a > 0 or (self.above_notes or self.below_notes) or (self.above_holds or self.below_holds):
            self.x, self.y = self.get_pos(time)
            self.r = -get_event_layer_value(self.rotate_events, time)
            self.x_scale = get_event_value(self.x_scale_events, time)
            self.y_scale = get_event_value(self.y_scale_events, time)
            self.color = get_color(self.color_events, time)
            self.text = get_text(self.text_events, time)
        if self.above_notes or self.below_notes or self.above_holds or self.below_holds:
            self.floor_position = get_fp(self.speed_events, time)

    def draw(self):
        if self.a > 0 and not self.ui:
            if self.text is not None:
                if self.last_text != self.text:
                    glDeleteTextures(1, [self.text_texture])
                    self.text_texture, self.text_w, self.text_h = get_text_texture_id(self.text, CMDYSJ_FONT, 52)
                    self.last_text = self.text
                draw_image_center_alpha_ex(self.x, self.y, self.r, self.a,
                                           self.color if -1 not in self.color else (1, 1, 1), 1, self.text_texture,
                                           self.text_w * to_sx(self.x_scale), self.text_h * to_sx(self.y_scale), True)
            elif self.texture is None:
                draw_line_ex(self.x, self.y, self.r, self.a, LINE_WIDTH*self.y_scale, WINDOW_WIDTH*3*self.x_scale, self.color if -1 not in self.color else (1, 1, 0.6))
            else:
                draw_image_center_alpha_ex(self.x, self.y, self.r, self.a, self.color if -1 not in self.color else (1, 1, 1), 1, self.texture[0], self.texture[1]*to_sx(self.x_scale), self.texture[2]*to_sx(self.y_scale))


    def draw_notes(self, time):
        for notes in self.above_notes:
            for n in notes[:]:
                if n.update(self.x, self.y, self.r, time, self.floor_position, 1, self.a):
                    break
                if n.hx and not n.is_fake:
                    self.hx_list.append(HE(self.x, self.y, self.r, n.pos_x, time, color=const.config["perfect_color"]))
                if n.click:
                    notes.remove(n)

        for notes in self.below_notes:
            for n in notes[:]:
                if n.update(self.x, self.y, self.r, time, self.floor_position, 0, self.a):
                    break
                if n.hx and not n.is_fake:
                    self.hx_list.append(HE(self.x, self.y, self.r, n.pos_x, time, color=const.config["perfect_color"]))
                if n.click:
                    notes.remove(n)

    def draw_holds(self, time, delta, bpm):
        dis = 30/bpm
        for notes in self.above_holds:
            for n in notes[:]:
                if n.update(self.x, self.y, self.r, time, self.floor_position, 1, self.a):
                    break
                if n.hx and not n.is_fake:
                    n.timer += delta
                    if n.timer >= dis:
                        self.hx_list.append(HE(self.x, self.y, self.r, n.pos_x, time, color=const.config["perfect_color"]))
                        n.timer = 0
                if n.click:
                    notes.remove(n)

        for notes in self.below_holds:
            for n in notes[:]:
                if n.update(self.x, self.y, self.r, time, self.floor_position, 0, self.a):
                    break
                if n.hx and not n.is_fake:
                    n.timer += delta
                    if n.timer >= dis:
                        self.hx_list.append(HE(self.x, self.y, self.r, n.pos_x, time, color=const.config["perfect_color"]))
                        n.timer = 0
                if n.click:
                    notes.remove(n)

    def draw_he(self, time):
        for he in self.hx_list[:]:
            he.draw(time)
            if he.over:
                self.hx_list.remove(he)

    def set_lines(self, lines: list):
        self.father_line = lines[self.father] if self.father != -1 else None



def is_intersection(midpoint, angle, width, height):
    x_mid, y_mid = midpoint
    if angle == 90 or angle == 270:
        return 0 <= x_mid <= width
    if angle == 0 or angle == 180:
        return 0 <= y_mid <= height
    slope = math.tan(angle)
    intercept = y_mid - slope * x_mid
    y_left = slope * 0 + intercept
    y_right = slope * width + intercept
    x_bottom = (0 - intercept) / slope
    x_top = (height - intercept) / slope
    return (0 <= y_left <= height) or (0 <= y_right <= height) or (0 <= x_bottom <= width) or (0 <= x_top <= width)


class Note:
    def __init__(self, data):
        self.r = 0
        self.fp = data["fp"]
        self.end_fp = data["end_fp"]
        self.type = data["type"]-1
        self.time = data["startTime"]
        self.end_time = data["endTime"]
        self.size = data["size"]
        self.is_fake = data["isFake"]
        self.pos_x = data["positionX"]
        self.speed = data["speed"]
        self.visible_time = data["visibleTime"]
        self.y_offset = data["yOffset"]
        self.above = data["above"]
        self.alpha = data["alpha"]
        self.x, self.y = 0, 0
        self.visible = False
        self.near_mid = False
        self.click = False
        self.judging = False
        self.hx = False
        self.timer = 99999999999


    def away_to_mid(self, cfp, r):
        fp_add_one = rotate_point(self.x, self.y, r+90, cfp+1)
        return getLineLength(*fp_add_one, *WINDOW_MID) - getLineLength(self.x, self.y, *WINDOW_MID) > 0

    def update(self, x, y, r, time, cfp, abv, a):
        if time >= self.time:
            self.hx = True
            if not self.is_fake and not self.judging:
                NOTE_SOUNDS[self.type].play()
                self.judging = True
            if self.type != 1:
                self.click = True
                return
            elif time > self.end_time:
                self.click = True
                return
        if time < self.time:
            no_below_r = r
            r += 0 if abv else 180
            radians = math.radians(r)
            fp = (self.fp - cfp)*self.speed
            if fp >= -0.0 and self.time <= time + self.visible_time:
                self.x, self.y = rotate_point(x, y, r+90, fp)
                self.x, self.y = rotate_point(self.x, self.y, no_below_r, self.pos_x)
                if self.away_to_mid(fp, r) and not is_intersection((self.x,self.y),radians, *WINDOW_SIZE):
                    return True
                if a >= 0:
                    if self.type != 1:
                        draw_image_center_alpha_ex(self.x, self.y, r, self.alpha, [1, 1, 1], 0.1, NOTE_TEXTURES[self.type][0], NOTE_TEXTURES[self.type][1]*self.size, NOTE_TEXTURES[self.type][2])
                    else:
                        end = (self.end_fp - cfp) * self.speed
                        end_x, end_y = rotate_point(x, y, r+90, end)
                        end_x, end_y = rotate_point(end_x, end_y, no_below_r, self.pos_x)
                        draw_image_top_ex(self.x, self.y, r-180, 0.1, NOTE_TEXTURES[self.type][0], NOTE_TEXTURES[self.type][1]*self.size, NOTE_TEXTURES[self.type][2], self.alpha)
                        draw_image_bottom_ex(end_x, end_y, r-180, 0.1, NOTE_TEXTURES[5][0],
                                          NOTE_TEXTURES[5][1] * self.size, NOTE_TEXTURES[5][2],
                                          self.alpha)
                        length = (self.end_fp-self.fp)*self.speed*10
                        if length > 0:
                            draw_image_bottom_ex(self.x, self.y, r-180,0.1, NOTE_TEXTURES[4][0], NOTE_TEXTURES[4][1]*self.size, length, self.alpha)
        elif self.type == 1:
            no_below_r = r
            r += 0 if abv else 180
            end = (self.end_fp - cfp)*self.speed
            end_x, end_y = rotate_point(x, y, r + 90, end)
            end_x, end_y = rotate_point(end_x, end_y, no_below_r, self.pos_x)
            body_x, body_y = rotate_point(x, y, no_below_r, self.pos_x)
            draw_image_bottom_ex(end_x, end_y, r - 180, 0.1, NOTE_TEXTURES[5][0],
                                 NOTE_TEXTURES[5][1] * self.size, NOTE_TEXTURES[5][2],
                                 self.alpha)
            draw_image_bottom_ex(body_x, body_y, r-180, 0.1, NOTE_TEXTURES[4][0], NOTE_TEXTURES[4][1]*self.size, end*10, self.alpha)
        return False

HE_size = 20*X_SCALE*const.config["note_size"]
cubic = lambda x: 1-math.pow(1-x, 3)

class HE:
    def __init__(self, x, y, r, xpos, time, _type:int=0, color: tuple[float, float, float]=(1., 0.88, 0.66)):
        self.type = _type
        self.xpos = xpos
        ra = math.radians(r)
        self.x = x + self.xpos*math.cos(ra)
        self.y = y + self.xpos*math.sin(ra)
        self.time = time
        self.over = False
        self.color = color
        if self.type != 0:
            self.distance = random.randint(150, 200)*X_SCALE*const.config["note_size"]
            self.angle = math.radians(random.randint(0, 360))
            self.a = 1
            self._cos = math.cos(self.angle)
            self._sin = math.sin(self.angle)
        else:
            self.cubes = [HE(x, y, r, xpos, time, 1, color=color) for _ in range(4)]

    def draw(self, _time):
        process = _time - self.time
        if process > 0.5:
            self.over = True
            return
        if self.type == 0:
            index = math.floor(process*60) if process<0.5 else 29
            draw_image_center_ex(self.x, self.y, 0, 0.65, *HE_TEXTURES[index], color=self.color)
            for i in self.cubes:
                i.draw(_time)
        else:
            process = process*2
            easing_process = cubic(process)
            real_distance = self.distance*easing_process
            x = self.x + real_distance*self._cos
            y = self.y + real_distance*self._sin
            if process >= 0.5:
                self.a = 1-(process-0.5)*2
            draw_quad_center_ex(x, y, HE_size, HE_size, (*self.color, self.a))