from .CombatSkillController import CombatSkillController


class CJSXJCombatController(CombatSkillController):
    """沉浸式戏剧的本地技能策略。

    ``8-1`` 是芙洛拉内置连招：非 BOSS 阶段保持走位和重击，识别到
    BOSS 后缩短重击间隔并启用锁敌/技能。其他角色走 UI 提供的自定义
    Q/E/Z 冷却配置；BOSS 的识别和特殊闪避仍由 ``AutoCJSXJTask`` 负责。
    """

    def configure(self, role_type="0", custom_config=None):
        """根据角色选择内置配置或读取沉浸式戏剧的自定义配置。"""
        custom_config = custom_config or {}
        self.role_type = role_type
        self.skill_type = role_type
        self.role = self.get_role_name(role_type)
        if role_type == "8-1":
            self.skill_config = {
                "skill_q_max_time": 99999, "skill_e_max_time": 1, "skill_e_max_count": 1,
                "walk_to_w_max_time": 4, "skill_click_max_time": 2,
                "skill_click_max_count": 1, "click_lock_boss_max_time": 1,
            }
        else:
            self.skill_config = {
                "skill_q_max_time": float(custom_config.get("skill_q_max_time", -1)),
                "skill_q_max_count": int(custom_config.get("skill_q_max_count", 1)),
                "skill_e_max_time": float(custom_config.get("skill_e_max_time", -1)),
                "skill_e_max_count": int(custom_config.get("skill_e_max_count", 1)),
                "skill_z_max_time": float(custom_config.get("skill_z_max_time", -1)),
                "skill_z_max_count": int(custom_config.get("skill_z_max_count", 1)),
            }
        self.apply_skill_z(
            custom_config.get("skill_z_max_time", -1),
            custom_config.get("skill_z_max_count", 1),
        )
        self.reset()
        self.print_skill_info()

    def reset(self):
        """只清理运行时计时，保留用户设置的技能间隔和释放次数。"""
        now = self.time()
        for key in list(self.skill_config):
            if key.endswith("_last_time"):
                self.skill_config[key] = 0
        if self.role_type == "8-1":
            self.skill_config["skill_click_last_time"] = 0

    def tick(self, boss=None):
        """执行一次战斗循环；返回值保持任务原有的“是否执行了动作”语义。"""
        if self.role_type != "8-1":
            if self._cast("skill_q", self.skill_q):
                return True
            if self._cast("skill_e", self.skill_e):
                return True
            if self._cast_z():
                return True
            return False

        if boss is not None:
            self.skill_config["skill_click_max_time"] = 1
            if self._ready("click_lock_boss"):
                self.lock_enemy()
                self.skill_config["click_lock_boss_last_time"] = self.time()
            self._cast("skill_e", self.skill_e, after_sleep=0.5)
        self._cast("skill_q", self.skill_q, after_sleep=3)
        if self._ready("walk_to_w"):
            self.walk_to_s(500)
            self.skill_config["walk_to_w_last_time"] = self.time()
        self._cast("skill_click", lambda after_sleep=0: self.combat_left_click(dur=500))
        self._cast_z()
        self.combat_left_click()
        return True
