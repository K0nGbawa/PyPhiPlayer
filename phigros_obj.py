import math
import random

import pygame
from OpenGL.GL import glColor4f
from OpenGL.GL import *
from PIL import Image

from playsound import DirectSound, open_audio

from const import WINDOW_WIDTH, WINDOW_HEIGHT, X, Y, X_SCALE
from func import phi_time2second, linear, draw_line_ex, draw_image_center_ex, get_texture_id, draw_image_top_ex, \
    draw_image_bottom_ex, draw_quad_center_ex, draw_quad_center_ex
from logger import *

cubic = lambda x: 1-math.pow(1-x, 3)

try:
    NOTE_TEXTURES: tuple = (get_texture_id(Image.open("./resources/textures/Tap.png")),
                            get_texture_id(Image.open("./resources/textures/Drag.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_Head.png")),
                            get_texture_id(Image.open("./resources/textures/Flick.png")),
                            get_texture_id(Image.open("./resources/textures/Hold.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_End.png")),
                            get_texture_id(Image.open("./resources/textures/TapHL.png")),
                            get_texture_id(Image.open("./resources/textures/DragHL.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_HeadHL.png")),
                            get_texture_id(Image.open("./resources/textures/FlickHL.png")),
                            get_texture_id(Image.open("./resources/textures/Hold_Body_HL.png")),
                            )
    NOTE_SOUNDS: tuple = (
        open_audio("./resources/sounds/tap.wav"),
        open_audio("./resources/sounds/drag.wav"),
        open_audio("./resources/sounds/tap.wav"),
        open_audio("./resources/sounds/flick.wav")
    )
    HE_TEXTURES: tuple = tuple([get_texture_id(Image.open(f"./resources/textures/HX/{i+1}.png")) for i in range(30)])
    NOTE_TEXTURES = tuple([(i[0], i[1]*X_SCALE, i[2] if index == 5 or index == 11 else i[2]*X_SCALE) for index, i in enumerate(NOTE_TEXTURES)])
    HE_TEXTURES = tuple([(i[0], i[1]*X_SCALE, i[2]*X_SCALE) for index, i in enumerate(HE_TEXTURES)])
except (TypeError, FileNotFoundError) as e:
    error(f"资源缺失：{e}")
    __import__("time").sleep(1)
    pygame.quit()
    quit()

def init_event(events: list):
    if events[0]["startTime"] != -999999:
        events[0]["startTime"] = -999999
    if events[-1]["endTime"] != 1000000000:
        events[-1]["endTime"] = 1000000000
    return events

def init_speed_event(events: list):
    for i in events:
        if i["startTime"] != 0 and i["endTime"] >= 0:
            i["startTime"] = 0
        elif i["startTime"] >= 0:
            break
        else:
            events.remove(i)
    if events[-1]["endTime"] != 1000000000:
        events[-1]["endTime"] = 1000000000
    return events

def convert_event_ex(event: dict, T: float):
    event["startTime"] = phi_time2second(event["startTime"], T)
    event["endTime"] = phi_time2second(event["endTime"], T)
    event["start"] *= WINDOW_WIDTH
    event["start2"] *= WINDOW_HEIGHT
    event["end"] *= WINDOW_WIDTH
    event["end2"] *= WINDOW_HEIGHT
    return event

def convert_event(event: dict, T: float):
    event["startTime"] = phi_time2second(event["startTime"], T)
    event["endTime"] = phi_time2second(event["endTime"], T)
    return event

def get_event_value(events: list[dict], index: int, time: float):
    executing_event = events[index]
    if time < executing_event["endTime"]:
        return linear(
            executing_event["startTime"],
            executing_event["endTime"],
            time,
            executing_event["start"],
            executing_event["end"]
            ), index
    else:
        return get_event_value(events, index+1, time)

def get_event_value_ex(events: list[dict], index: int, time: float):
    executing_event = events[index]
    if time < executing_event["endTime"]:
        return (linear(
                    executing_event["startTime"],
                    executing_event["endTime"],
                    time,
                    executing_event["start"],
                    executing_event["end"]
                    ),
                linear(
                    executing_event["startTime"],
                    executing_event["endTime"],
                    time,
                    executing_event["start2"],
                    executing_event["end2"]
                    ),
                index)
    else:
        return get_event_value_ex(events, index+1, time)

