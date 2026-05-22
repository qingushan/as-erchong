from ...res.cloud_task.CloudBaseTask import CloudBaseTask
from ...res.assets.cloud_color import *


class CloudAutoRoleBreakthroughTask(CloudBaseTask):
    # 云-角色突破

    def __init__(self, uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = "云-角色突破"

        self.level_grade = 10  # 副本等级
        self.level_boci = 1  # 波次
        self.level_property = "水"  # 副本属性
        self.level_max_count = 2  # 最大探索次数

        self.now_level_boci = 1  # 当前波次,默认1

        self.level_more_award = 0  # 委托手册
        self.level_more_award_boci = []  # 使用委托手册的轮次

        self.level_finish_count = 0  # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0  # 探索失败次数

        self.level_skill_e_time = 10  # 技能释放间隔
        self.level_skill_e_count = 1  # 技能释放次数
        self.level_skill_e_last_time = 0  # 最后一次释放技能时间
        self.level_skill_q_time = 10  # 大招释放间隔
        self.level_skill_q_count = 1  # 大招释放次数
        self.level_skill_q_last_time = 0  # 最后一次释放大招时间

        self.moling_info = {
            "地图":-1,
            "魔灵出现次数":0,
            "魔灵抓取成功次数":0,
        }
        self.init_task()

    def set_skill_config(self):
        # 初始化云游戏技能配置
        self.cloud_role_skill_util.init_config(self.uiconfig.get("role_tupo_role_skill", "0"))

    def set_role_skill_config_custom(self):
        # 构建自定义技能配置传入【云游戏角色技能搓招】
        skill_config = {
            "skill_q_max_time": self.level_skill_q_time,
            "skill_q_max_count": self.level_skill_q_count,
            "skill_e_max_time": self.level_skill_e_time,
            "skill_e_max_count": self.level_skill_e_count,
            "skill_z_max_time": float(self.uiconfig.get("role_tupo_skill_z_time", 30)),
            "skill_z_max_count": int(self.uiconfig.get("role_tupo_skill_z_count", 1)),
        }
        self.cloud_role_skill_util.set_role_skill_config_custom(skill_config)

    def init_task(self):
        # 初始化
        self.level_grade = int(self.uiconfig["role_tupo_grade"])
        self.level_max_count = int(self.uiconfig["role_tupo_max_num"])
        self.level_boci = int(self.uiconfig["role_tupo_boci_num"])
        self.level_property = self.uiconfig["role_tupo_property"]
        self.level_skill_e_time = float(self.uiconfig["role_tupo_skill_e_time"])
        self.level_skill_e_count = int(self.uiconfig["role_tupo_skill_e_count"])
        self.level_skill_q_time = float(self.uiconfig["role_tupo_skill_q_time"])
        self.level_skill_q_count = int(self.uiconfig["role_tupo_skill_q_count"])

        self.set_skill_config()
        self.set_role_skill_config_custom()

        self.level_more_award = int(self.uiconfig["role_tupo_level_more_award"])
        str_ = self.uiconfig["role_tupo_level_more_award_boci"]
        str_ = str_.replace("，", ",")
        if str_ == "-1":
            self.level_more_award_boci = list(range(1, self.level_boci + 1))
        elif "," not in str_:
            self.level_more_award_boci.append(int(str_))
        else:
            list_ = str_.split(",")
            for i in list_:
                self.level_more_award_boci.append(int(i))
        print(f"当前委托手册:{self.level_more_award}")
        print(f"使用委托手册的轮次:{self.level_more_award_boci}")

    def set_moling_config(self):
        # 抓取魔灵配置
        print("抓取魔灵，更改配置")
        self.level_grade = 10
        self.level_boci = 2
        self.level_skill_e_time = 1
        self.level_skill_e_count = 1
        self.level_skill_q_time = 999999
        self.uiconfig["role_tupo_action_crouch"] = "on"
        self.set_role_skill_config_custom()
        print("更改完成")

    def init_skill_time(self):
        # 重置技能时间
        self.level_skill_e_last_time = 0
        self.level_skill_q_last_time = 0
        self.cloud_role_skill_util.set_role_skill_config()

    def check_use_level_more_award(self):
        # 检查当前轮次是否需要使用委托手册
        if self.now_level_boci in self.level_more_award_boci:
            # 使用
            self.use_level_more_award(self.level_more_award)
        else:
            # 不使用
            self.use_level_more_award(0)

    def go_to_level(self):
        # 前往副本
        print(f"开始前往{self.task_name}副本")
        self.click_until_color_vanish(cloud_common_color, "角色血条-绿色", x=81, y=34)
        self.sleep(2)
        self.click_until_color(cloud_common_color, "左上角红色退出", x=172, y=411)
        self.sleep(1)
        self.click_color_to_color(cloud_common_color,"左上角红色退出",cloud_common_color,"历练委托菜单",x=96,y=186)
        self.sleep(1)
        self.click_color_to_color(cloud_common_color,"历练委托菜单",cloud_role_tupo_color,"委托-探险",x=1138,y=374)
        self.sleep(1)
        print(f"成功进入{self.task_name}副本选择界面")

    def select_level_grade(self):
        # 选择等级
        if self.level_grade == 10:
            self.click(175, 166)
        self.sleep(1)

    def select_property(self):
        # 选择属性
        if self.level_property == "水":
            self.click(857,624)
        elif self.level_property == "火":
            self.click(924,623)
        elif self.level_property == "风":
            self.click(990,624)
        elif self.level_property == "雷":
            self.click(1055,624)
        elif self.level_property == "光":
            self.click(1122,621)
        elif self.level_property == "暗":
            self.click(1187,624)
        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(cloud_role_tupo_color, "委托-探险")
        if res:
            self.click_color_to_color(cloud_role_tupo_color,"委托-探险",cloud_common_color,"委托手册选择界面",x=1122,y=676)
            self.sleep(1)
        res = self.find_my_color(cloud_common_color, "副本退出-再次进行")
        if res:
            self.click_color_to_color(cloud_common_color,"副本退出-再次进行",cloud_common_color,"委托手册选择界面",x=854,y=676)
            self.sleep(1)

        # 使用委托手册
        self.check_use_level_more_award()

        self.click_color_to_color(cloud_common_color,"委托手册选择界面",cloud_common_color,"角色血条-绿色",x=773,y=496,out_time=60)
        self.sleep(2)

        # 重置技能时间

        self.init_skill_time()

        print("成功进入副本")

    def go_to_activate_level(self):
        # 前往激活任务
        if self.level_grade == 10:
            res = self.go_to_activate_level_10()
            if res:
                return True
        return False

    def check_is_combat(self):
        # 判断是否成功进入战斗
        res = self.await_until_ocr(rect=[62,217,301,370], pattern="血清", time_out=5)
        if res:
            print("激活副本成功")
            return True
        else:
            print("激活副本失败")
            return False

    def unlocking(self):
        self.click(786,354,after_sleep=2)
        self.click(1059,581,after_sleep=2)

    def go_to_activate_level_10(self):
        map_type = -1   # 地图类型

        res = None
        for i in range(5):
            res = self.find_my_color(cloud_common_color, "任务黄色图标")
            if res:
                break
            self.sleep(1)
        
        if not res:
            print("没有识别到黄色图标，退出")
            return False
        
        # if 400 < res.x < 430:
        #     # 高地图
        #     map_type = 0
        # else:
        #     # 平地
        #     map_type = 1

        if 570 < res.x < 620:
            # 平地
            map_type = 1
        else:
            # 高地图
            map_type = 0
        
        print(f"详细地图：{map_type}")

        if self.uiconfig["role_tupo_capture_moling"] == "on":
            self.moling_info["地图"] = map_type

        if map_type == -1:
            print("未识别到地图，退出")
            return False

        if self.uiconfig["role_tupo_capture_moling"] == "on":
            if map_type == 0:
                print("该地图暂不支持抓魔灵，退出")
                return False

        if map_type == 0:
            return self.go_to_activate_level_10_A()
        elif map_type == 1:
            return self.go_to_activate_level_10_B()

    def go_to_activate_level_10_A(self):
        # 高地图
        self.rotate_view_to_left(180,dur=500,after_sleep=0.5)
        self.fly_spear(count=2)
        self.sleep(2)
        self.walk_to_s(1000*0.5,after_sleep=1)
        self.walk_to_w(1000*0.5,after_sleep=1)

        self.unlocking()

        res = self.check_is_combat()
        if not res:
            return False

        # 抓魔灵则不前往占位点
        if self.uiconfig["role_tupo_capture_moling"] == "on":
            return True

        # 解锁后前往占位点
        self.walk_to_s(1000*0.5,after_sleep=0.5)
        for i in range(2):
            self.rotate_view_to_right(400,dur=500,after_sleep=0.5)
        
        self.rotate_view_to_right(300,dur=500,after_sleep=0.5)
        self.rotate_view_to_top(100,dur=500,after_sleep=0.5)

        self.fly_spear(count=1)
        self.sleep(2)
        self.walk_to_d(1000*0.5,after_sleep=2)

        return True

    def go_to_activate_level_10_B(self):
        # 平地
        self.rotate_view_to_left(30,dur=500,after_sleep=0.5)
        self.rotate_view_to_top(150,dur=500,after_sleep=0.5)

        self.fly_spear(count=3)
        self.sleep(2)

        self.walk_to_s(1000,after_sleep=1)

        self.unlocking()

        res = self.check_is_combat()
        if not res:
            return False

        # 抓魔灵则不前往占位点
        if self.uiconfig["role_tupo_capture_moling"] == "on":
            return True

        self.sleep(10)
        # 解锁后前往占位点
        self.walk_to_d(1000*4,after_sleep=0.5)
        self.walk_to_s(1000*2,after_sleep=0.5)
        self.walk_to_d(1000*4,after_sleep=0.5)
        self.walk_to_w(1000*1.5,after_sleep=0.5)
        self.walk_to_d(1000*3,after_sleep=0.5)

        return True

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        res = self.find_my_color(cloud_common_color, "波次结束界面")
        if res:
            print("波次结束界面")
            self.click_color_to_color(cloud_common_color,"波次结束界面",cloud_common_color,"副本退出-再次进行",x=396,y=526,out_time=60)
            self.sleep(1)
            return True
        
        self.common_quit_level()

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(cloud_common_color, "副本退出-再次进行")
        if res:
            self.click_color_to_color(cloud_common_color,"副本退出-再次进行",cloud_common_color,"左上角红色退出",x=1094,y=673,out_time=60)
            self.sleep(1)
        res = self.find_my_color(cloud_role_tupo_color, "委托-探险")
        if res:
            self.click_color_to_color(cloud_role_tupo_color,"委托-探险",cloud_common_color,"左上角红色退出",x=92,y=29,out_time=60)
            self.sleep(1)

        self.click_until_color_vanish(cloud_common_color,"左上角红色退出",x=95,y=31)
        self.sleep(2)

        for i in range(3):
            self.click(735,669)

        res = self.find_my_color(cloud_common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def level_skill_q_is_ok(self):
        # 大招是否可以释放
        if self.level_skill_q_time < 0:
            return False
        if self.time() - self.level_skill_q_last_time >= self.level_skill_q_time:
            return True
        else:
            return False

    def level_skill_e_is_ok(self):
        # 技能是否可以释放
        if self.level_skill_e_time < 0:
            return False
        if self.time() - self.level_skill_e_last_time >= self.level_skill_e_time:
            return True
        else:
            return False

    def level_skill_e(self):
        # 释放技能
        for i in range(self.level_skill_e_count):
            self.skill_e()
        self.level_skill_e_last_time = self.time()

    def level_skill_q(self):
        # 释放大招
        for i in range(self.level_skill_q_count):
            self.skill_q()
            self.sleep(3)
            if self.uiconfig["role_tupo_action_crouch"] == "on":
                print("下蹲")
                for i in range(10):
                    res = self.find_my_color(cloud_common_color, "角色血条-绿色")
                    if res:
                        break
                    self.sleep(1)
                self.action_crouch()
                self.sleep(1)
        self.level_skill_q_last_time = self.time()

    def level_capture_moling(self):
        print("开始抓取魔灵")
        self.role_restoration()

        # 1

    def combat(self):
        # 战斗
        print("开始战斗")

        start_time = self.time()
        max_time = 60 * 5
        now_boci = 1  # 当前波次

        is_have_moling = False  # 魔灵是否出现

        while 1:
            if self.time() - start_time > max_time:
                return False

            # 判断是否有魔灵
            if self.uiconfig["role_tupo_capture_moling"] == "on":
                res = self.find_my_color(cloud_role_tupo_color, "魔灵左边任务图标")
                if res:
                    self.sleep(1)
                    res = self.find_my_color(cloud_role_tupo_color, "魔灵左边任务图标")
                    if res:
                        print("魔灵出现")
                        self.moling_info["魔灵出现次数"] += 1
                        is_have_moling = True
            
            # 是否开始抓取魔灵
            # if is_have_moling:
            #     self.level_capture_moling()
            #     print(self.moling_info)

            res = self.find_my_color(cloud_common_color, "波次结束界面")
            if res:
                self.sleep(1)
                res = self.find_my_color(cloud_common_color, "波次结束界面")
                if not res:
                    continue
                print(f"波次完成，当前波次：{now_boci}/{self.level_boci}")
                self.now_level_boci += 1

                if self.uiconfig["refresh_time_is_execute_mihan"] == "on":
                    res = self.is_refresh_time_execute_mihan()
                    if res:
                        self.click_color_to_color(cloud_common_color,"波次结束界面",cloud_common_color,"副本退出-再次进行",x=399,y=526,out_time=60)
                        self.sleep(1)
                        return True
                if now_boci >= self.level_boci:
                    self.click_color_to_color(cloud_common_color,"波次结束界面",cloud_common_color,"副本退出-再次进行",x=399,y=526,out_time=60)
                    self.sleep(1)
                    return True
                else:
                    self.click_color_to_color(cloud_common_color,"波次结束界面",cloud_common_color,"副本内选择掉落加成",x=897,y=528)
                    self.sleep(1)
                    # 使用委托手册
                    self.check_use_level_more_award()

                    self.click(637,492)
                    self.sleep(2)
                    start_time = self.time()
                    now_boci += 1

            self.cloud_role_skill_util.combat()
            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}"
        self.logui.change_log_text(text)

    def run(self):
        if self.uiconfig["role_tupo_capture_moling"] == "on":
            self.set_moling_config()
        self.refresh_log()
        self.go_to_level()
        self.select_level_grade()
        self.select_property()

        while 1:
            self.refresh_log()

            print(f"计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")

            if self.level_finish_count >= self.level_max_count:
                print(f"任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                self.level_exit()
                return True
            # 判断是否需要整点去执行密函

            if self.uiconfig["refresh_time_is_execute_mihan"] == "on":
                res = self.is_refresh_time_execute_mihan()
                if res:
                    self.level_exit()
                    return True
            self.go_in_level()

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
