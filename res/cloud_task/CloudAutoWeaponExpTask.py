from ...res.cloud_task.CloudBaseTask import CloudBaseTask
from ...res.assets.cloud_color import *

class CloudAutoWeaponExpTask(CloudBaseTask):
    # 云-武器经验

    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '云-武器经验'

        self.level_grade = 50   # 副本等级
        self.level_max_count = 2 # 最大探索次数

        self.now_level_boci = 1     # 当前波次,默认1
        self.level_more_award = 0  # 委托手册
        self.level_more_award_boci = [] # 使用委托手册的轮次
        
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.moling_info = {
            "魔灵出现次数":0,
            "魔灵捕捉成功次数":0,
            "捕捉的魔灵":[],
            "你好箱":0,
        }

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

        self.level_grade = int(self.uiconfig['wuqi_exp_grade'])
        self.level_max_count = int(self.uiconfig['wuqi_exp_max_num'])

        self.level_more_award = int(self.uiconfig['wuqi_exp_level_more_award'])
        str_ = self.uiconfig['wuqi_exp_level_more_award_boci']
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
        self.click_until_color_vanish(cloud_common_color, "角色血条-绿色", x=81, y=34)
        self.sleep(2)
        self.click_until_color(cloud_common_color, "左上角红色退出", x=172, y=411)
        self.sleep(1)
        self.click_color_to_color(cloud_common_color,"左上角红色退出",cloud_common_color,"历练委托菜单",x=96,y=186)
        self.sleep(1)
        self.click_color_to_color(cloud_common_color,"历练委托菜单",clound_weapon_exp_color,"委托-开始挑战",x=985,y=354)
        self.sleep(1)
        print(f"成功进入{self.task_name}副本选择界面")

    def select_level_grade(self):
        # 选择等级
        if self.level_grade == 60:
            self.click(173,348)

        self.sleep(1)

    def go_in_level(self):
        # 进入副本
        self.now_level_boci = 1
        print(f"开始进入副本---{self.level_grade}")
        res = self.find_my_color(clound_weapon_exp_color,"委托-开始挑战")
        if res:
            self.click_color_to_color(clound_weapon_exp_color,"委托-开始挑战",cloud_common_color,"委托手册选择界面",x=1119,y=675)
            self.sleep(1)

        res = self.find_my_color(cloud_common_color,"副本退出-再次进行")
        if res:
            self.click_color_to_color(cloud_common_color,"副本退出-再次进行",cloud_common_color,"委托手册选择界面",x=854,y=676)
            self.sleep(1)
        
        # 使用委托手册
        self.check_use_level_more_award()

        self.click_color_to_color(cloud_common_color,"委托手册选择界面",cloud_common_color,"角色血条-绿色",x=773,y=496,out_time=60)
        self.sleep(2)

        print("成功进入副本")

    def quit_level(self):
        # 退出当前副本
        self.common_quit_level()

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(cloud_common_color, "副本退出-再次进行")
        if res:
            self.click_color_to_color(cloud_common_color,"副本退出-再次进行",cloud_common_color,"左上角红色退出",x=1094,y=673,out_time=60)
            self.sleep(1)

        res = self.find_my_color(clound_weapon_exp_color,"委托-开始挑战")
        if res:
            self.click_color_to_color(clound_weapon_exp_color,"委托-开始挑战",cloud_common_color,"历练委托菜单",x=92,y=29,out_time=60)
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

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}  魔灵：{self.moling_info['魔灵出现次数']}/{self.moling_info['魔灵捕捉成功次数']}  你好箱：{self.moling_info['你好箱']}"
        self.logui.change_log_text(text)

    def ctach_moling(self):
        # 捉魔灵
        res = self.await_until_ocr(rect=[673,336,929,392], pattern="[开启挑战]+", time_out=5)
        if res:
            print("魔灵挑战")
        else:
            print("未识别到魔灵挑战")
            return False
        
        self.click(744,358)

        # 释放e
        for i in range(5):
            self.skill_e(after_sleep=0.5)
        
        # 等待挑战完成
        self.await_until_ocr(rect=[673,336,929,392], pattern="[投喂魔灵]+", time_out=60)
        self.click(744,358,after_sleep=2)

        # 识别魔灵
        res = self.ocr(rect=[212,495,704,653])
        moling_text = ""
        if res:
            moling_text = ""
            for r in res:
                moling_text += r.text + "+"
        else:
            moling_text = "识别错误"
        self.moling_info["捕捉的魔灵"].append(moling_text)

        if "你好" in moling_text:
            print("出你好箱了！！！！")
            self.moling_info["你好箱"] += 1

        self.click(1039,670,after_sleep=2)
        self.click(640,638,after_sleep=3)

        print("魔灵捕捉完成")
        self.moling_info["魔灵捕捉成功次数"] += 1
        self.role_restoration()

    def level_process(self):
        # 关卡处理逻辑
        if self.level_grade == 60:
            return self.level_process_60()
        
        return False

    def level_process_60(self):
        # 60级关卡处理
        map_type = -1   #0-正前方  1-左边  2-右边
        res = self.await_color(clound_weapon_exp_color,"敌人红色小图标",out_time=3)
        if not res:
            print("未检测到敌人位置图标，可能是队友头像遮挡")
            map_type = 1
        
        if map_type == -1:
            if 530 < res.x < 700:
                map_type = 0
            elif res.x < 530:
                map_type = 1
            elif res.x > 700:
                map_type = 2
        print(f"详细路线：{map_type}")

        if map_type == -1:
            return False

        if map_type == 0:
            return self.level_process_60_A()
        elif map_type == 1:
            return self.level_process_60_B()
        elif map_type == 2:
            return self.level_process_60_C()

    def level_process_60_A(self):
        # 正前方
        self.fly_spear(count=3)
        self.sleep(1)

        self.walk_to_a(1000,after_sleep=0.5)
        self.fly_spear(count=2)
        self.sleep(1)
        self.role_restoration()
        self.skill_q(after_sleep=3)

        self.walk_to_a(1000*2,after_sleep=0.2)
        self.rotate_view_to_top(150,dur=200,after_sleep=0.2)
        self.fly_spear(count=3)
        self.sleep(2)
        self.walk_to_a(1000*0.5,after_sleep=0.2)
        self.fly_spear(count=2)
        self.sleep(1)
        self.role_restoration()
        self.skill_q(after_sleep=3)

        for i in range(3):
            self.rotate_view_to_right(250,dur=200,after_sleep=0.2)
        self.rotate_view_to_top(50,dur=200,after_sleep=0.2)
        self.fly_spear(count=1)
        self.sleep(1)
        self.walk_to_a(1000*1.5,after_sleep=0.2)
        self.fly_spear(count=2)
        self.sleep(1)
        self.walk_to_s(1000*0.5,after_sleep=0.2)
        self.walk_to_a(1000*0.6,after_sleep=0.2)
        self.fly_spear(count=1)
        self.sleep(1)
        self.role_restoration()
        self.skill_q(after_sleep=5)
        self.skill_q(after_sleep=3)

        # 等待任务完成
        res = self.await_color(clound_weapon_exp_color,"左边绿色小图标",out_time=20)
        if res:
            print("任务完成")
        else:
            print("任务未完成，异常")
            return False

        # 判断是否出现魔灵
        for i in range(10):
            res = self.find_my_color(clound_weapon_exp_color, "左边紫色小图标")
            if res:
                break
            self.sleep(0.2)
        if res:
            print("出现魔灵")
            self.moling_info["魔灵出现次数"] += 1
            
            self.fly_spear(count=1)
            self.sleep(1)
            self.walk_to_w(1000*2,after_sleep=0.2)
            self.walk_to_d(1000*3.5,after_sleep=0.2)
            self.walk_to_w(1000*0.5,after_sleep=0.2)

            self.ctach_moling()
        
        print("开始撤离")
        self.fly_spear(count=1)
        self.sleep(1)
        self.walk_to_w(1000*2,after_sleep=0.2)
        self.walk_to_d(1000*3.5,after_sleep=0.2)
        for i in range(2):
            self.rotate_view_to_top(200,dur=200,after_sleep=0.2)
        for i in range(2):
            self.rotate_view_to_right(200,dur=200,after_sleep=0.2)
        self.fly_spear(count=2)
        self.sleep(2)
        self.walk_to_s(1000*0.5,after_sleep=0.2)
        # for i in range(2):
        #     self.rotate_view_to_down(150,dur=200,after_sleep=0.2)
        self.rotate_view_to_down(150,dur=200,after_sleep=0.2)
        for i in range(2):
            self.rotate_view_to_left(200,dur=200,after_sleep=0.2)
        self.fly_spear(count=4)
        self.sleep(2)
        self.walk_to_s(1000,after_sleep=0.2)

        res = self.await_until_color(cloud_common_color,"副本退出-再次进行",time_out=20)
        if res:
            print("挑战成功")
            return True
        else:
            print("挑战失败")
            return False

    def level_process_60_B(self):
        # 左边
        # 第一次复位后路线，1-前面 2-后面  3-坑里面
        map_type = -1
        self.rotate_view_to_left(180,dur=500,after_sleep=0.2)
        self.fly_spear(count=2)
        self.sleep(2)
        for i in range(2):
            self.rotate_view_to_left(250,dur=500,after_sleep=0.2)

        self.walk_to_a(1000*0.8,after_sleep=0.2)
        self.rotate_view_to_left(100,dur=500,after_sleep=0.2)
        self.rotate_view_to_top(100,dur=500,after_sleep=0.2)

        self.fly_spear(count=3)
        self.sleep(1)

        self.role_restoration()
        self.skill_q(after_sleep=5)

        res = self.await_color(clound_weapon_exp_color,"敌人红色小图标")
        if not res:
            map_type = 3
        
        if map_type == -1:
            if res.y < 270:
                print("前面")
                map_type = 1
            elif res.y > 470:
                print("后面")
                map_type = 2
            elif res.x < 410:
                print("坑里面")
                map_type = 3

        print(f"路线：{map_type}")
        if map_type == -1:
            return False
        elif map_type == 1:
            self.rotate_view_to_top(100,dur=500,after_sleep=0.2)
            self.fly_spear(count=2)
            self.sleep(1)
            self.walk_to_a(1000*0.3,after_sleep=0.2)
            self.walk_to_w(1000,after_sleep=0.2)
            self.walk_to_d(1000,after_sleep=0.2)
            self.fly_spear(count=3)
            self.sleep(1)
            self.skill_q(after_sleep=3)

            self.role_restoration()
            self.skill_q(after_sleep=5)

            self.sleep(3)
            self.skill_q(after_sleep=5)

            self.role_restoration()
            # for i in range(4):
            #     self.rotate_view_to_right(200,dur=200,after_sleep=0.2)
            # self.rotate_view_to_top(200,dur=200,after_sleep=1)
            # self.click_fly(after_sleep=3)
            # self.walk_to_w(1000*0.3,after_sleep=0.2)
            # self.walk_to_a(1000*2,after_sleep=0.5)
            # self.rotate_view_to_down(80,dur=200,after_sleep=0.2)
            # self.rotate_view_to_left(80,dur=200,after_sleep=0.5)
            # self.fly_spear(count=3)
            # self.sleep(2)
            self.fly_spear(count=1)
            self.sleep(1)
            self.walk_to_w(1000*1.5,after_sleep=0.2)
            self.walk_to_d(1000*3.8,after_sleep=0.2)
            self.walk_to_s(1000*2,after_sleep=0.2)
            self.walk_to_d(1000*9,after_sleep=0.2)
            self.skill_q(after_sleep=3)

            self.role_restoration()
            self.skill_q(after_sleep=3)

            # 等待任务完成
            res = self.await_color(clound_weapon_exp_color,"左边绿色小图标")
            if res:
                print("任务完成")
            else:
                print("任务未完成，异常")
                return False

            # 判断是否出现魔灵
            for i in range(10):
                res = self.find_my_color(clound_weapon_exp_color, "左边紫色小图标")
                if res:
                    break
                self.sleep(0.2)
            if res:
                print("出现魔灵")
                self.moling_info["魔灵出现次数"] += 1
                self.fly_spear(count=1)
                self.sleep(1)
                self.walk_to_s(1000*0.6,after_sleep=0.2)
                self.walk_to_a(1000*4,after_sleep=0.2)

                self.ctach_moling()
            
            print("开始撤离")
            self.walk_to_d(1000*2,after_sleep=0.2)
            self.walk_to_s(1000,after_sleep=0.2)
            self.walk_to_d(1000,after_sleep=0.2)
            self.rotate_view_to_top(200,dur=200,after_sleep=0.2)
            for i in range(3):
                self.rotate_view_to_right(200,dur=200,after_sleep=0.2)
            self.sleep(0.5)
            self.click_fly(after_sleep=3)
            self.rotate_view_to_down(50,dur=200,after_sleep=0.2)
            self.rotate_view_to_right(120,dur=200,after_sleep=0.2)
            self.fly_spear(count=5)
            self.walk_to_s(1000,after_sleep=0.2)

        elif map_type == 2:
            for i in range(6):
                self.rotate_view_to_left(250,dur=500,after_sleep=0.2)
            self.rotate_view_to_right(50,dur=500,after_sleep=0.2)
            self.rotate_view_to_top(200,dur=500,after_sleep=0.2)
            self.fly_spear(count=3)
            self.sleep(2)
            self.walk_to_s(1000*0.5,after_sleep=0.5)
            self.walk_to_a(1000*0.7,after_sleep=0.5)

            self.fly_spear(count=2)
            self.sleep(2)
            self.skill_q(after_sleep=3)

            self.rotate_view_to_down(100,dur=500,after_sleep=0.2)
            self.fly_spear(count=3)
            self.sleep(1)
            self.skill_q(after_sleep=3)

            self.role_restoration()
            self.sleep(2)
            for i in range(7):
                self.rotate_view_to_left(200,dur=200,after_sleep=0.2)
            self.rotate_view_to_top(100,dur=200,after_sleep=0.2)
            self.rotate_view_to_left(30,dur=200,after_sleep=0.3)
            self.fly_spear(count=7)
            self.sleep(1)

            self.skill_q(after_sleep=3)
            self.role_restoration()
            self.sleep(1)
            self.skill_q(after_sleep=3)

            # 等待任务完成
            res = self.await_color(clound_weapon_exp_color,"左边绿色小图标")
            if res:
                print("任务完成")
            else:
                print("任务未完成，异常")
                return False

            # 判断是否出现魔灵
            for i in range(10):
                res = self.find_my_color(clound_weapon_exp_color, "左边紫色小图标")
                if res:
                    break
                self.sleep(0.2)
            self.role_restoration()
            self.sleep(2)
            if res:
                print("出现魔灵")
                self.moling_info["魔灵出现次数"] += 1
                self.walk_to_d(1000*6.7,after_sleep=0.2)
                self.ctach_moling()

            print("开始撤离")
            for i in range(7):
                self.rotate_view_to_right(200,dur=200,after_sleep=0.2)
            self.walk_to_w(1000*2,after_sleep=0.2)
            self.walk_to_d(1000*1.5,after_sleep=0.2)
            self.walk_to_w(1000*2,after_sleep=0.2)
            self.walk_to_d(1000*1.5,after_sleep=0.2)
            self.walk_to_w(1000*2.5,after_sleep=0.2)
            self.walk_to_s(1000*0.5,after_sleep=0.2)
            self.walk_to_d(1000*0.8,after_sleep=0.2)
            self.rotate_view_to_top(100,dur=200,after_sleep=0.2)
            self.rotate_view_to_right(40,dur=200,after_sleep=0.5)
            self.fly_spear(count=5)

        elif map_type == 3:
            for i in range(6):
                self.rotate_view_to_left(200,dur=200,after_sleep=0.2)
            self.rotate_view_to_top(200,dur=200,after_sleep=0.2)
            self.click_fly(after_sleep=3)
            self.rotate_view_to_left(200,dur=200,after_sleep=0.2)
            self.rotate_view_to_left(30,dur=200,after_sleep=0.2)
            self.rotate_view_to_down(100,dur=200,after_sleep=0.2)
            self.fly_spear(count=3)
            self.sleep(1)
            self.skill_q(after_sleep=3)
            self.role_restoration()

            for i in range(8):
                self.rotate_view_to_left(200,dur=200,after_sleep=0.2)
            self.walk_to_a(1000*0.3,after_sleep=0.2)
            self.rotate_view_to_right(150,dur=200,after_sleep=0.2)
            self.rotate_view_to_top(50,dur=200,after_sleep=0.2)

            self.fly_spear(count=5)
            self.sleep(1)
            self.skill_q(after_sleep=3)

            # 等待任务完成
            res = self.await_color(clound_weapon_exp_color,"左边绿色小图标")
            if res:
                print("任务完成")
            else:
                print("任务未完成，异常")
                return False

            # 判断是否出现魔灵
            for i in range(10):
                res = self.find_my_color(clound_weapon_exp_color, "左边紫色小图标")
                if res:
                    break
                self.sleep(0.2)
            self.role_restoration()
            self.sleep(2)
            if res:
                print("出现魔灵")
                self.moling_info["魔灵出现次数"] += 1

                for i in range(20):
                    for i in range(3):
                        res = self.is_text_re_in_ocr(rect=[673,336,929,392], pattern="[开启挑战]+")
                        if res:
                            break
                    if res:
                        print("找到魔灵")
                        break
                    self.rotate_view_to_middle_by_color(clound_weapon_exp_color,"魔灵位置图标")
                    self.sleep(0.5)
                    self.walk_to_w(1000*0.5,after_sleep=0.5)

                self.ctach_moling()

            print("开始撤离")
            for i in range(7):
                self.rotate_view_to_right(200,dur=200,after_sleep=0.2)
            self.rotate_view_to_top(100,dur=200,after_sleep=0.2)
            self.rotate_view_to_right(30,dur=200,after_sleep=0.2)
            self.fly_spear(count=7)

        res = self.await_until_color(cloud_common_color,"副本退出-再次进行",time_out=20)
        if res:
            print("挑战成功")
            return True
        else:
            print("挑战失败")
            return False

    def level_process_60_C(self):
        # 右边
        self.fly_spear(count=2)
        self.sleep(2)
        for i in range(3):
            self.rotate_view_to_right(250,dur=500,after_sleep=0.2)

        self.fly_spear(count=1)
        self.sleep(1)

        self.walk_to_d(1000*0.4,after_sleep=0.2)
        self.fly_spear(count=1)
        self.sleep(1)

        self.role_restoration()
        self.skill_q(after_sleep=3)

        self.rotate_view_to_top(50,dur=500,after_sleep=0.2)
        self.fly_spear(count=4)
        self.sleep(1)

        self.role_restoration()
        self.skill_q(after_sleep=3)

        self.fly_spear(count=3)
        self.sleep(1)
        self.walk_to_s(1000*0.3,after_sleep=0.2)
        for i in range(3):
            self.rotate_view_to_right(200,dur=200,after_sleep=0.3)
        self.rotate_view_to_right(120,dur=200,after_sleep=0.2)
        self.fly_spear(count=1)
        self.sleep(1)
        self.fly_spear(count=3)
        self.sleep(1)
        self.walk_to_a(1000*0.5,after_sleep=0.2)
        self.walk_to_w(1000*2,after_sleep=0.2)

        self.role_restoration()
        self.skill_q(after_sleep=5)
        self.skill_q(after_sleep=3)

        # 等待任务完成
        res = self.await_color(clound_weapon_exp_color,"左边绿色小图标")
        if res:
            print("任务完成")
        else:
            print("任务未完成，异常")
            return False

        # 判断是否出现魔灵
        for i in range(10):
            res = self.find_my_color(clound_weapon_exp_color, "左边紫色小图标")
            if res:
                break
            self.sleep(0.2)
        self.role_restoration()
        self.sleep(2)
        if res:
            print("出现魔灵")
            self.moling_info["魔灵出现次数"] += 1
            self.walk_to_w(1000*4,after_sleep=0.2)
            self.walk_to_a(1000*3.5,after_sleep=0.2)
            self.walk_to_w(1000,after_sleep=0.2)
            self.ctach_moling()

        print("开始撤离")
        self.walk_to_d(1000*3,after_sleep=0.2)
        for i in range(3):
            self.rotate_view_to_left(200,dur=200,after_sleep=0.2)
        for i in range(2):
            self.rotate_view_to_top(200,dur=200,after_sleep=0.2)
        self.click_fly(after_sleep=4)
        self.rotate_view_to_down(250,dur=200,after_sleep=0.2)

        self.walk_to_w(1000,after_sleep=0.2)
        self.walk_to_d(1000*3,after_sleep=0.2)
        self.walk_to_w(1000*4,after_sleep=0.2)
        self.walk_to_a(1000*4,after_sleep=0.3)

        self.rotate_view_to_top(100,dur=200,after_sleep=0.2)
        self.rotate_view_to_left(120,dur=200,after_sleep=0.2)
        self.fly_spear(count=4)

        res = self.await_until_color(cloud_common_color,"副本退出-再次进行",time_out=20)
        if res:
            print("挑战成功")
            return True
        else:
            print("挑战失败")
            return False

    def run(self):
        self.init_task()
        self.refresh_log()
        self.go_to_level()
        self.select_level_grade()

        while 1:
            self.refresh_log()

            print(f"计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
            print(f"魔灵信息：{self.moling_info}")

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

            res = self.level_process()
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
