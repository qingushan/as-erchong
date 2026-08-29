from ...res.task.BaseTask import BaseTask
from ...res.assets.color import *

from ...res.task.AutoMijinTask import AutoMijinTask

import threading
import time
import re

from ascript.android import action
from ascript.android.screen import Colors


class AutoTestTask(BaseTask):
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.now_level = 0  # 当前关卡
        self.level_max_time = 60  # 每个关卡超时时间
        self.level_start_time = time.time()  # 当前关卡开始时间
        self.level_time_out_count = 0  # 关卡超时次数
        self.level_restart_status = False   # 关卡是否暂离重置

        self.level_max_count = 0 # 最大探索次数
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.gold = 0   # 时之纺线
        self.role = "夫人"

        self.moling_boss_max_time = 5   # boss战斗魔灵最大释放间隔
        self.moling_boss_last_time = 0  # boss战斗魔灵最后一次释放时间

        self.find_door_names = ["至暗幽影", "深邃幽影", "深渊回声", "休整", "离散幽影", "微茫幽影"]  # 需要查找的门的顺序

        self.is_boss_door = False   # 是否关底boss
        self.now_boss = ""      # 当次迷津关底boss

        # 进入门之后关卡显示的名字
        self.door_open_name = {
            "至暗幽影":"战斗",
            "深邃幽影":"战斗",
            "深渊回声":"奇遇",
            "休整":"休整",
            "离散幽影":"战斗",
            "微茫幽影":"战斗",
        }

        self.level_type_dict = {
            "-1":"其他",
            "0":"战斗",
            "1":"前往下一层",
            "2":"休整",
            "3":"奇遇",
        }

        self.inti_mijin(uiconfig)

    def go_to_mijin(self):
        print("开始前往迷津")
        self.go_to_lilian()
        self.click_color_to_color(common_color,"左上角红色退出",mijin_color,"历练-迷津",x=46,y=324)
        self.sleep(1)
        self.click_until_ocr(x=1103,y=513,rect=[19,498,1265,693],pattern="(坠入深渊|命运|翻阅手记)")
        self.sleep(1)
        print("成功进入迷津")

    def quit_mijin(self):
        print("开始退出迷津")
        self.click_color_to_color(common_color,"左上角红色退出",mijin_color,"历练-迷津",x=44,y=31)
        self.sleep(1)
        self.click_until_ocr(x=44, y=34, rect=[119, 277, 344, 385], pattern="商店")
        self.sleep(1)

        for i in range(3):
            self.click(634,666)

        res = self.find_my_color(common_color,"主界面左上角菜单")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def inti_mijin(self,uiconfig):
        # 迷津初始化
        map_role = {
            '0':'水母',
            '1':'夫人',
            '2':'止流'
        }

        if uiconfig:
            self.level_grade = uiconfig['mijin_grade']
            self.level_max_count = int(uiconfig['mijin_max_num'])
            self.role = map_role[uiconfig['mijin_role']]

            # 选门优先级
            res = int(uiconfig['mijin_select_door'])
            if res == 0:
                self.find_door_names = ["至暗幽影", "深邃幽影", "深渊回声", "休整", "离散幽影", "微茫幽影"]
            elif res == 1:
                self.find_door_names = ["至暗幽影", "深邃幽影", "离散幽影", "微茫幽影", "深渊回声", "休整"]
            elif res == 2:
                self.find_door_names = ["至暗幽影", "深邃幽影", "深渊回声", "离散幽影", "微茫幽影", "休整"]
            print(f"选门优先级:{self.find_door_names}")

            # 魔灵技能
            self.moling_common_max_time = float(uiconfig['mijin_combat_common_time']) # 普通战斗魔灵最大释放间隔
            self.moling_common_last_time = 0  # 普通战斗魔灵最后一次释放时间
            self.moling_boss_max_time = float(uiconfig['mijin_combat_boss_time']) # boss战斗魔灵最大释放间隔
            self.moling_boss_last_time = 0  # boss战斗魔灵最后一次释放时间
            print(f"普通战斗魔灵时间：{self.moling_common_max_time}")
            print(f"boss战斗魔灵时间：{self.moling_boss_max_time}")
        else:
            # 默认
            self.level_grade = "40"  # 迷津等级
            self.level_max_count = 10   # 迷津次数
            self.role = '水母'      # 角色

        print(f"迷津初始化成功:")
        print(f"迷津等级:{self.level_grade}")
        print(f"迷津次数:{self.level_max_count}")
        print(f"迷津角色:{self.role}")

        if self.role == '夫人':
            self.level_max_time = 60*3
            self.skill_time["大招"] = 15
        elif self.role == '止流':
            self.level_max_time = 60*3
            self.skill_time["大招"] = 15

    def run(self):
        # 判断是否运行旧版本
        if self.uiconfig['mijin_run_old'] == "on":
            print("运行旧版本")
            task = AutoMijinTask(self.uiconfig)
            task.run()
            return True

        self.refresh_log()
        self.go_to_mijin()
        while True:
            # 刷新日志
            self.refresh_log()

            # 复苏
            res = self.is_text_re_in_ocr(rect=[593,611,681,662],pattern="复苏")
            if res:
                print("复苏")
                self.click(636,633)
                self.sleep(1)
                continue

            # 判断当前是否boss战斗
            if self.is_boss():
                self.combat()
                continue

            res = self.check_level_is_timeout()
            r = self.find_my_color(common_color,"下蹲按钮")
            if res:
                self.level_start_time = time.time()
                if r:
                    if self.level_time_out_count >= 3:
                        self.close_mijin()
                    else:
                        self.quit_mijin_start()
                        continue

            # 判断当前是否战斗
            r1 = self.find_my_color(mijin_color,"右上角战斗红色")
            r2 = self.find_my_color(mijin_color,"任务")
            if r1 and (not r2):
                self.combat()
                continue

            res = self.recognition_level_type()
            if res == "-1":
                res = self.level_other()
            elif res == "0":
                res = self.level_combat()
            elif res == "1":
                res = self.level_to_to_next_level()
            elif res == "2":
                res = self.level_rest()
            elif res == "3":
                res = self.level_qiyu()

            res = self.ocr(rect=[4,0,1272,690])
            if not res:
                self.sleep(0.5)
                continue
            for r in res:
                text = r.text
                if self.re_matching("坠入深渊", text):
                    # 判断当前满足迷津次数
                    if self.level_finish_count >= self.level_max_count:
                        print(f"迷津任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                        self.quit_mijin()
                        return True

                    # 判断是否需要整点去执行密函
                    if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                        res = self.is_refresh_time_execute_mihan()
                        if res:
                            self.quit_mijin()
                            return True

                    self.click(r.center_x, r.center_y)
                    self.await_until_ocr(pattern="难度选择", time_out=30)
                    # 选择等级
                    self.select_grade()
                    self.click(1104, 626)
                    self.click(1129, 654)

                    self.now_level = 0
                    self.is_boss_door = False
                    self.now_boss = ""
                    self.init_now_level()
                    break

            self.sleep(0.5)

    def re_matching(self, pattern, text):
        # 使用正则匹配
        return re.findall(re.compile(pattern), text)

    def init_now_level(self):
        # 初始化当前关卡数据
        self.level_start_time = time.time()
        self.level_time_out_count = 0
        self.now_level = self.now_level + 1
        self.level_restart_status = False
        self.moling_common_last_time = 0
        self.moling_boss_last_time = 0
        print(f"当前关卡-----{self.now_level}")

    def close_mijin(self):
        # 退出迷津
        print("退出迷津")
        self.click_color_to_color(common_color,"下蹲按钮",mijin_color,"退出并结算",x=45,y=29)
        self.sleep(1)
        self.click_color_to_color(mijin_color,"退出并结算",common_color,"退出委托_确定",x=1207,y=639)
        self.sleep(1)
        self.click_color_to_color(common_color,"退出委托_确定",mijin_color,"迷津结束界面",x=795,y=436,out_time=60)
        self.sleep(1)
        # 识别时之纺线
        res = self.find_my_color(mijin_color,"迷津结束界面")
        if res:
            self.ocr_gold()

        self.click_color_to_color(mijin_color,"迷津结束界面",mijin_color,"右上角红色退出",x=1222,y=56,out_time=60)
        self.sleep(1)
        res = self.find_my_color(mijin_color,"右上角红色退出")
        if res:
            print("退出深渊成功")
            self.level_finish_count += 1
            self.level_faile_count += 1
        else:
            print("退出深渊失败！！！！！")

    def check_level_is_timeout(self):
        # 检查当前关卡是否超时
        # print(f"开始检测超时----{self.level_start_time}")
        if (time.time() - self.level_start_time) > self.level_max_time:
            print("关卡超时")
            self.level_time_out_count += 1
            return True
        else:
            return False

    def find_door_out_time(self):
        # 找门超时
        self.rotate_view_to_down(500)
        self.sleep(1)
        self.action_jump_fly()
        self.action_dodge_to_w()
        self.sleep(2)
        self.reset_role_view()
        self.rotate_view_to_right(500,dur=500,after_sleep=0.5)
        self.level_time_out_count += 1

    def select_buff(self):
        # 选择buff
        if self.role == '水母':
            pattern = "(流明枝|辉萤石)"
        elif self.role == '夫人':
            pattern = "(浮海月|技能范围|辉萤石|曳光虫)"
        elif self.role == '止流':
            pattern = "(浮海月|技能范围|辉萤石|曳光虫)"

        self.sleep(1)
        res = self.ocr(pattern=pattern, rect=[466, 104, 1257, 589])
        if res:
            x = res[0].center_x
            y = res[0].center_y
            self.click(x, y)
        else:
            # 刷新
            self.click(931, 683, after_sleep=2)
            res = self.ocr(pattern=pattern, rect=[466, 104, 1257, 589])
            if res:
                x = res[0].center_x
                y = res[0].center_y
                self.click(x, y)
            else:
                # 默认选择第一个
                self.click(609, 400)

                self.click(728,507)     # 防止出现bug，没有三个buff选项

        # 选择
        self.click(1155, 684, after_sleep=2)

    def select_grade(self):
        if self.level_grade == "30":
            self.click(130, 142)
        elif self.level_grade == "40":
            self.click(124, 188)
        elif self.level_grade == "50":
            self.click(124, 242)
        elif self.level_grade == "60":
            self.click(123, 297)
        elif self.level_grade == "70":
            self.click(130, 343)
        elif self.level_grade == "80":
            self.click(124, 395)

        self.sleep(1)

    def role_combat_0(self):
        # 水母战斗
        if self.is_boss():
            self.level_start_time = time.time()
            self.auot_lock_enemy()
            self.sleep(0.5)
            self.action_dodge_to_w()
            self.sleep(0.5)

        if self.skill_e_is_ok():
            for i in range(2):
                self.skill_e()

        if self.is_boss():
            print("BOSS")
            if self.skill_q_is_ok():
                self.skill_q()

            # 普攻
            for i in range(10*3):
                if self.is_boss():
                    self.auot_lock_enemy()
                    self.combat_left_click()
                    self.sleep(0.1)
                else:
                    break

    def role_combat_1(self):
        # 夫人战斗
        if self.is_boss():
            # bosss战斗初始化时间防止超时
            self.level_start_time = time.time()

            # 判断是否boss大招
            if self.find_my_color(cjsxj_color,"boss白色血条"):
                print(f"{self.now_boss}----大招")
                if self.now_boss in ['狼人','雪国的野兽','典狱长','西比尔','赛琪']:
                    self.action_dodge_to_s()
                    self.sleep(0.5)
                    return True

            if self.find_my_color(common_color,"BOSS处决"):
                print("boss处决")
                self.click(996,248)

            self.lock_enemy()
            # self.sleep(0.2)
            # self.lock_enemy()
            # self.sleep(0.2)
            # self.auot_lock_enemy()
            # self.sleep(0.5)

            self.action_dodge_to_w()
            self.sleep(1)
            self.lock_enemy()

            if self.skill_q_mp_is_ok():
                self.skill_q()
                self.sleep(2)
            
            for i in range(7):
                self.mijin_moling_boss()    # 魔灵
                if self.skill_e_mp_is_ok():
                    self.skill_e()
                else:
                    break
            
            # boss还在
            if self.is_boss():
                self.lock_enemy()
                # self.sleep(0.2)
                # self.lock_enemy()
                # self.sleep(0.2)
                # self.auot_lock_enemy()
                # self.sleep(0.5)
                res = self.find_my_color(common_color,"没有子弹")
                if res:
                    print("没有子弹了")
                    for i in range(50):
                        self.mijin_moling_boss()    # 魔灵
                        self.combat_left_click()
                else:
                    if self.uiconfig['mijin_ranged_weapon'] == "0":
                        # 其他武器
                        for i in range(50):
                            self.mijin_moling_boss()    # 魔灵
                            self.combat_right_click()
                    elif self.uiconfig['mijin_ranged_weapon'] == "1":
                        # 花弓
                        for i in range(5):
                            self.mijin_moling_boss()    # 魔灵
                            # 蓄力
                            x = self.action_button_position["远程攻击"][0]
                            y = self.action_button_position["远程攻击"][1]
                            self.click(x, y, dur=600, after_sleep=0.1)
                            # self.combat_right_click()
        else:
            self.mijin_moling_common()
            if self.skill_q_is_ok():
                self.skill_q()
            # if self.skill_z_is_ok():
            #     self.skill_z()
            for i in range(6):
                # 判断是否还在战斗
                r = self.find_my_color(mijin_color,"右上角战斗红色")
                if not r:
                    res = self.is_text_re_in_ocr(rect=[5,197,203,312],pattern="战斗")
                    if not res:
                        print("战斗结束")
                        return False
                self.mijin_moling_common()
                self.skill_e(after_sleep=0.5)
                self.skill_e(after_sleep=0.5)
                x = self.action_button_position["远程攻击"][0]
                y = self.action_button_position["远程攻击"][1]
                self.combat_bullet()
                self.slide(x,y,x+300,y,1000)

    def skill_2(self):
        # 止流连招
        self.skill_e(dur=1000, after_sleep=1)
        self.skill_e(after_sleep=1)
        for i in range(4):
            self.skill_q(after_sleep=0.5)
        self.sleep(1)

    def role_combat_2(self):
        # 止流战斗
        if self.is_boss():
            self.skill_time["大招"] = 5

            # bosss战斗初始化时间防止超时
            self.level_start_time = time.time()

            # 判断是否boss大招
            if self.find_my_color(cjsxj_color,"boss白色血条"):
                print(f"{self.now_boss}----大招")
                if self.now_boss in ['狼人','雪国的野兽','典狱长','西比尔','赛琪']:
                    self.action_dodge_to_s()
                    self.sleep(0.5)
                    return True

            if self.find_my_color(common_color,"BOSS处决"):
                print("boss处决")
                self.click(996,248)

            self.lock_enemy()
            self.action_dodge_to_w()
            self.sleep(1)
            self.lock_enemy()

            if self.skill_q_is_ok():
                self.skill_2()

            self.mijin_moling_boss()    # 魔灵
            
        else:
            self.skill_time["大招"] = 5

            if self.skill_q_is_ok():
                self.skill_2()

            self.mijin_moling_common()
            
    def walk_to_task(self):
        # 前往任务
        res = self.rotate_view_to_middle_by_color(mijin_color,"任务")
        if res:
            for i in range(5):
                self.action_jump_fly()
                self.sleep(1)
                if self.is_boss():
                    print("BOSS出现")
                    break

                if not self.find_my_color(mijin_color,"任务"):
                    break

    def level_combat(self):
        # 战斗关卡
        if self.find_my_color(mijin_color,"任务"):
            print('开始前往指定地点')
            self.walk_to_task()
            self.level_restart_status = True
        else:
            self.combat()

    def level_to_to_next_level(self):
        # 前往下一层
        print("开始前往下一层")
        start_time = time.time()
        max_time = 60

        # 校验是否有门，没有门则退出
        if not self.is_have_door():
            return False

        self.rotate_view_to_down(400)

        # self.rotate_to_combat_door()

        for door_name in self.find_door_names:
            while 1:
                if time.time() - start_time > max_time:
                    return False
                
                res = self.ocr(rect=[706,322,949,391],pattern=door_name)
                if not res:
                    res = self.rotate_view_to_middle_by_color(mijin_color,door_name,behind=True)
                    if not res:
                        break
                    self.walk_to_w()
                    self.sleep(0.5)

                res = None
                for i in range(3):
                    res = self.ocr(rect=[706,322,949,391],pattern=door_name)
                    if res:
                        break
                if res:
                    x = res[0].center_x
                    y = res[0].center_y
                    self.click(x, y)
                    pattern = self.door_open_name[door_name]
                    res = self.click_until_ocr(x,y,rect=[16,197,206,328],pattern=pattern)
                    if res:
                        print(f"成功进入---{door_name}")

                        # 进门后刷新技能
                        if self.role == '止流':
                            self.skill_time['大招_释放时间'] = 0

                        if door_name == "至暗幽影":
                            self.is_boss_door = True
                        self.init_now_level()
                        if door_name in ["离散幽影","微茫幽影"]:
                            self.is_map_jam_trees()
                        return True

                self.sleep(0.1)

    def level_qiyu(self):
        # 奇遇
        map_type = -1   # 奇遇地图  0：战斗奇遇
        is_paotai = False   # 是否炮台
        res = self.find_my_color(mijin_color,"任务")
        if res:
            if (self.center_x - 50) < res.x < (self.center_x + 50):
                print("黄色图标在中间")
                # 判断是否战斗奇遇
                if  res.y > 460:
                    print("战斗奇遇")
                    map_type = 0
                self.rotate_view_to_middle_by_color(mijin_color,"任务")
                self.walk_to_w(1000*4)
            # elif (370 < res.x < 400) and (360 < res.x < 390):
            elif (370 < res.x < 400) and (360 < res.y < 390):
                # 炮台
                print("准备炮台")
                # exit()
                is_paotai = True
                self.rotate_view_to_middle_by_color(mijin_color,"任务")
            else:
                for i in range(6):
                    self.walk_to_w(1000)
                self.sleep(0.5)
                self.rotate_view_direction_to_front(mijin_color,"任务",2)
                self.sleep(0.5)
                self.rotate_view_to_middle_by_color(mijin_color,"任务")
                self.sleep(0.5)
                self.walk_to_w(1000*3)
                self.sleep(0.5)

            for i in range(10):
                self.rotate_view_to_middle_by_color(mijin_color,"任务")
                res = self.is_text_re_in_ocr(rect=[706,322,949,391],pattern="火焰")
                if res:
                    break
                self.walk_to_w(300)
                self.sleep(0.5)

            res = None
            for i in range(5):
                res = self.is_text_re_in_ocr(rect=[706,322,949,391],pattern="火焰")
                if res:
                    break
                self.sleep(0.5)

            if not res:
                print("进入奇遇失败")
                return False
            
            x = res[0].x
            y = res[0].y
            # res = self.click_until_color(mijin_color,"奇遇界面",x,y)
            res = self.click_until_ocr(x,y,rect=[3,622,68,658],pattern="奇遇")
            if not res:
                return False
                
            for i in range(50):
                # r1 = self.find_my_color(common_color,"下蹲按钮")
                # r2 = self.find_my_color(mijin_color,"奇遇界面")
                # if r1 and (not r2):
                #     break
                if self.is_text_re_in_ocr(rect=[8,219,244,423], pattern="继续"):
                    break

                # if self.find_my_color(mijin_color,"奇遇界面"):
                if self.is_text_re_in_ocr(rect=[3,622,68,658],pattern="奇遇"):
                    self.click(41,32,after_sleep=0.1)
                if map_type == 0:
                    # 战斗奇遇
                    res = self.is_text_re_in_ocr(rect=[773,459,1252,703],pattern="(附和|是的|沉默|加入他们|回应|拥抱一東阳光)")
                    if res:
                        print("选择不战斗")
                        x = res[0].x
                        y = res[0].y
                        self.click(x,y)
                        for i in range(5):
                            self.click(1030,648,after_sleep=0.1)
                    if i > 30:
                        # 防止检测失败
                        self.click(1030,648,after_sleep=0.1)
                else:
                    self.click(1030,648,after_sleep=0.1)
            
            # 校验是否炮台
            if is_paotai:
                print("开始炮台奇遇")
                res = None
                for i in range(50):
                    res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
                    if res:
                        break
                    self.sleep(0.1)

                if res:
                    return True
                else:
                    print("找不到炮台操作")
                    for i in range(3):
                        self.d_and_jupm()
                        self.sleep(2)
                        for i in range(5):
                            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
                            if res:
                                return True
                            self.sleep(0.1)
                    print("查找炮台操作失败")
                    return False
            else:
                # 判断是否奇遇之后进入的战斗，是则向前冲刺
                if map_type == 0:
                    res = self.recognition_level_type()
                    if res == "0":
                        for i in range(3):
                            self.action_dodge_to_w()
                            self.sleep(0.5)
                return True
        else:
            # 校验是否有炮台
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
            if res:
                print("奇遇炮台")
                r = self.click_until_ocr(774,357,rect=[16,209,257,327],pattern="(炮台|积分)")
                if not r:
                    return False
                self.click_until_color(mijin_color,"退出炮台确定",42,36)
                self.sleep(1)
                self.click_until_ocr(x=796, y=428, rect=[548,202,782,284], pattern="积分")
                self.sleep(1)
                # self.click_color_to_color(mijin_color,"退出炮台确定",mijin_color,"炮台结算界面",x=796,y=428)
                # self.sleep(1)
                for i in range(50):
                    # r1 = self.find_my_color(common_color,"下蹲按钮")
                    # r2 = self.find_my_color(mijin_color,"炮台结算界面")
                    # if r1 and (not r2):
                    #     return True
                    if self.is_text_re_in_ocr(rect=[8, 219, 244, 423], pattern="继续"):
                        return True
                    self.click(634,659,after_sleep=1)
                return False
            else:
                # 判断是否有门，防止游戏bug导致卡死
                if self.is_have_door():
                    print("可能游戏bug！！！")
                    self.level_to_to_next_level()

    def level_other(self):
        # 其他
        # 商店卡死校验
        r1 = self.is_text_re_in_ocr(rect=[85,4,157,57],pattern="烛芯")
        r2 = self.find_my_color(common_color,"左上角红色退出")
        if r1 and r2:
            print("商店卡死，尝试修复----")
            self.click(44,31)
            self.sleep(3)
            return True

        res = self.ocr(rect=[4,0,1272,690])
        if not res:
            self.sleep(0.5)
            return False

        for r in res:
            text = r.text
            if self.re_matching("复苏", text):
                self.click(636,633)
                self.sleep(1)
            elif self.re_matching("(选择1枚烛芯|刷新|探索详情)", text):
                print("选择1枚烛芯")
                self.select_buff()
                self.level_start_time = time.time()
                return True
            elif self.re_matching("(获得遗物|获得烛芯|点击空白处关闭|激活套装|点击空白处继续)", text):
                self.click(154, 510)
                return True
            elif self.re_matching("探索成功", text):
                self.level_finish_count += 1
                self.level_ok_count += 1
                print(f"迷津完成,当前完成次数:{self.level_ok_count}")
                self.ocr_gold()
                self.click(1222, 55)
                self.await_until_ocr(pattern="坠入深渊", time_out=30)
                return True
            elif self.re_matching("探索失败", text):
                print("探索失败")
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.ocr_gold()
                self.click(1222, 55)
                return True
            elif self.re_matching("上次探索过深渊", text):
                self.click(392, 425)
                self.click(1088, 687)
                return True

    def level_rest(self):
        # 休整关卡
        # 判断是否有任务
        point = None
        for i in range(5):
            point = self.find_my_color(mijin_color,"任务")
            if point:
                break
            self.sleep(0.1)

        if point:
            if (self.center_x - 50) < point.x < (self.center_x + 50):
                # self.walk_to_color_disapper(mijin_color,"任务")
                print("中间")
                for i in range(4):
                    self.rotate_view_to_middle_by_color(mijin_color,"任务")
                    self.sleep(0.2)
                    self.walk_to_w()
                    self.sleep(0.2)
            else:
                for i in range(6):
                    self.walk_to_w(1000)
                self.sleep(1)
                self.walk_to_w(500)
                self.sleep(1)
                self.rotate_view_direction_to_front(mijin_color,"任务",2)
                self.sleep(0.5)
                self.rotate_view_to_middle_by_color(mijin_color,"任务")
                self.sleep(1)
                self.walk_to_w(1000*3)
                self.sleep(1)

            r = self.find_my_color(mijin_color,"至暗幽影")
            if r:
                print("前方boss关卡，开始购物")
                status_ = False
                for i in range(20):
                    self.rotate_view_to_middle_by_color(mijin_color,"任务")
                    for k in range(3):
                        res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["多行"],pattern="[烛芯]+")
                        if res:
                            status_ = True
                            break
                        self.sleep(0.5)
                    if status_:
                        break
                    self.walk_to_w(300)
                    self.sleep(0.5)

                if not status_:
                    print("查找商店失败")
                    return False
                
                self.go_to_shop()
            
            self.level_to_to_next_level()
        else:
            # 原来是5
            for i in range(6):
                self.walk_to_w(1000)
            self.sleep(1)
            self.walk_to_w(500)
            self.sleep(1)
            self.level_to_to_next_level()

    def combat(self):
        # 战斗
        # 识别boss
        if self.is_boss() and self.is_boss_door:
            if self.now_boss == "":
                self.now_boss = self.ocr_boss()

        if self.role == '水母':
            self.role_combat_0()
        elif self.role == '夫人':
            self.role_combat_1()
        elif self.role == '止流':
            self.role_combat_2()

    def recognition_level_type(self):
        # 识别当前关卡类型
        level_type = "-1"     # -1：其他 0：战斗 1：前往下一层 2：休整 3：奇遇
        # res = self.ocr(rect=[7,199,255,368])
        res = self.ocr(rect=[8,219,244,423])
        if not res:
            print(f"当前关卡类型：{self.level_type_dict[level_type]}")
            return level_type

        for r in res:
            text = r.text
            if self.re_matching("战斗", text):
                level_type = "0"
                break
            elif self.re_matching("继续", text):
                level_type = "1"
                break
            elif self.re_matching("休整", text):
                level_type = "2"
                break
            elif self.re_matching("(奇遇|篝火)", text):
                level_type = "3"
                break
        
        print(f"当前关卡类型：{self.level_type_dict[level_type]}")
        return level_type

    def rotate_to_combat_door(self):
        # 视角旋转至战斗门口
        combat_doors = ["至暗幽影", "深邃幽影", "离散幽影", "微茫幽影"]
        for i in range(10):
            for combat_door in combat_doors:
                res = self.find_my_color(mijin_color,combat_door)
                if res:
                    return True
            self.rotate_view_to_right(100,dur=500,after_sleep=0.1)

    def is_have_door(self):
        # 判断是否有门
        door_names = ["至暗幽影", "深邃幽影", "离散幽影", "微茫幽影", "休整", "深渊回声"]
        for door_name in door_names:
            res = self.find_my_color(mijin_color,door_name)
            if res:
                return True
            
        print("识别错误，不是找门")
        return False

    def is_map_jam_trees(self):
        # 判断是否卡死树木的地图
        res = self.find_my_color(mijin_color,"卡树地图")
        if res:
            print("卡树地图")
            self.action_jump_fly()
            self.sleep(1)
            self.action_jump_fly()
            return True
        else:
            return False

    def go_to_shop(self):
        # 商店购物
        print("开始商店购物")

        res = None
        for i in range(5):
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["多行"],pattern="[烛芯]+")
            if res:
                break
            self.sleep(0.2)

        if not res:
            print("未识别到商店")
            return False

        x = res[0].x
        y = res[0].y
        res = self.click_until_color(common_color,"左上角红色退出",x,y)
        
        if not res:
            print("进入商店失败")
            return False

        print("开始购买")
        for i in range(100):
            res = self.find_my_color(common_color,"左上角红色退出")
            if res:
                r = self.find_my_color(mijin_color,"商店确认")
                if not r:
                    break

                # 判断是否有钱购买
                n = Colors.count("#DA2A4A-#1c0905",rect=[1117,610,1147,636],sim=0.9)
                if n >10:
                    print("没有钱购买了")
                    break

            for i in range(5):
                self.click(96,173,after_sleep=0.1)
                self.click(1114,659,after_sleep=0.1)

            # 确保返回商店页面
            for i in range(10):
                if self.find_my_color(common_color,"左上角红色退出"):
                    break
                else:
                    self.click(1241,592,after_sleep=0.1)
            self.sleep(0.1)

        for i in range(20):
            self.click(1241,592,after_sleep=0.1)
        
        self.sleep(1)

        for i in range(10):
            if self.find_my_color(common_color,"左上角红色退出"):
                self.click(44,31)
                self.sleep(1)
            else:
                break
        self.sleep(1)
        
        # 校验商店是否退出
        res = self.await_until_ocr(rect=[8,219,244,423], pattern="休整")
        if res:
            print("商店退出成功")
        else:
            print("商店退出异常")

        # for i in range(10):
        #     if self.is_text_re_in_ocr(rect=[8,219,244,423], pattern="休整"):
        #         print("商店退出成功")
        #         break
        #     self.sleep(1)
        #
        #     if res:
        #         print("商店退出异常,重新尝试退出")
        #         self.click(44,31)
        #         self.sleep(3)
        #     else:
        #         print("商店退出成功")
        #         break

        print("购买完成")

        self.level_restart_status = True
        self.level_start_time = time.time()
        
    def quit_mijin_start(self):
        # 暂离重进
        print("暂离重进")
        self.click_color_to_color(common_color,"下蹲按钮",mijin_color,"退出并结算",x=45,y=29)
        self.sleep(1)
        self.click_color_to_color(mijin_color,"退出并结算",mijin_color,"右上角红色退出",x=1104,y=642,out_time=60)
        self.sleep(1)
        self.click_color_to_color(mijin_color,"右上角红色退出",mijin_color,"暂离_继续探索",x=1177,y=614)
        self.sleep(1)
        self.click_color_to_color(mijin_color,"暂离_继续探索",common_color,"下蹲按钮",x=1132,y=653,out_time=60)
        self.sleep(3)
        print("暂离成功")
        self.level_restart_status = True
        self.level_start_time = time.time()
        self.is_map_jam_trees()

    def rotate_view_to_middle_by_color(self, color_dict, color_name, behind=False):
        # 根据颜色旋转视角至中间
        # behind:释放开启后方检测
        start_time = time.time()  # 开始时间，超时则退出
        max_time = 60  # 最大超时时间

        while 1:
            if time.time() - start_time > max_time:
                return False

            point = self.find_my_color(color_dict,color_name)
            if point:
                res = self.position_is_left_or_right(point.x, point.y)
                if behind:
                    if res == 1:
                        return True
                else:
                    if (res == 1) or (res == 3):
                        return True
                if abs(point.x-self.center_x) > 100:
                    # print("大幅度旋转")
                    self.rotate_view_to_close_by_ori(res,rotate_x=100)
                else:
                    self.rotate_view_to_close_by_ori(res)

                # 旋转完之后检查目标是否还在，如果不在则检查
                if color_name in ["微茫幽影","离散幽影"]:
                    r1 = self.find_my_color(color_dict,color_name)
                    r2 = self.find_my_color(mijin_color,"深渊回声")
                    if (not r1) and r2:
                        print("开始旋转至深渊回声")
                        self.rotate_view_to_middle_by_color(mijin_color,"深渊回声")
                        self.walk_to_w(walk_time=1000*5)

            else:
                return False

            self.sleep(0.1)

        return False

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：迷津  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}  获得时之纺线：{self.gold}  当前关卡：{self.now_level}"
        self.logui.change_log_text(text)

    def ocr_gold(self):
        # 结算界面识别时之纺线
        self.sleep(5)
        res = self.ocr(rect=[544,522,744,611])
        if res:
            for r in res:
                text = r.text
                print(text)
                result = re.findall(r"\d+",text)
                print(result)
                if len(result) > 0:
                    gold = int(result[0])
                    print(f"获得时之纺线：{gold}")
                    self.gold += gold
                    break
        self.refresh_log()

    def mijin_moling_boss(self):
        # boss战斗是否释放魔灵
        if time.time() - self.moling_boss_last_time >= self.moling_boss_max_time:
            self.skill_z()
            self.moling_boss_last_time = time.time()

    def mijin_moling_common(self):
        # 普通战斗是否释放魔灵
        if time.time() - self.moling_common_last_time >= self.moling_common_max_time:
            self.skill_z()
            self.moling_common_last_time = time.time()