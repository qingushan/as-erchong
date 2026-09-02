import copy

from ...assets.color import common_color


class CombatSkillController:
    """本地游戏通用战斗技能控制器。

    普通副本通过本控制器选择技能模组和维护冷却状态。控制器不继承
    ``BaseAction``，而是把点击、找色、走位和技能动作委托给所属任务，避免创建
    一套与任务对象相互独立的设备状态。活动、沉浸式戏剧和联袂演绎只复用这里
    的动作委托、冷却判断和角色展示能力，各自的技能行为放在对应子类中。
    """

    ROLE_NAME_MAP = {
        "0": "自定义",
        "1": "赛琪",
        "2": "止流",
        "3": "苏乙",
        "4": "扶疏",
        "5": "猪妹",
        "6": "菲娜",
        "7": "煜明",
        "8": "芙洛拉",
        "9": "艾达",
    }

    def __init__(self, task):
        self.task = task
        self.role = "自定义"
        self.skill_type = "0"
        self.skill_config_custom = {}
        self.skill_config = {}
        # UI 设置的魔灵参数独立保存。普通内置模组每次进本都会重建配置，
        # 因此不能只改当前 skill_config，必须在重建后自动恢复这份覆盖值。
        self.skill_z_override = None

    def __getattr__(self, name):
        """将设备动作和识别方法统一转发给当前任务对象。"""
        return getattr(self.task, name)

    def _ready(self, name):
        """判断指定动作是否到达冷却时间，负数间隔表示禁用。"""
        interval = self.skill_config.get(name + "_max_time", -1)
        last_time = self.skill_config.get(name + "_last_time", 0)
        return interval >= 0 and self.time() - last_time >= interval

    def _cast(self, name, action, after_sleep=0, count_key=None):
        """按技能配置执行一组动作，并在全部动作结束后更新冷却时间。"""
        if not self._ready(name):
            return False
        count = self.skill_config.get(count_key or name + "_max_count", 1)
        for _ in range(count):
            action(after_sleep=after_sleep)
        self.skill_config[name + "_last_time"] = self.time()
        return True

    def _cast_z(self, after_sleep=0.1):
        """供普通和专用控制器复用的魔灵技能释放入口。"""
        return self._cast("skill_z", self.skill_z, after_sleep=after_sleep)

    def reset(self):
        """清理本轮技能计时，但保留当前模组和用户配置。"""
        now = self.time()
        for key in list(self.skill_config):
            if key.endswith("_last_time"):
                self.skill_config[key] = now if key == "skill_z_last_time" else 0
        self._restore_skill_z_override()

    @classmethod
    def get_role_name(cls, skill_type):
        """从技能模组首段解析仅用于日志展示的角色名称。"""
        role_code = str(skill_type or "0").split("-", 1)[0]
        return cls.ROLE_NAME_MAP.get(role_code, "未知角色")

    def print_skill_info(self):
        """统一输出角色展示名称和技能模组，角色名称不参与技能决策。"""
        print(f"主控角色：{self.role}  技能模组：{self.skill_type}")

    def init_config(self, role_type="0"):
        """初始化普通副本的技能模组。"""
        self.skill_type = role_type
        self.role = self.get_role_name(role_type)
        self.set_role_skill_config()
        self.print_skill_info()

    def set_role_skill_config_custom(self, skill_config):
        """保存 UI 传入的自定义 Q/E/Z 参数，并登记统一的魔灵覆盖值。"""
        self.skill_config_custom = {
            "skill_q_max_time": float(skill_config["skill_q_max_time"]),
            "skill_q_last_time": 0,
            "skill_q_max_count": int(skill_config["skill_q_max_count"]),
            "skill_e_max_time": float(skill_config["skill_e_max_time"]),
            "skill_e_last_time": 0,
            "skill_e_max_count": int(skill_config["skill_e_max_count"]),
            "skill_z_max_time": float(skill_config["skill_z_max_time"]),
            "skill_z_last_time": 0,
            "skill_z_max_count": int(skill_config["skill_z_max_count"]),
        }
        self.apply_skill_z(
            skill_config["skill_z_max_time"],
            skill_config["skill_z_max_count"],
        )

    def set_role_skill_config(self):
        """重建当前普通模组的默认参数，用于每次进入新副本时重置状态。"""
        if self.skill_type == "0":
            self.skill_config = copy.deepcopy(self.skill_config_custom)
        elif self.skill_type == "1-1":
            self.skill_config = {
                "skill_q_max_time": 999999, "skill_q_last_time": 0,
                "skill_e_max_time": 1, "skill_e_last_time": 0,
            }
        elif self.skill_type == "2-1":
            self.skill_config = {
                "skill_q_max_time": 1, "skill_q_last_time": 0,
                "skill_e_max_time": 9999999, "skill_e_max_count": 1,
                "skill_e_last_time": 0, "skill_z_max_time": 10,
                "skill_z_last_time": 0, "skill_z_max_count": 1,
            }
        elif self.skill_type == "3-2":
            self.skill_config = {
                "skill_q_max_time": 30, "skill_q_last_time": 0,
                "skill_e_max_time": -1, "skill_e_last_time": 0,
                "skill_z_max_time": 10, "skill_z_last_time": 0,
                "skill_z_max_count": 1, "is_q": False,
            }
        elif self.skill_type == "4-2":
            self.skill_config = {
                "skill_q_max_time": 10, "skill_q_last_time": 0,
                "skill_e_max_time": 7, "skill_e_max_count": 3,
                "skill_e_last_time": 0, "skill_z_max_time": 10,
                "skill_z_last_time": 0, "skill_z_max_count": 1,
            }
        elif self.skill_type == "5-2":
            self.skill_config = {
                "skill_q_max_time": -1, "skill_q_last_time": 0,
                "skill_e_max_time": 0.2, "skill_e_max_count": 1,
                "skill_e_last_time": 0, "skill_z_max_time": 10,
                "skill_z_last_time": 0, "skill_z_max_count": 1,
            }
        elif self.skill_type == "6-2":
            self.skill_config = {
                "skill_q_max_time": 999999, "skill_q_last_time": 0,
                "skill_e_max_time": 15, "skill_e_max_count": 1,
                "skill_e_last_time": 0, "skill_z_max_time": 10,
                "skill_z_last_time": 0, "skill_z_max_count": 1,
            }
        elif self.skill_type == "7-1":
            self.skill_config = {
                "skill_q_max_time": 30, "skill_q_last_time": 0,
                "skill_e_max_time": 0.1, "skill_e_max_count": 1,
                "skill_e_last_time": 0, "skill_z_max_time": 10,
                "skill_z_last_time": 0, "skill_z_max_count": 1,
            }
        elif self.skill_type == "8-2":
            self.skill_config = {
                "skill_q_max_time": 99999, "skill_q_last_time": 0,
                "skill_e_max_time": 1, "skill_e_max_count": 1,
                "skill_e_last_time": 0, "walk_to_w_max_time": 2,
                "walk_to_w_last_time": 0, "skill_click_max_time": 1,
                "skill_click_max_count": 1,
                "skill_click_last_time": self.time() - 6,
                "skill_z_max_time": 10, "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "8-2-2":
            self.skill_config = {
                "skill_q_max_time": 99999, "skill_q_last_time": 0,
                "skill_click_max_time": 2, "skill_click_max_count": 1,
                "skill_click_last_time": self.time() - 6,
                "walk_to_w_max_time": 80,
                "walk_to_w_last_time": self.time(),
                "skill_z_max_time": 10, "skill_z_last_time": 0,
                "skill_z_max_count": 1,
            }
        elif self.skill_type == "9-1":
            self.skill_config = {
                "skill_q_max_time": 99999, "skill_q_last_time": 0,
                "skill_z_max_time": 10, "skill_z_last_time": 0,
            }

        # 无论当前是自定义还是内置角色，都以任务页面的魔灵设置为准。
        # 这一步让任务类只负责传入一次 UI 配置，不再关心每个模组的默认值。
        self._restore_skill_z_override()

    def apply_skill_z(self, max_time, max_count):
        """保存并应用任务页面的魔灵配置，供全部本地控制器统一使用。"""
        self.skill_z_override = {
            "skill_z_max_time": float(max_time),
            "skill_z_max_count": int(max_count),
        }
        self._restore_skill_z_override()

    def _restore_skill_z_override(self):
        """在技能模组重建后恢复 UI 魔灵参数。"""
        if self.skill_z_override is None:
            return
        self.skill_config["skill_z_max_time"] = self.skill_z_override["skill_z_max_time"]
        self.skill_config["skill_z_last_time"] = 0
        self.skill_config["skill_z_max_count"] = self.skill_z_override["skill_z_max_count"]

    def combat(self):
        """根据普通副本技能模组执行一轮战斗动作。"""
        handlers = {
            "0": self.combat_custom,
            "1-1": self.combat_skill_1_1,
            "2-1": self.combat_skill_2_1,
            "3-2": self.combat_skill_3_2,
            "4-2": self.combat_skill_4_2,
            "5-2": self.combat_skill_5_2,
            "6-2": self.combat_skill_6_2,
            "7-1": self.combat_skill_7_1,
            "8-2": self.combat_skill_8_2,
            "8-2-2": self.combat_skill_8_2_2,
            "9-1": self.combat_skill_9_1,
        }
        handler = handlers.get(self.skill_type)
        if handler:
            return handler()
        return False

    def combat_custom(self):
        """按 Q、E、Z 的优先级执行用户自定义技能。"""
        if self._ready("skill_q"):
            for _ in range(self.skill_config["skill_q_max_count"]):
                self.skill_q()
                self.sleep(3)
            self.skill_config["skill_q_last_time"] = self.time()
            return True
        if self._ready("skill_e"):
            for _ in range(self.skill_config["skill_e_max_count"]):
                self.skill_e()
            self.skill_config["skill_e_last_time"] = self.time()
            return True
        if self._ready("skill_z"):
            for _ in range(self.skill_config["skill_z_max_count"]):
                self.skill_z()
            self.skill_config["skill_z_last_time"] = self.time()
            return True
        return False

    def combat_skill_1_1(self):
        """赛琪原地 E。"""
        if self._ready("skill_q"):
            self.skill_q()
            self.skill_config["skill_q_last_time"] = self.time()
            self.sleep(3)
            self.action_crouch()
            self.sleep(1)
        self._cast("skill_e", self.skill_e, after_sleep=1)
        self._cast_z()

    def combat_skill_2_1(self):
        """止流龙喷。"""
        if self._ready("skill_e"):
            self.skill_e(dur=1000, after_sleep=1.5)
            self.skill_e(after_sleep=1)
            self.skill_config["skill_e_last_time"] = self.time()
        self._cast("skill_q", self.skill_q, after_sleep=1)
        self._cast_z()

    def combat_skill_3_2(self):
        """苏乙灾厄武器连招。"""
        if self._ready("skill_q"):
            if self.skill_config["is_q"]:
                skill_inactive = None
                for _ in range(3):
                    skill_inactive = self.find_my_color(common_color, "苏乙大招-未释放")
                    if skill_inactive:
                        break
                for _ in range(3):
                    self.skill_q(after_sleep=0.5)
                self.sleep(1)
                if not skill_inactive:
                    for _ in range(4):
                        self.skill_q(after_sleep=0.5)
                    self.sleep(1)
            else:
                print("第一次释放大招")
                for _ in range(3):
                    self.skill_q(after_sleep=0.5)
                self.sleep(1)
                self.skill_config["is_q"] = True
            self.skill_config["skill_q_last_time"] = self.time()

        self._cast_z()
        for _ in range(3):
            if self.find_my_color(common_color, "苏乙大招-未释放"):
                for _ in range(3):
                    self.skill_q(after_sleep=0.5)
                self.sleep(1)
                self.skill_config["skill_q_last_time"] = self.time()
        self.combat_left_click()
        self.sleep(0.5)

    def combat_skill_4_2(self):
        """扶疏灾厄武器连招。"""
        self._cast("skill_q", self.skill_q, after_sleep=4)
        self._cast("skill_e", self.skill_e, after_sleep=0.5)
        self._cast_z()

    def combat_skill_5_2(self):
        """猪妹灾厄武器连招。"""
        self._cast("skill_e", self.skill_e, after_sleep=0.1)
        self._cast_z()

    def combat_skill_6_2(self):
        """菲娜灾厄武器连招。"""
        if self._ready("skill_q"):
            self.skill_q(after_sleep=3)
            for _ in range(3):
                self.skill_q(after_sleep=2)
            self.skill_config["skill_q_last_time"] = self.time()
        self._cast("skill_e", self.skill_e, after_sleep=0.5)
        self._cast_z()
        self.combat_left_click(dur=500)
        self.sleep(2)
        self.action_click_dodge()
        self.sleep(0.5)

    def combat_skill_7_1(self):
        """煜明跳跳龙连招。"""
        self._cast("skill_q", self.skill_q, after_sleep=3)
        if self._ready("skill_e"):
            self.skill_e(after_sleep=0.3)
            self.combat_left_click()
            self.skill_config["skill_e_last_time"] = self.time()
        self._cast_z()

    def combat_skill_8_2(self):
        """芙洛拉灾厄武器普通副本连招。"""
        self._cast("skill_q", self.skill_q, after_sleep=3)
        self._cast("skill_e", self.skill_e, after_sleep=0.5)
        self._cast(
            "skill_click",
            lambda after_sleep=0: self.combat_left_click(dur=500),
        )
        self._cast_z()
        if self._ready("walk_to_w"):
            self.walk_to_s(500)
            self.skill_config["walk_to_w_last_time"] = self.time()
        self.combat_left_click()

    def combat_skill_8_2_2(self):
        """芙洛拉灾厄武器扼守副本连招。"""
        self._cast("skill_q", self.skill_q, after_sleep=3)
        self._cast_z()

    def combat_skill_9_1(self):
        """艾达正常挂机。"""
        if self._ready("skill_q"):
            self.skill_q(after_sleep=4)
            for _ in range(15):
                self.skill_e(after_sleep=0.5)
            self.skill_config["skill_q_last_time"] = self.time()
        self._cast_z()

