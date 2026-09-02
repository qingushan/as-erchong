from ...res.task.BaseTask import BaseTask
from ...res.combat.local.CombatSkillController import CombatSkillController
from ...res.assets.color import *

class AutoRoleExpTask(BaseTask):
    # 角色经验
    def __init__(self,uiconfig=None):
        super().__init__()
        self.combat_skill = CombatSkillController(self)

        self.uiconfig = uiconfig

        self.task_name = '角色经验'

        self.level_grade = 60   # 副本等级
        self.level_max_count = 2 # 最大探索次数

        self.now_level_boci = 1     # 当前波次,默认1
        self.level_more_award = 0  # 委托手册
        self.level_more_award_boci = [] # 使用委托手册的轮次

        
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.level_skill_e_time = 10  # 技能释放间隔
        self.level_skill_e_last_time = 0  # 最后一次释放技能时间
        self.level_skill_q_time = 10  # 技能释放间隔
        self.level_skill_q_last_time = 0  # 最后一次释放大招时间

        self.map_type = 0

        self.set_skill_config()

    def set_skill_config(self):
        # 初始化技能配置
        self.combat_skill.init_config(self.uiconfig.get('role_exp_role_skill', '0'))

    def rotate_view_to_middle_by_color(self, color_dict, color_name):
        # 根据颜色旋转视角至中间
        start_time = self.time()  # 开始时间，超时则退出
        max_time = 60  # 最大超时时间

        while 1:
            if self.time() - start_time > max_time:
                return False

            point = self.find_my_color(color_dict,color_name)
            if point:
                res = self.position_is_left_or_right(point.x, point.y)
                if (res == 1) or (res == 3):
                    return True
                if abs(point.x-self.center_x) > 100:
                    self.rotate_view_to_close_by_ori(res,rotate_x=100)
                else:
                    self.rotate_view_to_close_by_ori(res)
            else:
                return False

            self.sleep(0.1)

        return False

    def init_task(self):
        # 初始化
        self.map_type = -1
        self.now_level_boci = 1

        self.level_grade = int(self.uiconfig['role_exp_grade'])
        self.level_max_count = int(self.uiconfig['role_exp_max_num'])

        # 构建自定义技能配置传入【角色技能搓招】
        skill_config = {
            "skill_q_max_time": float(self.uiconfig['role_exp_skill_q_time']),
            "skill_q_max_count": int(self.uiconfig.get('role_exp_skill_q_count', 1)),
            "skill_e_max_time": float(self.uiconfig['role_exp_skill_e_time']),
            "skill_e_max_count": int(self.uiconfig.get('role_exp_skill_e_count', 1)),
            "skill_z_max_time": float(self.uiconfig.get('role_exp_skill_z_time', 30)),
            "skill_z_max_count": int(self.uiconfig.get('role_exp_skill_z_count', 1)),
        }
        self.combat_skill.set_role_skill_config_custom(skill_config)

        self.level_more_award = int(self.uiconfig['role_exp_level_more_award'])
        str_ = self.uiconfig['role_exp_level_more_award_boci']
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
        self.go_to_lilian()
        self.sleep(1)
        self.click_color_to_color(common_color,"历练委托菜单",role_exp_color,"开始挑战",x=753,y=373)
        self.sleep(1)
        print(f"成功进入{self.task_name}副本选择界面")

    def select_level_grade(self):
        # 选择等级
        if self.level_grade == 5:
            self.click(121,167)
        elif self.level_grade == 20:
            self.click(121,212)
        elif self.level_grade == 35:
            self.click(122,260)
        elif self.level_grade == 40:
            self.click(123,303)
        elif self.level_grade == 50:
            self.click(128,351)
        elif self.level_grade == 60:
            self.click(125,395)
        elif self.level_grade == 70:
            self.click(124,442)

        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.map_type = -1
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(role_exp_color,"开始挑战")
        if res:
            self.click_color_to_color(role_exp_color,"开始挑战",common_color,"委托手册选择界面",x=1171,y=672)
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
        self.combat_skill.set_role_skill_config()

        print("成功进入副本")

    def check_is_combat(self):
        # 判断是否成功进入战斗
        res = self.await_until_ocr(rect=[11,206,276,334],pattern="制作血清",time_out=5)
        if res:
            print("激活副本成功")
            return True
        else:
            print("激活副本失败")
            return False

    def go_to_activate_level(self):
        # 前往激活任务
        if self.level_grade == 60:
            res = self.go_to_activate_level_60()
            if res:
                return True
        elif self.level_grade == 40:
            # 不用激活
            return True

        return False

    def leave_level(self):
        # 撤离
        print("开始撤离")
        if self.level_grade == 60:
            res = self.leave_level_60()
            if res:
                return True
        elif self.level_grade == 40:
            return True

        return False

    def unlocking(self):
        # 开锁
        res = self.click_until_ocr(796,360,rect=[1120,532,1232,618],pattern="快速")
        if not res:
            print("开锁失败")
            self.click(1227,44)
            self.sleep(2)
            return False
        self.sleep(1)
        self.click(1172,580)
        self.sleep(2)

        print("开锁成功")
        return True

    def go_to_activate_level_60(self):
        # 60级激活副本
        self.sleep(1)
        self.walk_to_w(1000*10)
        self.sleep(5)
        self.walk_to_d(1000*5)
        self.sleep(0.5)

        self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        self.sleep(0.5)

        self.walk_to_w(500)

        res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,70)
        if not res:
            return False
        self.sleep(0.5)

        for i in range(2):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)
        
        self.sleep(1)
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        self.sleep(0.5)
        self.walk_to_w(1000)

        self.sleep(0.5)
        for i in range(15):
            res = self.is_text_re_in_ocr(rect=[731,328,845,388],pattern="操作")
            if res:
                break
            self.walk_to_w(300)
            self.sleep(1)

        res = self.is_text_re_in_ocr(rect=[731,328,845,388],pattern="操作")
        if not res:
            print("激活副本失败")
            return False
        
        res = self.unlocking()
        if not res:
            return False

        self.role_restoration()
        self.await_until_color(common_color,"任务黄色图标",time_out=5)

        self.map_type = -1   # 0：前方   1：后面  2：右边   3:不可复位
        res = self.find_my_color(common_color,"任务黄色图标")
        print(res)
        if res:
            if res.x > 880:
                self.map_type = 2
            elif (440 < res.x < 500) and  (420 < res.y < 470):
                self.map_type = 1
            elif 650 < res.x < 690:
                self.map_type = 0
            else:
                self.map_type = 3
        print(f"当前地图：{self.map_type}")

        if self.map_type == -1:
            return False

        if self.map_type == 0:
            for i in range(11):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(0.5)
        
            self.action_jump_fly()
            self.sleep(1)
            
            self.role_restoration()

            res = self.check_is_combat()
            return res

        elif self.map_type == 1:
            for i in range(4):
                self.rotate_view_to_left(150,dur=500)
            self.sleep(0.5)
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            
            res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,300)
            if not res:
                return False
            self.sleep(0.5)

            self.fly_spear_num(5)
            self.sleep(2)
            self.walk_to_s()
            self.sleep(2)
            self.walk_to_w()
            self.sleep(0.5)

            res = self.rotate_view_direction_range(common_color,"任务黄色图标",1,70)
            if not res:
                return False
            self.sleep(0.5)

            self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            self.sleep(0.5)
            for i in range(3):
                self.fly_spear_num(1)
                self.sleep(1)
            
            self.role_restoration()

            res = self.check_is_combat()
            return res

        elif self.map_type == 2:
            self.rotate_view_to_right(150,dur=500)
            self.rotate_view_to_right(150,dur=500)
            self.sleep(0.5)
            for i in range(2):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
            
            self.walk_to_d(1000*2)

            self.action_jump_fly()
            self.sleep(1)
            
            self.walk_to_a(1000*2)
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False

            for i in range(3):
                self.action_jump_fly()
                self.sleep(0.5)

            self.role_restoration()

            res = self.check_is_combat()
            return res

        elif self.map_type == 3:
            for i in range(10):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(0.5)
        
            self.walk_to_d(1000*2)

            self.action_jump_fly()
            self.sleep(1)
            
            self.walk_to_a(1000*2)
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False

            for i in range(3):
                self.action_jump_fly()
                self.sleep(0.5)

            self.role_restoration()

            res = self.check_is_combat()
            return res

    def leave_level_60(self):
        # 60级撤离
        if self.map_type == 0:
            for i in range(3):
                self.rotate_view_to_right(150,dur=500)
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(role_exp_color,"撤离点图标")
            if not res:
                return False
            
            res = self.rotate_view_direction_range(role_exp_color,"撤离点图标",0,180)
            if not res:
                return False
            self.sleep(0.5)
            
            self.fly_spear_num(4)
            self.sleep(2)
            self.rotate_view_to_down(50,dur=500)
            # res = self.rotate_view_direction_range(role_exp_color,"撤离点图标",1,50)
            # if not res:
            #     return False
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(role_exp_color,"撤离点图标")
            if not res:
                return False
            for i in range(3):
                self.action_jump_fly()
                self.sleep(0.5)

        elif self.map_type == 1:
            for i in range(4):
                self.rotate_view_to_left(150,dur=500)
            self.sleep(0.5)
            res = self.rotate_view_to_middle_by_color(role_exp_color,"撤离点图标")
            if not res:
                return False
            self.sleep(0.5)
            self.rotate_view_to_left(50,dur=500)
            self.sleep(0.5)

            for i in range(6):
                self.action_jump_fly()
                self.sleep(0.5)
            
            self.walk_to_d(1000*4)
            self.sleep(0.5)
            self.walk_to_a(1000)
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(role_exp_color,"撤离点图标")
            if not res:
                return False
            
            for i in range(3):
                self.action_jump_fly()
                self.sleep(0.5)

        elif (self.map_type == 2) or (self.map_type == 3):
            self.rotate_view_to_right(200,dur=500)
            self.rotate_view_to_right(150,dur=500)
            self.sleep(0.5)
            res = self.rotate_view_to_middle_by_color(role_exp_color,"撤离点图标")
            if not res:
                return False
            self.sleep(0.5)
            self.rotate_view_to_left(50,dur=500)
            self.sleep(0.5)

            for i in range(6):
                self.action_jump_fly()
                self.sleep(0.5)
            
            self.walk_to_d(1000*4)
            self.sleep(0.5)
            self.walk_to_a(1000)
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(role_exp_color,"撤离点图标")
            if not res:
                return False
            
            for i in range(3):
                self.action_jump_fly()
                self.sleep(0.5)
            
        self.role_restoration()
        self.await_until_color(role_exp_color,"撤离点图标",time_out=5)

        res = self.find_my_color(role_exp_color,"撤离点图标")
        if res:
            if 530 < res.x <575:
                pass
            else:
                self.rotate_view_to_right(150,dur=500)
                self.rotate_view_to_right(150,dur=500)
                self.sleep(0.5)
        else:
            self.rotate_view_to_right(150,dur=500)
            self.rotate_view_to_right(150,dur=500)
            self.sleep(0.5)
    
        for i in range(15):
            res = self.find_my_color(common_color,"副本退出-再次进行")
            if res:
                break
            if self.find_my_color(role_exp_color,"撤离点图标"):
                self.rotate_view_to_middle_by_color(role_exp_color,"撤离点图标")
                self.action_jump_fly()
            self.sleep(1)
        
        if self.find_my_color(common_color,"副本退出-再次进行"):
            print("成功撤离")
            return True
        else:
            print("撤离失败")
            return False

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

        self.click_until_ocr(x=44, y=34, rect=[119, 277, 344, 385], pattern="商店")
        self.sleep(1)

        for i in range(3):
            self.click(778, 684)

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

        while 1:
            if self.time() - start_time > max_time:
                return False

            # 40级比较特殊，不需要撤离跑图
            if self.level_grade == 40:
                r = self.find_my_color(common_color,"副本退出-再次进行")
                if r:
                    print("战斗完成")
                    self.sleep(0.5)
                    return True
            else:
                r1 = self.find_my_color(role_exp_color,"右上角绿色图标")
                r2 = self.is_text_re_in_ocr(rect=[11,199,215,324],pattern="100%")
                if r1 or r2:
                    self.sleep(5)
                    print("战斗完成")
                    return True

            # 释放技能
            self.combat_skill.combat()

            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}"
        self.logui.change_log_text(text)

    def run(self):
        self.init_task()
        self.refresh_log()
        self.go_to_level()
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

            res = self.go_to_activate_level()
            if not res:
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
                continue

            res = self.combat()
            if not res:
                print("战斗异常")
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
                continue
            
            # 开始撤离
            res = self.leave_level()
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
                continue
