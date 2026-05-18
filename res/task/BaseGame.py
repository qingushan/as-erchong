from ascript.android.screen import FORMAT_IMAGE_DATA
from ...res.config import *
import time

from ascript.android.screen import Colors

import datetime


class BaseGame:
    def __init__(self):
        self.center_x = SCREEN_CENTER_X
        self.center_y = SCREEN_CENTER_Y
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        # 本地游戏
        self.walk_button_center_x = WALK_BUTTON_CENTER_X
        self.walk_button_center_y = WALK_BUTTON_CENTER_Y
        self.action_button_position = action_button_position
        self.interaction_text_rect = interaction_text_rect  # 文本交互区域
        # 云游戏
        self.cloud_walk_button_center_x = CLOUD_WALK_BUTTON_CENTER_X
        self.cloud_walk_button_center_y = CLOUD_WALK_BUTTON_CENTER_Y
        self.cloud_action_button_position = cloud_action_button_position
        self.cloud_interaction_text_rect = cloud_interaction_text_rect  # 文本交互区域

        self.skill_time = skill_time

        # self.boss_names = {}

    def sleep(self, sleep_time):
        time.sleep(sleep_time)

    def time(self):
        return time.time()

    def position_is_left_or_right(self, x, y):
        # 判断该坐标是屏幕左边、中间、右边、后面
        # 左边:0
        # 中间:1
        # 右边:2
        # 后面:3

        result = -1
        if (self.center_x - 20) < x < (self.center_x + 20):
            # 判断是否后面
            if y>= 470:
                result = 3
            else:
                result = 1
            # result = 1
        else:
            if x > self.center_x:
                result = 2
            else:
                result = 0
        return result

    def skill_e_is_ok(self):
        # 是否可以释放小技能
        r = (time.time() - self.skill_time["小技能_释放时间"]) > self.skill_time["小技能"]
        n = Colors.count("#FFFFC3",rect=[832,598,897,664],sim=0.95)
        # print(n)
        if r:
            if n > 100:
                return True

        return False

    def skill_q_is_ok(self):
        # 是否可以释放大招
        r = (time.time() - self.skill_time["大招_释放时间"]) > self.skill_time["大招"]
        n = Colors.count("#FFFFCC",rect=[921,602,976,657])
        if r:
            if n > 10:
                return True

        return False

    def skill_z_is_ok(self):
        # 是否可以释放魔灵
        n = Colors.count("#E2E4E6|#E4E7E9",rect=[1059,593,1125,651],sim=0.95)
        if n > 100:
            return True
        else:
            return False

    def get_time_hour(self):
        # 获取当前时间（小时）
        now = datetime.datetime.now()
        hour = now.hour
        return hour
            
