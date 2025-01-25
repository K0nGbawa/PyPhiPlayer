import math
import sys
import typing
from typing import Callable

import pygame.font
from OpenGL.GL import *
from PIL import Image, ImageFilter, ImageEnhance
from pydub import AudioSegment
from const import *
def get_texture_id(img: Image.Image) -> tuple[int, int, int]:
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    texture_id = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture_id)
    img_data = img.tobytes()
    img_width, img_height = img.size

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id, img_width, img_height

def get_texture_id_from_pygame_surface(surface: pygame.Surface, flip=True) -> tuple[int, int, int]:
    texture_id = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture_id)
    img_data = pygame.image.tobytes(surface, "RGBA", flip)
    img_width, img_height = surface.get_size()

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)

    return texture_id, img_width, img_height


def resize_image(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    w_percent = (target_width / float(img.size[0]))
    h_percent = (target_height / float(img.size[1]))
    if w_percent > h_percent:
        new_w = target_width
        new_h = int((float(img.size[1]) * w_percent))
    else:
        new_w = int((float(img.size[0]) * h_percent))
        new_h = target_height
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return img

def crop_image_to_window_size(img: Image.Image):
    if img.width > img.height:
        left = (img.width - WINDOW_WIDTH) // 2
        top = 0
        right = left + WINDOW_WIDTH
        bottom = img.height
    else:
        left = 0
        top = (img.height - WINDOW_HEIGHT) // 2
        right = img.width
        bottom = top + WINDOW_HEIGHT
    img = img.crop((left, top, right, bottom))
    return img

def lerp(sv, ev, x):
    return sv + (ev-sv)*x

def to_BG(img: Image.Image) -> Image.Image:
    blur = ImageFilter.GaussianBlur(75.)
    img = img.filter(blur)
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(0.6)
    img = resize_image(img, WINDOW_WIDTH, WINDOW_HEIGHT)
    img = crop_image_to_window_size(img)
    return img

def get_audio_length(file):
    audio = AudioSegment.from_file(file)
    return audio.duration_seconds

def get_argv(argv: str):
    if f"-{argv}" in sys.argv:
        value = sys.argv.index(f"-{argv}")+1
    else:
        value = input(f"{argv}: ")
    return value

def draw_image_left_top(x: float, y: float, tex_id: int, width:float, height:float, alpha=1., angle=0.):
    glColor4f(1., 1., 1., alpha)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x, y+height)
    glTexCoord2f(1, 0)
    glVertex2f(x+width, y+height)
    glTexCoord2f(1, 1)
    glVertex2f(x+width, y)
    glTexCoord2f(0, 1)
    glVertex2f(x, y)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_image_left_bottom(x: float, y: float, tex_id: int, width:float, height:float, alpha=1., angle=0.):
    glColor4f(1., 1., 1., alpha)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x, y)
    glTexCoord2f(1, 0)
    glVertex2f(x+width, y)
    glTexCoord2f(1, 1)
    glVertex2f(x+width, y+height)
    glTexCoord2f(0, 1)
    glVertex2f(x, y+height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_image_right_bottom(x: float, y: float, tex_id: int, width:float, height:float, alpha=1., angle=0.):
    glColor4f(1., 1., 1., alpha)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x-width, y)
    glTexCoord2f(1, 0)
    glVertex2f(x, y)
    glTexCoord2f(1, 1)
    glVertex2f(x, y+height)
    glTexCoord2f(0, 1)
    glVertex2f(x-width, y+height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_image_right_top(x: float, y: float, tex_id: int, width:float, height:float, alpha=1., angle=0.):
    glColor4f(1., 1., 1., alpha)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x-width, y-height)
    glTexCoord2f(1, 0)
    glVertex2f(x, y-height)
    glTexCoord2f(1, 1)
    glVertex2f(x, y)
    glTexCoord2f(0, 1)
    glVertex2f(x-width, y)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_image_center(x: float, y: float, tex_id: int, width:float, height:float, alpha=1., angle=0.):
    width *= 0.5
    height *= 0.5
    glColor4f(1., 1., 1., alpha)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x-width, y-height)
    glTexCoord2f(1, 0)
    glVertex2f(x+width, y-height)
    glTexCoord2f(1, 1)
    glVertex2f(x+width, y+height)
    glTexCoord2f(0, 1)
    glVertex2f(x-width, y+height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_image_center_ex(x: float, y: float, angle: float, scale:float, tex_id: int, width:float, height:float, color=(1,1,1), alpha=1):
    width *= 0.5*scale
    height *= 0.5*scale
    glColor4f(*color, alpha)
    glEnable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(x, y, 0.)
    glRotatef(angle, 0, 0, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(+width, -height)
    glTexCoord2f(1, 0)
    glVertex2f(-width, -height)
    glTexCoord2f(1, 1)
    glVertex2f(-width, height)
    glTexCoord2f(0, 1)
    glVertex2f(+width, height)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

def draw_image_center_alpha_ex(x: float, y: float, angle: float, alpha: float, color: list[float], scale:float, tex_id: int, width:float, height:float, flip=False):
    width *= 0.5*scale
    height *= 0.5*scale
    glColor4f(*color, alpha)
    glEnable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(x, y, 0.)
    glRotatef(angle, 0, 0, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    if flip:
        glTexCoord2f(0, 0)
        glVertex2f(-width, -height)
        glTexCoord2f(1, 0)
        glVertex2f(width, -height)
        glTexCoord2f(1, 1)
        glVertex2f(width, height)
        glTexCoord2f(0, 1)
        glVertex2f(-width, height)
    else:
        glTexCoord2f(0, 0)
        glVertex2f(-width, height)
        glTexCoord2f(1, 0)
        glVertex2f(+width, height)
        glTexCoord2f(1, 1)
        glVertex2f(+width, -height)
        glTexCoord2f(0, 1)
        glVertex2f(-width, -height)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

def draw_quad_center_ex(x: float, y: float, width:float, height:float, color: tuple[float, float, float, float]):
    width *= 0.5
    height *= 0.5
    glColor4f(*color)
    glPushMatrix()
    glTranslatef(x, y, 0.)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBegin(GL_QUADS)
    glVertex2f(-width, -height)
    glVertex2f(width, -height)
    glVertex2f(width, height)
    glVertex2f(-width, height)
    glEnd()
    glPopMatrix()

def draw_image_top_ex(x: float, y: float, angle: float, scale:float, tex_id: int, width:float, height:float, alpha=1):
    width *= 0.5*scale
    height *= scale
    glColor4f(1., 1., 1., alpha)
    glEnable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(x, y, 0.)
    glRotatef(angle, 0, 0, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(-width, 0)
    glTexCoord2f(1, 0)
    glVertex2f(width, 0)
    glTexCoord2f(1, 1)
    glVertex2f(width, height)
    glTexCoord2f(0, 1)
    glVertex2f(-width, height)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

def draw_image_left_top_ex(x: float, y: float, angle: float, scale:float, tex_id: int, width:float, height:float, alpha=1.):
    width *= scale
    height *= scale
    glColor4f(1., 1., 1., alpha)
    glEnable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(x, y, 0.)
    glRotatef(angle, 0, 0, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(0, 0)
    glTexCoord2f(1, 0)
    glVertex2f(width, 0)
    glTexCoord2f(1, 1)
    glVertex2f(width, -height)
    glTexCoord2f(0, 1)
    glVertex2f(0, -height)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

def draw_image_bottom_ex(x: float, y: float, angle: float, scale:float, tex_id: int, width:float, height:float, alpha=1):
    width *= 0.5*scale
    height *= scale
    glColor4f(1., 1., 1., alpha)
    glEnable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(x, y, 0.)
    glRotatef(angle, 0, 0, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(-width, -height)
    glTexCoord2f(1, 0)
    glVertex2f(width, -height)
    glTexCoord2f(1, 1)
    glVertex2f(width, 0)
    glTexCoord2f(0, 1)
    glVertex2f(-width, 0)
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

def phi_time2second(phi_time: int, T: float) -> float: return phi_time * T
def linear(sT: float, eT: float, nT: float, sV: float, eV: float) -> float: return sV + (nT - sT)/(eT - sT)*(eV - sV)

def draw_line_ex(x: float, y: float, angle: float, alpha: float, width: int, length, color: tuple[float, float, float]):
    length = length/2
    width = width/2
    glColor4f(*color, alpha)
    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(angle, 0, 0, 1)
    glBegin(GL_QUADS)
    glVertex2f(-length, -width)
    glVertex2f(length, -width)
    glVertex2f(length, width)
    glVertex2f(-length, width)
    glEnd()
    glPopMatrix()
    """radian = math.radians(angle)
    start_x = x+length*math.cos(radian)
    start_y = y+length*math.sin(radian)
    end_x = x-length*math.cos(radian)
    end_y = y-length*math.sin(radian)
    glColor4f(*color, alpha)
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(start_x, start_y)
    glVertex2f(end_x, end_y)
    glEnd()"""


def get_text_texture_id(text: str, font_path: str, font_size: int, flip=True) -> tuple[int, int, int]:
    font = pygame.font.Font(font_path, font_size)
    text = font.render(text, True, (255, 255, 255))
    del font
    return get_texture_id_from_pygame_surface(text, flip)

def rpe_beat_to_beat(beat: list[int, int, int]):
    return beat[0] + beat[1] / beat[2]

def rpe_beat_to_second(rpe_beat: list[int, int, int], bpm_list: list[dict]):
    rpe_beat = rpe_beat_to_beat(rpe_beat)
    return beat_to_second(rpe_beat, bpm_list)

def beat_to_second(beat: float, bpm_list: list[dict]):
    sec = 0.0
    for i, e in enumerate(bpm_list):
        bpmv = e["bpm"]
        if i != len(bpm_list) - 1:
            et_beat = bpm_list[i + 1]["startTime"] - e["startTime"]
            if beat >= et_beat:
                sec += et_beat * (60 / bpmv)
                beat -= et_beat
            else:
                sec += beat * (60 / bpmv)
                break
        else:
            sec += beat * (60 / bpmv)
    return sec

ease_funcs: list[typing.Callable[[float], float]] = [
  lambda t: t, # linear - 1
  lambda t: math.sin((t * math.pi) / 2), # out sine - 2
  lambda t: 1 - math.cos((t * math.pi) / 2), # in sine - 3
  lambda t: 1 - (1 - t) * (1 - t), # out quad - 4
  lambda t: t ** 2, # in quad - 5
  lambda t: -(math.cos(math.pi * t) - 1) / 2, # io sine - 6
  lambda t: 2 * (t ** 2) if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2, # io quad - 7
  lambda t: 1 - (1 - t) ** 3, # out cubic - 8
  lambda t: t ** 3, # in cubic - 9
  lambda t: 1 - (1 - t) ** 4, # out quart - 10
  lambda t: t ** 4, # in quart - 11
  lambda t: 4 * (t ** 3) if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2, # io cubic - 12
  lambda t: 8 * (t ** 4) if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2, # io quart - 13
  lambda t: 1 - (1 - t) ** 5, # out quint - 14
  lambda t: t ** 5, # in quint - 15
  lambda t: 1 if t == 1 else 1 - 2 ** (-10 * t), # out expo - 16
  lambda t: 0 if t == 0 else 2 ** (10 * t - 10), # in expo - 17
  lambda t: (1 - (t - 1) ** 2) ** 0.5, # out circ - 18
  lambda t: 1 - (1 - t ** 2) ** 0.5, # in circ - 19
  lambda t: 1 + 2.70158 * ((t - 1) ** 3) + 1.70158 * ((t - 1) ** 2), # out back - 20
  lambda t: 2.70158 * (t ** 3) - 1.70158 * (t ** 2), # in back - 21
  lambda t: (1 - (1 - (2 * t) ** 2) ** 0.5) / 2 if t < 0.5 else (((1 - (-2 * t + 2) ** 2) ** 0.5) + 1) / 2, # io circ - 22
  lambda t: ((2 * t) ** 2 * ((2.5949095 + 1) * 2 * t - 2.5949095)) / 2 if t < 0.5 else ((2 * t - 2) ** 2 * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) / 2, # io back - 23
  lambda t: 0 if t == 0 else (1 if t == 1 else 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1), # out elastic - 24
  lambda t: 0 if t == 0 else (1 if t == 1 else - 2 ** (10 * t - 10) * math.sin((t * 10 - 10.75) * (2 * math.pi / 3))), # in elastic - 25
  lambda t: 7.5625 * (t ** 2) if (t < 1 / 2.75) else (7.5625 * (t - (1.5 / 2.75)) * (t - (1.5 / 2.75)) + 0.75 if (t < 2 / 2.75) else (7.5625 * (t - (2.25 / 2.75)) * (t - (2.25 / 2.75)) + 0.9375 if (t < 2.5 / 2.75) else (7.5625 * (t - (2.625 / 2.75)) * (t - (2.625 / 2.75)) + 0.984375))), # out bounce - 26
  lambda t: 1 - (7.5625 * ((1 - t) ** 2) if ((1 - t) < 1 / 2.75) else (7.5625 * ((1 - t) - (1.5 / 2.75)) * ((1 - t) - (1.5 / 2.75)) + 0.75 if ((1 - t) < 2 / 2.75) else (7.5625 * ((1 - t) - (2.25 / 2.75)) * ((1 - t) - (2.25 / 2.75)) + 0.9375 if ((1 - t) < 2.5 / 2.75) else (7.5625 * ((1 - t) - (2.625 / 2.75)) * ((1 - t) - (2.625 / 2.75)) + 0.984375)))), # in bounce - 27
  lambda t: (1 - (7.5625 * ((1 - 2 * t) ** 2) if ((1 - 2 * t) < 1 / 2.75) else (7.5625 * ((1 - 2 * t) - (1.5 / 2.75)) * ((1 - 2 * t) - (1.5 / 2.75)) + 0.75 if ((1 - 2 * t) < 2 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.25 / 2.75)) * ((1 - 2 * t) - (2.25 / 2.75)) + 0.9375 if ((1 - 2 * t) < 2.5 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.625 / 2.75)) * ((1 - 2 * t) - (2.625 / 2.75)) + 0.984375))))) / 2 if t < 0.5 else (1 +(7.5625 * ((2 * t - 1) ** 2) if ((2 * t - 1) < 1 / 2.75) else (7.5625 * ((2 * t - 1) - (1.5 / 2.75)) * ((2 * t - 1) - (1.5 / 2.75)) + 0.75 if ((2 * t - 1) < 2 / 2.75) else (7.5625 * ((2 * t - 1) - (2.25 / 2.75)) * ((2 * t - 1) - (2.25 / 2.75)) + 0.9375 if ((2 * t - 1) < 2.5 / 2.75) else (7.5625 * ((2 * t - 1) - (2.625 / 2.75)) * ((2 * t - 1) - (2.625 / 2.75)) + 0.984375))))) / 2, # io bounce - 28
  lambda t: 0 if t == 0 else (1 if t == 0 else (-2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 if t < 0.5 else (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 + 1) # io elastic - 29
]

def get_ease(t: int) -> typing.Callable[[float], float]:
    return ease_funcs[t-1]

def tween_execute(st: float, et: float, t: float, sv: float, ev: float, ease: int) -> float:
    return get_ease(ease)((t - st) / ((et if et > st else st + 0.001) - st)) * (ev - sv) + sv

def rpe_y_to_window_y(y: float, i, f):
    return (y/900+0.5)*WINDOW_HEIGHT if i == 0 and f == -1 else y/900*WINDOW_HEIGHT

def rpe_x_to_window_x(x: float, i, f):
    return (x/1350+0.5)*WINDOW_WIDTH if i == 0 and f == -1 else x/1350*WINDOW_WIDTH

def tween_color(st: float, et: float, t: float, sv: list[float], ev: list[float], ease: int) -> list[float]:
    return [get_ease(ease)((t - st) / ((et if et > st else st + 0.001) - st)) * (ev[i] - sv_) + sv_ for i, sv_ in enumerate(sv)]

def tween_text(st: float, et: float, t: float, sv: str, ev: str, ease: int):
    if not (sv is None or ev is None):
        if sv == ev:
            return sv.replace("%P%", "")
        if "%P%" in sv and "%P%" in ev:
            sv, ev = sv.replace("%P%", ""), ev.replace("%P%", "")
            try: sv, ev = float(sv), float(ev)
            except ValueError: return "0"
            result = (ev - sv) * get_ease(ease)((t - st) / ((et - st) if et > st else 0.001)) + sv
            return f"{int(result)}" if int(sv) == sv or int(ev) == ev else f"{result:.3f}"
        elif not sv and not ev: return ""
        elif ev.startswith(sv):
            index = int((len(ev) - len(sv)) * get_ease(ease)((t - st) / ((et - st) if et > st else 0.001))) + len(sv) - 1
            return ev[:index]
        elif sv.startswith(ev):
            index = int((len(sv) - len(ev)) * get_ease(ease)((t - st) / ((et - st) if et > st else 0.001))) + len(ev) - 1
            return sv[:index]

