from ...res.task.BaseTask import BaseTask
from ...res.assets.color import *

import numpy as np
import re
import random

class AutoFishTask(BaseTask):
    # 钓鱼
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '钓鱼'  
        self.fish_bait = -1     # 鱼饵数量 
        self.maps = ["冰湖城","净界岛","下水道"]
        self.now_map = '冰湖城'
        self.fish_premiums = 0  # 授渔以鱼次数

        self.is_have_easy = False   # 是否有悠闲

        self.level_max_count = 2 # 最大探索次数
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

    def init_task(self):
        # 初始化
        self.maps = []
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.level_max_count = int(self.uiconfig['fish_max_num'])

        if self.uiconfig['fish_map_bhc'] == 'on':
            self.maps.append("冰湖城")
        
        if self.uiconfig['fish_map_jjd'] == 'on':
            self.maps.append("净界岛")

        if self.uiconfig['fish_map_xsd'] == 'on':
            self.maps.append("下水道")

        if self.uiconfig['fish_map_fxb'] == 'on':
            self.maps.append("浮星埠")

        if self.uiconfig['fish_map_bnc'] == 'on':
            self.maps.append("百年春")

        if self.uiconfig['fish_map_csy'] == 'on':
            self.maps.append("潮声岩")

        if self.uiconfig['fish_map_krg'] == 'on':
            self.maps.append("枯荣阁")

        if self.uiconfig['fish_map_wms'] == 'on':
            self.maps.append("微茫市")

        if self.uiconfig['fish_map_djyw'] == 'on':
            self.maps.append("东郊野外")

        if self.uiconfig['fish_map_cxq'] == 'on':
            self.maps.append("城西区")

        if self.uiconfig['fish_map_ylx'] == 'on':
            self.maps.append("由来巷")
        
        print(f"初始化完成，当前执行钓点：{self.maps}")

    def get_fish_bait(self):
        # 获取鱼饵数量
        res = self.ocr(rect=[1114,1,1223,52])
        if res:
            for r in res:
                text = r.text
                print(text)
                result = re.findall(r"\d+",text)
                print(result)
                if len(result) > 0:
                    n = int(result[0])
                    self.fish_bait = n
                    print(f"当前鱼饵数量：{self.fish_bait}")
                    break

    def go_home(self):
        # 回家
        self.click_color_to_color(common_color,"主界面左上角菜单",common_color,"左上角红色退出",x=123,y=92)
        self.sleep(2)
        self.click_color_to_color(common_color,"左上角红色退出",fish_color,"回家-确定",x=52,y=611)
        self.sleep(1)
        self.click_color_to_color(fish_color,"回家-确定",common_color,"角色血条-绿色",x=770,y=413)
        self.sleep(2)
        print("成功返回家")

    def go_to_level(self,map_name):
        # 前往副本
        print(f"开始前往钓鱼地点---{map_name}")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=211,y=324)
        self.sleep(2)
        self.click(47,397)
        self.sleep(2)
        self.click(144,141)
        self.sleep(2)
        self.click_until_color(fish_color,"追踪当前钓鱼点",1107,654)
        self.sleep(1)

        if map_name == "冰湖城":
            self.click(49,187,after_sleep=2)
            self.click(214,124,after_sleep=2)
        elif map_name == "净界岛":
            self.click(46,114)
        elif map_name == "下水道":
            self.click(49,187,after_sleep=2)
            self.click(376,124,after_sleep=2)
        elif map_name == "浮星埠":
            self.click(49,259,after_sleep=2)
            self.click(214,126,after_sleep=2)
        elif map_name == "百年春":
            self.click(49,259,after_sleep=2)
            self.click(375,123,after_sleep=2)
        elif map_name == "潮声岩":
            self.click(49,259,after_sleep=2)
            self.click(531,124,after_sleep=2)
        elif map_name == "枯荣阁":
            self.click(49,259,after_sleep=2)
            self.click(694,124,after_sleep=2)
        elif map_name == "微茫市":
            self.click(49,259,after_sleep=2)
            self.click(857,123,after_sleep=2)
        elif map_name == "东郊野外":
            self.click(48,324,after_sleep=2)
            self.click(215,122,after_sleep=2)
        elif map_name == "城西区":
            self.click(48,324,after_sleep=2)
            self.click(376,122,after_sleep=2)
        elif map_name == "由来巷":
            self.click(48,324,after_sleep=2)
            self.click(537,122,after_sleep=2)
        
        self.sleep(1)
        self.click_color_to_color(fish_color,"追踪当前钓鱼点",common_color,"地图传送",x=997,y=657)
        self.sleep(1)
        
        self.click(1071,654,random_range=0)
        self.sleep(10)
        self.await_until_color(common_color,"角色血条-绿色",time_out=120)
        print("传送成功")

        if map_name == "城西区":
            self.walk_to_s(500)
            self.sleep(0.5)
            self.walk_to_a(1000*4)
            self.sleep(0.5)
            self.walk_to_w(1000)
            self.sleep(0.5)

        for i in range(20):
            res = self.is_text_re_in_ocr(rect=[735,333,828,382],pattern="鱼")
            if res:
                break
            if map_name == "浮星埠":
                self.walk_to_a(300)
            else:
                self.walk_to_w(300)
            self.sleep(1)

        res = self.is_text_re_in_ocr(rect=[735,333,828,382],pattern="鱼")
        if not res:
            print("未找到钓鱼入口")
            return False

        self.click_until_color(common_color,"左上角红色退出",783,357)
        self.sleep(1)
        if self.uiconfig["fish_insane"] == 'on':
            # 疯狂钓鱼
            self.click_color_to_color(common_color,"左上角红色退出",fish_color,"悠闲甩杆图标",x=1147,y=666)
            self.is_have_easy = True
            print("疯狂钓鱼！！")
        else:
            res = self.click_color_to_color(common_color,"左上角红色退出",fish_color,"甩杆图标",x=1147,y=666)
            if not res:
                self.is_have_easy = True
                print("悠闲钓鱼！！")
            else:
                print("没有悠闲")
        print(f"成功进入{map_name}钓点")
        self.sleep(1)

        self.get_fish_bait()
        return True

    def get_fish_location(self):
        # 获取鱼图标的位置
        res = self.find_my_color(fish_color,"鱼图标")
        # print(f"鱼图标:{res}")
        if res:
            return (res.x,res.y)
        else:
            return False

    def get_bule_bg_centre(self):
        # 获取蓝色背景的中心坐标
        xy_list = []    # 背景点所有坐标点
        res = self.findall_my_color(fish_color,"鱼不在范围内")
        if res:
            # print("鱼不在范围内")
            for r in res:
                x = r.x
                y = r.y
                xy_list.append((x,y))
        else:
            res = self.findall_my_color(fish_color,"鱼在范围内")
            if res:
                # print("鱼在范围内")
                for r in res:
                    x = r.x
                    y = r.y
                    xy_list.append((x,y))
        
        # print(f"蓝色背景所有坐标点：{xy_list}")

        if len(xy_list) == 0:
            return False

        # 按 y 值排序
        sorted_coordinates = sorted(xy_list, key=lambda x: x[1])

        # 计算中心坐标
        center_x = np.mean([x[0] for x in sorted_coordinates])
        center_y = np.mean([x[1] for x in sorted_coordinates])

        # print(f"\n中心坐标是：({center_x:.2f}, {center_y:.2f})")
        return (center_x,center_y)

    def fish_action(self,fish_x,fish_y,bule_bg_x,bule_bg_y):
        # 根据识别的坐标执行动作
        difference_y = abs(bule_bg_y-fish_y)
        if bule_bg_y > fish_y:
            # 点击
            if difference_y > 100:
                self.click(1147,589,dur=1000,after_sleep=0.01)
                # for i in range(10):
                #     self.click(1147,589,after_sleep=0.01)
            else:
                self.click(1147,589,after_sleep=0.01)

    def swing_the_rod(self):
        # 甩杆
        if self.is_have_easy:
            res = self.click_color_to_color(fish_color,"悠闲甩杆图标",fish_color,"等鱼上钩图标",x=1146,y=586)
        else:
            res = self.click_color_to_color(fish_color,"甩杆图标",fish_color,"等鱼上钩图标",x=1146,y=586)
        if not res:
            print("没有鱼饵或者次数到达上限了")
            return False

        if self.is_have_easy:
            res = self.await_until_color(fish_color,"悠闲甩杆图标",time_out=30)
        else:
            res = self.await_until_color(fish_color,"甩杆图标",time_out=30)
        if res:
            print("鱼上钩了")
            for i in range(3):
                self.click(1147,589,after_sleep=0.1)
            return True
        else:
            print("鱼没有上钩")
            return True

    def fishing(self):
        # 钓鱼
        start_time = self.time()
        max_time = 60*5

        if self.is_have_easy:
            self.await_until_ocr(rect=[370,28,932,653],pattern="(鱼了|图鉴)",time_out=20)
            print("成功钓到鱼了")
            self.sleep(1)
            self.click(927,641)
            self.click(927,641)
            res = self.await_until_ocr(rect=[437,52,848,223],pattern="的机会",time_out=5)
            if res:
                print("触发了授渔以鱼")
                self.fish_premiums += 1
                self.click_until_color(fish_color,"等鱼上钩图标",x=1177,y=578)
                self.await_until_color(fish_color,"悠闲甩杆图标",time_out=30)
                for i in range(3):
                    self.click(1147,589,after_sleep=0.1)
                self.await_until_ocr(rect=[370,28,932,653],pattern="(鱼了|图鉴)",time_out=20)
                self.sleep(1)
                self.click(927,641)
                self.click(927,641)

            self.click_until_color(fish_color,"悠闲甩杆图标",x=927,y=641)
            return True


        while 1:
            if self.time() - start_time > max_time:
                print("钓鱼超时")
                return False

            r1 = self.get_fish_location()
            r2 = self.get_bule_bg_centre()
            if r1 and r2:
                fish_x = r1[0]
                fish_y = r1[1]
                bule_bg_x = r2[0]
                bule_bg_y = r2[1]
                self.fish_action(fish_x,fish_y,bule_bg_x,bule_bg_y)
            # elif (not r1) and (not r2):
            res = self.find_my_color(fish_color,"右上角问号")
            if not res:
                self.sleep(0.5)
                res = self.find_my_color(fish_color,"右上角问号")
            if not res:
                print("钓鱼结束")
                res = self.await_until_ocr(rect=[370,28,932,653],pattern="(鱼了|图鉴)",time_out=5)
                if res:
                    print("成功钓到鱼了")
                    self.sleep(1)
                    self.click(927,641)
                    self.click(927,641)
                    res = self.await_until_ocr(rect=[437,52,848,223],pattern="的机会",time_out=5)
                    if res:
                        print("触发了授渔以鱼")
                        self.fish_premiums += 1
                        self.click_until_color(fish_color,"等鱼上钩图标",x=1177,y=578)
                        self.await_until_color(fish_color,"甩杆图标",time_out=30)
                        for i in range(3):
                            self.click(1147,589,after_sleep=0.1)
                        continue
                    self.click_until_color(fish_color,"甩杆图标",x=927,y=641)
                    return True
                else:
                    print("钓鱼失败")
                    return False
            self.sleep(0.01)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  当前钓点：{self.now_map}   授渔以鱼次数：{self.fish_premiums}   次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}"
        self.logui.change_log_text(text)

    def level_exit(self):
        if self.is_have_easy:
            self.click_color_to_color(fish_color,"悠闲甩杆图标",common_color,"左上角红色退出",x=32,y=35)
        else:
            self.click_color_to_color(fish_color,"甩杆图标",common_color,"左上角红色退出",x=32,y=35)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"主界面左上角菜单",x=32,y=35)
        print("返回主界面成功")

    def run(self):
        fish_x = 0
        fish_y = 0
        bule_bg_x = 0
        bule_bg_y = 0

        self.init_task()
        self.refresh_log()
        for man_name in self.maps:
            self.level_finish_count = 0
            res = self.go_to_level(man_name)
            if not res:
                print(f"前往钓点失败----{man_name}")
                # self.click_until_color(common_color,"左上角红色退出",x=46,y=105)
                # self.sleep(1)
                # self.click_color_to_color(common_color,"左上角红色退出",common_color,"主界面左上角菜单",x=32,y=35)
                continue

            self.now_map = man_name
            while 1:
                if self.uiconfig["fish_insane"] == 'on':
                    # 疯狂钓鱼
                    # 判断是还有鱼，没有则退出
                    if self.is_text_re_in_ocr(rect=[381,34,908,596],pattern="水中暂时无鱼"):
                        print("当前钓点已无鱼，退出")
                        self.click_until_color(fish_color, "悠闲甩杆图标", 1146, 586)
                        self.sleep(1)
                        self.level_exit()
                        break

                    self.click(x=1146,y=586,after_sleep=random.uniform(0.4,1.5))
                else:
                    self.refresh_log()

                    if self.level_finish_count >= self.level_max_count:
                        print(f"任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                        self.level_exit()
                        break

                    # 判断是否需要整点去执行密函
                    if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                        res = self.is_refresh_time_execute_mihan()
                        if res:
                            self.level_exit()
                            return True

                    # 判断是否还有鱼饵
                    self.get_fish_bait()

                    res = self.swing_the_rod()
                    if not res:
                        self.level_exit()
                        break

                    res = self.fishing()
                    if res:
                        self.level_finish_count += 1
                        self.level_ok_count += 1
                    else:
                        self.level_finish_count += 1
                        self.level_faile_count += 1

