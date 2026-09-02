from ...res.task.BaseTask import BaseTask
from ...res.combat.local.CombatSkillController import CombatSkillController
from ...res.assets.color import *

class AutoJjbTask(BaseTask):
    # 皎皎币
    def __init__(self,uiconfig=None):
        super().__init__()
        self.combat_skill = CombatSkillController(self)

        self.uiconfig = uiconfig

        self.task_name = '皎皎币'

        self.level_grade = 60   # 副本等级
        self.level_boci = 1       # 波次    
        self.now_level_boci = 1     # 当前波次,默认1

        self.level_more_award = 0  # 委托手册
        self.level_more_award_boci = [] # 使用委托手册的轮次

        self.level_max_count = 2 # 最大探索次数
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.set_skill_config()

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

    def set_skill_config(self):
        # 初始化技能配置
        self.combat_skill.init_config(self.uiconfig['jjb_role_skill'])

    def init_jjb(self):
        # 初始化
        self.level_grade = int(self.uiconfig['jjb_grade'])
        self.level_max_count = int(self.uiconfig['jjb_max_num'])
        self.level_boci = int(self.uiconfig['jjb_boci_num'])

        self.level_more_award = int(self.uiconfig['jjb_level_more_award'])
        
        str_ = self.uiconfig['jjb_level_more_award_boci']
        str_ = str_.replace("，",",")
        if str_ == "-1":
            self.level_more_award_boci = list(range(1,self.level_boci+1))
        elif "," not in str_:
            self.level_more_award_boci.append(int(str_))
        else:
            list_ = str_.split(",")
            for i in list_:
                self.level_more_award_boci.append(int(i))
        
        # 构建自定义技能配置传入【角色技能搓招】
        skill_config = {
            "skill_q_max_time": float(self.uiconfig['jjb_skill_q_time']),
            "skill_q_max_count": int(self.uiconfig['jjb_skill_q_count']),
            "skill_e_max_time": float(self.uiconfig['jjb_skill_e_time']),
            "skill_e_max_count": int(self.uiconfig['jjb_skill_e_count']),
            "skill_z_max_time": float(self.uiconfig['jjb_skill_z_time']),
            "skill_z_max_count": int(self.uiconfig['jjb_skill_z_count']),
        }
        self.combat_skill.set_role_skill_config_custom(skill_config)

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
        print("开始前往皎皎币副本")
        self.go_to_lilian()
        self.sleep(2)
        for i in range(3):
            self.slide(1193,376,178,376,dur=500)
        self.sleep(2)
        self.click_color_to_color(jjb_color,"历练-委托-皎皎币",jjb_color,"委托-开始挑战",x=929,y=376)
        self.sleep(1)
        print("成功进入皎皎币副本选择界面")

    def select_level_grade(self):
        # 选择等级
        if self.level_grade == 40:
            self.click(126,165)
        elif self.level_grade == 50:
            self.click(129,211)
        elif self.level_grade == 60:
            self.click(120,257)
        elif self.level_grade == 70:
            self.click(118,306)
        elif self.level_grade == 80:
            self.click(121,348)

        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(jjb_color,"委托-开始挑战")
        if res:
            self.click_color_to_color(jjb_color,"委托-开始挑战",common_color,"委托手册选择界面",x=1169,y=672)
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

    def go_to_activate_level(self):
        # 前往激活任务
        if self.level_grade == 60:
            res = self.go_to_activate_level_60()
            if res:
                return True
        elif self.level_grade == 50:
            res = self.go_to_activate_level_50_new()
            if res:
                return True
        elif self.level_grade == 80:
            res = self.go_to_activate_level_50()
            if res:
                return True

        return False

    def check_combat(self):
        # 检查是否激活副本
        res = self.is_text_re_in_ocr(rect=[11,199,251,364],pattern="(保护|波次|探险家)")
        if res:
            print("副本激活成功")
            return True
        return False

    def go_to_activate_level_50_new(self):
        for i in range(10):
            self.action_jump_fly()
            self.sleep(1)
            res = self.check_combat()
            if res:
                print("副本激活成功")
                return True
        return False

    def go_to_activate_level_50(self):
        # 50级激活副本

        for i in range(10):
            self.rotate_view_to_middle_by_color(common_color, "任务黄色图标")
            self.action_jump_fly()
            self.sleep(1)
            res = self.check_combat()
            if res:
                return True
        return False

        # map_type = -1    # 地图
        # # 识别当前地图
        #
        # res = self.await_color(common_color,"任务黄色图标")
        # if not res:
        #     print("未识别到黄色图标")
        #     return False
        #
        # res = self.find_my_color(common_color,"任务黄色图标")
        # if 590 < res.x < 612:
        #     map_type = 0
        # elif res.x > 840:
        #     map_type = 1
        # elif 625 < res.x < 653:
        #     map_type = 2
        #
        # print(f"当前地图：{map_type}")
        # if map_type == -1:
        #     print("未识别到地图")
        #     return False
        #
        # if map_type == 0:
        #     res = self.go_to_activate_level_50_A()
        # elif map_type == 1:
        #     res = self.go_to_activate_level_50_B()
        # elif map_type == 2:
        #     res = self.go_to_activate_level_50_C()
        #
        # if res:
        #     self.walk_to_w()
        #     self.sleep(1)
        #
        # return res

    def go_to_activate_level_50_A(self):
        # 3条路线
        map_tyep = -1       # 0:前方电梯  1：没有电梯  2：左边直达任务地点
        for i in range(6):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)

        self.walk_to_s()
        self.sleep(0.5)
        self.walk_to_a(1000*5)

        for i in range(2):
            self.walk_to_d(400)
            self.sleep(0.5)

        self.walk_to_w(1000*6)

        self.walk_to_s()
        self.walk_to_d(2000)
        self.walk_to_w()
        self.sleep(1)
        self.walk_to_d()
        self.sleep(1)
        self.walk_to_w()
        self.walk_to_d()

        for i in range(3):
            self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            self.action_jump_fly()
            self.sleep(1)

        self.role_restoration()
        self.sleep(1)
        res = self.find_my_color(common_color,"任务黄色图标")
        if res:
            if (370 < res.x < 400) and (270 < res.y < 300):
                map_tyep = 2
            elif 350 < res.x < 410:
                map_tyep = 1
            else:
                map_tyep = 0
        print(f"详细路线：{map_tyep}")

        if map_tyep == 0:
            for i in range(3):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
            
            self.role_restoration()
            self.walk_to_s(1000*2)

            res = self.check_is_combat()
            return res
        elif map_tyep == 1:
            for i in range(10):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
                res = self.check_combat()
                if res:
                    return True
            
            return False
        elif map_tyep == 2:
            self.walk_to_a(1000*5)
            self.sleep(1)
            self.skill_z()
            self.sleep(1)

            type_ = 0
            res = self.find_my_color(common_color,"任务黄色图标")
            if res:
                if (410 < res.x < 440) and (410 < res.y < 430):
                    type_ = 0
                else:
                    type_ = 1
            print(f"相似详细路线：{type_}")

            if type_ == 0:
                self.walk_to_s(1000*1.2)
                self.walk_to_a(1000*2)
                self.sleep(0.5)
            elif type_ == 1:
                self.walk_to_w(1000*1.2)
                self.walk_to_a(1000*2)
                self.sleep(0.5)

            res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",2)
            if not res:
                return False
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.sleep(0.5)

            for i in range(10):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
                res = self.check_combat()
                if res:
                    return True


        return False

    def go_to_activate_level_50_B(self):
        # 3条路线
        map_tyep = -1       # 0:前方电梯  1：前方直接是任务地点   2:过门后是任务地点

        self.action_jump_fly()
        self.sleep(2)
        self.walk_to_w(1000*4)
        self.sleep(0.5)

        res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",3)
        if not res:
            return False
        self.sleep(0.5)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        self.sleep(0.5)

        for i in range(3):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)

        self.role_restoration()
        self.sleep(1)

        res = self.find_my_color(common_color,"任务黄色图标")
        if res:
            if 720 < res.x < 770:
                map_tyep = 2
            elif res.y > 450:
                map_tyep = 1
            else:
                map_tyep = 0
        print(f"详细路线：{map_tyep}")
        
        if map_tyep == 0:
            # self.rotate_view_to_left(150,dur=500)
            # self.rotate_view_to_left(150,dur=500)

            res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",2)
            if not res:
                return False
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.sleep(0.5)

            for i in range(15):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                res = self.is_text_re_in_ocr(rect=[732,319,897,395],pattern="启动")
                if res:
                    break
                self.walk_to_w(300)
                self.sleep(1)
            
            res = self.is_text_re_in_ocr(rect=[732,319,897,395],pattern="启动")
            if not res:
                print("副本激活失败")
                return False

            for i in range(3):
                self.click(805,360)
            
            self.sleep(15)

            for i in range(5):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)

            self.role_restoration()
            self.walk_to_w(1000*2)

            res = self.check_is_combat()
            return res
        elif map_tyep == 1:
            self.rotate_view_to_left(200,dur=500)
            # self.rotate_view_to_left(200,dur=500)
            # self.rotate_view_to_left(200,dur=500)

            res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",2)
            if not res:
                return False
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.sleep(0.5)

            for i in range(7):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
                res = self.check_combat()
                if res:
                    return True
            
            return False
        elif map_tyep == 2:
            res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",3)
            if not res:
                return False
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.sleep(0.5)

            for i in range(2):
                self.action_jump_fly()
                self.sleep(1)

            for i in range(10):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
                res = self.check_combat()
                if res:
                    return True
            
            return False
        
        return False

    def go_to_activate_level_50_C(self):
        # 2条路线
        map_type = -1  # 0:直走电梯     1：重置角色位置
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        for i in range(3):
            self.action_jump_fly()
            self.sleep(1)

        self.role_restoration()
        self.sleep(1)
        res = self.find_my_color(common_color,"任务黄色图标")
        if res:
            if res.x > 850:
                map_tyep = 1
            else:
                map_tyep = 0
        print(f"详细路线：{map_tyep}")
        
        if map_tyep == 0:
            # self.rotate_view_to_right(200,dur=500)
            # self.rotate_view_to_right(200,dur=500)

            res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",3)
            if not res:
                return False
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.sleep(0.5)

            for i in range(20):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                res = self.is_text_re_in_ocr(rect=[732,319,897,395],pattern="启动")
                if res:
                    break
                self.walk_to_w(300)
                self.sleep(1)
            
            res = self.is_text_re_in_ocr(rect=[732,319,897,395],pattern="启动")
            if not res:
                print("副本激活失败")
                return False

            for i in range(3):
                self.click(805,360)
            
            self.sleep(15)

            for i in range(13):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
                res = self.check_combat()
                if res:
                    return True
            
            return False

        elif map_tyep == 1:
            self.walk_to_d(1000*1)
            self.walk_to_s(1000*2.5)
            self.walk_to_d(1000*4)
            self.walk_to_w(1000*1.2)
            self.sleep(0.5)
            self.walk_to_d(1000)
            self.sleep(0.5)
            # self.rotate_view_to_right(150,dur=500)
            # self.rotate_view_to_right(150,dur=500)

            res = self.rotate_view_direction_to_front(common_color,"任务黄色图标",3)
            if not res:
                return False
            self.sleep(0.5)

            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.sleep(0.5)
            
            for i in range(10):
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if not res:
                    return False
                self.action_jump_fly()
                self.sleep(1)
                res = self.check_combat()
                if res:
                    return True
            
            return False

        return False

    def go_to_activate_level_60(self):
        # 60级激活副本
        map_type = -1    # 地图 
        # 识别当前地图
        res = self.find_my_color(jjb_color,"60级A图")
        if res:
            map_type = 0

        res = self.find_my_color(jjb_color,"60级B图")
        if res:
            map_type = 1

        print(f"当前地图：{map_type}")
        if map_type == -1:
            print("未识别到地图")
            return False

        if map_type == 0:
            res = self.go_to_activate_level_60_A()
        elif map_type == 1:
            res = self.go_to_activate_level_60_B()

        return res

    def go_to_activate_level_60_A(self):
        self.rotate_view_to_top(100)
        self.fly_spear_num(4)
        self.sleep(2)
        self.rotate_view_to_down(50,dur=500)

        self.fly_spear_num(2)
        self.sleep(2)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        self.rotate_view_to_top(50)
        self.fly_spear_num(6)
        self.sleep(3)

        self.walk_to_s()
        self.sleep(2)
        self.walk_to_w()
        self.rotate_view_to_down(100,dur=500)
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        
        self.fly_spear_num(3)
        self.sleep(1)

        self.role_restoration()
        self.walk_to_w(1000*3)

        res = self.check_is_combat()
        return res

    def go_to_activate_level_60_B(self):
        self.action_jump_fly()
        self.role_restoration()
        self.rotate_view_to_right(200)
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False
        self.rotate_view_to_top(100)

        self.fly_spear_num(2)
        self.sleep(2)

        self.rotate_view_to_down(70,dur=500)
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        self.fly_spear_num(2)
        self.sleep(2)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        self.rotate_view_to_top(80)
        self.fly_spear_num(5)
        self.sleep(2)
        self.rotate_view_to_down(150,dur=500)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        self.fly_spear_num(4)
        self.sleep(1)

        self.role_restoration()
        self.walk_to_s(1000*3)

        res = self.check_is_combat()
        return res

    def check_is_combat(self):
        # 判断是否成功进入战斗
        res = self.await_until_ocr(rect=[2,164,235,341],pattern="(轮次|波次|探险家)",time_out=5)
        if res:
            print("激活副本成功")
            return True
        else:
            print("激活副本失败")
            return False

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"地图esc界面",x=40,y=29)
        self.sleep(1)
        self.click_color_to_color(common_color,"地图esc界面",common_color,"退出委托-确定",x=1189,y=639)
        self.sleep(1)
        self.click_color_to_color(common_color,"退出委托-确定",common_color,"副本退出-再次进行",x=777,y=412)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(common_color,"副本退出-再次进行")
        if res:
            self.click_color_to_color(common_color,"副本退出-再次进行",common_color,"左上角红色退出",x=1141,y=672,out_time=60)
            self.sleep(1)

        res = self.find_my_color(jjb_color,"委托-开始挑战")
        if res:
            self.click_color_to_color(jjb_color,"委托-开始挑战",common_color,"左上角红色退出",x=44,y=32,out_time=60)
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

        max_time = 60 * 7

        now_boci = 1  # 当前波次

        while 1:
            if self.time() - start_time > max_time:
                print("战斗超时")
                return False

            res = self.find_my_color(common_color,"副本退出-再次进行")
            if res:
                print("任务失败！！！")
                return True

            res = self.find_my_color(common_color,"波次结束界面")
            if res:
                print(f"波次完成，当前波次：{now_boci}/{self.level_boci}")
                self.now_level_boci += 1
                self.sleep(1)

                # 判断是否需要整点去执行密函
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

            # 释放技能
            self.combat_skill.combat()

            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}"
        self.logui.change_log_text(text)

    def run(self):
        self.init_jjb()
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
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                print("战斗超时")
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
