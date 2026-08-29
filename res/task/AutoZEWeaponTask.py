from ...res.task.BaseTask import BaseTask
from ...res.assets.color import *

from ascript.android import system

import re


class AutoZEWeaponTask(BaseTask):
    # 灾厄武器
    def __init__(self, uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '灾厄武器'

        self.level_type = None  # 模式
        self.level_property = None  # 属性
        self.level_max_count = 0  # 副本执行次数

        self.level_model_type = "探险"

        self.level_max_grade = 0  # 打到多少级
        self.now_level_grade = 0  # 当前等级

        self.level_finish_count = 0  # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0  # 探索失败次数

        self.init_task()
        self.set_skill_config()

    def set_skill_config(self):
        # 初始化技能配置
        skill_model = self.uiconfig.get('ze_weapon_role', '0')
        if self.level_model_type == "扼守":
            if skill_model == "8-2":
                skill_model = "8-2-2"

        self.role_skill_util.init_config(skill_model)

    def rotate_view_to_middle_by_color(self, color_dict, color_name):
        # 根据颜色旋转视角至中间
        start_time = self.time()  # 开始时间，超时则退出
        max_time = 60  # 最大超时时间

        while 1:
            if self.time() - start_time > max_time:
                return False

            point = self.find_my_color(color_dict, color_name)
            if point:
                res = self.position_is_left_or_right(point.x, point.y)
                if (res == 1) or (res == 3):
                    return True
                if abs(point.x - self.center_x) > 100:
                    self.rotate_view_to_close_by_ori(res, rotate_x=100)
                else:
                    self.rotate_view_to_close_by_ori(res)
            else:
                return False

            self.sleep(0.1)

        return False

    def init_task(self):
        # 初始化
        self.level_type = int(self.uiconfig['ze_weapon_level'])
        self.level_max_count = int(self.uiconfig['ze_weapon_max_num'])
        self.level_max_grade = int(self.uiconfig['ze_weapon_max_grade'])
        self.level_property = self.uiconfig['ze_weapon_property']
        self.level_model_type = self.uiconfig['ze_weapon_level_type']

        if self.level_type == 1:
            self.level_max_grade = 999999

        if self.uiconfig["ze_weapon_semi_automatic"] == "on":
            self.level_max_grade = 99999

    def go_to_level(self):
        # 前往副本
        print(f"开始前往{self.task_name}副本")
        self.go_to_lilian()
        self.sleep(1)
        self.click_color_to_color(common_color, "历练委托菜单", ze_weapon_color, "历练菜单-深境委托", x=1200, y=652)
        self.sleep(1)

        x = None
        y = None
        if self.level_model_type == "探险":
            x = 535
            y = 434
        elif self.level_model_type == "扼守":
            x = 726
            y = 336

        self.click_color_to_color(ze_weapon_color, "历练菜单-深境委托", ze_weapon_color, "副本开始菜单", x=x, y=y)
        self.sleep(1)
        print(f"成功进入{self.task_name}副本选择界面")

    def select_property(self):
        # 选择属性
        if self.level_property == '水':
            self.click(723,616)
        elif self.level_property == '火':
            self.click(824,611)
        elif self.level_property == '风':
            self.click(922,612)
        elif self.level_property == '雷':
            self.click(1021,611)
        elif self.level_property == '光':
            self.click(1120,611)
        elif self.level_property == '暗':
            self.click(1221,612)

        self.sleep(2)

    def go_in_level(self):
        # 进入副本
        if (self.level_type == 2) or (self.level_type == 0):
            # 房主/单人
            res = self.find_my_color(common_color, "副本退出-再次进行")
            if res:
                self.click_color_to_color(common_color, "副本退出-再次进行", common_color, "角色血条-绿色", x=1141, y=672, out_time=60)
                self.sleep(1)

            self.go_to_level()
            self.select_property()

            print(f"开始进入副本---{self.task_name}")
            res = self.find_my_color(ze_weapon_color, "副本开始菜单")
            if res:
                self.click_color_to_color(ze_weapon_color, "副本开始菜单", ze_weapon_color, "深境罗盘选择界面", x=1073, y=673)
                self.sleep(3)

            xy = self.get_small_tickets_location()
            if xy:
                self.click(x=xy[0], y=xy[1], after_sleep=1)
                self.click_color_to_color(ze_weapon_color, "深境罗盘选择界面", common_color, "角色血条-绿色", x=1144, y=541, out_time=60)
                self.sleep(2)
            else:
                print("查找罗盘失败！！！")
                self.click(945, 542)
                self.sleep(2)
                return False
        else:
            max_time = 60 * 10
            start_time = self.time()
            while 1:
                if self.time() - start_time > max_time:
                    print("进入副本超时")
                    system.exit()

                res = self.find_my_color(ze_weapon_color, "队友-副本开始确认")
                if res:
                    print("同意进入副本----")
                    self.click(872,180,after_sleep=2)
                    self.click(590,423, after_sleep=2)
                    self.click(858, 100,after_sleep=3)

                res = self.is_text_re_in_ocr(rect=[22, 226, 252, 337], pattern="(血清)")
                if res:
                    print("开始战斗")
                    for i in range(1):
                        self.action_jump_fly()
                        self.sleep(1)
                    break

        # 重置技能时间
        self.role_skill_util.set_role_skill_config()

        print("成功进入副本")
        return True

    def go_to_activate_level(self):
        # 前往激活任务
        if self.level_model_type == "探险":
            return self.go_to_activate_level_tanxian()
        elif self.level_model_type == "扼守":
            return self.go_to_activate_level_esho()

    def go_to_activate_level_tanxian(self):
        # 前往激活任务-探险
        if (self.level_type == 2) or (self.level_type == 0):
            self.walk_to_w(1000 * 2)
            self.sleep(1)

            for i in range(20):
                self.rotate_view_to_middle_by_color(common_color, "任务黄色图标")
                self.walk_to_w(300)
                self.sleep(1)
                res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"], pattern="操作")
                if res:
                    break

            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"], pattern="操作")
            if not res:
                print("激活副本失败")
                return False

            res = self.unlocking()
            if not res:
                return False

            res = self.check_is_combat()
            if not res:
                return False

        # 队友直接返回True
        return True

    def go_to_activate_level_esho(self):
        # 前往激活任务-扼守
        for i in range(4):
            self.action_jump_fly(after_sleep=1.5)
        self.sleep(1)
        self.walk_to_a(400)
        self.sleep(1)
        for i in range(3):
            self.action_jump_fly(after_sleep=1.5)
        self.sleep(1)
        self.walk_to_d(1000*2)
        self.sleep(1)
        self.walk_to_w(1000 * 2)
        self.sleep(1)

        for i in range(10):
            self.rotate_view_to_middle_by_color(common_color, "任务黄色图标")
            self.walk_to_w(300)
            self.sleep(1)
            res = self.is_text_re_in_ocr(rect=[9,224,250,380], pattern="(保护|探险家|皎皎|波次)")
            if res:
                print("副本激活成功")
                return True

        print("激活失败")
        return False

    def check_is_combat(self):
        # 判断是否成功进入战斗
        res = self.await_until_ocr(rect=[22, 226, 252, 337], pattern="(血清)", time_out=10)
        if res:
            print("激活副本成功")
            return True
        else:
            print("激活副本失败")
            return False

    def unlocking(self):
        # 开锁
        res = self.click_until_ocr(796, 360, rect=[1062, 541, 1154, 624], pattern="快速")
        if not res:
            print("开锁失败")
            self.click(1227, 44)
            self.sleep(2)
            return False
        self.sleep(1)
        self.click(1106, 581)
        self.sleep(2)

        print("开锁成功")
        return True

    def get_small_tickets_location(self):
        # 获取最低等级的门票位置
        print("获取最低等级的门票位置")

        small_grade = 9999
        small_grade_location = None

        res = self.ocr(rect=[523, 206, 1257, 514])
        if res:
            for r in res:
                text = r.text
                result = re.findall(r"\d+", text)
                if len(result) > 0:
                    n = int(result[0])
                    if n < small_grade:
                        small_grade = n
                        small_grade_location = (r.center_x, r.center_y)

        print(f"获取结果：\n等级：{small_grade}\n位置：{small_grade_location}")
        if small_grade_location:
            self.now_level_grade = small_grade
            self.refresh_log()

        return small_grade_location

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        res = self.find_my_color(ze_weapon_color, "队友-副本结束")
        if res:
            print("结束界面")
            self.click_color_to_color(ze_weapon_color, "队友-副本结束", common_color, "副本退出-再次进行", x=392, y=526, out_time=60),675
            self.sleep(3)
            return True
        self.click_color_to_color(common_color, "角色血条-绿色", common_color, "地图esc界面", x=40, y=29)
        self.sleep(1)
        self.click_color_to_color(common_color, "地图esc界面", common_color, "退出委托-确定", x=1189, y=639)
        self.sleep(1)
        self.click_color_to_color(common_color, "退出委托-确定", common_color, "副本退出-再次进行", x=777, y=412, out_time=60)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(ze_weapon_color, "队友-副本结束")
        if res:
            self.click_color_to_color(ze_weapon_color, "队友-副本结束", common_color, "角色血条-绿色", x=1141, y=672,out_time=60)
            self.sleep(1)

        # res = self.find_my_color(role_tupo_color, "委托-探险")
        # if res:
        #     self.click_color_to_color(role_tupo_color, "委托-探险", common_color, "左上角红色退出", x=44, y=32,
        #                               out_time=60)
        #     self.sleep(1)
        #
        # self.click_color_to_color(common_color, "左上角红色退出", common_color, "主界面左上角菜单", x=43, y=34)
        # self.sleep(2)

        for i in range(3):
            self.click(778, 684)

        res = self.find_my_color(common_color, "角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def combat(self):
        # 战斗
        print("开始战斗")
        if self.level_model_type == "探险":
            return self.combat_tanxian()
        elif self.level_model_type == "扼守":
            return self.combat_esho()

    def combat_tanxian(self):
        # 战斗
        print("探险战斗")

        if self.uiconfig["ze_weapon_semi_automatic"] != "on":
            # 全自动
            # 先复位
            self.role_restoration()
            self.await_until_ocr(rect=[22, 226, 252, 337], pattern="(血清)", time_out=10)

            self.walk_to_a(walk_time=1000*3)
            self.walk_to_s(walk_time=1000*21)
            self.sleep(0.5)
            if self.uiconfig["ze_weapon_role"] == "5-2":
                # 猪妹
                self.walk_to_w(walk_time=1000*2)
                self.sleep(0.5)
                self.rotate_view_to_right(slide_distance=100, after_sleep=0.5)
            elif self.uiconfig["ze_weapon_role"] == "7-1":
                # 煜明
                self.walk_to_w(walk_time=500)
                self.sleep(0.5)
                self.walk_to_s(walk_time=300)
            else:
                self.walk_to_w(walk_time=500)
            self.sleep(0.5)

        start_time = self.time()

        max_time = 60 * 9999

        while 1:
            res = self.find_my_color(ze_weapon_color, "队友-副本结束")
            if res:
                res = self.is_text_re_in_ocr(rect=[1016,628,1268,714],pattern="退出")
                if res:
                    print("战斗失败结束----队友-副本结束")
                    self.click_color_to_color(ze_weapon_color, "队友-副本结束", common_color, "角色血条-绿色", x=1143, y=675, out_time=60)
                    self.sleep(1)
                    return True

            res = self.find_my_color(common_color, "副本退出-再次进行")
            if res:
                res = self.is_text_re_in_ocr(rect=[1016, 628, 1268, 714], pattern="退出")
                if res:
                    print("战斗失败结束----副本退出-再次进行")
                    self.click_color_to_color(common_color, "副本退出-再次进行", common_color, "角色血条-绿色", x=1143, y=675, out_time=60)
                    self.sleep(1)
                    return True

            if self.time() - start_time > max_time:
                return False

            # 死亡检测
            if self.is_text_re_in_ocr(rect=[535,618,751,652],pattern="复苏"):
                print("死亡，复活")
                self.click(638,635,after_sleep=5)

                # 等待复活
                self.await_until_color(color_dict=common_color, color_name="角色血条-绿色",time_out=9)

                # 重置技能时间
                self.role_skill_util.set_role_skill_config()

            if self.level_type == 2:
                # 单人模式
                res = self.find_my_color(ze_weapon_color, "行动抉择")
            else:
                res = self.find_my_color(ze_weapon_color, "多人模式-行动抉择")
            if res:
                self.sleep(1)
                res = self.is_text_re_in_ocr(rect=[125,393,1155,693],pattern="(撤离|继续|挑战)")
                if not res:
                    continue

                print(f"波次完成，当前等级：{self.now_level_grade}/{self.level_max_grade}")

                if self.now_level_grade >= self.level_max_grade:
                    if self.level_type == 2:
                        # 单人模式
                        self.click_color_to_color(ze_weapon_color, "行动抉择", common_color, "副本退出-再次进行", x=397,y=463, out_time=60)
                        self.sleep(3)
                        return True
                    else:
                        # 多人模式
                        self.click_color_to_color(ze_weapon_color, "多人模式-行动抉择", common_color, "副本退出-再次进行", x=401,y=518, out_time=60)
                        self.sleep(3)
                        return True
                else:
                    if self.level_type == 2:
                        # 单人模式
                        self.click(x=909, y=463)
                        self.sleep(1)
                    else:
                        # 多人模式
                        self.click(x=902, y=516)
                        self.sleep(1)
                    # 等待返回游戏
                    for i in range(20):
                        res1 = self.is_text_re_in_ocr(rect=[22, 226, 252, 337], pattern="血清")
                        res2 = self.is_text_re_in_ocr(rect=[1016, 628, 1268, 714], pattern="退出")
                        if res1 or res2:
                            break
                        self.sleep(1)

                    start_time = self.time()
                    self.now_level_grade += 5
                    self.refresh_log()

            # 释放技能
            self.role_skill_util.combat()

            self.sleep(0.1)

    def combat_esho(self):
        # 战斗
        print("扼守战斗")

        start_time = self.time()

        max_time = 60 * 9999

        while 1:
            res = self.find_my_color(ze_weapon_color, "队友-副本结束")
            if res:
                res = self.is_text_re_in_ocr(rect=[1016,628,1268,714],pattern="退出")
                if res:
                    print("战斗失败结束----队友-副本结束")
                    self.click_color_to_color(ze_weapon_color, "队友-副本结束", common_color, "角色血条-绿色", x=1143, y=675, out_time=60)
                    self.sleep(1)
                    return True

            res = self.find_my_color(common_color, "副本退出-再次进行")
            if res:
                res = self.is_text_re_in_ocr(rect=[1016, 628, 1268, 714], pattern="退出")
                if res:
                    print("战斗失败结束----副本退出-再次进行")
                    self.click_color_to_color(common_color, "副本退出-再次进行", common_color, "角色血条-绿色", x=1143, y=675, out_time=60)
                    self.sleep(1)
                    return True

            if self.time() - start_time > max_time:
                return False

            # 死亡检测
            if self.is_text_re_in_ocr(rect=[535,618,751,652],pattern="复苏"):
                print("死亡，复活")
                self.click(638,635,after_sleep=5)

                # 等待复活
                self.await_until_color(color_dict=common_color, color_name="角色血条-绿色",time_out=9)

                # 重置技能时间
                self.role_skill_util.set_role_skill_config()

            if self.level_type == 2:
                # 单人模式
                res = self.find_my_color(ze_weapon_color, "行动抉择")
            else:
                res = self.find_my_color(ze_weapon_color, "多人模式-行动抉择")
            if res:
                self.sleep(1)
                res = self.is_text_re_in_ocr(rect=[125,393,1155,693],pattern="(撤离|继续|挑战)")
                if not res:
                    continue

                print(f"波次完成，当前等级：{self.now_level_grade}/{self.level_max_grade}")

                if self.now_level_grade >= self.level_max_grade:
                    if self.level_type == 2:
                        # 单人模式
                        self.click_color_to_color(ze_weapon_color, "行动抉择", common_color, "副本退出-再次进行", x=397,y=463, out_time=60)
                        self.sleep(3)
                        return True
                    else:
                        # 多人模式
                        self.click_color_to_color(ze_weapon_color, "多人模式-行动抉择", common_color, "副本退出-再次进行", x=401,y=518, out_time=60)
                        self.sleep(3)
                        return True
                else:
                    if self.level_type == 2:
                        # 单人模式
                        self.click(x=909, y=463)
                        self.sleep(1)
                    else:
                        # 多人模式
                        self.click(x=902, y=516)
                        self.sleep(1)
                    # 等待返回游戏
                    for i in range(20):
                        res1 = self.is_text_re_in_ocr(rect=[9,224,250,380], pattern="(保护|探险家|皎皎|波次)")
                        res2 = self.is_text_re_in_ocr(rect=[1016, 628, 1268, 714], pattern="退出")
                        if res1 or res2:
                            break
                        self.sleep(1)

                    start_time = self.time()
                    self.now_level_grade += 5
                    self.refresh_log()

            # 释放技能
            self.role_skill_util.combat()

            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}   当前副本等级：{self.now_level_grade}  成功：{self.level_ok_count}  失败：{self.level_faile_count}"
        self.logui.change_log_text(text)

    def run(self):
        self.refresh_log()

        if self.uiconfig["ze_weapon_semi_automatic"] == "on":
            # 半自动
            self.combat()
            return True

        # if (self.level_type == 2) or (self.level_type == 0):
        #     # 房主/单人模式
        #     self.go_to_level()
        #     self.select_property()

        while 1:
            self.refresh_log()

            print(f"计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")

            if self.level_finish_count >= self.level_max_count:
                print(f"任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                self.level_exit()
                return True

            res = self.go_in_level()
            if not res:
                continue

            res = self.go_to_activate_level()
            if not res:
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
                continue

            res = self.combat()
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                print("战斗超时")
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
