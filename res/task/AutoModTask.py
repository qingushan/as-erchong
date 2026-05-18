from ...res.task.BaseTask import BaseTask
from ...res.util.RoleSkillUtil import RoleSkillUtil
from ...res.assets.color import *

import json

class AutoModTask(BaseTask):
    # 夜航手册
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '夜航手册'

        self.level_boci = 1       # 波次    
        self.now_level_boci = 1     # 当前波次,默认1

        self.level_more_award = 0  # 委托手册
        self.level_more_award_boci = [] # 使用委托手册的轮次

        self.mod_config_list = []   # 需要执行的任务
        self.level_grade = 65   # 副本等级
        self.level_number = '第三个'     # 选择等级之后第几个副本
        self.level_type = '扼守'            # 副本类型：扼守/驱离

        self.level_max_count = 2 # 最大探索次数
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.set_skill_config()
        self.init_level()

    def set_skill_config(self):
        # 初始化技能配置
        self.role_skill_util.init_config(self.uiconfig.get('mod_role_skill', '0'))

    def init_level(self):
        # 初始化
        # self.level_grade = int(self.uiconfig['mod_grade'])
        # self.level_max_count = int(self.uiconfig['mod_max_num'])
        # self.level_number = self.uiconfig['mod_level_number']

        self.mod_config_list = self.uiconfig["mod_config_list"]
        self.mod_config_list = json.loads(self.mod_config_list)

        # 构建自定义技能配置传入【角色技能搓招】
        skill_config = {
            "skill_q_max_time": float(self.uiconfig['mod_skill_q_time']),
            "skill_q_max_count": int(self.uiconfig['mod_skill_q_count']),
            "skill_e_max_time": float(self.uiconfig['mod_skill_e_time']),
            "skill_e_max_count": int(self.uiconfig['mod_skill_e_count']),
            "skill_z_max_time": float(self.uiconfig.get('mod_skill_z_time', 30)),
            "skill_z_max_count": int(self.uiconfig.get('mod_skill_z_count', 1)),
        }
        self.role_skill_util.set_role_skill_config_custom(skill_config)

        print(f"夜航手册执行配置：{self.mod_config_list}")
        print(type(self.mod_config_list))

        self.level_more_award = int(self.uiconfig['mod_level_more_award'])
        
        str_ = self.uiconfig['mod_level_more_award_boci']
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
        print("开始前往夜航手册副本")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=126,y=415)
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"历练委托菜单",x=47,y=184)
        self.sleep(1)
        self.click_color_to_color(common_color,"历练委托菜单",mod_color,"选择关卡界面",x=802,y=96)
        self.sleep(1)
        print("成功进入夜航手册副本选择界面")

    def select_level_grade(self):
        # 选择等级
        self.slide(450,177,450,562,dur=500)
        self.sleep(2)
        if self.level_grade == 20:
            self.click(450,172)
        elif self.level_grade == 30:
            self.click(449,236)
        elif self.level_grade == 40:
            self.click(449,303)
        elif self.level_grade == 50:
            self.click(448,372)
        elif self.level_grade == 55:
            self.click(447,438)
        elif self.level_grade == 60:
            self.click(448,505)
        elif self.level_grade == 65:
            self.click(450,573)
        # elif self.level_grade == 70:
        #     self.slide(450,562,450,177,dur=500)
        #     self.sleep(2)
        #     self.click(447,505)
        # elif self.level_grade == 80:
        #     self.slide(450,562,450,177,dur=500)
        #     self.sleep(2)
        #     self.click(447,572)
        elif self.level_grade == 70:
            self.click(452,642)
        elif self.level_grade == 75:
            self.slide(450,562,450,177,dur=500)
            self.sleep(2)
            self.click(446,569)
        elif self.level_grade == 80:
            self.slide(450,562,450,177,dur=500)
            self.sleep(2)
            self.click(448,636)

        self.sleep(1)

    def select_level_grade_activity_shr(self):
        # 收获日选择等级
        for i in range(2):
            self.slide(450,177,450,562,dur=500)
            self.sleep(2)
        if self.level_grade == 20:
            self.click(450,172)
        elif self.level_grade == 30:
            self.click(449,236)
        elif self.level_grade == 40:
            self.click(449,303)
        elif self.level_grade == 50:
            self.click(448,372)
        elif self.level_grade == 55:
            self.click(447,438)
        elif self.level_grade == 60:
            self.click(448,505)
        elif self.level_grade == 65:
            self.click(450,573)
        elif self.level_grade == 70:
            self.slide(450,562,450,177,dur=500)
            self.sleep(2)
            self.click(447,438)
        elif self.level_grade == 75:
            self.slide(450,562,450,177,dur=500)
            self.sleep(2)
            self.click(447,505)
        elif self.level_grade == 80:
            self.slide(450,562,450,177,dur=500)
            self.sleep(2)
            self.click(447,573)

        self.sleep(1)

    def select_level(self):
        # 选择第几个关卡，关卡过多则下滑采用负数
        print("普通选择关卡")
        x = None
        y = None
        if self.level_number == "第一个":
            x = 1183
            y = 178
        elif self.level_number == "第二个":
            x = 1183
            y = 266
        elif self.level_number == "第三个":
            x = 1183
            y = 355
        elif self.level_number == "第四个":
            x = 1183
            y = 443
        elif self.level_number == "第五个":
            x = 1183
            y = 537
        elif self.level_number == "倒数第一个":
            for i in range(2):
                self.slide(611,537,611,177,dur=500)
                self.sleep(1)
            x = 1183
            y = 537
        elif self.level_number == "倒数第二个":
            for i in range(2):
                self.slide(611,537,611,177,dur=500)
                self.sleep(1)
            x = 1183
            y = 443
        elif self.level_number == "倒数第三个":
            for i in range(2):
                self.slide(611,537,611,177,dur=500)
                self.sleep(1)
            x = 1183
            y = 355
        elif self.level_number == "倒数第四个":
            for i in range(2):
                self.slide(611,537,611,177,dur=500)
                self.sleep(1)
            x = 1183
            y = 266
        elif self.level_number == "倒数第五个":
            for i in range(2):
                self.slide(611,537,611,177,dur=500)
                self.sleep(1)
            x = 1183
            y = 174
        elif self.level_number == "60级驱逐":
            self.sleep(10)

        self.click_color_to_color(mod_color,"选择关卡界面",mod_color,"选择关卡界面确认选择",x=x,y=y)
        self.sleep(1)

    def select_level_activity_shr(self):
        # 收获日选关卡
        print("收获日选择关卡")
        # 选择第几个关卡，关卡过多则下滑采用负数
        x = None
        y = None
        if self.level_number == "第一个":
            x = 1183
            y = 178
        elif self.level_number == "第二个":
            x = 1183
            y = 266
        elif self.level_number == "第三个":
            x = 1183
            y = 355
        elif self.level_number == "第四个":
            x = 1183
            y = 443
        elif self.level_number == "第五个":
            x = 1183
            y = 537
            self.sleep(5)
        elif self.level_number == "倒数第一个":
            self.slide(611,465,611,177,dur=500)
            self.sleep(1)
            self.slide(611,465,611,177,dur=500)
            self.sleep(1)
            x = 1183
            y = 465
        elif self.level_number == "倒数第二个":
            self.slide(611,465,611,177,dur=500)
            self.sleep(1)
            self.slide(611,465,611,177,dur=500)
            self.sleep(1)
            x = 1183
            y = 374
        elif self.level_number == "倒数第三个":
            self.slide(611,465,611,177,dur=500)
            self.sleep(1)
            self.slide(611,465,611,177,dur=500)
            self.sleep(1)
            x = 1183
            y = 285
        elif self.level_number == "倒数第四个":
            self.slide(611,465,611,177,dur=500)
            self.sleep(1)
            self.slide(611,465,611,177,dur=500)
            self.sleep(1)
            x = 1183
            y = 197

        self.click_color_to_color(common_color,"左上角红色退出",mod_color,"选择关卡界面确认选择",x=x,y=y)
        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}---{self.level_number}")
        res = self.find_my_color(mod_color,"选择关卡界面确认选择")
        if res:
            self.click_color_to_color(mod_color,"选择关卡界面确认选择",common_color,"委托手册选择界面",x=1067,y=672)
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
        if self.level_type == '驱离':
            self.go_to_activate_level_quli()
            return True

        if self.level_type == '驱逐':
            return True
        
        if self.level_grade == 65:
            res = self.go_to_activate_level_65()
            if res:
                return True
        elif self.level_grade == 30:
            res = self.go_to_activate_level_65()
            if res:
                return True
        elif self.level_grade == 50:
            res = self.go_to_activate_level_50()
            if res:
                return True
        elif self.level_grade == 75:
            res = self.go_to_activate_level_75()
            if res:
                return True
        elif self.level_grade == 80:
            res = self.go_to_activate_level_80()
            if res:
                return True

        return False

    def go_to_activate_level_quli(self):
        # 驱离激活
        if self.level_grade == 80:
            if self.level_number == "第一个":
                for i in range(7):
                    self.action_jump_fly()
                    self.sleep(0.5)
            elif self.level_number == "第二个":
                for i in range(5):
                    self.action_jump_fly()
                    self.sleep(0.5)
        else:
            res = self.find_my_color(mod_color,"驱离电梯图")
            if res:
                print("电梯图")
                self.sleep(1)
                self.walk_to_w(1000*10)
                self.sleep(5)
            else:
                self.action_jump_fly()
                self.sleep(1)

    def go_to_activate_level_65(self):
        # 65级激活副本
        for i in range(2):
            self.action_jump_fly()
            self.sleep(1)
        
        # 旋转视角避免ai队友头像挡住任务图标
        self.rotate_view_to_left(300,500)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        
        self.walk_to_w(walk_time=3000)
        self.sleep(1)

        self.walk_to_d(walk_time=3000)
        self.sleep(1)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        self.walk_to_w(walk_time=1000)
        self.sleep(1)

        for i in range(11):
            self.action_jump_fly()
            self.sleep(0.5)
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False

        self.role_restoration()

        res = self.await_until_ocr(rect=[11,203,252,376],pattern="(波次|保护|探险家)",time_out=10)
        if res:
            print("激活副本成功")
            return True
        else:
            print("激活副本失败")
            return False

    def check_esho_combat(self):
        # 检查扼守是否激活副本
        res = self.is_text_re_in_ocr(rect=[11,199,251,364],pattern="(保护|波次|探险家)")
        if res:
            print("副本激活成功")
            return True
        return False

    def go_to_activate_level_50(self):
        # 50级激活副本
        map_type = -1    # 地图 
        # 识别当前地图
        res = self.find_my_color(mod_color,"50级A图")
        if res:
            map_type = 0

        res = self.find_my_color(mod_color,"50级B图")
        if res:
            map_type = 1

        res = self.find_my_color(mod_color,"50级C图")
        if res:
            map_type = 2

        print(f"当前地图：{map_type}")
        if map_type == -1:
            print("未识别到地图")
            return False

        if map_type == 0:
            res = self.go_to_activate_level_50_A()
        elif map_type == 1:
            res = self.go_to_activate_level_50_B()
        elif map_type == 2:
            res = self.go_to_activate_level_50_C()

        return res

    def go_to_activate_level_50_A(self):
        # 2条路线
        map_type = -1  # 0:直走电梯     1：重置角色位置

        for i in range(6):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)

        self.walk_to_s()
        self.sleep(0.5)
        self.walk_to_a(6000)

        for i in range(2):
            self.walk_to_d(400)
            self.sleep(0.5)

        self.walk_to_w(1000*6)

        self.walk_to_s()
        self.walk_shift_to_d(2000)
        self.walk_to_w()
        self.sleep(1)
        self.walk_to_d()
        self.sleep(1)

        for i in range(5):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.walk_to_w()
            
        self.role_restoration()
        self.sleep(1)

        res = self.find_my_color(common_color,"任务黄色图标")
        if res:
            if (380 < res.x < 420) and (250 < res.y < 285):
                map_type = 0
            else:
                map_type = 1
        else:
            map_type = 1
        print(f"详细路线：{map_type}")

        if map_type == 0:
            # 上楼梯
            self.walk_to_a(1000*1)
            self.walk_to_w(1000*2.5)
            self.walk_to_a(1000*4)
            self.walk_to_s(1000*1.2)
            self.sleep(0.5)
            self.walk_to_a(1000)
            self.sleep(0.5)

            res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",2)
            if not res:
                return False
            self.sleep(0.5)
            
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False

            for i in range(10):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
                res = self.check_esho_combat()
                if res:
                    self.walk_to_w(1000*2)
                    return True
                
            return False
        elif map_type == 1:
            # 左边直走
            res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",2)
            if not res:
                return False
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False

            for i in range(10):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
                res = self.check_esho_combat()
                if res:
                    self.walk_to_w(1000*2)
                    return True
                
            return False

        return False

    def go_to_activate_level_50_B(self):
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        for i in range(4):
            self.action_jump_fly()
            self.sleep(0.5)

        self.role_restoration()
        self.sleep(1)

        # 上楼梯
        self.walk_to_d(1000*1)
        self.walk_to_s(1000*2.5)
        self.walk_to_d(1000*4)
        self.walk_to_w(1000*1.2)
        self.sleep(0.5)
        self.walk_to_d(1000)
        self.sleep(0.5)

        res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",3)
        if not res:
            return False
        self.sleep(0.5)
        
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        for i in range(10):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)
            res = self.check_esho_combat()
            if res:
                self.walk_to_w(1000*2)
                return True
            
        return False

        # res = self.find_my_color(common_color,"任务黄色图标")
        # if res:
        #     if res.y > 455:
        #         map_tyep = 0
        # print(f"详细路线：{map_tyep}")


        
        # for i in range(5):
        #     res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        #     if not res:
        #         return False
        #     self.action_jump_fly()
        #     res = self.is_text_re_in_ocr(rect=[716,312,1028,400],pattern="启动")
        #     if res:
        #         m_type = 1
        #         for i in range(3):
        #             self.click(822,358)
        #         break
        #     self.sleep(0.5)
        
        # 校验
        # if m_type == 0:
        #     self.walk_to_s()
        #     res = self.is_text_re_in_ocr(rect=[716,312,1028,400],pattern="启动")
        #     if res:
        #         m_type = 1
        #         for i in range(3):
        #             self.click(822,358)

        # if m_type == 0:
        #     self.role_restoration()
        #     self.rotate_view_to_down(500)
        #     res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        #     if not res:
        #         return False
        #     self.walk_to_w(1000*4)
        #     self.action_jump_fly()
        #     self.walk_to_w(2000)

        #     for i in range(4):
        #         res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        #         if not res:
        #             return False
        #         self.walk_to_w()

        #     self.role_restoration()
        #     # self.rotate_view_to_right(300,500)
        #     # self.sleep(0.5)
        #     res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",3)
        #     if not res:
        #         return False
        #     self.sleep(0.5)
        #     self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        #     self.walk_to_w(2000)
        # else:
        #     self.sleep(10)
        #     for i in range(4):
        #         self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        #         self.action_jump_fly()
        #         self.sleep(1)
        #     self.role_restoration()
        #     self.walk_to_d(2000)

        # res = self.await_until_ocr(pattern="(波次|探险家)",time_out=10)
        # if res:
        #     print("激活副本成功")
        #     return True
        # else:
        #     print("激活副本失败")
        #     return False

    def go_to_activate_level_50_C(self):
        # 2条路线
        self.walk_to_w(1000*8)
        self.sleep(0.5)
        
        res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",3)
        if not res:
            return False
        self.sleep(0.5)
        
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        for i in range(3):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)
        
        self.role_restoration()
        self.sleep(1)

        # res = self.find_my_color(common_color,"任务黄色图标")
        # if res:
        #     if res.y > 455:
        #         map_type = 0
        # print(f"详细路线：{map_type}")

        # self.rotate_view_to_right(150,500)
        # self.sleep(0.5)

        res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",3)
        if not res:
            return False
        self.sleep(0.5)
        
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        for i in range(2):
            self.action_jump_fly()
            self.sleep(1)

        for i in range(10):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)
            res = self.check_esho_combat()
            if res:
                self.walk_to_w(1000*2)
                return True
            
        return False

        # for i in range(6):
        #     res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        #     if not res:
        #         return False
        #     self.action_jump_fly()
        #     self.sleep(1)
        #     res = self.is_text_re_in_ocr(rect=[716,312,1028,400],pattern="启动")
        #     if res:
        #         break
            
        # res = self.is_text_re_in_ocr(rect=[716,312,1028,400],pattern="启动")
        # if res:
        #     pass
        # else:
        #     self.walk_to_s()

        # res = self.is_text_re_in_ocr(rect=[716,312,1028,400],pattern="启动")
        # if res:
        #     for i in range(3):
        #         self.click(822,358)
        # else:
        #     return False

        # self.sleep(12)
        # for i in range(4):
        #     self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        #     self.action_jump_fly()
        #     self.sleep(1)

        # self.role_restoration()
        # self.walk_to_s(2000)
        
        # res = self.await_until_ocr(pattern="(波次|探险家)",time_out=10)
        # if res:
        #     print("激活副本成功")
        #     return True
        # else:
        #     print("激活副本失败")
        #     return False

    def go_to_activate_level_75(self):
        for i in range(10):
            self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            self.action_jump_fly()
            self.sleep(1)
            res = self.is_text_re_in_ocr(rect=[11,199,251,364],pattern="(保护|波次|探险家)")
            if res:
                print("副本激活成功")
                return True
        print("激活副本失败")
        return False

    def go_to_activate_level_80(self):
        for i in range(10):
            self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            self.action_jump_fly()
            self.sleep(1)
            res = self.is_text_re_in_ocr(rect=[11,199,251,364],pattern="(保护|波次|探险家)")
            if res:
                print("副本激活成功")
                return True
        print("激活副本失败")
        return False

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
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

        if self.uiconfig["mod_activity_shr"] == "on":
            # 收获日退出
            res = self.find_my_color(mod_color,"选择关卡界面确认选择")
            if res:
                self.click(44,32)
                self.sleep(3)
                self.click(44,32)
                self.sleep(3)
        else:
            res = self.find_my_color(mod_color,"选择关卡界面确认选择")
            if res:
                self.click_color_to_color(mod_color,"选择关卡界面确认选择",mod_color,"选择关卡界面",x=44,y=32,out_time=60)
                self.sleep(1)

            self.click_color_to_color(mod_color,"选择关卡界面",common_color,"主界面左上角菜单",x=43,y=34)
            self.sleep(2)

        for i in range(3):
            self.click(634,666)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def combat_quzhu(self):
        # 驱逐战斗
        # 第一阶段战斗
        for i in range(3):
            self.skill_e()
        # 等待小怪死亡
        status_ = False
        for i in range(15):
            res = self.find_my_color(mod_color,'小怪红色图标')
            if res:
                if res.y < 210:
                    print("第一阶段完成")
                    status_ = True
                    break
            self.sleep(1)
        if not status_:
            return False
        
        self.sleep(2)

        # 前往第二阶段
        res = self.rotate_view_direction_range(mod_color,"小怪红色图标",0,200)
        if not res:
            return False
        self.sleep(0.5)

        self.fly_spear_num(2)
        for i in range(8):
            self.click(994,293,after_sleep=0.5)
        
        # 第二阶段战斗
        for i in range(3):
            self.skill_e()
        # 等待小怪死亡
        status_ = False
        for i in range(15):
            res = self.find_my_color(mod_color,'小怪红色图标')
            if res:
                if res.x > 860:
                    print("第二阶段完成")
                    status_ = True
                    break
            self.sleep(1)
        if not status_:
            return False
        
        self.sleep(2)

        # 前往第三阶段
        self.rotate_view_to_middle_by_color(mod_color,"小怪红色图标")

        self.fly_spear_num(2)
        for i in range(8):
            self.click(994,293,after_sleep=0.5)
        self.sleep(1)
        self.click(994,293)

        # 第三阶段战斗
        for i in range(3):
            self.skill_e()
        self.sleep(5)

        self.walk_to_w()
        self.sleep(0.5)

        self.fly_spear_num(1)
        self.sleep(1)
        for i in range(2):
            self.skill_e()
        self.sleep(3)

        self.walk_to_a(1000*2)
        self.sleep(1)

        self.rotate_view_to_middle_by_color(mod_color,"小怪红色图标")
        self.fly_spear_num(4)
        self.sleep(2)

        for i in range(3):
            self.skill_e()

        #等待战斗结束
        res = self.await_until_color(common_color,"副本退出-再次进行",time_out=30)
        if res:
            print("战斗成功")
            return True
        else:
            print("战斗异常")
            return False

    def combat(self):
        # 战斗
        print("开始战斗")

        # 判断是否驱逐
        if self.level_type == '驱逐':
            res = self.combat_quzhu()
            return res

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

            # 释放技能
            self.role_skill_util.combat()

            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}"
        self.logui.change_log_text(text)

    def get_level_type(self):
        # 判断当前任务类型
        if self.level_grade in [30, 50, 65]:
            self.level_type = '扼守'
        elif self.level_grade == 75:
            if self.level_number == "第一个":
                self.level_type = '驱离'
            elif self.level_number == "第二个":
                self.level_type = '驱离'
            elif self.level_number == "第三个":
                self.level_type = '驱离'
            elif self.level_number == "第四个":
                self.level_type = '扼守'
            elif self.level_number == "第五个":
                self.level_type = '扼守'
            elif self.level_number == "倒数第一个":
                self.level_type = '扼守'
            elif self.level_number == "倒数第二个":
                self.level_type = '扼守'
            elif self.level_number == "倒数第三个":
                self.level_type = '驱离'
            elif self.level_number == "倒数第四个":
                self.level_type = '驱离'
            else:
                self.level_type = '驱离'
        elif self.level_grade == 80:
            if self.level_number == "第一个":
                self.level_type = '驱离'
            elif self.level_number == "第二个":
                self.level_type = '驱离'
            elif self.level_number == "第三个":
                self.level_type = '扼守'
            elif self.level_number == "第四个":
                self.level_type = '扼守'
        elif self.level_grade == 60:
            if self.level_number == "60级驱逐":
                self.level_type = '驱逐'
            else:
                self.level_type = '驱离'
        else:
            self.level_type = '驱离'
        print(f"当前任务类型---{self.level_type}")

    def run(self):
        # self.init_level()

        for item in self.mod_config_list:
            print(f"开始执行----{item}")
            self.level_grade = int(item["grade"])
            self.level_max_count = int(item["num"])
            self.level_number = item["level"]

            self.level_finish_count = 0 # 探索完成次数，不论成功失败
            self.level_ok_count = 0  # 探索成功次数
            self.level_faile_count = 0 # 探索失败次数

            self.get_level_type()

            self.refresh_log()
            self.go_to_level()
            
            if self.uiconfig["mod_activity_shr"] == "on":
                self.select_level_grade_activity_shr()
                self.select_level_activity_shr()
            else:
                self.select_level_grade()
                self.select_level()
            
            while 1:
                self.refresh_log()

                print(f"计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")

                if self.level_finish_count >= self.level_max_count:
                    print(f"任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                    self.level_exit()
                    break

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

            
            



