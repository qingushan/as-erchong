from ...res.task.BaseTask import BaseTask
from ...res.assets.color import *

class AutoWeaponBreakTask(BaseTask):
    # 武器突破
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '武器突破'

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

    def init_skill_time(self):
        # 重置技能时间
        self.level_skill_e_last_time = 0
        self.level_skill_q_last_time = 0

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
        self.sleep(2)
        
        for i in range(3):
            self.slide(1193,376,900,376,dur=500)
            self.sleep(2)
            if self.await_until_click_ocr(rect=[423,484,1248,613],pattern="(调停|武器突破)",time_out=5):
                self.sleep(2)
                break
            
        res = self.await_until_color(weapon_tupo,"开始挑战")
        if not res:
            print("进入武器突破副本失败")
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
        if self.level_grade == 70:
            self.click(130,395)
        elif self.level_grade == 80:
            self.click(131,441)

        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(weapon_tupo,"开始挑战")
        if res:
            self.click_color_to_color(weapon_tupo,"开始挑战",common_color,"委托手册选择界面",x=1171,y=672)
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
        self.init_skill_time()

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

        res = self.find_my_color(weapon_tupo,"开始挑战")
        if res:
            self.click(44,32)
            self.sleep(3)

        self.click_until_ocr(x=44, y=34, rect=[119, 277, 344, 385], pattern="商店")
        self.sleep(2)

        for i in range(3):
            self.click(778,684)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def level_skill_q_is_ok(self):
        # 大招是否可以释放
        if self.level_skill_q_time < 0:
            return False

        if self.time() - self.level_skill_q_last_time >= self.level_skill_q_time:
            return True
        else:
            return False

    def level_skill_e_is_ok(self):
        # 技能是否可以释放
        if self.level_skill_e_time < 0:
            return False

        if self.time() - self.level_skill_e_last_time >= self.level_skill_e_time:
            return True
        else:
            return False

    def walk_lr_to_middle(self,color_dict, color_name):
        # 左右移动使目标到中间
        start_time = self.time()
        max_time = 10

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.findall_my_color(color_dict, color_name)
            if not res:
                continue
            
            # 查找最近的点
            xy = []
            for r in res:
                x = r.x
                y = r.y
                distance = abs(self.center_x - x)
                list_ = [distance,x,y]
                xy.append(list_)
            xy.sort(key=lambda x:x[0])
            min_x = xy[0][1]
            min_y = xy[0][2]
            # print(f"最近的点坐标：{min_x},{min_y}")

            if (self.center_x - 30) < min_x < (self.center_x + 30):
                print("中间了")
                return True

            if min_x > self.center_x:
                self.walk_to_d(300)
            else:
                self.walk_to_a(300)

            self.sleep(1)

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

    def go_to_activate_level(self):
        # 前往激活任务
        if (self.level_grade == 70) or (self.level_grade == 80):
            # res = self.go_to_activate_level_70()
            res = self.go_to_activate_level_80()
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

        self.skill_q()
        self.sleep(3)

        self.walk_to_w()

        for i in range(3):
            self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            self.walk_to_w(300)
            self.sleep(0.5)

        self.sleep(0.5)
        self.w_and_jupm()
        self.sleep(1)

        res = None
        for i in range(5):
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="引信")
            if res:
                break
            self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            self.walk_to_w(300)
            self.sleep(2)

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

        if self.uiconfig['wuqi_tupo_moling_run'] == 'on':
            # 使用魔灵遁逃
            self.skill_z()
            self.sleep(1)
        else:
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
            self.fly_spear_num(1)
            self.sleep(1)
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

            self.walk_to_d(1000*5)
            self.sleep(1)

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

    def go_to_activate_level_80(self):
        for i in range(2):
            self.action_jump_fly()
            self.sleep(1)

        res = None
        for i in range(5):
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"], pattern="引信")
            if res:
                break
            self.rotate_view_to_middle_by_color(common_color, "任务黄色图标")
            self.walk_to_w(300)
            self.sleep(2)

        if not res:
            print("激活副本失败")
            return False

        res = self.unlocking()
        if not res:
            return False

        self.await_until_color(weapon_tupo, "大烟花红色图标", time_out=5)

        self.walk_to_d(300)
        self.sleep(0.5)

        self.walk_to_w(1500)
        self.sleep(3)

        res = self.combat()
        if not res:
            return False

        if self.uiconfig['wuqi_tupo_moling_run'] == 'on':
            # 使用魔灵遁逃
            self.skill_z()
            res = self.await_until_color(common_color, "副本退出-再次进行", time_out=30)
            if res:
                print("挑战成功")
                return True
            else:
                print("挑战失败")
                return False
        else:
            # 开始撤离
            self.walk_to_a(300)
            self.sleep(0.5)

            for i in range(3):
                self.action_jump_fly()
                self.sleep(1)

            self.walk_to_d(1000*2)
            self.sleep(1)

            for i in range(4):
                self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
                self.sleep(0.5)
                self.action_jump_fly()
                self.sleep(1)
            self.sleep(1)

            self.walk_to_d(1000)
            self.sleep(0.5)

            for i in range(20):
                self.rotate_view_to_middle_by_color(husong_color, "撤离点图标")
                self.sleep(0.5)
                self.action_jump_fly()
                self.sleep(1)

                if self.find_my_color(common_color, "副本退出-再次进行"):
                    print("挑战成功")
                    return True

            print("挑战异常")
            return False


    def test(self):
        self.role_restoration()
        self.sleep(1)
        self.walk_to_d(1000*5)
        self.sleep(0.5)
        self.walk_to_a(1000)
        self.sleep(0.5)
        self.action_jump_fly()
        self.sleep(1)
        self.walk_to_w(200)
        self.sleep(0.5)
        self.walk_to_d(1000*5)
        self.sleep(0.5)
        self.walk_to_a(1000)
        self.sleep(0.5)
        self.walk_to_s(1000*6)
        self.sleep(0.5)
        self.walk_to_w(1000)
        self.sleep(0.5)
        self.walk_to_d(1000*5)
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

        self.walk_to_w(1000*1.5)
        self.sleep(0.5)

        res = self.rotate_view_direction_to_front(husong_color,"撤离点图标",3)
        if not res:
            return False

        res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
        if not res:
            return False
        self.sleep(0.5)

        res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,50)
        if not res:
            return False
        self.sleep(0.5)

        for i in range(4):
            self.fly_spear_num(1)
            self.sleep(1)
        self.sleep(3)

        # 过河
        res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,150)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(2)
        self.sleep(1)

        self.walk_to_w(500)
        self.sleep(0.5)

        self.fly_spear_num(3)
        self.sleep(0.1)
        self.combat_left_click()
        self.sleep(2)

        self.walk_to_s(1000*2)

        for i in range(5):
            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                break
            self.walk_to_w(300)
            self.sleep(1)
        
        res = self.await_until_color(common_color,"副本退出-再次进行",time_out=20)
        if res:
            print("挑战成功")
            return True
        else:
            print("挑战失败")
            return False

    def combat(self):
        # 战斗
        print("开始战斗")
        start_time = self.time()

        max_time = 60

        # for i in range(4):
        #     self.skill_e()
        # self.sleep(2)

        while 1:
            if self.time() - start_time > max_time:
                return False

            # res = self.find_my_color(weapon_tupo,"右上角绿色图标")
            res = self.is_text_re_in_ocr(rect=[21,222,228,351],pattern="撤离")
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
                # self.sleep(1)

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
            