def convert_note(data: dict, T:float) -> dict:
    data["time"] = phi_time2second(data["time"], T)
    data["holdTime"] = phi_time2second(data["holdTime"], T)
    return data

def calc_note_position(fp: float, xpos: float, x: float, y: float, r:float, dire:int, speed: float) -> tuple[float, float]:
    r = math.radians(r)
    r_90 = r + (math.pi / 2) * dire
    x = x + fp * math.cos(r_90) * Y * speed + xpos * math.cos(r) * X
    y = y + fp * math.sin(r_90) * Y * speed + xpos * math.sin(r) * X
    return x, y

class Line:
    def __init__(self, data: dict):
        self.delta = 0
        self.bpm = data["bpm"]
        self.HE_dis = 30/self.bpm
        self.T = 1.875 / self.bpm
        self.move_events = init_event(list(map(lambda x: convert_event_ex(x, self.T), data["judgeLineMoveEvents"])))
        self.rotate_events = init_event(list(map(lambda x: convert_event(x, self.T), data["judgeLineRotateEvents"])))
        self.alpha_events = init_event(list(map(lambda x: convert_event(x, self.T), data["judgeLineDisappearEvents"])))
        self.speed_events = init_speed_event(list(map(lambda x: convert_event(x, self.T), data["speedEvents"])))
        self.me_index = 0
        self.re_index = 0
        self.ae_index = 0
        self.x, self.y, self.me_index = get_event_value_ex(self.move_events, 0, 0)
        self.a, self.ae_index = get_event_value(self.alpha_events, 0, 0)
        self.r, self.re_index = get_event_value(self.rotate_events, 0, 0)
        self.above_notes = [Note(convert_note(note, self.T), 1) for note in sorted(data["notesAbove"], key=lambda x: x["time"])]
        self.below_notes = [Note(convert_note(note, self.T), -1) for note in sorted(data["notesBelow"], key=lambda x: x["time"])]
        self.above_holds = []
        self.above_note_index = 0
        self.below_note_index = 0
        self.current_floor_position = 0
        self.HE = []
        self.combo = 0
        self.perfect = 0

    def calc(self, time, delta):
        self.x, self.y, self.me_index = get_event_value_ex(self.move_events, self.me_index, time)
        self.a, self.ae_index = get_event_value(self.alpha_events, self.ae_index, time)
        self.r, self.re_index = get_event_value(self.rotate_events, self.re_index, time)
        self.current_floor_position = self.calc_current_floor_position(time)
        self.delta = delta

    def draw_HE(self, time):
        for he in self.HE[:]:
            he.draw(time)
            if he.over:
                self.HE.remove(he)

    def draw(self):
        if self.a > 0:
            draw_line_ex(self.x, self.y, self.r, self.a, 5, 4000, (1, 1, 0.66))

    def calc_current_floor_position(self, time):
        fp = 0
        for event in self.speed_events:
            if time > event["endTime"]:
                fp += event["value"] * (event["endTime"] - event["startTime"])
            elif time > event["startTime"]:
                fp += event["value"] * (time - event["startTime"])
                break
        return fp

    def draw_notes(self, time):
        for index, note in enumerate(self.above_notes):
            if note.floor_position - self.current_floor_position > 3.666667:
                break
            judged = note.draw(self.x, self.y, self.r, self.current_floor_position, time)
            if note.judge:
                if note.type == 2:
                    note.timer += self.delta
                    if note.timer >= self.HE_dis:
                        self.HE.append(HE(self.x, self.y, self.r, note.xPosition, time))
                        note.timer = 0
                else:
                    self.HE.append(HE(self.x, self.y, self.r, note.xPosition, time))
            if judged:
                self.combo += 1
                self.perfect += 1
        for index, note in enumerate(self.below_notes):
            if note.floor_position - self.current_floor_position > 3.666667:
                break
            judged = note.draw(self.x, self.y, self.r, self.current_floor_position, time)
            if note.judge:
                if note.type == 2:
                    note.timer += self.delta
                    if note.timer >= self.HE_dis:
                        self.HE.append(HE(self.x, self.y, self.r, note.xPosition, time))
                        note.timer = 0
                else:
                    self.HE.append(HE(self.x, self.y, self.r, note.xPosition, time))
            if judged:
                self.combo += 1
                self.perfect += 1
        self.above_notes = list(filter(lambda n: not n.judged, self.above_notes))
        self.below_notes = list(filter(lambda n: not n.judged, self.below_notes))

    def get_combo(self):
        tmp = self.combo
        self.combo = 0
        return tmp


