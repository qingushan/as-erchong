class CombatSkillController:
    """本地任务战斗技能控制器基类。

    控制器只负责“什么时候释放什么技能”以及保存本轮战斗状态；点击、
    找色、OCR、走位等设备相关动作仍由传入的任务对象实现。这样技能策略
    可以从任务流程中独立出来，同时继续使用本地游戏现有的坐标和动作封装。
    ``skill_config`` 中约定 ``*_max_time`` 为冷却间隔、``*_last_time``
    为上次释放时间、``*_max_count`` 为一次触发的释放次数。
    """

    def __init__(self, task):
        self.task = task
        self.skill_config = {}

    def __getattr__(self, name):
        # 不在控制器中复制 BaseAction 的坐标实现，所有动作动态转发给任务。
        return getattr(self.task, name)

    def _ready(self, name):
        """判断指定技能是否到达冷却时间；负数间隔表示禁用该技能。"""
        interval = self.skill_config.get(name + "_max_time", -1)
        last_time = self.skill_config.get(name + "_last_time", 0)
        return interval >= 0 and self.time() - last_time >= interval

    def _cast(self, name, action, after_sleep=0, count_key=None):
        """按统一计时规则释放技能，并在整组动作完成后更新时间戳。"""
        if not self._ready(name):
            return False
        count = self.skill_config.get(count_key or name + "_max_count", 1)
        for _ in range(count):
            action(after_sleep=after_sleep)
        self.skill_config[name + "_last_time"] = self.time()
        return True

    def _cast_z(self, after_sleep=0.1):
        """活动和自定义策略共用的魔灵技能释放入口。"""
        return self._cast("skill_z", self.skill_z, after_sleep=after_sleep)

    def reset(self):
        """重置进入新副本时的运行时计时，不改变技能参数。"""
        now = self.time()
        for key in list(self.skill_config):
            if key.endswith("_last_time"):
                self.skill_config[key] = now if key == "skill_z_last_time" else 0
