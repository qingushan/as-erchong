from .CombatSkillController import CombatSkillController


class LMYYCombatController(CombatSkillController):
    """联袂演绎的本地技能策略。

    技能类型沿用原配置值：``5-3`` 为猪妹、``7-3`` 为煜明、``8-3``
    为芙洛拉。控制器只处理战斗内的锁敌、追踪、Q/E/Z 和重击节奏，
    大厅筛选、进出副本以及当前 BOSS 识别继续由联袂演绎任务负责。
    """

    def configure(self, skill_type, trace_boss="0"):
        """加载角色连招和追踪 BOSS 方式，并初始化本轮计时器。"""
        self.skill_type = skill_type
        self.trace_boss = trace_boss
        self.skill_config = {
            "5-3": {"skill_e_max_time": 0, "skill_e_max_count": 1,
                    "skill_z_max_time": 10, "skill_z_max_count": 1,
                    "click_lock_boss_max_time": 3, "dodge_max_time": 5},
            "7-3": {"skill_q_max_time": 99999, "skill_e_max_time": 0,
                    "skill_e_max_count": 1, "skill_z_max_time": 10,
                    "skill_z_max_count": 1, "click_lock_boss_max_time": 3},
            "8-3": {"skill_q_max_time": 99999, "skill_e_max_time": 1,
                    "skill_e_max_count": 1, "skill_z_max_time": 10,
                    "skill_z_max_count": 1, "dodge_to_w_max_time": 9999,
                    "skill_click_max_time": 1, "click_lock_boss_max_time": 1},
        }.get(skill_type, {})
        self.skill_config["lmyy_trace_boss"] = trace_boss
        self.reset()

    def reset(self):
        """进入新副本时清零冷却；芙洛拉重击仍保留原来的 3 秒延迟。"""
        now = self.time()
        for key in list(self.skill_config):
            if key.endswith("_last_time"):
                self.skill_config[key] = now if key == "skill_click_last_time" and self.skill_type == "8-3" else 0
        if self.skill_type == "8-3":
            self.skill_config["skill_click_last_time"] = now + 3

    def add_skill_z(self, max_time, max_count):
        """覆盖活动页面配置的魔灵冷却和单次释放次数。"""
        self.skill_config["skill_z_max_time"] = float(max_time)
        self.skill_config["skill_z_max_count"] = int(max_count)
        self.skill_config["skill_z_last_time"] = 0

    def tick(self):
        """执行一次联袂演绎战斗循环，不负责判断副本是否结束。"""
        if self.skill_type == "5-3":
            if self._ready("click_lock_boss"):
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()
            if self._ready("dodge"):
                if self.trace_boss == "0":
                    self.sleep(0.3)
                    self.action_jump_fly(after_sleep=0.5)
                elif self.trace_boss == "1":
                    self.fly_spear()
                self.skill_config["dodge_last_time"] = self.time()
            self._cast("skill_e", self.skill_e, after_sleep=0.1)
            self._cast_z()
        elif self.skill_type == "7-3":
            if self._ready("click_lock_boss"):
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()
            self._cast("skill_q", self.skill_q, after_sleep=3)
            self.skill_e(after_sleep=0.3)
            self.combat_left_click()
            self._cast_z()
        elif self.skill_type == "8-3":
            if self._ready("click_lock_boss"):
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()
            if self._ready("skill_q"):
                for _ in range(3):
                    self.skill_q(after_sleep=0.5)
                self.sleep(1.5)
                self.skill_config["skill_q_last_time"] = self.time()
            self._cast("skill_e", self.skill_e, after_sleep=0.5)
            self._cast("skill_click", lambda after_sleep=0: self.combat_left_click(dur=500))
            self._cast("dodge_to_w", lambda after_sleep=0: self.action_dodge_to_w())
            self._cast_z()
            self.combat_left_click()
