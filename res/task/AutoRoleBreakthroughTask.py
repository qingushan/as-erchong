from ...res.task.BaseTask import BaseTask
from ...res.util.RoleSkillUtil import RoleSkillUtil
from ...res.assets.color import *

class AutoRoleBreakthroughTask(BaseTask):
    # 角色突破
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '角色突破'

        self.level_grade = 30   # 副本等级
        self.level_boci = 1       # 波次    
        self.level_property = '水'  # 副本属性
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

        self.capture_moling = False  # 是否抓取魔灵
        self.moling_count = 0   # 已抓取的魔灵数量
        self.moling_names = []  # 抓取的具体魔灵

        self.set_skill_config()

    def set_skill_config(self):
        # 初始化技能配置
        self.role_skill_util.init_config(self.uiconfig.get('role_tupo_role_skill', '0'))

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
        self.level_grade = int(self.uiconfig['role_tupo_grade'])
        self.level_max_count = int(self.uiconfig['role_tupo_max_num'])
        self.level_boci = int(self.uiconfig['role_tupo_boci_num'])
        self.level_property = self.uiconfig['role_tupo_property']

        # 构建自定义技能配置传入【角色技能搓招】
        skill_config = {
            "skill_q_max_time": float(self.uiconfig['role_tupo_skill_q_time']),
            "skill_q_max_count": int(self.uiconfig['role_tupo_skill_q_count']),
            "skill_e_max_time": float(self.uiconfig['role_tupo_skill_e_time']),
            "skill_e_max_count": int(self.uiconfig['role_tupo_skill_e_count']),
            "skill_z_max_time": float(self.uiconfig.get('role_tupo_skill_z_time', 30)),
            "skill_z_max_count": int(self.uiconfig.get('role_tupo_skill_z_count', 1)),
        }
        self.role_skill_util.set_role_skill_config_custom(skill_config)

        # 是否抓取魔灵
        # if (self.uiconfig['role_tupo_moling'] == "on"):
        #     print("抓取魔灵")
        #     self.capture_moling = True
        # else:
        #     print("不抓取魔灵")
        #     self.capture_moling = False

        self.level_more_award = int(self.uiconfig['role_tupo_level_more_award'])
        str_ = self.uiconfig['role_tupo_level_more_award_boci']
        str_ = str_.replace("，",",")
        if str_ == "-1":
            self.level_more_award_boci = list(range(1,self.level_boci+1))
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
        self.click_color_to_color(common_color,"主界面左上角菜单",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=126,y=415)
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"历练委托菜单",x=47,y=184)
        self.sleep(1)
        self.click_color_to_color(common_color,"历练委托菜单",role_tupo_color,"委托-探险",x=1165,y=385)
        self.sleep(1)
        print(f"成功进入{self.task_name}副本选择界面")

    def select_level_grade(self):
        # 选择等级
        if self.level_grade == 10:
            self.click(117,166)
        elif self.level_grade == 20:
            self.click(119,213)
        elif self.level_grade == 30:
            self.click(119,261)
        elif self.level_grade == 40:
            self.click(115,305)
        elif self.level_grade == 50:
            self.click(118,348)
        elif self.level_grade == 60:
            self.click(118,395)
        elif self.level_grade == 70:
            self.click(112,440)

        self.sleep(1)

    def select_property(self):
        # 选择属性
        if self.level_property == '水':
            self.click(904,625)
        elif self.level_property == '火':
            self.click(971,621)
        elif self.level_property == '风':
            self.click(1036,623)
        elif self.level_property == '雷':
            self.click(1103,623)
        elif self.level_property == '光':
            self.click(1169,621)
        elif self.level_property == '暗':
            self.click(1235,621)
        
        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(role_tupo_color,"委托-探险")
        if res:
            self.click_color_to_color(jjb_color,"委托-开始挑战",common_color,"委托手册选择界面",x=1168,y=672)
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

        print("成功进入副本")

    def go_to_activate_level(self):
        # 前往激活任务
        if self.level_grade == 30:
            res = self.go_to_activate_level_30()
            if res:
                return True
        elif self.level_grade == 60:
            res = self.go_to_activate_level_30()
            if res:
                return True

        return False

    def check_is_combat(self):
        # 判断是否成功进入战斗
        res = self.await_until_ocr(rect=[4,166,159,316],pattern="(轮次|血清)",time_out=5)
        if res:
            print("激活副本成功")
            return True
        else:
            print("激活副本失败")
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

    def go_to_activate_level_30(self):
        # 30级激活副本
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
        self.walk_to_w(1000*1.5)

        self.sleep(0.5)
        for i in range(15):
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
            if res:
                break
            self.walk_to_w(300)
            self.sleep(1)

        res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
        if not res:
            print("激活副本失败")
            return False
        
        res = self.unlocking()
        if not res:
            return False

        res = self.check_is_combat()
        if not res:
            return False

        # 向后走
        for i in range(5):
            self.walk_to_s(1000)
        self.sleep(0.5)

        for i in range(1):
            self.walk_to_d(1000)
        self.sleep(0.5)

        for i in range(2):
            self.walk_to_s(1000)
        self.sleep(0.5)

        self.walk_to_w(300)
        self.sleep(0.5)

        return True

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        res = self.find_my_color(common_color,"波次结束界面")
        if res:
            print("波次结束界面")
            self.click_color_to_color(common_color,"波次结束界面",common_color,"副本退出-再次进行",x=392,y=526,out_time=60)
            self.sleep(3)
            return True
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

        res = self.find_my_color(role_tupo_color,"委托-探险")
        if res:
            self.click_color_to_color(role_tupo_color,"委托-探险",common_color,"左上角红色退出",x=44,y=32,out_time=60)
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

    def is_have_moling(self):
        # 判断是否有魔灵
        res = self.find_my_color(role_tupo_color,"魔灵任务-图标")
        if res:
            return True
        else:
            return False

    def go_to_capture_moling(self):
        # 前往抓取魔灵
        map_type = -1   # 魔灵位置  0：前方
        self.role_restoration()
        self.sleep(1)
        res = self.find_my_color(role_tupo_color,"魔灵图标")
        print(res)
        if not res:
            print("未识别到魔灵位置！！！")
            return False
        
        if (710 < res.x < 740):
            map_type = 0

        print(f"魔灵位置：{map_type}")
        if map_type == 0:
            self.rotate_view_to_middle_by_color(role_tupo_color,"魔灵图标")
            self.sleep(0.5)
            self.rotate_view_direction_range(role_tupo_color,"魔灵图标",0,200)
            self.fly_spear_num(7)
            self.sleep(3)
            # for i in range(5):
            #     self.action_jump_fly()
            #     self.sleep(1)

            # self.rotate_view_to_middle_by_color(role_tupo_color,"魔灵图标")
            # self.sleep(0.5)
            # self.rotate_view_direction_range(role_tupo_color,"魔灵图标",0,150)
            # self.sleep(0.5)
            # self.rotate_view_direction_range(role_tupo_color,"魔灵图标",2,20)
            # self.sleep(0.5)
            # self.fly_spear_num(4)
            # self.sleep(3)

            self.walk_to_s()
            self.walk_to_w()
            self.sleep(1)

            self.fly_spear_num(2)
            self.sleep(2)

            # self.walk_to_w(2000)

            self.rotate_view_to_middle_by_color(role_tupo_color,"魔灵图标")
            self.sleep(0.5)

            self.fly_spear_num(2)
            self.sleep(2)
            self.walk_to_s()
            self.sleep(1)
            for i in range(4):
                self.walk_to_a()
            self.sleep(1)

            self.walk_to_d(500)
            # self.walk_to_a()

    def combat(self):
        # 战斗
        print("开始战斗")
        start_time = self.time()

        max_time = 60 * 5

        now_boci = 1  # 当前波次

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.find_my_color(common_color,"波次结束界面")
            if res:
                self.sleep(1)
                res = self.find_my_color(common_color,"波次结束界面")
                if not res:
                    continue
                    
                print(f"波次完成，当前波次：{now_boci}/{self.level_boci}")
                self.now_level_boci += 1
                
                if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                    res = self.is_refresh_time_execute_mihan()
                    if res:
                        self.click_color_to_color(common_color,"波次结束界面",common_color,"副本退出-再次进行",x=392,y=526,out_time=60)
                        self.sleep(3)
                        return True

                if now_boci >= self.level_boci:
                    self.click_color_to_color(common_color,"波次结束界面",common_color,"副本退出-再次进行",x=392,y=526,out_time=60)
                    self.sleep(3)
                    return True
                else:
                    self.click_color_to_color(common_color,"波次结束界面",common_color,"副本内选择掉落加成",x=896,y=526)
                    self.sleep(1)

                    # 使用委托手册
                    self.check_use_level_more_award()

                    self.click(640,496)
                    self.sleep(3)
                    start_time = self.time()
                    now_boci += 1

            # # 判断是否抓取魔灵
            # if self.capture_moling:
            #     res = self.is_have_moling()
            #     if res:
            #         self.go_to_capture_moling()

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
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                print("战斗超时")
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
