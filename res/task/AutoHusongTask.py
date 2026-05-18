from ascript.android.screen import Colors
from ...res.task.BaseTask import BaseTask
from ...res.assets.color import *

class AutoHusongTask(BaseTask):
    # 护送
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '护送'

        self.level_grade = 60   # 副本等级
        self.level_max_count = 2 # 最大探索次数

        self.now_level_boci = 1     # 当前波次,默认1
        self.level_more_award = 0  # 委托手册
        self.level_more_award_boci = [] # 使用委托手册的轮次

        
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.map_type = -1      # 地图类型

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

    def init_level(self):
        # 初始化
        self.map_type = -1
        self.now_level_boci = 1

        self.level_grade = int(self.uiconfig['husong_grade'])
        self.level_max_count = int(self.uiconfig['husong_max_num'])

        self.level_more_award = int(self.uiconfig['husong_level_more_award'])
        str_ = self.uiconfig['husong_level_more_award_boci']
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
        print("开始前往护送副本")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=126,y=415)
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"历练委托菜单",x=47,y=184)
        self.sleep(2)

        for i in range(3):
            self.slide(1193,376,178,376,dur=500)
        self.sleep(2)

        self.click_color_to_color(jjb_color,"历练-委托-皎皎币",husong_color,"委托-开始挑战",x=506,y=391)
        self.sleep(1)
        print("成功进入护送副本选择界面")

    def select_level_grade(self):
        # 选择等级
        if self.level_grade == 70:
            self.click(138, 346)

        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.map_type = -1
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(husong_color,"委托-开始挑战")
        if res:
            self.click_color_to_color(husong_color,"委托-开始挑战",common_color,"委托手册选择界面",x=1171,y=672)
            self.sleep(1)

        res = self.find_my_color(common_color,"副本退出-再次进行")
        if res:
            self.click_color_to_color(common_color,"副本退出-再次进行",common_color,"委托手册选择界面",x=894,y=676)
            self.sleep(1)
        
        # 使用委托手册
        self.check_use_level_more_award()

        self.click_color_to_color(common_color,"委托手册选择界面",common_color,"角色血条-绿色",x=774,y=505,out_time=60)
        self.sleep(2)

        print("成功进入副本")

    def leave_level_70(self):
        # 离开关卡
        self.role_restoration()
        self.role_restoration()

        if self.map_type == 0:
            self.skill_q()
            self.await_until_color(common_color,"角色血条-绿色")
            self.sleep(0.3)

            self.walk_to_w(1000*4)        

            self.walk_to_d(300)
            self.sleep(1)
            for i in range(3):
                self.walk_to_w(500)
                self.sleep(0.5)
            self.walk_to_a(1000*2)
            self.sleep(0.5)
            self.walk_to_w(1000*3)
            self.sleep(0.5)

            self.skill_q()
            self.await_until_color(common_color,"角色血条-绿色")
            self.sleep(0.3)

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False
        elif self.map_type == 1:
            self.skill_q()
            self.await_until_color(common_color,"角色血条-绿色")
            self.sleep(0.3)
        
            self.walk_to_d(1000*5)
            self.walk_to_s(300)
            self.sleep(1)

            for i in range(3):
                self.walk_to_d(500)
                self.sleep(0.5)

            for i in range(3):
                self.walk_to_w(700)
                self.sleep(0.5)

            
            self.walk_to_d(1000*3)
            self.sleep(0.5)

            self.skill_q()
            self.await_until_color(common_color,"角色血条-绿色")
            self.sleep(0.3)


            res = self.rotate_view_direction_to_front(husong_color,"撤离点图标",3)
            if not res:
                return False
            # self.rotate_view_to_right(150,dur=500)
            # self.rotate_view_to_right(150,dur=500)
            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False

        res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
        if not res:
            return False
        
        for i in range(4):
            self.fly_spear()
            self.sleep(0.5)
        
        self.sleep(1)

        self.role_restoration()
        self.sleep(1)
        res = self.find_my_color(husong_color,'地图撤离点')
        if not res:
            print("没有找到地图撤离点")
            return False
        print(res)
        r = self.find_my_color(husong_color,'撤离点图标')
        map_type = -1
        if 110 < res.x < 125:
            if r:
                if r.x > 880:
                    map_type = 2    # 右边房间撤离点
            if map_type == -1:
                map_type = 0    # 右边撤离点
        elif 90 < res.x < 100:
            map_type = 3    # 右边复杂地形
        elif res.x > 170:
            map_type = 1    # 前方撤离点

        # map_type = 3
        print(f"撤离点---{map_type}")
        
        if map_type == 0:
            self.walk_to_a(1000*5)
            self.sleep(0.5)

            # self.rotate_view_to_right(150,dur=500)
            # self.rotate_view_to_right(150,dur=500)

            # for i in range(4):
            #     res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            #     if not res:
            #         self.rotate_view_to_left(100,dur=500)

            res = self.rotate_view_direction_to_front(husong_color,"撤离点图标",3)
            if not res:
                return False

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False

            res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,250)
            if not res:
                return False
            self.sleep(0.5)

            self.rotate_view_to_top(10,dur=100)

            self.fly_spear_num(4)
            self.sleep(3)

            self.walk_to_s(1000)
            self.sleep(1)
            self.walk_to_w(1000)
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False
            
            res = self.rotate_view_direction_range(husong_color,"撤离点图标",1,40)
            if not res:
                return False
            self.sleep(0.5)

            self.fly_spear_num(2)
            self.sleep(2)

            self.walk_to_d(1000*2)
            self.sleep(0.5)
            self.walk_to_a(700)
            self.sleep(0.5)


        elif map_type == 1:
            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            # if not res:
            #     return False
            self.sleep(2)

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")

            res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,200)
            if not res:
                return False
            self.sleep(0.5)

            self.fly_spear_num(3)
            self.sleep(2)

            self.walk_to_s(1000)
            self.sleep(1)
            self.walk_to_w(1000)
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False
            
            res = self.rotate_view_direction_range(husong_color,"撤离点图标",1,50)
            if not res:
                return False
            self.sleep(0.5)

            self.fly_spear_num(2)
            self.sleep(2)

            self.walk_to_d(1000*2)
            self.sleep(0.5)
            self.walk_to_a(700)
            self.sleep(0.5)

        elif map_type == 2:
            # self.rotate_view_to_right(100,dur=500)
            # self.rotate_view_to_right(100,dur=500)

            res = self.rotate_view_direction_to_front(husong_color,"撤离点图标",3)
            if not res:
                return False

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False
            
            res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,250)
            if not res:
                return False
            self.sleep(0.5)

            self.rotate_view_to_top(10,dur=100)

            self.fly_spear_num(3)
            self.sleep(2)

            self.walk_to_a(1000)
            self.sleep(1)

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False
            
            res = self.rotate_view_direction_range(husong_color,"撤离点图标",1,50)
            if not res:
                return False
            self.sleep(0.5)

            for i in range(2):
                res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
                if not res:
                    return False
                self.fly_spear_num(1)
                self.sleep(1)
            
            self.walk_to_d(1000*2)
            self.sleep(0.5)
            self.walk_to_a(700)
            self.sleep(0.5)
        elif map_type == 3:
            # self.rotate_view_to_right(150,dur=500)
            # self.rotate_view_to_right(150,dur=500)
            # self.rotate_view_to_right(150,dur=500)
            # self.sleep(1)
            # for i in range(4):
            #     res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            #     if not res:
            #         self.rotate_view_to_left(150,dur=500)

            res = self.rotate_view_direction_to_front(husong_color,"撤离点图标",3)
            if not res:
                return False

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False

            res = self.rotate_view_direction_range(husong_color,"撤离点图标",0,270)
            if not res:
                return False
            self.sleep(0.5)

            self.rotate_view_to_top(10,dur=100)

            self.fly_spear_num(5)
            self.sleep(3)
            self.walk_to_w(500)
            self.sleep(0.5)
            self.slide(211,553,307,502,dur=1000*3)
            self.sleep(0.5)
            # self.walk_to_a(700)
            # self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            if not res:
                return False
            
            res = self.rotate_view_direction_range(husong_color,"撤离点图标",1,50)
            if not res:
                return False
            self.sleep(0.5)

            self.fly_spear_num(2)
            self.sleep(2)
            self.walk_to_d(1000*2)
            self.sleep(0.5)
            self.walk_to_d(1000*2)
            self.sleep(0.5)
            self.walk_to_a(700)
            self.sleep(0.5)

        for i in range(15):
            res = self.find_my_color(common_color,'副本退出-再次进行')
            if res:
                print("护送完成")
                return True

            res = self.find_my_color(common_color,'角色血条-绿色')
            if not res:
                res = self.await_until_color(common_color,"副本退出-再次进行")
                if res:
                    print("护送完成")
                    return True
                else:
                    continue
    
            self.rotate_view_to_middle_by_color(husong_color,"撤离点图标")
            self.fly_spear_num(1)
            self.sleep(1)

        print("护送失败")
        return False

    def go_to_activate_level(self):
        # 前往激活任务
        if self.level_grade == 70:
            res = self.go_to_activate_level_70()
            if res:
                return True

        return False

    def go_to_activate_level_70(self):
        self.map_type = -1  # 0:重置前方是解救人质的  1:重置前方右边是解救人质的

        self.role_restoration()
        self.sleep(1)

        res = self.find_my_color(common_color,'任务黄色图标')
        if not res:
            return False
        print(res)

        if 650 < res.x < 700:
            self.map_type = 0
        elif 870 < res.x < 920:
            self.map_type = 1

        res = self.find_my_color(husong_color,'70级电梯图')
        if res:
            self.map_type = 2
        
        print(f"当前地图：{self.map_type}")
        if self.map_type == -1:
            print("未识别到地图")
            return False

        if self.map_type == 0:
            res = self.go_to_activate_level_70_A()
        elif self.map_type == 1:
            res = self.go_to_activate_level_70_B()
        elif self.map_type == 2:
            res = self.go_to_activate_level_70_C()
        
        if not res:
            return False
        
        res = self.leave_level_70()
        return res

    def level_70_to_save_people(self):
        # 70级救人
        if self.map_type == 0:
            # 准备救人
            self.role_restoration()

            self.skill_q()
            self.await_until_color(common_color,"角色血条-绿色")
            self.sleep(0.3)

            self.walk_to_w(1000*4)        

            self.walk_to_d(300)
            self.sleep(1)
            self.walk_to_w(1000*1.5)

            self.walk_to_d(1000)
            self.walk_to_w(500)

            self.walk_to_d(1000*1.5)
            self.walk_to_s(500)
            self.walk_to_d(1000*1.5)

            self.sleep(1)

            self.walk_to_a(1000*1.5)
            self.walk_to_w(1000)
            self.walk_to_a(1000*1.5)
            self.sleep(0.5)
            self.slide(206,553,324,473,dur=1000*2)
            self.walk_to_a(500)
            self.sleep(0.5)

            self.skill_q()
            self.sleep(1)

            res = self.is_ok_person()
            if res:
                return True

            res = self.rotate_view_to_middle_by_color(husong_color,"前方任务黄色图标")
            # if not res:
            #     return False
            self.sleep(1)

            self.skill_q()
            self.await_until_color(common_color,"角色血条-绿色")
            self.sleep(0.3)

            self.walk_to_w(1000*2)
            self.sleep(0.5)
            self.walk_to_a(500)
            self.walk_to_w(1000*2)
            self.sleep(2)

            self.walk_to_s(1000*2)

            res = self.is_ok_person()
            if res:
                self.skill_q()
                self.sleep(1)
                return True

            self.slide(208,551,90,614,dur=1000*5)
            self.walk_to_w(1000*2)
            self.sleep(1)

            res = self.is_ok_person()
            if res:
                self.skill_q()
                self.sleep(1)
                return True
        elif self.map_type == 1:
            # 准备救人
            self.role_restoration()

            self.skill_q()
            self.await_until_color(common_color,"角色血条-绿色")
            self.sleep(0.3)
            
            self.walk_to_d(1000*5)
            self.walk_to_s(300)
            self.sleep(1)

            self.walk_to_d(1000*1.5)
            self.walk_to_s(1000)
            self.walk_to_d(500)
            self.walk_to_s(1000*1.5)
            self.walk_to_a(500)
            self.walk_to_s(1000*1.5)

            self.sleep(1)

            self.walk_to_w(1000*1.5)
            self.walk_to_d(1000)
            self.walk_to_w(1000*1.5)
            self.sleep(0.5)

            self.slide(203,553,298,609,dur=1000*2)

            self.walk_to_w(500)
            self.sleep(0.5)

            self.skill_q()
            self.sleep(1)

            res = self.is_ok_person()
            if res:
                return True

            for i in range(3):
                self.rotate_view_to_right(100,dur=500,after_sleep=0.5)
            self.sleep(1)

            status_ = False     # 是否找到前方黄色图标
            for i in range(4):
                res = self.await_until_color(husong_color,"前方任务黄色图标",time_out=3)
                if not res:
                    status_ = False
                    self.rotate_view_to_left(100,dur=500,after_sleep=0.5)
                else:
                    status_ = True

            if status_:
                self.rotate_view_to_middle_by_color(husong_color,"前方任务黄色图标")
            self.sleep(1)

            self.skill_q()
            self.await_until_color(common_color,"角色血条-绿色")
            self.sleep(0.3)

            self.walk_to_w(1000*1.5)
            self.sleep(0.5)
            self.walk_to_a(500)
            self.walk_to_w(1000*1.5)
            self.sleep(2)

            self.walk_to_s(1000*2)

            res = self.is_ok_person()
            if res:
                self.skill_q()
                self.sleep(1)
                return True

            self.slide(208,551,90,614,dur=1000*5)
            self.walk_to_w(1000*2)
            self.sleep(1)

            res = self.is_ok_person()
            if res:
                self.skill_q()
                self.sleep(1)
                return True
        
        print("解救人质失败")
        return False

    def go_to_activate_level_70_A(self):
        for i in range(11):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(0.5)
        
        self.action_jump_fly()
        self.sleep(1)
        
        # 救人
        res = self.level_70_to_save_people()
        return res

    def go_to_activate_level_70_B(self):
        self.rotate_view_to_right(150,dur=500)
        self.rotate_view_to_right(150,dur=500)
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

        for i in range(2):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)
        
        self.action_jump_fly()
        self.sleep(1)

        # 救人
        res = self.level_70_to_save_people()
        return res

    def go_to_activate_level_70_C(self):
        map_type = -1

        self.walk_to_w(1000*10)
        self.sleep(5)

        res = self.find_my_color(common_color,'任务黄色图标')
        if not res:
            return False
        print(res)

        if 650 < res.x < 680:
            map_type = 1
            self.map_type = 1
        else:
            map_type = 0
            self.map_type = 0

        if map_type == 0:
            res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,100)
            if not res:
                return False
            self.sleep(0.5)

            self.fly_spear_num(5)
            self.sleep(3)

            self.rotate_view_to_left(150,dur=500)
            self.rotate_view_to_left(150,dur=500)
            self.sleep(0.5)

            res = self.rotate_view_direction_range(common_color,"任务黄色图标",1,50)
            if not res:
                return False
            self.sleep(0.5)

            for i in range(7):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(0.5)
        
            self.action_jump_fly()
            self.sleep(1)

            # 救人
            res = self.level_70_to_save_people()
            return res
        

        elif map_type == 1:
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False

            res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,200)
            if not res:
                return False
            self.sleep(0.5)

            self.fly_spear_num(7)
            self.sleep(2)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return 
                
            res = self.rotate_view_direction_range(common_color,"任务黄色图标",1,30)
            if not res:
                return False
            self.sleep(0.5)

            self.fly_spear_num(3)
            self.sleep(2)


            # 救人
            res = self.level_70_to_save_people()
            return res
        
        return False
        
    def go_to_activate_level_80(self):
        # 80级激活副本
        self.map_type = -1  # 地图
        # 识别当前地图

        res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,270)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(4)
        self.sleep(2)

        res = self.rotate_view_direction_range(common_color,"任务黄色图标",1,50)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(2)
        self.sleep(3)

        res = self.find_my_color(common_color,'任务黄色图标')
        print(res)

        # 518  637   827    894
        if res:
            if res.x < 550:
                self.map_type = 0
            elif 550 < res.x < 700:
                self.map_type = 1
            # 850
            elif 700 < res.x < 890:
                self.map_type = 2
            elif res.x > 860:
                self.map_type = 3

        print(f"当前地图：{self.map_type}")
        if self.map_type == -1:
            print("未识别到地图")
            return False

        if self.map_type == 0:
            res = self.go_to_activate_level_80_A()
        elif self.map_type == 1:
            res = self.go_to_activate_level_80_B()
        elif self.map_type == 2:
            res = self.go_to_activate_level_80_C()
        elif self.map_type == 3:
            res = self.go_to_activate_level_80_D()

        return res

    def goto_bridge(self):
        # 过桥
        self.role_restoration()
        if self.map_type == 3:
            for i in range(4):
                self.rotate_view_to_right(100,dur=500,after_sleep=0.5)
        else:
            for i in range(3):
                self.rotate_view_to_right(100,dur=500,after_sleep=0.5)
            pass

        self.fly_spear()
        self.sleep(0.8)
        self.fly_spear_num(2)
        self.sleep(1)

        self.find_hostage()

    def find_hostage(self):
        # 查找人质
        self.walk_to_w(500)

        self.walk_to_a(4000)

        self.skill_z()

        self.walk_to_w(1000*3)

        if self.is_ok_person():
            return True

        self.walk_to_s(1000*5)
        self.sleep(0.5)
        self.rotate_view_to_middle_by_color(husong_color,"前方任务黄色图标")
        self.fly_spear_num(1)
        self.sleep(0.5)
        self.rotate_view_to_right(280,dur=500)
        self.sleep(0.5)
        self.walk_to_w(2000)
        # res = self.walk_lr_to_middle()
        # if not res:
        #     return False

        for i in range(10):
            res = self.is_text_re_in_ocr(rect=[731,328,845,388],pattern="操作")
            if res:
                break
            self.walk_to_w(500)
            self.sleep(1)

        res = self.is_text_re_in_ocr(rect=[731,328,845,388],pattern="操作")
        if not res:
            return False
        
        res = self.unlocking()
        if not res:
            return False

        if self.is_ok_person():
            return True
        
        self.walk_to_s()
        self.rotate_view_to_left(280,dur=500)
        self.rotate_view_to_middle_by_color(husong_color,"前方任务黄色图标")
        self.rotate_view_to_top(150)
        self.fly_spear_num(2)
        self.sleep(3)

        res = self.walk_lr_to_middle()
        if not res:
            return False

        for i in range(10):
            res = self.is_text_re_in_ocr(rect=[731,328,845,388],pattern="操作")
            if res:
                break
            self.walk_to_w()
            self.sleep(1)

        res = self.is_text_re_in_ocr(rect=[731,328,845,388],pattern="操作")
        if not res:
            return False
        
        res = self.unlocking()
        if not res:
            return False

        if self.is_ok_person():
            return True
        
    def is_ok_person(self):
        # 是否成功解救人质
        res = self.find_my_color(husong_color,"右上角绿色图标")
        if res:
            print("人质解救成功")
            return True
        else:
            print("人质没解救成功")
            return False

    def go_to_activate_level_80_A(self):
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        
        # self.rotate_view_to_top(80)
        res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,50)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(5)
        self.sleep(3)

        self.fly_spear_num(2)
        self.sleep(1)
        
        # 准备过河
        self.goto_bridge()

    def go_to_activate_level_80_B(self):
        self.fly_spear_num(5)
        self.sleep(2)

        self.fly_spear_num(2)
        self.sleep(2)

        self.fly_spear_num(3)
        self.sleep(1)

        # 准备过河
        self.goto_bridge()
        
    def go_to_activate_level_80_C(self):
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        self.sleep(0.5)
        

        res = self.rotate_view_direction_range(common_color,"任务黄色图标",3,20)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(6)
        self.sleep(2)

        exit()
        self.walk_to_s(300)

        self.rotate_view_to_right(280)

        self.fly_spear_num(2)
        self.sleep(1)

        self.walk_to_w()
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        self.rotate_view_to_top(50)

        self.fly_spear_num(3)
        self.sleep(2)

        self.walk_to_s()
        self.sleep(1)

        self.fly_spear_num(2)
        self.sleep(1)
        
        # 准备过河
        self.goto_bridge()

    def go_to_activate_level_80_D(self):
        self.role_restoration()
        self.walk_to_d(300)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        self.sleep(0.5)

        res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,100)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(2)
        self.sleep(2)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(4)
        self.sleep(1)

        # 准备过河
        self.goto_bridge()

    def walk_lr_to_middle(self):
        # 左右移动使目标到中间
        start_time = self.time()
        max_time = 10

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.findall_my_color(common_color,"任务黄色图标")
            if not res:
                return False
            
            # 查找最近的点
            xy = []
            for r in res:
                x = r.x
                y = r.y
                distance = abs(self.center_x - x)
                list_ = [distance,x,y]
                xy.append(list_)
            xy.sort(key=lambda x:x[0])
            print(xy)
            min_x = xy[0][1]
            min_y = xy[0][2]
            print(f"最近的点坐标：{min_x},{min_y}")

            if (self.center_x - 20) < min_x < (self.center_x + 20):
                print("中间了")
                return True

            if min_x > self.center_x:
                self.walk_to_d(300)
            else:
                self.walk_to_a(300)

            self.sleep(0.5)

    def quit_level(self):
        # 退出当前副本
        res = self.find_my_color(common_color,'副本退出-再次进行')
        if res:
            print("失败错误，任务完成")
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

        res = self.find_my_color(husong_color,"委托-开始挑战")
        if res:
            self.click_color_to_color(husong_color,"委托-开始挑战",jjb_color,"历练-委托-皎皎币",x=44,y=32,out_time=60)
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

    def mod_skill_q_is_ok(self):
        # 大招是否可以释放
        if self.time() - self.mod_skill_q_last_time >= self.mod_skill_q_time:
            return True
        else:
            return False

    def mod_skill_e_is_ok(self):
        # 技能是否可以释放
        if self.time() - self.mod_skill_e_last_time >= self.mod_skill_e_time:
            return True
        else:
            return False

    def combat(self):
        # 战斗
        print("开始战斗")
        start_time = self.time()

        if self.level_type == '扼守':
            max_time = 60 * 5
        elif self.level_type == '驱离':
            max_time = 60 * 3

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.find_my_color(common_color,"副本退出-再次进行")
            if res:
                print("战斗完成")
                return True

            if self.mod_skill_q_is_ok():
                self.skill_q()
                self.mod_skill_q_last_time = self.time()
                self.sleep(1)
            
            if self.mod_skill_e_is_ok():
                self.skill_e()
                self.mod_skill_e_last_time = self.time()
                self.sleep(1)

            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}"
        self.logui.change_log_text(text)

    def run(self):
        self.init_level()
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
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()

            
            