class Note:
    def __init__(self, data: dict, dire:int):
        self.judge = False
        if "HX" in data:
            self.HX = data["HX"]
        self.judge_time = data["time"]
        self.judged = False
        self.type = data["type"]-1
        self.hold_time = data["holdTime"]
        self.end_time = self.judge_time+self.hold_time
        self.floor_position = data["floorPosition"]
        self.current_fp = self.floor_position
        self.xPosition = data["positionX"]
        self.speed = data["speed"]
        self.x = 999
        self.y = 999
        self.dire = dire
        self.r_offset = 180*-(self.dire+1)/2
        self.timer = 1000000
        self.hold_len = self.hold_time * self.speed * Y

    def draw(self, x: float, y: float, r: float, current_fp: float, time: float):
        self.current_fp = (self.floor_position - current_fp) if self.type != 2 or time < self.judge_time else 0
        if self.current_fp >= -0.001:
            if self.type == 2 and self.speed > 0 and self.end_time > time:
                self.x, self.y = calc_note_position(self.current_fp if self.judge_time > time else 0, self.xPosition, x, y,
                                                    r, self.dire, 1)
                if time < self.judge_time:
                    hold_len = self.hold_len
                    draw_image_top_ex(self.x, self.y, r+self.r_offset, 0.1, *self.get_texture())
                else:
                    hold_len = (self.end_time - time) * self.speed * Y
                r_90 = math.radians(r) + math.pi/2
                _cos = hold_len*math.cos(r_90)*self.dire
                _sin = hold_len*math.sin(r_90)*self.dire
                draw_image_center_ex(self.x+_cos/2, self.y+_sin/2, r+self.r_offset, 1, NOTE_TEXTURES[4+self.HX*6][0], NOTE_TEXTURES[4+self.HX*6][1]*.1, hold_len)
                draw_image_bottom_ex(self.x+_cos, self.y+_sin, r+self.r_offset, 0.1, *NOTE_TEXTURES[5])
            elif self.type != 2:
                self.x, self.y = calc_note_position(self.current_fp, self.xPosition, x, y, r, self.dire, self.speed)
                draw_image_center_ex(self.x, self.y, r+self.r_offset, 0.1, *self.get_texture())
        if time >= self.judge_time and not self.judge:
            NOTE_SOUNDS[self.type].play()
            self.judge = True
            self.judged = self.type != 2
            return self.judged
        elif time > self.end_time:
            self.judged = True
            return True
        else:
            return False
    def get_texture(self): return NOTE_TEXTURES[self.type] if not self.HX else NOTE_TEXTURES[self.type + 6]

HE_size = 20*X_SCALE

class HE:
    def __init__(self, x, y, r, xpos, time, _type:int=0):
        self.type = _type
        self.xpos = xpos*X
        ra = math.radians(r)
        self.x = x + self.xpos*math.cos(ra)
        self.y = y + self.xpos*math.sin(ra)
        self.time = time
        self.over = False
        if self.type != 0:
            self.distance = random.randint(150, 200)*X_SCALE
            self.angle = math.radians(random.randint(0, 360))
            self.a = 1
            self._cos = math.cos(self.angle)
            self._sin = math.sin(self.angle)
        else:
            self.cubes = [HE(x, y, r, xpos, time, 1) for _ in range(4)]

    def draw(self, time):
        process = time - self.time
        if process > 0.5:
            self.over = True
            return
        if self.type == 0:
            index = math.floor(process*60) if process<0.5 else 29
            draw_image_center_ex(self.x, self.y, 0, 0.65, *HE_TEXTURES[index])
            for i in self.cubes:
                i.draw(time)
        else:
            process = process*2
            easing_process = cubic(process)
            real_distance = self.distance*easing_process
            x = self.x + real_distance*self._cos
            y = self.y + real_distance*self._sin
            if process >= 0.5:
                self.a = 1-(process-0.5)*2
            draw_quad_center_ex(x, y, HE_size, HE_size, (1, 0.88, 0.66, self.a))


