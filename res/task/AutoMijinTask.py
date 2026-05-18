from ...res.task.BaseTask import BaseTask
from ...res.assets.color import mijin_color, common_color

import threading
import time
import re

from ascript.android import action
from ascript.android.screen import Colors


class AutoMijinTask(BaseTask):
    def __init__(self,uiconfig=None):
        super().__init__()

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

        self.moling_boss_max_time = 5   # boss战斗魔灵最大释放间隔
        self.moling_boss_last_time = 0  # boss战斗魔灵最后一次释放时间

        self.inti_mijin(uiconfig)

    def go_to_mijin(self):
        print("开始前往迷津")
        self.click_color_to_color(common_color,"主界面左上角菜单",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=126,y=415)
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",mijin_color,"历练-迷津",x=46,y=324)
        self.sleep(1)
        self.click_until_ocr(x=1103,y=513,rect=[19,498,1265,693],pattern="(坠入深渊|命运|翻阅手记)")
        self.sleep(1)
        print("成功进入迷津")

    def quit_mijin(self):
        print("开始退出迷津")
        self.click_color_to_color(common_color,"左上角红色退出",mijin_color,"历练-迷津",x=44,y=31)
        self.sleep(1)
        self.click_color_to_color(mijin_color,"历练-迷津",common_color,"主界面左上角菜单",x=44,y=34)
        self.sleep(2)

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
            '1':'夫人'
        }

        if uiconfig:
            self.level_grade = uiconfig['mijin_grade']
            self.level_max_count = int(uiconfig['mijin_max_num'])
            self.role = map_role[uiconfig['mijin_role']]
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

    def run(self):
        self.refresh_log()
        self.go_to_mijin()
        while True:
            # 刷新日志
            self.refresh_log()

            # 复苏
            r = self.find_my_color(mijin_color,"复苏")
            if r:
                print("复苏")
                self.click(636,633)
                self.sleep(1)
                continue

            # 判断当前是否boss战斗
            if self.is_boss():
                self.release_skills()
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
            if self.find_my_color(mijin_color,"右上角战斗红色"):
                self.combat()
                continue

            res = self.ocr(rect=[4,0,1272,690])
            # print(res)
            if not res:
                self.sleep(0.5)
                continue

            for r in res:
                text = r.text
                if self.re_matching("(前往下一层深渊|继续探索)", text):
                    self.walk_to_door()
                    break
                elif self.re_matching("复苏", text):
                    self.click(636,633)
                    self.sleep(1)
                elif text == "战斗":
                    self.combat()
                    break
                elif self.re_matching("(选择1枚烛芯|刷新|探索详情)", text):
                    print("选择1枚烛芯")
                    self.select_buff()
                    self.level_start_time = time.time()
                    break
                elif self.re_matching("(获得遗物|获得烛芯|点击空白处关闭|激活套装|点击空白处继续)", text):
                    self.click(154, 510)
                    break
                elif self.re_matching("探索成功", text):
                    self.level_finish_count += 1
                    self.level_ok_count += 1
                    print(f"迷津完成,当前完成次数:{self.level_ok_count}")
                    self.ocr_gold()
                    self.click(1222, 55)
                    self.await_until_ocr(pattern="坠入深渊", time_out=30)
                    break
                elif self.re_matching("探索失败", text):
                    print("探索失败")
                    self.level_finish_count += 1
                    self.level_faile_count += 1
                    self.ocr_gold()
                    self.click(1222, 55)
                    break
                elif self.re_matching("坠入深渊", text):
                    # 判断当前满足迷津次数
                    if self.level_finish_count >= self.level_max_count:
                        print(f"迷津任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                        self.quit_mijin()
                        return True

                    self.click(r.center_x, r.center_y)
                    self.await_until_ocr(pattern="难度选择", time_out=30)
                    # 选择等级
                    self.select_grade()
                    self.click(1104, 626)
                    self.click(1129, 654)

                    self.now_level = 0
                    self.init_now_level()
                    break
                elif self.re_matching("上次探索过深渊", text):
                    self.click(392, 425)
                    self.click(1088, 687)
                    break

            self.sleep(1)

    def re_matching(self, pattern, text):
        # 使用正则匹配
        return re.findall(re.compile(pattern), text)

    def init_now_level(self):
        # 初始化当前关卡数据
        self.level_start_time = time.time()
        self.level_time_out_count = 0
        self.now_level = self.now_level + 1
        self.level_restart_status = False
        print(f"当前关卡-----{self.now_level}")

    def close_mijin(self):
        # 退出迷津
        print("退出迷津")
        self.click_color_to_color(common_color,"下蹲按钮",mijin_color,"退出并结算",x=45,y=29)
        self.sleep(1)
        self.click_color_to_color(mijin_color,"退出并结算",common_color,"退出委托_确定",x=1207,y=639)
        self.sleep(1)
        self.click_color_to_color(common_color,"退出委托_确定",mijin_color,"迷津结束界面",x=776,y=413,out_time=60)
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

    def release_skills(self):
        if self.role == '水母':
            self.role_combat_0()
        elif self.role == '夫人':
            self.role_combat_1()

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

            if self.find_my_color(common_color,"BOSS处决"):
                print("boss处决")
                self.click(996,248)

            self.auot_lock_enemy()
            self.sleep(0.5)

            self.action_dodge_to_w()
            self.sleep(1)

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
                self.auot_lock_enemy()
                self.sleep(0.5)
                res = self.find_my_color(common_color,"没有子弹")
                if res:
                    print("没有子弹了")
                    for i in range(50):
                        self.mijin_moling_boss()    # 魔灵
                        self.combat_left_click()
                else:
                    for i in range(50):
                        self.mijin_moling_boss()    # 魔灵
                        self.combat_right_click()
        else:
            if self.skill_q_is_ok():
                self.skill_q()
            if self.skill_z_is_ok():
                self.skill_z()
            for i in range(6):
                # 判断是否还在战斗
                r = self.find_my_color(mijin_color,"右上角战斗红色")
                if not r:
                    print("战斗结束")
                    break
                self.skill_e(after_sleep=0.5)
                self.skill_e(after_sleep=0.5)
                x = self.action_button_position["远程攻击"][0]
                y = self.action_button_position["远程攻击"][1]
                self.combat_bullet()
                # self.slide(x,y,x+500,y,1000)
                self.slide(x,y,x+300,y,1000)

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

    def combat(self):
        # 战斗
        if self.find_my_color(mijin_color,"任务"):
            print('有任务-----')
            self.walk_to_task()
            self.level_restart_status = True
        else:
            self.release_skills()

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

    def walk_to_door(self):
        print("开始寻找门口")
        start_time = time.time()
        max_time = 60

        # 校验是否有门，没有门则退出
        if not self.is_have_door():
            return False

        # 判断是否有任务
        point = None
        for i in range(5):
            point = self.find_my_color(mijin_color,"任务")
            if point:
                break
            self.sleep(0.1)
        if point:
            if (self.center_x - 50) < point.x < (self.center_x + 50):
                print("中间---")
                self.walk_to_color_disapper(mijin_color,"任务")
                self.go_to_shop()
            else:
                for i in range(2):
                    self.action_jump_fly()
                    self.sleep(1)

                self.rotate_view_to_middle_by_color(mijin_color,"任务")
                self.sleep(1)
                self.walk_to_w(walk_time=500)
                self.sleep(1)
                
                self.rotate_view_direction_range(mijin_color,"任务",0,250)

                self.sleep(1)
                self.action_jump_fly()
                self.sleep(2)
                self.reset_role_view()
                self.go_to_shop()

        self.rotate_view_to_down(400)

        self.rotate_to_combat_door()

        # if not self.level_restart_status:
        #     self.quit_mijin_start()

        door_names = ["至暗幽影", "深邃幽影", "离散幽影", "微茫幽影", "休整"]
        for door_name in door_names:
            while 1:
                if time.time() - start_time > max_time:
                    return False

                if door_name == "至暗幽影":
                    r1 = self.find_my_color(mijin_color,"至暗幽影")
                    point = self.find_my_color(mijin_color,"任务")
                    # print(f"至暗幽影---{r1}---{point}")
                    if point and r1:
                        if (self.center_x - 50) < point.x < (self.center_x + 50):
                            print("中间---")
                            self.walk_to_color_disapper(mijin_color,"任务")
                            self.go_to_shop()
                        else:
                            for i in range(2):
                                self.action_jump_fly()
                                self.sleep(1)

                            self.rotate_view_to_middle_by_color(mijin_color,"任务")
                            self.sleep(1)
                            self.walk_to_w(walk_time=500)
                            self.sleep(1)

                            self.rotate_view_direction_range(mijin_color,"任务",0,250)
                            self.sleep(1)
                            self.action_jump_fly()
                            self.sleep(2)
                            self.reset_role_view()
                            self.go_to_shop()

                    else:
                        res = self.rotate_view_to_middle_by_color(mijin_color,door_name)
                        if not res:
                            break

                        self.walk_to_w()
                        self.sleep(0.5)
                else:
                    res = self.rotate_view_to_middle_by_color(mijin_color,door_name)
                    if not res:
                        break
                    self.walk_to_w()
                    self.sleep(0.5)

                res = self.ocr(pattern=door_name)
                if res:
                    x = res[0].center_x
                    y = res[0].center_y
                    self.click(x, y)
                    if door_name == "休整":
                        pattern = "休整"
                    else:
                        pattern = "战斗"
                    res = self.await_until_ocr(pattern=pattern, rect=[16,197,206,328])
                    if res:
                        print(f"成功进入---{door_name}")
                        if door_name == "至暗幽影":
                            pass
                        self.init_now_level()
                        self.is_map_jam_trees()
                        return True

                self.sleep(0.1)

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
            return
            False

    def go_to_shop(self):
        # 商店购物
        print("开始商店购物")
        self.sleep(2)
        r = None
        for i in range(2):
            r = self.await_until_click_ocr(pattern="烛芯兑换",time_out=5)
            if r:
                break
            else:
                self.walk_to_w(walk_time=300)
                self.sleep(1)

        if not r:
            print("未识别到商店")
            return False
        
        r = self.await_color(mijin_color,"右上角红色退出")
        if not r:
            print("进入商店失败")
            return False

        print("开始购买")
        for i in range(100):
            r = self.find_my_color(mijin_color,"商店确认")
            if not r:
                break

            # 判断是否有钱购买
            n = Colors.count("#DA2A4A-#1c0905",rect=[1117,610,1147,636],sim=0.9)
            if n >10:
                print("没有钱购买了")
                break
            
            self.click(1112,654)
            self.click(1241,592)
            self.click(1241,592)
            self.click_until_color(mijin_color,"右上角红色退出",1241,592)
            self.sleep(1)

        self.click_until_color(mijin_color,"右上角红色退出",1241,592)
        self.click_color_to_color(mijin_color,"右上角红色退出",common_color,"下蹲按钮",x=44,y=31)
        self.sleep(1)
        
        # 校验商店是否退出
        for i in range(5):
            res = self.find_my_color(mijin_color,"右上角红色退出")
            if res:
                print("商店退出异常,重新尝试退出")
                self.click(44,31)
                self.sleep(3)
            else:
                print("商店退出成功")
                break

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

    def mijin_moling_boss(self):
        # boss战斗是否释放魔灵
        if time.time() - self.moling_boss_last_time >= self.moling_boss_max_time:
            self.skill_z()
            self.moling_boss_last_time = time.time()