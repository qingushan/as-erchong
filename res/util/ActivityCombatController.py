from .CombatSkillController import CombatSkillController
from ..assets.color import common_color


class ActivityCombatController(CombatSkillController):
    """狩月人之阶活动的本地技能策略。

    类型后缀 ``-1`` 表示分组赛（凹分），``-2`` 表示常规赛（纪念币）。
    活动的开场连招、锁敌时机和分数模式与普通副本不同，因此统一放在
    本控制器中；活动页面仍只负责选择角色、模式和魔灵参数。
    """

    CONFIGS = {
        "7-4-1": {"index_": 0, "skill_z_max_time": 9999, "skill_z_max_count": 1},
        "7-4-2": {"skill_q_max_time": 30, "skill_z_max_time": 9999, "skill_z_max_count": 1},
        "2-4-1": {"skill_z_max_time": 9999, "skill_z_max_count": 1},
        "2-4-2": {"skill_z_max_time": 9999, "skill_z_max_count": 1},
        "3-4-1": {
            "max_time": 15, "skill_last_time": 0, "skill_e_time": 24,
            "skill_z_max_time": 9999, "skill_z_max_count": 1
        },
        "3-4-2": {
            "max_time": 15, "skill_last_time": 0, "skill_e_time": 40,
            "skill_z_max_time": 9999, "skill_z_max_count": 1
        },
        "8-4-1": {
            "max_time": 0.8, "skill_z_max_time": 9999, "skill_z_max_count": 1,
            "skill_e_max_time": -1, "skill_e_max_count": 1,
            # 战斗循环开始 15 秒后进入第二阶段：加快重击，并停止自动释放 E。
            "phase_switch_time": 15, "phase_switched": False,
            "combat_start_time": 0,
        },
        "8-4-2": {
            "skill_e_max_time": 3, "skill_e_max_count": 1,
            "skill_z_max_time": 10, "skill_z_max_count": 1,
            "skill_click_max_time": 5, "skill_click_max_count": 1,
            "click_lock_boss_max_time": 99999
        },
    }

    def configure(self, skill_type, skill_z_max_time=9999, skill_z_max_count=1):
        """加载活动角色/模式配置，并应用 UI 传入的魔灵参数。"""
        self.skill_type = skill_type
        self.skill_config = dict(self.CONFIGS.get(skill_type, {}))
        self.skill_config.update({
            "skill_z_max_time": float(skill_z_max_time),
            "skill_z_max_count": int(skill_z_max_count),
        })
        self.reset()

    def reset(self):
        """重置进入副本后的计时器和分组赛连招索引。"""
        now = self.time()
        for key in list(self.skill_config):
            if key.endswith("_last_time"):
                if key == "skill_z_last_time":
                    self.skill_config[key] = now
                elif key == "skill_click_last_time" and self.skill_type == "8-4-2":
                    # 芙洛拉常规活动保留进入副本后约 5 秒再重击的节奏。
                    self.skill_config[key] = now
                else:
                    self.skill_config[key] = 0
        if "index_" in self.skill_config:
            self.skill_config["index_"] = 0
        if self.skill_type == "8-4-1":
            # 每次进入新副本都从第一阶段重新开始，不能沿用上一局已经切换的状态。
            self.skill_config["max_time"] = 2
            self.skill_config["skill_e_max_time"] = 0.5
            self.skill_config["phase_switched"] = False
            self.skill_config["combat_start_time"] = 0

    def before(self):
        """执行寻敌前的开场连招，对应原 RoleSkillUtil.combat_before。"""
        if self.skill_type in ("7-4-1", "7-4-2"):
            self.skill_q(after_sleep=3)
        elif self.skill_type in ("2-4-1", "2-4-2"):
            for _ in range(2):
                self.action_jump_fly()
                self.sleep(0.5)
            self.walk_to_w(walk_time=500)
            self.skill_e(dur=1000, after_sleep=1.5)
            self.skill_e(after_sleep=1)
            self.skill_q(after_sleep=4)
            self.skill_e(after_sleep=1.5)
            self.walk_to_w(walk_time=1000)
        elif self.skill_type in ("3-4-1", "3-4-2"):
            self.walk_to_w(walk_time=6000)
            self.sleep(1)
            self.skill_q(after_sleep=4)
            self.combat_left_click()
            self.sleep(2)
            self.combat_left_click()
            self.sleep(1)
            self.walk_to_w(walk_time=2000)
        elif self.skill_type in ("8-4-1", "8-4-2"):
            for _ in range(2):
                self.action_jump_fly()
                self.sleep(0.5)
            self.sleep(1)
            # 芙洛拉开场跳跃后视角可能偏离任务目标；先将黄色任务图标转到屏幕中央，
            # 再释放大招，避免大招和后续走位朝错误方向执行。该调用复用活动任务的
            # rotate_view_to_middle_by_color 实现，控制器本身不重复坐标和找色逻辑。

            self.skill_q(after_sleep=4 + 10)
            self.skill_q(after_sleep=4)
            self.skill_q(after_sleep=4 + 4)

            self.rotate_view_to_middle_by_color(common_color, "任务黄色图标")
            self.sleep(1)

            self.sleep(6)

            if self.skill_type == "8-4-1":
                for i in range(8):
                    self.skill_e(after_sleep=0.5)
                self.combat_left_click(dur=500)
                self.sleep(0.5)
                for i in range(2):
                    self.skill_e(after_sleep=0.5)
            else:
                for _ in range(2):
                    self.action_jump_fly()

    def start(self):
        """执行寻敌后的首次准备，并建立活动技能的计时基准。"""
        if self.skill_type == "7-4-2":
            self.lock_enemy()
        elif self.skill_type == "2-4-2":
            self.lock_enemy()
            self.action_dodge_to_w()
            self.sleep(1)
        elif self.skill_type == "3-4-2":
            self.lock_enemy()
        now = self.time()
        if self.skill_type in ("3-4-1", "3-4-2"):
            self.skill_config["last_time"] = now
            self.skill_config["skill_last_time"] = now
        elif self.skill_type == "8-4-1":
            # 以正式进入战斗循环的时间作为 30 秒阶段切换基准；开场连招耗时不计入。
            self.skill_config["combat_start_time"] = now
            self.skill_config["last_time"] = 0
        self.skill_config["skill_z_last_time"] = 0

    def tick(self):
        """执行一次活动战斗循环；副本完成判断由活动任务外层完成。"""
        if self.skill_type == "7-4-1":
            if self.skill_config["index_"] >= 3:
                self.skill_e(after_sleep=0.1)
                self.rotate_view_to_right(250, dur=100, after_sleep=0.1)
                self.rotate_view_to_right(250, dur=100, after_sleep=0.1)
                self.skill_config["index_"] = 0
            else:
                self.skill_e(after_sleep=0.3)
            self.combat_left_click()
            self._cast_z()
            self.skill_config["index_"] += 1
            self.sleep(0.2)
        elif self.skill_type == "7-4-2":
            self._cast("skill_q", self.skill_q)
            self.skill_e(after_sleep=0.4)
            self.combat_left_click()
            self._cast_z()
            self.sleep(0.1)
        elif self.skill_type in ("2-4-1", "2-4-2"):
            self.skill_q(after_sleep=1 if self.skill_type == "2-4-1" else 0.5)
            self._cast_z()
            self.sleep(0.1)
        elif self.skill_type in ("3-4-1", "3-4-2"):
            if self.time() - self.skill_config["skill_last_time"] > self.skill_config["skill_e_time"]:
                for _ in range(3):
                    self.skill_q(after_sleep=0.5)
                if self.skill_type == "3-4-1":
                    self.skill_config["skill_e_time"] = 9999
                    self.sleep(2)
                    self.skill_q(after_sleep=4)
                else:
                    self.sleep(2)
                    for _ in range(3):
                        self.skill_q(after_sleep=0.5)
                    self.sleep(2)
                self.skill_config["skill_last_time"] = self.time()
            if self.time() - self.skill_config["last_time"] > self.skill_config["max_time"]:
                self.skill_e(after_sleep=0.2)
                self.skill_config["last_time"] = self.time()
                for _ in range(3):
                    self.combat_left_click()
                    self.sleep(0.3)
            elif self.skill_type == "3-4-1":
                self.combat_left_click()
                self.sleep(0.5)
            else:
                self.skill_e_suyi_0()
            self._cast_z()
            self.sleep(0.1)
        elif self.skill_type == "8-4-1":
            # 第二阶段只切换一次。将 E 间隔设为极大值等价于停止自动释放 E，
            # 同时把重击间隔从 2 秒缩短到 0.5 秒。
            if (not self.skill_config["phase_switched"] and
                    self.time() - self.skill_config["combat_start_time"] >=
                    self.skill_config["phase_switch_time"]):
                self.skill_config["max_time"] = 0.8
                self.skill_config["skill_e_max_time"] = 99999
                self.skill_config["phase_switched"] = True
                print("芙洛拉分组赛进入第二阶段：重击间隔0.5秒，停止自动释放E技能")

            # 第一阶段持续向右调整视角；满 30 秒切换第二阶段后立即停止旋转。
            # if not self.skill_config["phase_switched"]:
            #     self.rotate_view_to_right(250, dur=100, after_sleep=0.1)

            if self.time() - self.skill_config["last_time"] > self.skill_config["max_time"]:
                self.combat_left_click(dur=500)
                self.skill_config["last_time"] = self.time()
            # self._cast("skill_e", self.skill_e, after_sleep=0.5)
            self._cast_z()
            self.sleep(0.1)
        elif self.skill_type == "8-4-2":
            if self._ready("click_lock_boss"):
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()
            self._cast("skill_e", self.skill_e, after_sleep=0.5)
            self._cast("skill_click", lambda after_sleep=0: self.combat_left_click(dur=500))
            self._cast_z()
            self.combat_left_click()
            self.sleep(0.1)
