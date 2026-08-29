from ...res.cloud_task.CloudBaseTask import CloudBaseTask
from ...res.assets.cloud_color import *

class CloudAutoFindPropWorldTask(CloudBaseTask):
    # 云-锄大地
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '云-锄大地'

        self.level_grade = 70   # 副本等级
        self.level_max_count = 2 # 最大探索次数

        self.now_level_boci = 1     # 当前波次,默认1
        self.level_more_award = 0  # 委托手册
        self.level_more_award_boci = [] # 使用委托手册的轮次

        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.level_skill_e_time = 4  # 技能释放间隔
        self.level_skill_e_last_time = 0  # 最后一次释放技能时间
        self.level_skill_q_time = 15  # 技能释放间隔
        self.level_skill_q_last_time = 0  # 最后一次释放大招时间

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
        self.now_level_boci = 1

        self.level_grade = int(self.uiconfig['wuqi_tupo_grade'])
        self.level_max_count = int(self.uiconfig['wuqi_tupo_max_num'])

        self.level_more_award = int(self.uiconfig['wuqi_tupo_level_more_award'])
        str_ = self.uiconfig['wuqi_tupo_level_more_award_boci']
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
        self.click_until_color_vanish(cloud_common_color,"角色血条-绿色",x=81,y=34)
        self.sleep(2)
        self.click_until_color(cloud_common_color,"左上角红色退出",x=172,y=411)
        self.sleep(1)
        self.click_color_to_color(cloud_common_color,"左上角红色退出",cloud_common_color,"历练委托菜单",x=96,y=186)
        self.sleep(2)
        for i in range(3):
            self.slide(1150,383,800,383,dur=500,after_sleep=2)
            self.sleep(2)
            if self.await_until_click_ocr(rect=[429,542,1158,626],pattern="(调停|武器突破)",time_out=5):
                self.sleep(2)
                break

        res = self.await_until_color(cloud_weapon_tupo,"开始挑战")
        if not res:
            print("进入武器突破副本失败")
            self.click_until_color_vanish(cloud_common_color,"左上角红色退出",x=95,y=31)
            self.sleep(2)

            for i in range(3):
                self.click(735,669)

            res = self.find_my_color(cloud_common_color,"角色血条-绿色")
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
        if self.level_grade == 70:
            self.click(168,393)
        elif self.level_grade == 80:
            self.click(167,439)

        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(cloud_weapon_tupo,"开始挑战")
        if res:
            self.click_color_to_color(cloud_weapon_tupo,"开始挑战",cloud_common_color,"委托手册选择界面",x=1121,y=674)
            self.sleep(1)

        res = self.find_my_color(cloud_common_color,"副本退出-再次进行")
        if res:
            self.click_color_to_color(cloud_common_color,"副本退出-再次进行",cloud_common_color,"委托手册选择界面",x=852,y=678)
            self.sleep(1)
        
        # 使用委托手册
        self.check_use_level_more_award()

        self.click_color_to_color(cloud_common_color,"委托手册选择界面",cloud_common_color,"角色血条-绿色",x=780,y=496,out_time=60)
        self.sleep(2)

        print("成功进入副本")

    def quit_level(self):
        # 退出当前副本
        self.click_color_to_color(cloud_common_color,"角色血条-绿色",cloud_common_color,"地图esc界面",x=86,y=34)
        self.sleep(1)
        self.click_color_to_color(cloud_common_color,"地图esc界面",cloud_common_color,"退出委托-确定",x=1143,y=639)
        self.sleep(1)
        self.click_color_to_color(cloud_common_color,"退出委托-确定",cloud_common_color,"副本退出-再次进行",x=781,y=414,out_time=60)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(cloud_common_color,"副本退出-再次进行")
        if res:
            self.click_color_to_color(cloud_common_color,"副本退出-再次进行",cloud_common_color,"左上角红色退出",x=1094,y=678,out_time=60)
            self.sleep(1)

        res = self.find_my_color(cloud_weapon_tupo,"开始挑战")
        if res:
            self.click_color_to_color(cloud_weapon_tupo,"开始挑战",cloud_common_color,"历练委托菜单",x=95,y=31,out_time=60)
            self.sleep(1)

        self.click_until_color_vanish(cloud_common_color,"左上角红色退出",x=95,y=31)
        self.sleep(2)

        for i in range(3):
            self.click(735,669)

        res = self.find_my_color(cloud_common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def go_to_activate_level(self):
        # 前往激活任务
        if (self.level_grade == 70) or (self.level_grade == 80):
            # res = self.go_to_activate_level_70()
            res = self.test()
            if res:
                return True

        return False
    
    def go_to_activate_level_70(self):
        res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,270)
        if not res:
            return False
        
        self.sleep(0.5)

        self.fly_spear_num(5)

        self.sleep(2)

        self.walk_to_s()
        self.sleep(1)
        self.walk_to_w()
        self.sleep(1)

        self.fly_spear_num(6)
        self.sleep(2)

        self.walk_to_a()
        self.sleep(1)

        res = self.walk_lr_to_middle(common_color,"任务黄色图标")
        if not res:
            return False
        
        self.sleep(0.5)
        self.walk_to_w(1000*8)
        self.sleep(0.5)

        self.skill_z()
        self.sleep(0.5)
        self.walk_to_w()

        for i in range(3):
            self.walk_to_w(300)
            self.sleep(0.5)
        self.sleep(0.5)
        self.w_and_jupm()
        self.sleep(1)

        for i in range(5):
            res = self.is_text_re_in_ocr(rect=[759,327,853,383],pattern="引信")
            if res:
                break
            self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            self.walk_to_w(300)
            self.sleep(2)

        res = self.is_text_re_in_ocr(rect=[759,327,853,383],pattern="引信")
        if not res:
            print("激活副本失败")
            return False

        res = self.unlocking()
        if not res:
            return False
        
        self.await_until_color(weapon_tupo,"大烟花红色图标",time_out=5)

        self.rotate_view_to_middle_by_color(weapon_tupo,"大烟花红色图标")
        self.sleep(0.5)

        self.w_and_jupm()
        self.sleep(2)
        for i in range(2):
            self.action_jump_fly()
            self.sleep(1)
        self.sleep(0.5)

        self.walk_to_w()
        self.sleep(0.5)

        res = self.combat()
        if not res:
            return False

        # 开始撤离
        self.role_restoration()
        self.sleep(1)
        self.walk_to_d(1000*3)
        self.sleep(0.5)
        self.skill_z()
        self.sleep(1)
        self.walk_to_d(1000*2)
        self.sleep(0.5)
        self.walk_to_a(1000)
        self.sleep(0.5)
        # self.action_jump_fly()
        self.fly_spear_num(1)
        self.sleep(1)
        # self.walk_to_w(500)
        # self.sleep(0.5)
        self.walk_to_d(1000*5)
        self.sleep(0.5)
        self.walk_to_a(1000)
        self.sleep(0.5)
        self.walk_to_s(1000*6)
        self.sleep(0.5)
        self.walk_to_w(1000)
        self.sleep(0.5)
        self.walk_to_d(1000*6)
        self.sleep(0.5)
        self.walk_to_a(1000)
        self.sleep(0.5)
        for i in range(7):
            self.action_jump_fly()
            self.sleep(0.2)
        self.sleep(1)
        self.walk_to_s(1000)
        self.sleep(0.5)

        res = self.rotate_view_direction_to_front(husong_color,"撤离点图标",3)
        if not res:
            return False

        res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
        if not res:
            return False

        res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,200)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(5)
        self.sleep(3)
        self.role_restoration()
        self.sleep(1)

        for i in range(1):
            self.action_jump_fly()
            self.sleep(1)
        self.rotate_view_to_down(400,dur=500)
        self.sleep(1)
        self.rotate_view_to_top(20,dur=100,after_sleep=0.1)
        self.sleep(0.5)
        self.fly_spear_num(1)
        self.sleep(2)

        self.walk_to_d(500)
        self.sleep(0.5)

        res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,80)
        if not res:
            return False
        self.sleep(0.5)

        for i in range(4):
            self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            self.sleep(0.5)
            self.fly_spear_num(1)
            self.sleep(1)
        self.sleep(3)

        # 过河
        res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
        if not res:
            return False
        self.sleep(0.5)

        res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,150)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(2)
        self.sleep(1)

        self.walk_to_w(500)
        self.sleep(0.5)
        # self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
        # self.sleep(0.5)

        self.fly_spear_num(3)
        self.sleep(0.1)
        self.combat_left_click()
        self.sleep(2)

        self.walk_to_s(1000*2)

        for i in range(5):
            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                break
            self.fly_spear_num(1)
            self.sleep(1)
        
        res = self.await_until_color(common_color,"副本退出-再次进行",time_out=20)
        if res:
            print("挑战成功")
            return True
        else:
            print("挑战失败")
            return False

        # # 战斗结束，旧跑法
        # self.walk_to_s(1000*4)
        # self.sleep(1)
        # self.walk_to_w(300)
        # self.sleep(0.5)

        # for i in range(4):
        #     self.rotate_view_to_left(50,dur=100,after_sleep=0.5)
        # self.sleep(0.5)

        # res = self.rotate_view_to_middle_by_color(weapon_tupo,"撤离点图标")
        # if not res:
        #     return False
        # self.sleep(0.5)

        # res = self.rotate_view_direction_range(weapon_tupo,"撤离点图标",0,250)
        # if not res:
        #     return False
        # self.sleep(0.5)

        # res = self.rotate_view_direction_range(weapon_tupo,"撤离点图标",2,20)
        # if not res:
        #     return False
        # self.sleep(0.5)

        # self.fly_spear_num(4)
        # self.sleep(2)
        # self.walk_to_w(300)
        # self.walk_to_s(500)
        # self.walk_to_w(300)
        # self.sleep(1)

        # self.slide(209,551,169,465,1000*8)
        # self.sleep(1)

        # self.walk_to_d(500)
        # self.walk_to_s(500)
        # self.walk_to_w(300)
        # self.walk_to_a(300)

        # for i in range(3):
        #     self.rotate_view_to_down(200,dur=200,after_sleep=0.5)
        # self.sleep(0.5)

        # self.action_jump_fly(after_time=0.4)
        # self.walk_to_a()
        # self.sleep(1.5)

        # # 开始飞枪出地图
        # for i in range(3):
        #     self.rotate_view_to_top(80,dur=500,after_sleep=0.5)

        # res = self.rotate_view_direction_to_location(weapon_tupo,"撤离点图标",y=[390,420])
        # if not res:
        #     return False
        # self.sleep(0.5)
    
        # for i in range(2):
        #     self.rotate_view_to_left(50,dur=100,after_sleep=0.5)

        # res = self.rotate_view_direction_to_location(weapon_tupo,"撤离点图标",x=[880,900])
        # if not res:
        #     return False
        # self.sleep(0.5)

        # self.fly_spear_num(5)
        # self.sleep(6)

        # res = self.rotate_view_direction_range(weapon_tupo,"撤离点图标",0,30)
        # if not res:
        #     return False
        # self.sleep(0.5)

        # self.fly_spear_num(2)
        # self.sleep(1)

        # self.walk_to_w()
        # self.walk_to_s(1000*3)
        # self.walk_to_w(1000*2.5)
        # self.sleep(1)

        # self.fly_spear_num(3)
        # self.sleep(0.1)
        # self.combat_left_click()
        # self.sleep(2)

        # self.walk_to_s(1000*2)

        # for i in range(5):
        #     res = self.rotate_view_to_middle_by_color(weapon_tupo,"撤离点图标")
        #     if not res:
        #         break
        #     self.walk_to_w(300)
        #     self.sleep(1)
        
        # res = self.await_until_color(common_color,"副本退出-再次进行",time_out=20)
        # if res:
        #     print("挑战成功")
        #     return True
        # else:
        #     print("挑战失败")
        #     return False

    def role_restoration(self):
        # 角色复位
        print("角色复位")
        self.click(81,29)
        self.click(888,637)
        self.click(93,393)
        self.click(1042,267)
        self.click(778,410)
        print("角色复位成功")

    def test(self):
        self.action_click_walk(after_sleep=1)
        while 1:
            self.skill_z(after_sleep=0.1)
            res = self.rotate_view_to_middle_by_color(cloud_common_color,"魔灵图标")
            res = self.walk_to_w_new(walk_time=1000*3, after_sleep=0.01, ocr_text="[投喂魔灵]+", is_click_ocr=True)
            print(res)
            res = self.find_my_color(cloud_find_prop_world_color,"抓魔灵界面")
            if res:
                print("成功进入抓魔灵界面")
                break
            
            self.sleep(0.1)


    def combat(self):
        # 战斗
        print("开始战斗")
        start_time = self.time()

        max_time = 60

        for i in range(2):
            self.skill_e()
            self.sleep(1)
        self.sleep(2)

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.find_my_color(weapon_tupo,"右上角绿色图标")
            if res:
                self.sleep(1)
                print("成功击败大烟花")
                return True

            if self.level_skill_q_is_ok():
                self.skill_q()
                self.level_skill_q_last_time = self.time()
                self.sleep(3)
            
            if self.level_skill_e_is_ok():
                self.skill_e()
                self.level_skill_e_last_time = self.time()
                self.sleep(1)

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
            
            self.go_in_level()

            res = self.go_to_activate_level()
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                print("副本异常")
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
                continue
            

