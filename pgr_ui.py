from func import *
from const import *
from PIL import Image


class UI:
    def __init__(self, _name: str, level: str):
        self.combo = 0
        self.score = 0.
        self.name = get_text_texture_id(_name, UI_FONT, int(25*X_SCALE))
        self.level = get_text_texture_id(level, UI_FONT, int(25*X_SCALE))
        self.name_pos = (20*X_SCALE, 15*Y_SCALE)
        self.level_pos = (WINDOW_WIDTH-20*X_SCALE, 15*Y_SCALE)
        self.score_num = get_text_texture_id(str(round(self.score)).zfill(7), UI_FONT, int(30*X_SCALE))
        self.score_pos = (WINDOW_WIDTH-20*X_SCALE, WINDOW_HEIGHT-15*Y_SCALE)
        self.combo_num = get_text_texture_id(str(self.combo), UI_FONT, int(45*X_SCALE))
        self.combo_label = get_text_texture_id("COMBO", UI_FONT, int(15*X_SCALE))
        self.combo_label_pos = (WINDOW_WIDTH/2, WINDOW_HEIGHT-65*Y_SCALE)
        self.combo_pos = (WINDOW_WIDTH/2, WINDOW_HEIGHT-35*Y_SCALE)
        self.pause = get_texture_id(Image.open("./resources/textures/Pause.png"))
        self.pause = (self.pause[0], self.pause[1]*X_SCALE, self.pause[2]*X_SCALE)
        self.pause_pos = (20*X_SCALE, WINDOW_HEIGHT-20*Y_SCALE)

    def draw_ui(self):
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