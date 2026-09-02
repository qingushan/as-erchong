from ...res.task.BaseAction import BaseAction
from ...res.task.BaseFind import BaseFind
from ...res.task.LogUi import LogUi,MosaicUI
from ...res.assets.color import mijin_color, common_color

import time

from ascript.android.screen import FindColors
from ascript.android.screen import Colors
from ascript.android.system import KeyValue

import re
import json

class BaseTask(BaseAction, BaseFind):
    def __init__(self):
        super().__init__()
        self.logui = LogUi()

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

    def walk_to_color_disapper(self, color_dict, color_name):
        # 朝某个颜色走直到颜色消失
        start_time = time.time()
        max_time = 60

        while 1:
            if time.time() - start_time > max_time:
                return False

            point = self.find_my_color(color_dict,color_name)
            if point:
                res = self.position_is_left_or_right(point.x, point.y)
                if res == 1:
                    self.walk_to_w()
                    self.sleep(0.5)
                else:
                    self.rotate_view_to_close_by_ori(res)
            else:
                return True

            self.sleep(0.1)

    def is_boss(self):
        # 判断当前是否BOSS
        if self.find_my_color(common_color,"BOSS_血条_红色"):
            return True

        if self.find_my_color(common_color,"BOSS_血条_白色"):
            return True

        return False

    def auot_lock_enemy(self):
        # 自动索敌
        if self.find_my_color(common_color,"锁敌"):
            self.lock_enemy()
            self.sleep(0.2)

    def await_skill_dodge(self,out_time=10):
        # 等待闪避出现
        start_time = time.time()
        while 1:
            if time.time() - start_time > out_time:
                return False

            res = self.find_color(common_color["闪避"]["colors"],rect=common_color["闪避"]["rect"])
            if res:
                return True

            self.sleep(0.1)

    def await_color(self,color_dict,color_name,out_time=10):
        # 等待某个颜色出现
        start_time = time.time()
        while 1:
            if time.time() - start_time > out_time:
                return False

            res = self.find_my_color(color_dict,color_name)
            if res:
                return True

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

        start_time = time.time()
        while 1:
            if time.time() - start_time > out_time:
                print(f"点击跳转失败：{color_name_1}---{color_name_2}")
                return False

            res = self.find_my_color(color_dict_2,color_name_2)
            if res:
                return True

            if time.time() - click_last_time >= click_time:
                res = self.find_my_color(color_dict_1,color_name_1)
                if res:
                    self.sleep(0.5)
                    print(f"点击---{color_name_1}")
                    if click_x:
                        self.click(click_x,click_y)
                    else:
                        self.click(res.x,res.y)
                    click_last_time = time.time()

            self.sleep(0.1)

    def click_until_color(self,color_dict,color_name,x,y,out_time=10):
        # 点击直到某个颜色出现
        click_time = 3     # 点击间隔
        click_last_time = 0 # 最后一次点击间隔

        start_time = time.time()
        while 1:
            if time.time() - start_time > out_time:
                return False

            res = self.find_my_color(color_dict,color_name)
            if res:
                return True

            if time.time() - click_last_time >= click_time:
                self.click(x,y)
                click_last_time = time.time()

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

        start_time = time.time()
        while 1:
            if time.time() - start_time > time_out:
                return False

            res = self.is_text_re_in_ocr(rect=rect,pattern=pattern,bitmap=bitmap,confidence=confidence)
            if res:
                return True

            if time.time() - click_last_time >= click_time:
                self.click(x,y)
                click_last_time = time.time()

            self.sleep(0.1)

    def fly_spear_num(self,count):
        # 连续飞枪
        for i in range(count):
            self.fly_spear()
            self.sleep(0.3)

    def unlocking(self):
        # 开锁
        res = self.click_until_ocr(796,360,rect=[691,98,1266,687],pattern="快速破解")
        if not res:
            print("开锁失败")
            return False
        self.sleep(1)
        res = self.await_until_click_ocr(rect=[691,98,1266,687],pattern="快速破解",time_out=3)
        if not res:
            print("查找快速破解失败")
            return False
        self.sleep(2)

        print("开锁成功")
        return True

    def use_level_more_award(self,grade=0):
        # 使用委托手册
        if grade == 0:
            self.click(386,403)
        elif grade == 1:
            self.click(516,403)
        elif grade == 2:
            self.click(639,405)
        elif grade == 3:
            self.click(767,405)
        elif grade == 4:
            self.click(886,403)
        
        self.sleep(1)

    def rotate_view_direction_range(self,color_dict,color_name,direction,difference_xy):
        # direction：方向  0-上  1-下  2-左  3-右
        # 旋转视角，通过对比参照物的坐标实现固定的视角旋转
        res = self.await_color(color_dict,color_name)
        if not res:
            return False
        
        res = self.find_my_color(color_dict,color_name)
        if not res:
            return False
        
        x = res.x
        y = res.y

        start_time = time.time()  # 开始时间，超时则退出
        max_time = 30  # 最大超时时间

        while 1:
            if time.time() - start_time > max_time:
                return False

            point = self.find_my_color(color_dict,color_name)
            if not point:
                continue

            if direction == 0:
                # 上
                if abs(point.y-y) >= difference_xy:
                    return True
                
                self.rotate_view_to_top(10, dur=100, after_sleep=0.2)
            elif direction == 1:
                # 下
                if abs(point.y-y) >= difference_xy:
                    return True

                self.rotate_view_to_down(10, dur=100, after_sleep=0.2)
            elif direction == 2:
                # 左
                if abs(point.x-x) >= difference_xy:
                    return True
                
                self.rotate_view_to_left(10, dur=100, after_sleep=0.2)
            elif direction == 3:
                # 右
                if abs(point.x-x) >= difference_xy:
                    return True
                
                self.rotate_view_to_right(10, dur=100, after_sleep=0.2)

            self.sleep(0.1)

        return False

    def rotate_view_direction_to_location(self,color_dict,color_name,x=[0,1280],y=[0,720]):
        # 旋转视角使目标到达指定位置
        res = self.await_color(color_dict,color_name)
        if not res:
            return False
        
        res = self.find_my_color(color_dict,color_name)
        if not res:
            return False

        start_time = time.time()  # 开始时间，超时则退出
        max_time = 30  # 最大超时时间

        while 1:
            if time.time() - start_time > max_time:
                return False

            point = self.find_my_color(color_dict,color_name)
            if not point:
                continue

            status1 = False
            status2 = False

            if x[0] <= point.x <= x[1]:
                status1 = True
            else:
                if point.x > x[1]:
                    self.rotate_view_to_right(10, dur=100, after_sleep=0.2)
                else:
                    self.rotate_view_to_left(10, dur=100, after_sleep=0.2)
            
            if y[0] <= point.y <= y[1]:
                status2 = True
            else:
                if point.y > y[1]:
                    self.rotate_view_to_down(10, dur=100, after_sleep=0.2)
                else:
                    self.rotate_view_to_top(10, dur=100, after_sleep=0.2)

            if status1 and status2:
                return True

            self.sleep(0.1)

        return False

    def rotate_view_direction_to_front(self,color_dict,color_name,direction):
        # 向某个方向旋转使目标出现在前方
        # direction：方向  0-上  1-下  2-左  3-右

        start_time = time.time()  # 开始时间，超时则退出
        max_time = 30  # 最大超时时间
        
        while 1:
            if time.time() - start_time > max_time:
                return False

            point = self.find_my_color(color_dict,color_name)
            if point:
                # 判断当前目标是否在前方
                x1 = self.center_x - 100
                x2 = self.center_x + 100
                if x1 < point.x < x2:
                    return True 

            if direction == 0:
                # 上
                self.rotate_view_to_top(50, dur=100, after_sleep=0.2)
            elif direction == 1:
                # 下
                self.rotate_view_to_down(50, dur=100, after_sleep=0.2)
            elif direction == 2:
                # 左
                self.rotate_view_to_left(50, dur=100, after_sleep=0.2)
            elif direction == 3:
                # 右
                self.rotate_view_to_right(50, dur=100, after_sleep=0.2)

            self.sleep(0.3)

        return False
    
    def ocr_boss(self):
        # 识别boss
        # 巨噬者、审判官、狼人、雪国的野兽、典狱长、西比尔、赛琪
        boss_name = ""
        res = self.ocr(rect=[411,10,869,71])
        if res:
            for r in res:
                if (re.findall(re.compile(r'\?|？'), r.text)):
                    boss_name = "狼人"
                    break
                if (re.findall(re.compile(r'雪国'), r.text)):
                    boss_name = "雪国的野兽"
                    break
                if (re.findall(re.compile('(炼火|典狱长)'), r.text)):
                    boss_name = "典狱长"
                    break
                if (re.findall(re.compile('西比尔'), r.text)):
                    boss_name = "西比尔"
                    break
                if (re.findall(re.compile('羽化'), r.text)):
                    boss_name = "赛琪"
                    break
                if (re.findall(re.compile('巨噬者'), r.text)):
                    boss_name = "巨噬者"
                    break
                if (re.findall(re.compile('审判官'), r.text)):
                    boss_name = "审判官"
                    break
        print(f"当前boss：{boss_name}")
        return boss_name

    def init_is_execute_mihan_info(self):
        # 初始化是否执行密函信息
        is_execute_mihan = {
            "是否执行":"不执行",
            "上一次执行时间":"-1"
        }
        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        KeyValue.save('is_execute_mihan',json_str)

    def set_is_execute_mihan_false(self):
        # 设置是否执行委托密函为不执行
        is_execute_mihan = {
            "是否执行":"不执行",
            "上一次执行时间":"-1"
        }
        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        str_ = KeyValue.get('is_execute_mihan',json_str)
        is_execute_mihan = json.loads(str_)
        is_execute_mihan["是否执行"] = "不执行"

        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        KeyValue.save('is_execute_mihan',json_str)
        self.sleep(1)

    def set_is_execute_mihan_true(self):
        # 设置是否执行委托密函为执行
        is_execute_mihan = {
            "是否执行":"不执行",
            "上一次执行时间":"-1"
        }
        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        str_ = KeyValue.get('is_execute_mihan',json_str)
        is_execute_mihan = json.loads(str_)
        is_execute_mihan["是否执行"] = "执行"

        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        KeyValue.save('is_execute_mihan',json_str)
        self.sleep(1)

    def get_is_execute_mihan(self):
        # 获取是否执行密函
        is_execute_mihan = {
            "是否执行":"不执行",
            "上一次执行时间":"-1"
        }
        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        str_ = KeyValue.get('is_execute_mihan',json_str)
        is_execute_mihan = json.loads(str_)

        self.sleep(1)
        return is_execute_mihan.get("是否执行","不执行")

    def get_is_execute_mihan_time(self):
        # 获取密函上一次执行时间
        is_execute_mihan = {
            "是否执行":"不执行",
            "上一次执行时间":"-1"
        }
        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        str_ = KeyValue.get('is_execute_mihan',json_str)
        is_execute_mihan = json.loads(str_)

        self.sleep(1)
        result = int(is_execute_mihan.get("上一次执行时间","-1"))

        return result

    def set_is_execute_mihan_time(self,time_):
        # 设置密函上一次执行时间
        is_execute_mihan = {
            "是否执行":"不执行",
            "上一次执行时间":"-1"
        }
        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        str_ = KeyValue.get('is_execute_mihan',json_str)
        is_execute_mihan = json.loads(str_)
        is_execute_mihan["上一次执行时间"] = time_

        json_str = json.dumps(is_execute_mihan, ensure_ascii=False)
        KeyValue.save('is_execute_mihan',json_str)
        self.sleep(1)

    def is_refresh_time_execute_mihan(self):
        # 是否整点刷新密函
        now_hour = self.get_time_hour()
        last_hour = self.get_is_execute_mihan_time()
        if now_hour == last_hour:
            return False
        else:
            print("整点刷新了----")
            self.set_is_execute_mihan_true()
            return True
    
    def role_restoration(self):
        # 角色复位
        print("角色复位")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"地图esc界面",x=40,y=29)
        self.sleep(1)
        self.click_color_to_color(common_color,"地图esc界面",common_color,"左上角红色退出",x=936,y=636)
        self.sleep(1)
        self.click_until_ocr(x=38,y=439,rect=[112,176,354,225],pattern="开启")
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"设置-重置位置-确定",x=1071,y=659)
        self.sleep(1)
        self.click_color_to_color(common_color,"设置-重置位置-确定",common_color,"角色血条-绿色",x=795,y=429)
        self.sleep(1)
        print("角色复位成功")

    def go_home(self):
        # 回家
        print("回家")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"左上角红色退出",x=121,y=114)
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"回家-确定",x=55,y=623)
        self.sleep(1)
        self.click(781,413,after_sleep=10)
        self.await_color(common_color,"角色血条-绿色",out_time=60*3)
        self.sleep(1)
        print("成功回家")

    def go_to_lilian(self):
        """
        前往历练
        """
        self.click_until_ocr(x=38, y=30, rect=[119, 277, 344, 385], pattern="商店")
        self.sleep(1)
        self.click_until_ocr(x=175, y=547, rect=[85, 2, 276, 64], pattern="历练")
        self.sleep(1)
        self.click_until_ocr(x=39, y=198, rect=[545, 71, 714, 124], pattern="委托")
        self.sleep(1)
