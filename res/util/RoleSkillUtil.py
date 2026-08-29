# from ...res.task.BaseTask import BaseTask
from ...res.task.BaseAction import BaseAction
from ...res.task.BaseFind import BaseFind
from ...res.assets.color import *
import copy

class RoleSkillUtil(BaseAction):
    # 角色技能搓招
    def __init__(self):
        super().__init__()

        self.role = None    # 角色
        self.skill_type = None   # 技能模组
        self.skill_config_custom = {}   # 自定义技能配置，通过外部设置
        self.skill_config = {}  #角色技能配置
        self.options = {}  # 角色技能额外参数
        self.combat_options = {}    # 战斗时额外参数

        self.base_find = BaseFind()
        
    def init_config(self, role_type="0", options=None):
        # 初始化配置
        self.skill_type = role_type

        if options:
            self.options = copy.deepcopy(options)
        else:
            self.options = {}

        if self.skill_type == "0":
            self.role = "自定义"
        elif self.skill_type == "1-1":
            self.role = "赛琪"
        elif self.skill_type == "2-1":
            self.role = "止流"
        elif self.skill_type == "3-2":
            self.role = "苏乙"
        elif self.skill_type == "4-2":
            self.role = "扶疏"
        elif self.skill_type == "5-2":
            self.role = "猪妹"
        elif self.skill_type == "5-3":
            self.role = "猪妹"
        elif self.skill_type == "6-2":
            self.role = "菲娜"
        elif self.skill_type == "7-1":
            self.role = "煜明"
        elif self.skill_type == "7-3":
            self.role = "煜明"
        elif self.skill_type == "8-1":
            self.role = "芙洛拉"
        elif self.skill_type == "8-2":
            self.role = "芙洛拉"
        elif self.skill_type == "8-3":
            self.role = "芙洛拉"
        elif self.skill_type == "7-4-1" or self.skill_type == "7-4-2":
            self.role = "煜明"
        elif self.skill_type == "2-4-1" or self.skill_type == "2-4-2":
            self.role = "止流"
        elif self.skill_type == "3-4-1" or self.skill_type == "3-4-2":
            self.role = "苏乙"
        elif self.skill_type == "8-4-1" or self.skill_type == "8-4-2":
            self.role = "芙洛拉"

        self.set_role_skill_config()
        
        print(f"当前角色：{self.role}")
        print(f"技能模组{self.skill_type}")

    def set_combat_options(self, option):
        self.combat_options = copy.deepcopy(option)

    def set_role_skill_config_custom(self,skill_config):
        # 自定义技能配置,只设置一次

        # 大招
        self.skill_config_custom["skill_q_max_time"] = float(skill_config["skill_q_max_time"])
        self.skill_config_custom["skill_q_last_time"] = 0
        self.skill_config_custom["skill_q_max_count"] = int(skill_config["skill_q_max_count"])


        # 技能
        self.skill_config_custom["skill_e_max_time"] = skill_config["skill_e_max_time"]
        self.skill_config_custom["skill_e_last_time"] = 0
        self.skill_config_custom["skill_e_max_count"] = int(skill_config["skill_e_max_count"])

        # 魔灵
        self.skill_config_custom["skill_z_max_time"] = skill_config["skill_z_max_time"]
        self.skill_config_custom["skill_z_last_time"] = 0
        self.skill_config_custom["skill_z_max_count"] = int(skill_config["skill_z_max_count"])

    def set_role_skill_config(self):
        # 设置角色技能配置
        if self.skill_type == "0":
            # 自定义技能
            self.skill_config = copy.deepcopy(self.skill_config_custom)
        elif self.skill_type == "1-1":
            # 赛琪原地e
            self.skill_config = {
                "skill_q_max_time":999999,
                "skill_q_last_time":0,
                "skill_e_max_time":1,
                "skill_e_last_time":0,
            }
        elif self.skill_type == "2-1":
            # 止流龙喷
            # self.skill_config = {
            #     "skill_q_max_time": 2,
            #     "skill_q_last_time": 0,
            #     "skill_e_max_time": -1,
            #     "skill_e_last_time": 0,
            # }
            self.skill_config = {
                "skill_q_max_time": 1,
                "skill_q_last_time": 0,
                "skill_e_max_time": 9999999,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1
            }
        elif self.skill_type == "3-2":
            # 苏乙-灾厄
            self.skill_config = {
                "skill_q_max_time": 30,
                "skill_q_last_time": 0,
                "skill_e_max_time": -1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
                "is_q":False        # 是否释放过大招
            }
        elif self.skill_type == "4-2":
            # 扶疏-灾厄
            self.skill_config = {
                "skill_q_max_time": 10,
                "skill_q_last_time": 0,
                "skill_e_max_time": 7,
                "skill_e_max_count": 3,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1
            }
        elif self.skill_type == "5-2":
            # 猪妹-灾厄
            self.skill_config = {
                "skill_q_max_time": -1,
                "skill_q_last_time": 0,
                "skill_e_max_time": 0.2,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1
            }
        elif self.skill_type == "5-3":
            # 猪妹-联袂演绎
            self.skill_config = {
                "skill_q_max_time": -1,
                "skill_q_last_time": 0,
                "skill_e_max_time": 0,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
                "click_lock_boss_max_time": 3,  # 锁boss间隔
                "click_lock_boss_last_time": 0,
                "dodge_max_time": 5,  # 向前闪避
                "dodge_last_time": 0,
                "lmyy_trace_boss": self.options.get("lmyy_trace_boss", "0")   # 追踪boss方式
            }
        elif self.skill_type == "6-2":
            # 菲娜-灾厄
            self.skill_config = {
                "skill_q_max_time": 999999,
                "skill_q_last_time": 0,
                "skill_e_max_time": 15,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1
            }
        elif self.skill_type == "7-1":
            # 煜明跳跳龙
            self.skill_config = {
                "skill_q_max_time": 30,
                "skill_q_last_time": 0,
                "skill_e_max_time": 0.1,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1
            }
        elif self.skill_type == "7-3":
            # 煜明-联袂演绎
            self.skill_config = {
                "skill_q_max_time": 99999,
                "skill_q_last_time": 0,
                "skill_e_max_time": 0,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
                "click_lock_boss_max_time": 3,  # 锁boss间隔
                "click_lock_boss_last_time": 0,
                "dodge_max_time": 5,  # 向前闪避
                "dodge_last_time": 0,
                "lmyy_trace_boss": self.options.get("lmyy_trace_boss", "0")  # 追踪boss方式
            }
        elif self.skill_type == "8-1":
            # 芙洛拉
            self.skill_config = {
                "skill_q_max_time": 99999,
                "skill_q_last_time": 0,
                "skill_e_max_time": 1,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "walk_to_w_max_time": 4,   # 向后走
                "walk_to_w_last_time": 0,
                "skill_click_max_time": 2,  # 重击
                "skill_click_max_count": 1,
                "skill_click_last_time": 0,
                "click_lock_boss_max_time": 1,  # 锁boss间隔
                "click_lock_boss_last_time": 0,
            }
        elif self.skill_type == "8-2":
            # 芙洛拉-灾厄武器
            self.skill_config = {
                "skill_q_max_time": 99999,
                "skill_q_last_time": 0,
                "skill_e_max_time": 1,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "walk_to_w_max_time": 2,  # 向后走
                "walk_to_w_last_time": 0,
                "skill_click_max_time": 1,  # 重击
                "skill_click_max_count": 1,
                "skill_click_last_time": self.time() - 6,   # 5秒后重击
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1
            }
        elif self.skill_type == "8-2-2":
            # 芙洛拉-灾厄武器-扼守
            self.skill_config = {
                "skill_q_max_time": 99999,
                "skill_q_last_time": 0,
                "skill_click_max_time": 2,  # 重击
                "skill_click_max_count": 1,
                "skill_click_last_time": self.time() - 6,   # 5秒后重击
                "walk_to_w_max_time": 80,  # 向前走
                "walk_to_w_last_time": self.time(),
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1
            }
        elif self.skill_type == "8-3":
            # 芙洛拉-联袂演绎
            self.skill_config = {
                "skill_q_max_time": 99999,
                # "skill_q_last_time": self.time() - 99994,   # 5秒后开大
                "skill_q_last_time": 0,   # 5秒后开大
                "skill_e_max_time": 1,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
                "dodge_to_w_max_time": 9999,   # 闪避
                "dodge_to_w_last_time": 0,
                "skill_click_max_time": 1,  # 重击
                "skill_click_max_count": 1,
                "skill_click_last_time": self.time() + 3,
                "click_lock_boss_max_time": 1,  # 锁boss间隔
                "click_lock_boss_last_time": 0,
            }
        elif self.skill_type == "7-4-1":
            # 煜明-活动-分组赛
            self.skill_config = {
                "index_": 0,
                "skill_z_max_time": 9999,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "7-4-2":
            # 煜明-活动-常规
            self.skill_config = {
                "skill_q_max_time": 30,
                "skill_q_last_time": 0,
                "skill_z_max_time": 9999,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "2-4-1":
            # 止流-活动-分组赛
            self.skill_config = {
                "skill_z_max_time": 9999,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "2-4-2":
            # 止流-活动-常规
            self.skill_config = {
                "skill_z_max_time": 9999,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "3-4-1":
            # 苏乙-活动-分组赛
            self.skill_config = {
                "max_time": 15,          # 技能e间隔
                "last_time": 0,
                "skill_last_time": 0,
                "skill_e_time": 24,      # 多少秒开始炸
                "skill_z_max_time": 9999,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "3-4-2":
            # 苏乙-活动-常规
            self.skill_config = {
                "max_time": 15,          # 技能e间隔
                "last_time": 0,
                "skill_last_time": 0,
                "skill_e_time": 40,      # 多少秒开始炸
                "skill_z_max_time": 9999,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "8-4-1":
            # 芙洛拉-活动-分组赛
            self.skill_config = {
                "max_time": 5,           # 重击间隔
                "last_time": 0,
                "skill_z_max_time": 9999,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "8-4-2":
            # 芙洛拉-活动-常规
            self.skill_config = {
                "skill_e_max_time": 3,
                "skill_e_max_count": 1,
                "skill_e_last_time": 0,
                "skill_z_max_time": 10,
                "skill_z_last_time": 0,
                "skill_z_max_count": 1,
                "skill_click_max_time": 5,  # 重击
                "skill_click_max_count": 1,
                "skill_click_last_time": self.time(),
                "click_lock_boss_max_time": 99999,  # 锁boss间隔
                "click_lock_boss_last_time": 0,
            }

    def add_skill_z(self,skill_config):
        """
        添加魔灵技能
        """
        self.skill_config["skill_z_max_time"] = float(skill_config["skill_z_max_time"])
        self.skill_config["skill_z_last_time"] = 0
        self.skill_config["skill_z_max_count"] = int(skill_config["skill_z_max_count"])
        print("成功添加魔灵技能")
        print(self.skill_config)

    def combat(self):
        # 战斗
        # print(f"释放技能：{self.role}")
        if self.skill_type == "0":
            self.combat_custom()
        elif self.skill_type == "1-1":
            self.combat_skill_1_1()
        elif self.skill_type == "2-1":
            self.combat_skill_2_1()
        elif self.skill_type == "3-2":
            self.combat_skill_3_2()
        elif self.skill_type == "4-2":
            self.combat_skill_4_2()
        elif self.skill_type == "5-2":
            self.combat_skill_5_2()
        elif self.skill_type == "5-3":
            self.combat_skill_5_3()
        elif self.skill_type == "6-2":
            self.combat_skill_6_2()
        elif self.skill_type == "7-1":
            self.combat_skill_7_1()
        elif self.skill_type == "7-3":
            self.combat_skill_7_3()
        elif self.skill_type == "8-1":
            self.combat_skill_8_1()
        elif self.skill_type == "8-2":
            self.combat_skill_8_2()
        elif self.skill_type == "8-2-2":
            self.combat_skill_8_2_2()
        elif self.skill_type == "8-3":
            self.combat_skill_8_3()
        elif self.skill_type == "7-4-1":
            self.combat_skill_7_4_1()
        elif self.skill_type == "7-4-2":
            self.combat_skill_7_4_2()
        elif self.skill_type == "2-4-1":
            self.combat_skill_2_4_1()
        elif self.skill_type == "2-4-2":
            self.combat_skill_2_4_2()
        elif self.skill_type == "3-4-1":
            self.combat_skill_3_4_1()
        elif self.skill_type == "3-4-2":
            self.combat_skill_3_4_2()
        elif self.skill_type == "8-4-1":
            self.combat_skill_8_4_1()
        elif self.skill_type == "8-4-2":
            self.combat_skill_8_4_2()

    def combat_before(self):
        # 活动-开场连招（进入副本后、寻敌前执行，对应原 combat_befor）
        if self.skill_type in ("7-4-1", "7-4-2"):
            self.combat_before_yuming()
        elif self.skill_type in ("2-4-1", "2-4-2"):
            self.combat_before_zhiliu()
        elif self.skill_type in ("3-4-1", "3-4-2"):
            self.combat_before_suyi()
        elif self.skill_type in ("8-4-1", "8-4-2"):
            self.combat_before_fll()

    def combat_start(self):
        # 活动-进入战斗循环前的准备（寻敌后执行，对应原各 combat_xxx 开头）
        if self.skill_type == "7-4-2":
            # 煜明常规：开场锁敌
            self.lock_enemy()
        elif self.skill_type == "2-4-2":
            # 止流常规：锁敌 + 向前闪避
            self.lock_enemy()
            self.action_dodge_to_w()
            self.sleep(1)
        elif self.skill_type == "3-4-2":
            # 苏乙常规：开场锁敌
            self.lock_enemy()

        # 初始化各模式战斗计时基准
        now = self.time()
        if self.skill_type in ("3-4-1", "3-4-2"):
            self.skill_config["last_time"] = now
            self.skill_config["skill_last_time"] = now
        elif self.skill_type == "8-4-1":
            self.skill_config["last_time"] = now
        self.skill_config["skill_z_last_time"] = now

    def combat_before_yuming(self):
        # 煜明开场
        self.skill_q(after_sleep=3)
        # 大招计时从开场起算（对应原 combat_befor）
        self.skill_config["skill_q_last_time"] = self.time()

    def combat_before_zhiliu(self):
        # 止流开场
        for i in range(2):
            self.action_jump_fly()
            self.sleep(0.5)
        self.walk_to_w(walk_time=1000 * 0.5)
        self.skill_e(dur=1000, after_sleep=1.5)
        self.skill_e(after_sleep=1)
        self.skill_q(after_sleep=4)
        self.skill_e(after_sleep=1.5)
        self.walk_to_w(walk_time=1000)

    def combat_before_suyi(self):
        # 苏乙开场
        self.walk_to_w(walk_time=1000 * 6)
        self.sleep(1)
        self.skill_q(after_sleep=4)
        self.combat_left_click()
        self.sleep(2)
        self.combat_left_click()
        self.sleep(1)
        self.walk_to_w(walk_time=1000 * 2)

    def combat_before_fll(self):
        # 芙洛拉开场
        for i in range(2):
            self.action_jump_fly()
            self.sleep(0.5)
        self.skill_q(after_sleep=4)
        for i in range(2):
            self.action_jump_fly()
            # self.sleep(0.5)
        self.sleep(0.5)
        if self.skill_type == "8-4-1":
            # 分组赛
            self.skill_e()

    def _combat_skill_z(self):
        # 活动通用魔灵释放
        if self.skill_config.get("skill_z_max_time", -1) >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.3)
                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_7_4_1(self):
        # 煜明-活动-分组赛
        if self.skill_config["index_"] >= 3:
            self.skill_e(after_sleep=0.1)
            self.rotate_view_to_right(250, dur=100, after_sleep=0.1)
            self.rotate_view_to_right(250, dur=100, after_sleep=0.1)
            self.skill_config["index_"] = 0
        else:
            self.skill_e(after_sleep=0.3)

        self.combat_left_click()
        self._combat_skill_z()

        self.skill_config["index_"] += 1
        self.sleep(0.2)

    def combat_skill_7_4_2(self):
        # 煜明-活动-常规
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            self.skill_q()
            self.skill_config["skill_q_last_time"] = self.time()

        self.skill_e(after_sleep=0.4)
        self.combat_left_click()
        self._combat_skill_z()
        self.sleep(0.1)

    def combat_skill_2_4_1(self):
        # 止流-活动-分组赛
        self.skill_q(after_sleep=1)
        self._combat_skill_z()
        self.sleep(0.1)

    def combat_skill_2_4_2(self):
        # 止流-活动-常规
        self.skill_q(after_sleep=0.5)
        self._combat_skill_z()
        self.sleep(0.1)

    def combat_skill_3_4_1(self):
        # 苏乙-活动-分组赛
        if self.time() - self.skill_config["skill_last_time"] > self.skill_config["skill_e_time"]:
            for i in range(3):
                self.skill_q(after_sleep=0.5)
            self.skill_config["skill_e_time"] = 9999
            self.sleep(2)
            self.skill_q(after_sleep=4)

        if self.time() - self.skill_config["last_time"] > self.skill_config["max_time"]:
            self.skill_e(after_sleep=0.2)
            self.skill_config["last_time"] = self.time()
            for i in range(3):
                self.combat_left_click()
                self.sleep(0.3)
        else:
            self.combat_left_click()
            self.sleep(0.5)

        self._combat_skill_z()
        self.sleep(0.1)

    def combat_skill_3_4_2(self):
        # 苏乙-活动-常规
        if self.time() - self.skill_config["skill_last_time"] > self.skill_config["skill_e_time"]:
            for i in range(3):
                self.skill_q(after_sleep=0.5)
            self.sleep(2)
            for i in range(3):
                self.skill_q(after_sleep=0.5)
            self.sleep(2)
            self.skill_config["skill_last_time"] = self.time()

        if self.time() - self.skill_config["last_time"] > self.skill_config["max_time"]:
            self.skill_e(after_sleep=0.2)
            self.skill_config["last_time"] = self.time()
            for i in range(3):
                self.combat_left_click()
                self.sleep(0.3)
        else:
            self.skill_e_suyi_0()

        self._combat_skill_z()
        self.sleep(0.1)

    def combat_skill_8_4_1(self):
        # 芙洛拉-活动-分组赛
        if self.time() - self.skill_config["last_time"] > self.skill_config["max_time"]:
            self.combat_left_click(dur=500)
            self.skill_config["last_time"] = self.time()

        self._combat_skill_z()
        self.sleep(0.1)

    def combat_skill_8_4_2(self):
        # 芙洛拉-活动-常规
        # 锁boss
        if self.skill_config["click_lock_boss_max_time"] >= 0:
            if self.time() - self.skill_config["click_lock_boss_last_time"] >= self.skill_config[
                "click_lock_boss_max_time"]:
                # 锁boss
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()

        # 技能
        if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
            self.skill_e(after_sleep=0.5)
            self.skill_config["skill_e_last_time"] = self.time()

        # 重击
        if self.time() - self.skill_config["skill_click_last_time"] >= self.skill_config["skill_click_max_time"]:
            self.combat_left_click(dur=500)
            self.skill_config["skill_click_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

        self.combat_left_click()
        self.sleep(0.1)

    def combat_custom(self):
        # 自定义战斗
        
        # 大招
        if self.skill_config["skill_q_max_time"] >= 0:
            if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
                # 释放大招
                for i in range(self.skill_config["skill_q_max_count"]):
                    self.skill_q()
                    self.sleep(3)

                self.skill_config["skill_q_last_time"] = self.time()
                return True

        # 技能
        if self.skill_config["skill_e_max_time"] >= 0:
            if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
                # 释放技能
                for i in range(self.skill_config["skill_e_max_count"]):
                    self.skill_e()
                
                self.skill_config["skill_e_last_time"] = self.time()

                return True

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z()
                
                self.skill_config["skill_z_last_time"] = self.time()

                return True

    def combat_skill_1_1(self):
        # 赛琪原地e

        # 大招 
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            # 释放大招
            self.skill_q()

            self.skill_config["skill_q_last_time"] = self.time()

            self.sleep(3)

            # 按下蹲键
            self.action_crouch()
            self.sleep(1)

        # 原地e
        if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
            # 释放原地e
            # self.skill_e_saiqi_1()

            self.skill_e()

            self.skill_config["skill_e_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_2_1(self):
        # 止流龙喷

        # 叠被动
        if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
            # 叠被动
            self.skill_e(dur=1000, after_sleep=1.5)
            self.skill_e(after_sleep=1)

            self.skill_config["skill_e_last_time"] = self.time()

        # 大招
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            # 释放大招
            # 止流龙喷
            # self.skill_e(dur=1000, after_sleep=1.5)
            # self.skill_e(after_sleep=1)

            self.skill_q(after_sleep=1)

            self.skill_config["skill_q_last_time"] = self.time()

            # self.sleep(3)

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_3_2(self):
        # 苏乙-灾厄

        # 大招
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            # 释放大招
            if self.skill_config["is_q"]:
                # print("重新释放大招")

                res  = None
                for i in range(3):
                    res = self.base_find.find_my_color(common_color, "苏乙大招-未释放")
                    if res:
                        break

                if res:
                    for i in range(3):
                        self.skill_q(after_sleep=0.5)
                    self.sleep(1)
                else:
                    # 已经释放
                    for i in range(3):
                        self.skill_q(after_sleep=0.5)
                    self.sleep(1)

                    for i in range(4):
                        self.skill_q(after_sleep=0.5)
                    self.sleep(1)

            else:
                print("第一次释放大招")
                for i in range(3):
                    self.skill_q(after_sleep=0.5)
                self.sleep(1)
                self.skill_config["is_q"] = True

            self.skill_config["skill_q_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

        res  = None
        for i in range(3):
            res = self.base_find.find_my_color(common_color, "苏乙大招-未释放")
            if res:
                for i in range(3):
                    self.skill_q(after_sleep=0.5)
                self.sleep(1)
                self.skill_config["skill_q_last_time"] = self.time()
                
        self.combat_left_click()
        # self.skill_e_suyi_0()
        self.sleep(0.5)

    def combat_skill_4_2(self):
        # 扶疏-灾厄

        # 大招
        if self.skill_config["skill_q_max_time"] >= 0:
            if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
                # 释放大招
                self.skill_q(after_sleep=4)
                self.skill_config["skill_q_last_time"] = self.time()

        # 技能
        if self.skill_config["skill_e_max_time"] >= 0:
            if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
                # 释放技能
                for i in range(self.skill_config["skill_e_max_count"]):
                    self.skill_e(after_sleep=0.5)

                self.skill_config["skill_e_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_5_2(self):
        # 猪妹-灾厄

        # 技能
        if self.skill_config["skill_e_max_time"] >= 0:
            if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
                # 释放技能
                for i in range(self.skill_config["skill_e_max_count"]):
                    self.skill_e(after_sleep=0.1)

                self.skill_config["skill_e_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_5_3(self):
        # 猪妹-联袂演绎

        # 锁boss
        if self.skill_config["click_lock_boss_max_time"] >= 0:
            if self.time() - self.skill_config["click_lock_boss_last_time"] >= self.skill_config["click_lock_boss_max_time"]:
                # 锁boss
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()

        # 向前闪避
        if self.skill_config["dodge_max_time"] >= 0:
            if self.time() - self.skill_config["dodge_last_time"] >= self.skill_config["dodge_max_time"]:
                # 向前闪避
                if self.skill_config["lmyy_trace_boss"] == "0":
                    self.sleep(0.3)
                    self.action_jump_fly(after_sleep=0.5)
                elif self.skill_config["lmyy_trace_boss"] == "1":
                    # self.sleep(0.1)
                    self.fly_spear()
                
                self.skill_config["dodge_last_time"] = self.time() 

        # 技能
        if self.skill_config["skill_e_max_time"] >= 0:
            if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
                # 释放技能
                for i in range(self.skill_config["skill_e_max_count"]):
                    self.skill_e(after_sleep=0.1)
                self.skill_config["skill_e_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)
                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_6_2(self):
        # 菲娜-灾厄

        # 大招
        if self.skill_config["skill_q_max_time"] >= 0:
            if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
                # 释放大招
                self.skill_q(after_sleep=3)
                for i in range(3):
                    self.skill_q(after_sleep=2)

                self.skill_config["skill_q_last_time"] = self.time()

        # 技能
        if self.skill_config["skill_e_max_time"] >= 0:
            if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
                # 释放技能
                for i in range(self.skill_config["skill_e_max_count"]):
                    self.skill_e(after_sleep=0.5)

                self.skill_config["skill_e_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

        # 蓄力 + 闪避
        self.combat_left_click(dur=500)
        self.sleep(2)
        self.action_click_dodge()
        self.sleep(0.5)

    def combat_skill_7_1(self):
        # 煜明跳跳龙

        # 大招
        if self.skill_config["skill_q_max_time"] >= 0:
            if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
                # 释放大招
                self.skill_q(after_sleep=3)
                self.skill_config["skill_q_last_time"] = self.time()

        # 技能
        if self.skill_config["skill_e_max_time"] >= 0:
            if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
                # 释放技能
                self.skill_e(after_sleep=0.3)
                self.combat_left_click()
                self.skill_config["skill_e_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_7_3(self):
        # 煜明-联袂演绎

        # 锁boss
        if self.skill_config["click_lock_boss_max_time"] >= 0:
            if self.time() - self.skill_config["click_lock_boss_last_time"] >= self.skill_config[
                "click_lock_boss_max_time"]:
                # 锁boss
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()

        # 向前闪避
        # if self.skill_config["dodge_max_time"] >= 0:
        #     if self.time() - self.skill_config["dodge_last_time"] >= self.skill_config["dodge_max_time"]:
        #         # 向前闪避
        #         if self.skill_config["lmyy_trace_boss"] == "0":
        #             self.sleep(0.3)
        #             self.action_jump_fly(after_sleep=0.5)
        #         elif self.skill_config["lmyy_trace_boss"] == "1":
        #             # self.sleep(0.1)
        #             self.fly_spear()
        #
        #         self.skill_config["dodge_last_time"] = self.time()

                # 大招
        if self.skill_config["skill_q_max_time"] >= 0:
            if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
                # 释放大招
                self.skill_q(after_sleep=3)
                self.skill_config["skill_q_last_time"] = self.time()

        # 技能
        if self.skill_config["skill_e_max_time"] >= 0:
            if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
                # 释放技能
                self.skill_e(after_sleep=0.3)
                self.combat_left_click()
                self.skill_config["skill_e_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_8_1(self):
        # 芙洛拉

        if (self.combat_options.get("CJSXJ_BOSS", None) is not None) and (self.skill_config["skill_click_max_time"] != 1):
            # boss战斗，将重击时间间隔修改为1
            self.skill_config["skill_click_max_time"] = 1

        # 锁boss
        if self.combat_options:
            if self.combat_options.get("CJSXJ_BOSS", None) is not None:
                if self.skill_config["click_lock_boss_max_time"] >= 0:
                    if self.time() - self.skill_config["click_lock_boss_last_time"] >= self.skill_config["click_lock_boss_max_time"]:
                        # 锁boss
                        self.lock_enemy()
                        self.skill_config["click_lock_boss_last_time"] = self.time()

        # 大招
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            # 释放大招
            self.skill_q(after_sleep=3)
            self.skill_config["skill_q_last_time"] = self.time()

        # 向后走
        if self.time() - self.skill_config["walk_to_w_last_time"] >= self.skill_config["walk_to_w_max_time"]:
            self.walk_to_s(500)
            self.skill_config["walk_to_w_last_time"] = self.time()

        # 技能
        if self.combat_options.get("CJSXJ_BOSS", None) is not None:
            if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
                self.skill_e(after_sleep=0.5)
                self.skill_config["skill_e_last_time"] = self.time()

        # 重击
        if self.time() - self.skill_config["skill_click_last_time"] >= self.skill_config["skill_click_max_time"]:
            self.combat_left_click(dur=500)
            self.skill_config["skill_click_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

        self.combat_left_click()

    def combat_skill_8_2(self):
        # 芙洛拉-灾厄武器

        # 大招
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            # 释放大招
            self.skill_q(after_sleep=3)
            self.skill_config["skill_q_last_time"] = self.time()

        # 技能
        if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
            self.skill_e(after_sleep=0.5)
            self.skill_config["skill_e_last_time"] = self.time()

        # 重击
        if self.time() - self.skill_config["skill_click_last_time"] >= self.skill_config["skill_click_max_time"]:
            self.combat_left_click(dur=500)
            self.skill_config["skill_click_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

        # 向后走
        if self.time() - self.skill_config["walk_to_w_last_time"] >= self.skill_config["walk_to_w_max_time"]:
            self.walk_to_s(500)
            self.skill_config["walk_to_w_last_time"] = self.time()

        self.combat_left_click()

    def combat_skill_8_2_2(self):
        # 芙洛拉-灾厄武器-扼守

        # 大招
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            # 释放大招
            self.skill_q(after_sleep=3)
            self.skill_config["skill_q_last_time"] = self.time()

        # # 向前
        # if self.time() - self.skill_config["walk_to_w_last_time"] >= self.skill_config["walk_to_w_max_time"]:
        #     if self.time() - self.skill_config["skill_click_last_time"] >= 1:
        #         self.action_jump_fly(after_sleep=2)
        #         self.skill_config["walk_to_w_last_time"] = self.time()
        # # 重击
        # if self.time() - self.skill_config["skill_click_last_time"] >= self.skill_config["skill_click_max_time"]:
        #     self.combat_left_click(dur=500)
        #     self.skill_config["skill_click_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

    def combat_skill_8_3(self):
        # 芙洛拉-联袂演绎

        # 锁boss
        if self.skill_config["click_lock_boss_max_time"] >= 0:
            if self.time() - self.skill_config["click_lock_boss_last_time"] >= self.skill_config["click_lock_boss_max_time"]:
                # 锁boss
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()

        # 大招
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            # 释放大招
            for i in range(3):
                self.skill_q(after_sleep=0.5)
            self.sleep(1.5)
            self.skill_config["skill_q_last_time"] = self.time()

        # 技能
        if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
            self.skill_e(after_sleep=0.5)
            self.skill_config["skill_e_last_time"] = self.time()

        # 重击
        if self.time() - self.skill_config["skill_click_last_time"] >= self.skill_config["skill_click_max_time"]:
            self.combat_left_click(dur=500)
            self.skill_config["skill_click_last_time"] = self.time()

        # 闪避
        if self.time() - self.skill_config["dodge_to_w_last_time"] >= self.skill_config["dodge_to_w_max_time"]:
            self.action_dodge_to_w()
            self.skill_config["dodge_to_w_last_time"] = self.time()

        # 魔灵
        if self.skill_config["skill_z_max_time"] >= 0:
            if self.time() - self.skill_config["skill_z_last_time"] >= self.skill_config["skill_z_max_time"]:
                # 释放魔灵
                for i in range(self.skill_config["skill_z_max_count"]):
                    self.skill_z(after_sleep=0.1)

                self.skill_config["skill_z_last_time"] = self.time()

        self.combat_left_click()