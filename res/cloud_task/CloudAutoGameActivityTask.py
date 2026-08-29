from ...res.cloud_task.CloudBaseTask import CloudBaseTask
from ...res.assets.cloud_color import *
import re


class CloudAutoGameActivityTask(CloudBaseTask):
    # 云-活动
    def __init__(self, uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '云-活动'
        self.game_activity_name = '狩月人之阶'

        self.level_role = '自定义'  # 主控角色
        self.level_max_score = 0  # 最高分

        self.level_max_count = 2  # 最大探索次数
        self.level_finish_count = 0  # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0  # 探索失败次数

        self.level_skill_e_time = 10  # 技能释放间隔
        self.level_skill_e_count = 1  # 技能释放次数
        self.level_skill_e_last_time = 0  # 最后一次释放技能时间
        self.level_skill_q_time = 10  # 大招释放间隔
        self.level_skill_q_count = 1  # 大招释放次数
        self.level_skill_q_last_time = 0  # 最后一次释放大招时间
        self.level_skill_z_time = 10  # 魔灵释放间隔
        self.level_skill_z_count = 1  # 魔灵释放次数
        self.level_skill_z_last_time = 0  # 最后一次释放魔灵时间

        self.is_lock_enemy = False  # 是否索敌
        self.rotate_view_to_down_count = 0  # 向下旋转视角次数

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
        self.game_activity_name = self.uiconfig['game_activity_name']
        self.level_grade = int(self.uiconfig['game_activity_grade'])
        self.level_max_count = int(self.uiconfig['game_activity_max_num'])
        self.level_skill_z_time = float(self.uiconfig['game_activity_skill_z_time'])
        self.level_skill_z_count = int(self.uiconfig['game_activity_skill_z_count'])

        # 主控角色（与本地活动共用 game_activity_role，取值 7-4/2-4/3-4/8-4）
        role_base = self.uiconfig['game_activity_role']
        role_name_map = {"7-4": "煜明", "2-4": "止流", "3-4": "苏乙", "8-4": "芙洛拉"}
        self.level_role = role_name_map.get(role_base, "自定义")

        # 分组赛=-1 / 常规(纪念币)=-2
        mode = "1" if self.uiconfig['game_activity_get_score'] == 'on' else "2"
        self.skill_type = f"{role_base}-{mode}"

        self.cloud_role_skill_util.init_config(self.skill_type)
        self.apply_skill_z()

        print(f"主控角色：{self.level_role}  技能模组：{self.skill_type}")

    def apply_skill_z(self):
        # 注入 UI 配置的魔灵间隔/次数
        skill_config = {
            "skill_z_max_time": self.level_skill_z_time,
            "skill_z_max_count": self.level_skill_z_count,
        }
        self.cloud_role_skill_util.add_skill_z(skill_config)

    def select_level_grade(self):
        # 选择等级
        if self.uiconfig['game_activity_get_score'] == "on":
            self.click(153,260)
        else:
            if self.level_grade == 60:
                self.click(157,118)
            elif self.level_grade == 75:
                self.click(157,179)
            elif self.level_grade == 110:
                self.click(153,260)
            elif self.level_grade == 150:
                self.click(150,314)
        self.sleep(1)

    def init_skill_time(self):
        # 重置技能时间
        self.level_skill_e_last_time = 0
        self.level_skill_q_last_time = 0
        self.level_skill_z_last_time = 0

        self.cloud_role_skill_util.set_role_skill_config()
        self.apply_skill_z()

    def go_to_level(self):
        # 前往副本
        print(f"开始前往---{self.game_activity_name}")
        self.click_until_color_vanish(cloud_common_color, "角色血条-绿色", x=81, y=34)
        self.sleep(2)
        self.click_until_color(cloud_common_color, "左上角红色退出", x=384, y=270)
        self.sleep(2)

        res = None
        for i in range(3):
            for i in range(5):
                res = self.is_text_re_in_ocr(rect=[26,77,282,645], pattern="(狩月|之阶)")
                if res:
                    break
                self.sleep(0.5)
            if res:
                break
            else:
                self.slide(131,566, 136,142, dur=500)
                self.sleep(2)
        if not res:
            print("没有找到--{self.game_activity_name}，退出")
            self.click_until_color_vanish(cloud_common_color, "左上角红色退出", x=95, y=31)
            self.sleep(2)

            for i in range(3):
                self.click(735, 669)

            res = self.find_my_color(cloud_common_color, "角色血条-绿色")
            if res:
                print("成功返回主界面")
            else:
                print("返回主界面失败")

            return False

        x = res[0].x
        y = res[0].y

        self.click_until_ocr(x=x, y=y, rect=[910,74,1217,155], pattern="(狩月|之阶)")
        self.sleep(1)

        # 分组赛凹分
        if self.uiconfig['game_activity_get_score'] == 'on':
            self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_前往", cloud_game_activity_color,"狩月人之阶_分组赛_主界面", x=1036, y=684),
        else:
            self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_前往", cloud_game_activity_color,"狩月人之阶_主界面_狩月纪念币", x=1036, y=684)
        self.sleep(2)
        print(f"成功进入---{self.game_activity_name}")
        return True

    def go_in_level(self):
        # 进入副本
        self.init_skill_time()
        self.is_lock_enemy = False
        self.rotate_view_to_down_count = 0

        print(f"开始进入副本---")
        # 分组赛凹分
        if self.uiconfig['game_activity_get_score'] == 'on':
            res = self.find_my_color(cloud_game_activity_color, "狩月人之阶_分组赛_主界面")
            if res:
                self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_分组赛_主界面", cloud_common_color,"角色血条-绿色", x=1079, y=675, out_time=60)
                self.sleep(2)
                print("成功进入副本")
                return True

            res = self.find_my_color(cloud_game_activity_color, "狩月人之阶_挑战完成")
            if res:
                self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_挑战完成", cloud_common_color, "角色血条-绿色",x=520, y=669, out_time=60)
                self.sleep(2)
                print("成功进入副本")
                return True
        else:
            res = self.find_my_color(cloud_game_activity_color, "狩月人之阶_主界面_狩月纪念币")
            if res:
                self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_主界面_狩月纪念币", cloud_common_color,"角色血条-绿色", x=1079, y=675, out_time=60)
                self.sleep(2)
                print("成功进入副本")
                return True

            res = self.find_my_color(cloud_game_activity_color, "狩月人之阶_挑战完成")
            if res:
                self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_挑战完成", cloud_common_color, "角色血条-绿色",x=520, y=669, out_time=60)
                self.sleep(2)
                print("成功进入副本")
                return True

        return False

    def go_to_activate_level(self):
        # 前往激活任务
        print("开始前往激活任务")
        for i in range(20):
            res = self.find_my_color(cloud_game_activity_color, "狩月人之阶_开始战斗")
            if res:
                print("激活任务成功")
                return True
            res = self.rotate_view_to_middle_by_color(cloud_common_color, "任务黄色图标")
            if not res:
                print("没有找到黄色")
                return True
            self.action_jump_fly()
            self.sleep(0.5)

        return False

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        self.click(81, 29)
        self.click(1143, 641)
        self.click_until_color(cloud_game_activity_color, "狩月人之阶_挑战完成", x=779, y=413, out_time=60)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        # 分组赛凹分
        if self.uiconfig['game_activity_get_score'] == 'on':
            res = self.find_my_color(cloud_game_activity_color, "狩月人之阶_挑战完成")
            if res:
                self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_挑战完成", cloud_game_activity_color,"狩月人之阶_分组赛_主界面", x=758, y=668, out_time=60)
                self.sleep(1)

            self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_分组赛_主界面", cloud_common_color, "角色血条-绿色",x=81, y=32, out_time=20)
            self.sleep(2)
        else:
            res = self.find_my_color(cloud_game_activity_color, "狩月人之阶_挑战完成")
            if res:
                self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_挑战完成", cloud_game_activity_color,"狩月人之阶_主界面_狩月纪念币", x=758, y=668, out_time=60)
                self.sleep(1)

            self.click_color_to_color(cloud_game_activity_color, "狩月人之阶_主界面_狩月纪念币", cloud_common_color,"角色血条-绿色", x=81, y=32, out_time=20)
            self.sleep(2)

        res = self.find_my_color(cloud_common_color, "角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def get_score(self):
        # 获取分数
        print("开始识别分数")
        score = -1

        res = self.ocr(rect=[422,260,885,383])
        if res:
            for r in res:
                text = r.text
                print(text)
                result = re.findall(r"\d+", text)
                print(result)
                if len(result) > 0:
                    n = int(result[0])
                    score = n
                    break
        print(f"当前分数：{score}")
        if score > self.level_max_score:
            self.level_max_score = score

    def combat_befor(self):
        # 战斗前准备（开场连招委派给技能模组）
        self.cloud_role_skill_util.combat_before()

    def combat(self):
        # 战斗（统一循环：判断挑战完成，否则逐帧委派技能模组）
        print("开始战斗")
        self.cloud_role_skill_util.combat_start()

        while 1:
            res = self.find_my_color(cloud_game_activity_color, "狩月人之阶_挑战完成")
            if res:
                print("挑战成功")
                self.sleep(1)
                self.get_score()
                return True

            self.cloud_role_skill_util.combat()

    def level_skill_z_is_ok(self):
        # 魔灵是否可以释放
        if self.level_skill_z_time < 0:
            return False

        if self.time() - self.level_skill_z_last_time >= self.level_skill_z_time:
            return True
        else:
            return False

    def level_skill_z(self):
        # 释放魔灵
        for i in range(self.level_skill_z_count):
            self.skill_z(after_sleep=0.3)

        self.level_skill_z_last_time = self.time()


    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}-{self.game_activity_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}  最高分：{self.level_max_score}"
        self.logui.change_log_text(text)

    def run(self):
        self.init_task()
        self.refresh_log()

        res = self.go_to_level()
        if not res:
            return False

        self.select_level_grade()

        while 1:
            self.refresh_log()

            print(f"计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")

            if self.level_finish_count >= self.level_max_count:
                print(f"任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                self.level_exit()
                return True

            # 判断是否需要整点去执行密函
            # if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
            #     res = self.is_refresh_time_execute_mihan()
            #     if res:
            #         self.level_exit()
            #         return True

            self.go_in_level()
            self.combat_befor()

            res = self.go_to_activate_level()
            if not res:
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
                continue

            res = self.combat()
            if res:
                self.sleep(2)
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                self.level_finish_count += 1
                self.level_faile_count += 1