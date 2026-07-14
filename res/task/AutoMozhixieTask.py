from ...res.task.BaseTask import BaseTask
from ...res.util.RoleSkillUtil import RoleSkillUtil
from ...res.assets.color import *

class AutoMozhixieTask(BaseTask):
    # 魔之楔
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '魔之楔'

        self.level_grade = 60   # 副本等级
        self.level_max_count = 2 # 最大探索次数

        self.now_level_boci = 1     # 当前波次,默认1
        self.level_more_award = 0  # 委托手册
        self.level_more_award_boci = [] # 使用委托手册的轮次

        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.level_skill_e_time = 10  # 技能释放间隔
        self.level_skill_e_count = 1  # 技能释放次数
        self.level_skill_e_last_time = 0  # 最后一次释放技能时间
        self.level_skill_q_time = 10  # 大招释放间隔
        self.level_skill_q_count = 1  # 大招释放次数
        self.level_skill_q_last_time = 0  # 最后一次释放大招时间

        self.set_skill_config()

    def set_skill_config(self):
        # 初始化技能配置
        self.role_skill_util.init_config(self.uiconfig.get('mozhixie_role_skill', '0'))

    def init_task(self):
        # 初始化
        self.now_level_boci = 1

        self.level_grade = int(self.uiconfig['mozhixie_grade'])
        self.level_max_count = int(self.uiconfig['mozhixie_max_num'])

        # 构建自定义技能配置传入【角色技能搓招】
        skill_config = {
            "skill_q_max_time": float(self.uiconfig['mozhixie_skill_q_time']),
            "skill_q_max_count": int(self.uiconfig['mozhixie_skill_q_count']),
            "skill_e_max_time": float(self.uiconfig['mozhixie_skill_e_time']),
            "skill_e_max_count": int(self.uiconfig['mozhixie_skill_e_count']),
            "skill_z_max_time": float(self.uiconfig.get('mozhixie_skill_z_time', 30)),
            "skill_z_max_count": int(self.uiconfig.get('mozhixie_skill_z_count', 1)),
        }
        self.role_skill_util.set_role_skill_config_custom(skill_config)

        self.level_more_award = int(self.uiconfig['mozhixie_level_more_award'])
        str_ = self.uiconfig['mozhixie_level_more_award_boci']
        str_ = str_.replace("，",",")
        if str_ == "-1":
            self.level_more_award_boci.append(1)
        elif "," not in str_:
            self.level_more_award_boci.append(int(str_))
        else:
            list_ = str_.split(",")
            for i in list_:
                self.level_more_award_boci.append(int(i))
        
        print(f"当前委托手册:{self.level_more_award}")
        print(f"使用委托手册的轮次:{self.level_more_award_boci}")

    def add_moling_skill(self):
        """
        添加魔灵技能
        """
        skill_config = {
            "skill_z_max_time": float(self.uiconfig.get('mozhixie_skill_z_time', 30)),
            "skill_z_max_count": int(self.uiconfig.get('mozhixie_skill_z_count', 1))
        }
        self.role_skill_util.add_skill_z(skill_config)

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
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=126,y=415)
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"历练委托菜单",x=47,y=184)
        self.sleep(2)
        
        for i in range(3):
            self.slide(1193,376,900,376,dur=500)
            self.sleep(2)
            if self.await_until_click_ocr(rect=[423,484,1248,613],pattern="(驱离|魔之楔)",time_out=5):
                self.sleep(2)
                break
            
        res = self.await_until_color(mozhixie_color,"开始挑战")
        if not res:
            print("进入魔之楔副本失败")
            self.click_color_to_color(common_color,"左上角红色退出",common_color,"主界面左上角菜单",x=43,y=34)
            self.sleep(2)

            for i in range(3):
                self.click(634,666)

            res = self.find_my_color(common_color,"角色血条-绿色")
            if res:
                print("成功返回主界面")
            else:
                print("返回主界面失败")
            
            return False
        self.sleep(1)
        print(f"成功进入{self.task_name}副本选择界面")
        return True

    def select_level_grade(self):
        # 选择等级
        if self.level_grade == 40:
            self.click(126,169)
        elif self.level_grade == 60:
            self.click(124,209)
        elif self.level_grade == 80:
            self.click(124,255)
        elif self.level_grade == 100:
            self.click(124,303)

        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(mozhixie_color,"开始挑战")
        if res:
            self.click_color_to_color(mozhixie_color,"开始挑战",common_color,"委托手册选择界面",x=1171,y=672)
            self.sleep(1)

        res = self.find_my_color(common_color,"副本退出-再次进行")
        if res:
            self.click_color_to_color(common_color,"副本退出-再次进行",common_color,"委托手册选择界面",x=894,y=676)
            self.sleep(1)
        
        # 使用委托手册
        self.check_use_level_more_award()

        self.click_color_to_color(common_color,"委托手册选择界面",common_color,"角色血条-绿色",x=774,y=505,out_time=60)
        self.sleep(2)

        # 重置技能时间
        self.role_skill_util.set_role_skill_config()

        # 添加魔灵技能
        self.add_moling_skill()

        print("成功进入副本")

    def quit_level(self):
        # 退出当前副本
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"地图esc界面",x=40,y=29)
        self.sleep(1)
        self.click_color_to_color(common_color,"地图esc界面",common_color,"退出委托-确定",x=1189,y=639)
        self.sleep(1)
        self.click_color_to_color(common_color,"退出委托-确定",common_color,"副本退出-再次进行",x=777,y=412,out_time=60)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(common_color,"副本退出-再次进行")
        if res:
            self.click_color_to_color(common_color,"副本退出-再次进行",common_color,"左上角红色退出",x=1141,y=672,out_time=60)
            self.sleep(1)

        res = self.find_my_color(role_exp_color,"开始挑战")
        if res:
            self.click_color_to_color(role_exp_color,"开始挑战",common_color,"历练委托菜单",x=44,y=32,out_time=60)
            self.sleep(1)

        self.click_color_to_color(common_color,"左上角红色退出",common_color,"主界面左上角菜单",x=43,y=34)
        self.sleep(2)

        for i in range(3):
            self.click(634,666)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def combat(self):
        # 战斗
        print("开始战斗")
        start_time = self.time()

        max_time = 60 * 5

        self.sleep(1)

        res = self.find_my_color(mod_color,"驱离电梯图")
        if res:
            print("电梯图")
            self.walk_to_w(1000*10)
            self.sleep(5)
        else:
            for i in range(1):
                self.action_jump_fly()
                self.sleep(0.5)
            self.sleep(1)

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.find_my_color(common_color,"副本退出-再次进行")
            if res:
                self.sleep(1)
                print("战斗完成")
                return True

            # 释放技能
            self.role_skill_util.combat()

            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}"
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
            if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                res = self.is_refresh_time_execute_mihan()
                if res:
                    self.level_exit()
                    return True
            
            self.go_in_level()

            res = self.combat()
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                print("战斗超时")
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
                continue
            

