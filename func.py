import math
import sys

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

def get_texture_id_from_pygame_surface(surface: pygame.Surface) -> tuple[int, int, int]:
    texture_id = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture_id)
    img_data = pygame.image.tobytes(surface, "RGBA", True)
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

def draw_image_left_top(x: float, y: float, tex_id: int, width:float, height:float):
    glColor4f(1., 1., 1., 1.)
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

def draw_image_left_bottom(x: float, y: float, tex_id: int, width:float, height:float):
    glColor4f(1., 1., 1., 1.)
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

def draw_image_right_bottom(x: float, y: float, tex_id: int, width:float, height:float):
    glColor4f(1., 1., 1., 1.)
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

def draw_image_right_top(x: float, y: float, tex_id: int, width:float, height:float):
    glColor4f(1., 1., 1., 1.)
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

def draw_image_center(x: float, y: float, tex_id: int, width:float, height:float):
    width *= 0.5
    height *= 0.5
    glColor4f(1., 1., 1., 1.)
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

def draw_image_center_ex(x: float, y: float, angle: float, scale:float, tex_id: int, width:float, height:float):
    width *= 0.5*scale
    height *= 0.5*scale
    glColor4f(1., 1., 1., 1.)
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
    glVertex2f(width, height)
    glTexCoord2f(0, 1)
    glVertex2f(-width, height)
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
    glTexCoord2f(0, 0)
    glVertex2f(-width, -height)
    glTexCoord2f(1, 0)
    glVertex2f(width, -height)
    glTexCoord2f(1, 1)
    glVertex2f(width, height)
    glTexCoord2f(0, 1)
    glVertex2f(-width, height)
    glEnd()
    glPopMatrix()

def draw_image_top_ex(x: float, y: float, angle: float, scale:float, tex_id: int, width:float, height:float):
    width *= 0.5*scale
    height *= scale
    glColor4f(1., 1., 1., 1.)
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

def draw_image_left_top_ex(x: float, y: float, angle: float, scale:float, tex_id: int, width:float, height:float):
    width *= scale
    height *= scale
    glColor4f(1., 1., 1., 1.)
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

def draw_image_bottom_ex(x: float, y: float, angle: float, scale:float, tex_id: int, width:float, height:float):
    width *= 0.5*scale
    height *= scale
    glColor4f(1., 1., 1., 1.)
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
    radian = math.radians(angle)
    start_x = x+length*math.cos(radian)
    start_y = y+length*math.sin(radian)
    end_x = x-length*math.cos(radian)
    end_y = y-length*math.sin(radian)
    glColor4f(*color, alpha)
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(start_x, start_y)
    glVertex2f(end_x, end_y)
    glEnd()

def get_text_texture_id(text: str, font_path: str, font_size: int) -> tuple[int, int, int]:
    font = pygame.font.Font(font_path, font_size)
    text = font.render(text, True, (255, 255, 255))
    del font
    return get_texture_id_from_pygame_surface(text)
