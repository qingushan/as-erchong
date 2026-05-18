# from ...res.task.BaseTask import BaseTask
from ...res.task.BaseAction import BaseAction

class RoleSkillUtil(BaseAction):
    # 角色技能搓招
    def __init__(self):
        super().__init__()

        self.role = None    # 角色
        self.skill_type = None   # 技能模组
        self.skill_config_custom = {}   # 自定义技能配置，通过外部设置
        self.skill_config = {}  #角色技能配置
        
    def init_config(self, role_type="0"):
        # 初始化配置
        self.skill_type = role_type

        if self.skill_type == "0":
            self.role = "自定义"
        elif self.skill_type == "1-1":
            self.role = "赛琪"
        elif self.skill_type == "2-1":
            self.role = "止流"

        self.set_role_skill_config()
        
        print(f"当前角色：{self.role}")
        print(f"技能模组{self.skill_type}")

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
            self.skill_config = self.skill_config_custom
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
            self.skill_config = {
                "skill_q_max_time": 2,
                "skill_q_last_time": 0,
                "skill_e_max_time": -1,
                "skill_e_last_time": 0,
            }
    
    def combat(self):
        # 战斗
        # print(f"释放技能：{self.role}")
        if self.skill_type == "0":
            self.combat_custom()
        elif self.skill_type == "1-1":
            self.combat_skill_1_1()
        elif self.skill_type == "2-1":
            self.combat_skill_2_1()

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

            return True

        # 原地e
        if self.time() - self.skill_config["skill_e_last_time"] >= self.skill_config["skill_e_max_time"]:
            # 释放原地e
            self.skill_e_saiqi_1()

            self.skill_config["skill_e_last_time"] = self.time()

            return True

    def combat_skill_2_1(self):
        # 止流龙喷

        # 大招
        if self.time() - self.skill_config["skill_q_last_time"] >= self.skill_config["skill_q_max_time"]:
            # 释放大招
            # 止流龙喷
            self.skill_e(dur=1000, after_sleep=1.5)
            self.skill_e(after_sleep=1)
            self.skill_q(after_sleep=4)

            self.skill_config["skill_q_last_time"] = self.time()

            self.sleep(3)

            return True