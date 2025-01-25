from func import *
from const import *
from PIL import Image


class UI:
    def __init__(self, _name: str, level: str, length: float):
        self.combo = 0
        self.score = 0.
        self.name = get_text_texture_id(_name, UI_FONT, int(25*X_SCALE))
        self.level = get_text_texture_id(level, UI_FONT, int(25*X_SCALE))
        self.name_pos = (20*X_SCALE, 15*Y_SCALE)
        self.level_pos = (WINDOW_WIDTH-20*X_SCALE, 15*Y_SCALE)
        self.score_num = get_text_texture_id(str(round(self.score)).zfill(7), UI_FONT, int(30*X_SCALE))
        self.score_pos = (WINDOW_WIDTH-20*X_SCALE, WINDOW_HEIGHT-15*Y_SCALE)
        self.combo_num = get_text_texture_id(str(self.combo), UI_FONT, int(40*X_SCALE))
        self.combo_label = get_text_texture_id(config["combo_label"], UI_FONT, int(15*X_SCALE))
        self.combo_label_pos = (WINDOW_WIDTH/2, WINDOW_HEIGHT-60*Y_SCALE)
        self.combo_pos = (WINDOW_WIDTH/2, WINDOW_HEIGHT-30*Y_SCALE)
        self.pause = get_texture_id(Image.open("./resources/textures/Pause.png"))
        self.pause = (self.pause[0], self.pause[1]*X_SCALE, self.pause[2]*X_SCALE)
        self.pause_pos = (20*X_SCALE, WINDOW_HEIGHT-20*Y_SCALE)
        self.length = length

    def draw_ui(self, time):
        process = (time / self.length) * WINDOW_WIDTH
        draw_line_ex(process/2, WINDOW_HEIGHT-2.5*Y_SCALE, 0, 0.88, 5*Y_SCALE, process, (0.66, 0.66, 0.66))
        draw_line_ex(process+1*X_SCALE, WINDOW_HEIGHT-2.5*Y_SCALE, 0, 1, 5*Y_SCALE, 2*X_SCALE, (1, 1, 1))
        draw_image_left_bottom(*self.name_pos, *self.name)
        draw_image_right_bottom(*self.level_pos, *self.level)
        draw_image_right_top(*self.score_pos, *self.score_num)
        draw_image_left_top_ex(*self.pause_pos, 0, .12, *self.pause)
        if self.combo >= 3:
            draw_image_center(*self.combo_pos, *self.combo_num)
            draw_image_center(*self.combo_label_pos, *self.combo_label)
    def set_score(self, score: float):
        self.score = score
        glDeleteTextures(1, [self.score_num])
        self.score_num = get_text_texture_id(str(round(self.score)).zfill(7), UI_FONT, int(30*X_SCALE))


    def set_combo(self, combo: int):
        self.combo = combo
        glDeleteTextures(1, [self.combo_num])
        self.combo_num = get_text_texture_id(str(self.combo), UI_FONT, int(45*X_SCALE))