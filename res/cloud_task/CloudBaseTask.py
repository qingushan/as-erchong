from ...res.cloud_task.CloudBaseAction import CloudBaseAction
from ...res.task.BaseFind import BaseFind
from ...res.task.LogUi import LogUi,MosaicUI
from ...res.util.CloudRoleSkillUtil import CloudRoleSkillUtil
from ...res.assets.cloud_color import *

from ascript.android.screen import FindColors
from ascript.android.screen import Colors
from ascript.android.action import Path
from ascript.android import action

import re

class CloudBaseTask(CloudBaseAction, BaseFind):
    # 云-任务基类

    def __init__(self):
        super().__init__()
        self.logui = LogUi()
        self.cloud_role_skill_util = CloudRoleSkillUtil()

    def await_color(self,color_dict,color_name,out_time=10):
        # 等待某个颜色出现
        start_time = self.time()
        while 1:
            if self.time() - start_time > out_time:
                return False

            res = self.find_my_color(color_dict,color_name)
            if res:
                return res

            self.sleep(0.1)

    def click_color_to_color(self,color_dict_1,color_name_1,color_dict_2,color_name_2,x=None,y=None,out_time=10):
        # 在某个页面点击直到下一个页面出现，默认点击color_dict_1
        click_x = None
        click_y = None
        click_time = 3     # 点击间隔
        click_last_time = 0 # 最后一次点击间隔
        if x:
            click_x = x
        if y:
            click_y = y

        start_time = self.time()
        while 1:
            if self.time() - start_time > out_time:
                print(f"点击跳转失败：{color_name_1}---{color_name_2}")
                return False

            res = self.find_my_color(color_dict_2,color_name_2)
            if res:
                return True

            if self.time() - click_last_time >= click_time:
                res = self.find_my_color(color_dict_1,color_name_1)
                if res:
                    self.sleep(0.5)
                    print(f"点击---{color_name_1}")
                    if click_x:
                        self.click(click_x,click_y)
                    else:
                        self.click(res.x,res.y)
                    click_last_time = self.time()

            self.sleep(0.1)

    def click_until_color(self,color_dict,color_name,x,y,out_time=10):
        # 点击直到某个颜色出现
        click_time = 3     # 点击间隔
        click_last_time = 0 # 最后一次点击间隔

        start_time = self.time()
        while 1:
            if self.time() - start_time > out_time:
                return False

            res = self.find_my_color(color_dict,color_name)
            if res:
                return True

            if self.time() - click_last_time >= click_time:
                self.click(x,y)
                click_last_time = self.time()

            self.sleep(0.1)

    def click_until_color_vanish(self,color_dict,color_name,x,y,out_time=10):
        # 点击直到某个颜色消失
        click_time = 3     # 点击间隔
        click_last_time = 0 # 最后一次点击间隔

        start_time = self.time()
        while 1:
            if self.time() - start_time > out_time:
                return False

            res = self.find_my_color(color_dict,color_name)
            if not res:
                return True

            if self.time() - click_last_time >= click_time:
                self.click(x,y)
                click_last_time = self.time()

            self.sleep(0.1)

    def await_until_click_ocr(self,rect=None, pattern=None, bitmap=None, confidence=0.1, time_out=10):
        # ocr等待某个文字出现并点击
        res = self.await_until_ocr(rect=rect, pattern=pattern, bitmap=bitmap, confidence=confidence, time_out=time_out)
        if res:
            x = res[0].center_x
            y = res[0].center_y
            self.click(x,y)
            return True
        
        return False

    def click_until_ocr(self,x,y,rect=None, pattern=None, bitmap=None, confidence=0.1, time_out=10):
        # 点击直到某个ocr出现
        click_time = 3     # 点击间隔
        click_last_time = 0 # 最后一次点击间隔

        start_time = self.time()
        while 1:
            if self.time() - start_time > time_out:
                return False

            res = self.is_text_re_in_ocr(rect=rect,pattern=pattern,bitmap=bitmap,confidence=confidence)
            if res:
                return True

            if self.time() - click_last_time >= click_time:
                self.click(x,y)
                click_last_time = self.time()

            self.sleep(0.1)
    
    def use_level_more_award(self,grade=0):
        # 使用委托手册
        if grade == 0:
            self.click(389,409)
        elif grade == 1:
            self.click(514,406)
        elif grade == 2:
            self.click(640,406)
        elif grade == 3:
            self.click(765,407)
        elif grade == 4:
            self.click(890,406)
        
        # self.sleep(1)

    def rotate_view_to_close_by_ori(self, ori,rotate_x=10):
        # 根据目标方位旋转视角, 使视角靠近目标
        # 左边:0
        # 中间:1
        # 右边:2
        # 后面:3

        if ori == 0:
            # 左转
            self.rotate_view_to_left(rotate_x, dur=100, after_sleep=0.2)
        elif ori == 1:
            return
        elif ori == 2:
            # 右转
            self.rotate_view_to_right(rotate_x, dur=100, after_sleep=0.2)
        elif ori == 3:
            # 向后
            self.rotate_view_to_right(slide_distance=500, dur=1000, after_sleep=0.2)

    def rotate_view_to_middle_by_color(self, color_dict, color_name):
        # 根据颜色旋转视角至中间
        start_time = time.time()  # 开始时间，超时则退出
        max_time = 60  # 最大超时时间

        while 1:
            if time.time() - start_time > max_time:
                return False

            point = self.find_my_color(color_dict,color_name)
            if point:
                res = self.position_is_left_or_right(point.x, point.y)
                if res == 1:
                    return True
                if abs(point.x-self.center_x) > 100:
                    # print("大幅度旋转")
                    self.rotate_view_to_close_by_ori(res,rotate_x=100)
                else:
                    self.rotate_view_to_close_by_ori(res)
            else:
                return False

            self.sleep(0.1)

        return False

    def walk_to_w_new(self, walk_time=1000, after_sleep=1, ocr_text=None, is_click_ocr=False):
        status = False

        line1 = Path(0,walk_time)
        x1 = self.cloud_walk_button_center_x
        y1 = self.cloud_walk_button_center_y
        line1.moveTo(x1,y1) 
        line1.lineTo(x1,y1 - 100)
        action.gesture([line1])

        start_time = self.time()
        is_find_text = False    # 是否找到文字
        while 1:
            if self.time() - start_time >= walk_time/1000:
                break
            
            if ocr_text:
                res = self.is_text_re_in_ocr(rect=self.cloud_interaction_text_rect["多行"],pattern=ocr_text)
                if res:
                    print(f"找到----{ocr_text}")
                    status = True
                    is_find_text = [res[0].x,res[0].y]
                    self.walk_to_s(walk_time=300, after_sleep=0.01)
                    break
            else:
                pass

            self.sleep(0.01)
        
        if is_click_ocr and is_find_text:
            for i in range(3):
                print("点击")
                self.click(is_find_text[0], is_find_text[1], after_sleep=0.1)
        
        self.sleep(after_sleep)
        return status

    def common_quit_level(self):
        # 退出副本
        print("退出副本")
        self.click(81,29)
        self.click(1143,641)
        self.click_until_color(cloud_common_color, "副本退出-再次进行", x=779, y=413, out_time=60)
        self.sleep(1)
        print("退出副本完成")

    def role_restoration(self):
        # 角色复位
        print("角色复位")
        self.click(81,29)
        self.click(888,637)
        self.click(93,393)
        self.click(1044,426)
        self.click(778,410)
        print("角色复位成功")


    def go_to_lilian(self):
        """
        前往历练
        """
        self.click_until_ocr(x=81, y=34, rect=[119, 277, 344, 385], pattern="商店")
        self.sleep(1)
        self.click_until_ocr(x=208, y=590, rect=[85, 2, 276, 64], pattern="历练")
        self.sleep(1)
        self.click_until_ocr(x=96, y=186, rect=[545, 71, 714, 124], pattern="委托")
        self.sleep(1)