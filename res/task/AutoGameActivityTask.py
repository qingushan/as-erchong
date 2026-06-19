from ...res.task.BaseTask import BaseTask
from ...res.assets.color import *
import re

class AutoGameActivityTask(BaseTask):
    # 活动
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '活动'
        self.game_activity_name = '狩月人之阶'

        self.level_role = '自定义' # 主控角色
        self.level_max_score = 0 # 最高分

        self.level_max_count = 2 # 最大探索次数
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.level_skill_e_time = 10  # 技能释放间隔
        self.level_skill_e_count = 1  # 技能释放次数
        self.level_skill_e_last_time = 0  # 最后一次释放技能时间
        self.level_skill_q_time = 10  # 大招释放间隔
        self.level_skill_q_count = 1  # 大招释放次数
        self.level_skill_q_last_time = 0  # 最后一次释放大招时间
        self.level_skill_z_time = 10  # 魔灵释放间隔
        self.level_skill_z_count = 1  # 魔灵释放次数
        self.level_skill_z_last_time = 0  # 最后一次释放魔灵时间

        self.is_lock_enemy = False  # 是否索敌
        self.rotate_view_to_down_count = 0   # 向下旋转视角次数

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
        self.game_activity_name = self.uiconfig['game_activity_name']
        self.level_grade = int(self.uiconfig['game_activity_grade'])
        self.level_max_count = int(self.uiconfig['game_activity_max_num'])
        # self.level_skill_e_time = float(self.uiconfig['game_activity_skill_e_time'])
        # self.level_skill_e_count = int(self.uiconfig['game_activity_skill_e_count'])
        # self.level_skill_q_time = float(self.uiconfig['game_activity_skill_q_time'])
        # self.level_skill_q_count = int(self.uiconfig['game_activity_skill_q_count'])
        self.level_skill_z_time = float(self.uiconfig['game_activity_skill_z_time'])
        self.level_skill_z_count = int(self.uiconfig['game_activity_skill_z_count'])

        # 主控角色
        role_index = int(self.uiconfig['game_activity_role'])
        if role_index == 0:
            self.level_role = "煜明"
        elif role_index == 1:
            self.level_role = "止流"
        elif role_index == 2:
            self.level_role = "苏乙"
        
        print(f"主控角色：{self.level_role}")

    def level_qiju(self):
        # 棋局
        while 1:
            self.await_until_color(common_color, "左上角红色退出", time_out=60)
            self.click_color_to_color(common_color,"左上角红色退出",test_color,"棋局界面",x=1147,y=651,out_time=60)
            self.click(127,675,after_sleep=2)
            self.click(228,348,after_sleep=2)
            self.click(322,595,after_sleep=2)
            self.click(640,685,after_sleep=2)
            self.click(1138,458,after_sleep=2)
            self.click(781,410,after_sleep=2)
            self.await_until_color(test_color, "棋局结束", time_out=60*2)
            self.click(761,664,after_sleep=2)

    def select_level_grade(self):
        # 选择等级
        if self.uiconfig['game_activity_get_score'] == "on":
            self.click(121,236)
        else:
            if self.level_grade == 60:
                self.click(114,121)
            elif self.level_grade == 75:
                self.click(114,173)
            elif self.level_grade == 110:
                self.click(127,234)
        self.sleep(1)

    def init_skill_time(self):
        # 重置技能时间
        self.level_skill_e_last_time = 0
        self.level_skill_q_last_time = 0
        self.level_skill_z_last_time = 0

    def go_to_level(self):
        # 前往副本
        print(f"开始前往---{self.game_activity_name}")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=339,y=239)
        self.sleep(2)
        res = None
        for i in range(3):
            for i in range(5):
                res = self.is_text_re_in_ocr(rect=[3,75,281,641],pattern="(狩月|之阶)")
                if res:
                    break
                self.sleep(0.5)
            if res:
                break
            else:
                self.slide(98,533,106,113,dur=500)
                self.sleep(2)
        if not res:
            print(f"没有找到--{self.game_activity_name}，退出")
            self.click_color_to_color(common_color,"左上角红色退出",common_color,"主界面菜单展示",x=40,y=32)
            self.sleep(1)
            for i in range(3):
                self.click(634,666)

            res = self.find_my_color(common_color,"角色血条-绿色")
            if res:
                print("成功返回主界面")
            else:
                print("返回主界面失败")
            
            return False
        
        x = res[0].x
        y = res[0].y
            
        self.click_color_to_color(common_color,"左上角红色退出",game_activity_color,"狩月人之阶_前往",x=x,y=y)
        self.sleep(1)

        # 分组赛凹分
        if self.uiconfig['game_activity_get_score'] == 'on':
            self.click_color_to_color(game_activity_color,"狩月人之阶_前往",game_activity_color,"狩月人之阶_分组赛_主界面",x=1073,y=680)
        else:
            self.click_color_to_color(game_activity_color,"狩月人之阶_前往",game_activity_color,"狩月人之阶_主界面_狩月纪念币",x=1073,y=680)
        self.sleep(2)
        print(f"成功进入---{self.game_activity_name}")
        return True

    def go_in_level(self):
        # 进入副本
        self.init_skill_time()
        self.is_lock_enemy = False
        self.rotate_view_to_down_count = 0

        print(f"开始进入副本---")
        # 分组赛凹分
        if self.uiconfig['game_activity_get_score'] == 'on':
            res = self.find_my_color(game_activity_color,"狩月人之阶_分组赛_主界面")
            if res:
                self.click_color_to_color(game_activity_color,"狩月人之阶_分组赛_主界面",common_color,"角色血条-绿色",x=1074,y=675,out_time=60)
                self.sleep(2)
                print("成功进入副本")
                return True

            res = self.find_my_color(game_activity_color,"狩月人之阶_挑战完成")
            if res:
                self.click_color_to_color(game_activity_color,"狩月人之阶_挑战完成",common_color,"角色血条-绿色",x=521,y=667,out_time=60)
                self.sleep(2)
                print("成功进入副本")
                return True
        else:
            res = self.find_my_color(game_activity_color,"狩月人之阶_主界面_狩月纪念币")
            if res:
                self.click_color_to_color(game_activity_color,"狩月人之阶_主界面_狩月纪念币",common_color,"角色血条-绿色",x=1114,y=675,out_time=60)
                self.sleep(2)
                print("成功进入副本")
                return True

            res = self.find_my_color(game_activity_color,"狩月人之阶_挑战完成")
            if res:
                self.click_color_to_color(game_activity_color,"狩月人之阶_挑战完成",common_color,"角色血条-绿色",x=521,y=667,out_time=60)
                self.sleep(2)
                print("成功进入副本")
                return True
        
        return False

    def go_to_activate_level(self):
        # 前往激活任务
        print("开始前往激活任务")
        for i in range(20):
            res = self.find_my_color(game_activity_color,"狩月人之阶_开始战斗")
            if res:
                print("激活任务成功")
                return True
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                print("没有找到黄色")
                return True
            self.action_jump_fly()
            self.sleep(0.5)

        return False

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"地图esc界面",x=40,y=29)
        self.sleep(1)
        self.click_color_to_color(common_color,"地图esc界面",common_color,"退出委托-确定",x=1189,y=639)
        self.sleep(1)
        self.click_color_to_color(common_color,"退出委托-确定",game_activity_color,"狩月人之阶_挑战完成",x=777,y=412)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        # 分组赛凹分
        if self.uiconfig['game_activity_get_score'] == 'on':
            res = self.find_my_color(game_activity_color,"狩月人之阶_挑战完成")
            if res:
                self.click_color_to_color(game_activity_color,"狩月人之阶_挑战完成",game_activity_color,"狩月人之阶_分组赛_主界面",x=753,y=667,out_time=60)
                self.sleep(1)

            self.click_color_to_color(game_activity_color,"狩月人之阶_分组赛_主界面",common_color,"角色血条-绿色",x=43,y=34,out_time=20)
            self.sleep(2)
        else:
            res = self.find_my_color(game_activity_color,"狩月人之阶_挑战完成")
            if res:
                self.click_color_to_color(game_activity_color,"狩月人之阶_挑战完成",game_activity_color,"狩月人之阶_主界面_狩月纪念币",x=753,y=667,out_time=60)
                self.sleep(1)

            self.click_color_to_color(game_activity_color,"狩月人之阶_主界面_狩月纪念币",common_color,"角色血条-绿色",x=43,y=34,out_time=20)
            self.sleep(2)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def get_score(self):
        # 获取分数
        print("开始识别分数")
        score = -1

        res = self.ocr(rect=[477,255,802,374])
        if res:
            for r in res:
                text = r.text
                print(text)
                result = re.findall(r"\d+",text)
                print(result)
                if len(result) > 0:
                    n = int(result[0])
                    score = n
                    break
        print(f"当前分数：{score}")
        if score > self.level_max_score:
            self.level_max_score = score

    def combat_befor(self):
        # 战斗前准备
        if self.level_role == "煜明":
            self.skill_q(after_sleep=3)
            self.level_skill_q_last_time = self.time()
        elif self.level_role == "止流":
            for i in range(2):
                self.action_jump_fly()
                self.sleep(0.5)
            self.walk_to_w(walk_time=1000*0.5)
            self.skill_e(dur=1000, after_sleep=1.5)
            self.skill_e(after_sleep=1)
            self.skill_q(after_sleep=4)
            self.skill_e(after_sleep=1.5)
            self.walk_to_w(walk_time=1000)
        elif self.level_role == "苏乙":
            self.walk_to_w(walk_time=1000 * 6)
            self.sleep(1)
            self.skill_q(after_sleep=4)
            self.combat_left_click()
            self.sleep(2)
            self.combat_left_click()
            self.sleep(1)

            self.walk_to_w(walk_time=1000 * 2)

    def combat(self):
        # 战斗
        print("开始战斗")

        if self.level_role == "煜明":
            return self.combat_yuming()
        elif self.level_role == "止流":
            return self.combat_zhiliu()
        elif self.level_role == "苏乙":
            return self.combat_suyi()
    
    def combat_yuming(self):
        # 煜明战斗
        if self.uiconfig['game_activity_get_score'] == 'on':
            # 分组赛
            index_ = 0
            while 1:
                res = self.find_my_color(game_activity_color,"狩月人之阶_挑战完成")
                if res:
                    print("挑战成功")
                    self.sleep(1)
                    self.get_score()
                    return True

                if index_ >= 3:
                    self.skill_e(after_sleep=0.1)
                    self.rotate_view_to_right(250, dur=100, after_sleep=0.1)
                    self.rotate_view_to_right(250, dur=100, after_sleep=0.1)
                    index_ = 0
                else:
                    self.skill_e(after_sleep=0.3)

                self.combat_left_click()

                if self.level_skill_z_is_ok():
                    self.level_skill_z()
                
                index_ += 1
                self.sleep(0.2)
        else:
            self.level_skill_q_time = 30
            self.lock_enemy()
            while 1:
                res = self.find_my_color(game_activity_color,"狩月人之阶_挑战完成")
                if res:
                    print("挑战成功")
                    self.sleep(1)
                    self.get_score()
                    return True

                if self.level_skill_q_is_ok():
                    self.skill_q()
                    self.level_skill_q_last_time = self.time()

                self.skill_e(after_sleep=0.4)
                self.combat_left_click()

                if self.level_skill_z_is_ok():
                    self.level_skill_z()
                
                self.sleep(0.1)

    def combat_zhiliu(self):
        # 止流战斗
        if self.uiconfig['game_activity_get_score'] == 'on':
            # 分组赛
            while 1:
                res = self.find_my_color(game_activity_color,"狩月人之阶_挑战完成")
                if res:
                    print("挑战成功")
                    self.sleep(1)
                    self.get_score()
                    return True

                self.skill_q(after_sleep=1)

                if self.level_skill_z_is_ok():
                    self.level_skill_z()
                
                self.sleep(0.1)
        else:
            self.lock_enemy()
            self.action_dodge_to_w()
            self.sleep(1)

            while 1:
                res = self.find_my_color(game_activity_color,"狩月人之阶_挑战完成")
                if res:
                    print("挑战成功")
                    self.sleep(1)
                    self.get_score()
                    return True

                self.skill_q(after_sleep=0.5)

                if self.level_skill_z_is_ok():
                    self.level_skill_z()
                
                self.sleep(0.1)

    def combat_suyi(self):
        # 苏乙战斗
        if self.uiconfig['game_activity_get_score'] == 'on':
            # 分组赛
            # 每隔5秒释放一次e
            max_time = 15
            last_time = self.time()

            skill_last_time = self.time()
            skill_e_time = 24   # 多少秒开始炸
            while 1:
                res = self.find_my_color(game_activity_color, "狩月人之阶_挑战完成")
                if res:
                    print("挑战成功")
                    self.sleep(1)
                    self.get_score()
                    return True

                if self.time() - skill_last_time > skill_e_time:
                    for i in range(3):
                        self.skill_q(after_sleep=0.5)
                    skill_e_time = 9999
                    self.sleep(2)
                    self.skill_q(after_sleep=4)

                if self.time() - last_time > max_time:
                    self.skill_e(after_sleep=0.2)
                    last_time = self.time()
                    for i in range(3):
                        self.combat_left_click()
                        self.sleep(0.3)
                else:
                    self.combat_left_click()
                    self.sleep(0.5)

                if self.level_skill_z_is_ok():
                    self.level_skill_z()

                self.sleep(0.1)
        else:
            self.lock_enemy()

            # 每隔5秒释放一次e
            max_time = 15
            last_time = self.time()

            skill_last_time = self.time()
            skill_e_time = 40  # 多少秒开始炸

            while 1:
                res = self.find_my_color(game_activity_color, "狩月人之阶_挑战完成")
                if res:
                    print("挑战成功")
                    self.sleep(1)
                    self.get_score()
                    return True

                if self.time() - skill_last_time > skill_e_time:
                    for i in range(3):
                        self.skill_q(after_sleep=0.5)
                    self.sleep(2)
                    for i in range(3):
                        self.skill_q(after_sleep=0.5)
                    self.sleep(2)
                    skill_last_time = self.time()

                if self.time() - last_time > max_time:
                    self.skill_e(after_sleep=0.2)
                    last_time = self.time()
                    for i in range(3):
                        self.combat_left_click()
                        self.sleep(0.3)
                else:
                    # self.combat_left_click()
                    self.skill_e_suyi_0()
                    # self.sleep(0.5)

                if self.level_skill_z_is_ok():
                    self.level_skill_z()

                self.sleep(0.1)

    def level_skill_q_is_ok(self):
        # 大招是否可以释放
        if self.level_skill_q_time < 0:
            return False

        if (self.time() - self.level_skill_q_last_time) >= self.level_skill_q_time:
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

    def level_skill_z_is_ok(self):
        # 魔灵是否可以释放
        if self.level_skill_z_time < 0:
            return False

        if self.time() - self.level_skill_z_last_time >= self.level_skill_z_time:
            return True
        else:
            return False

    def level_skill_e(self):
        # 释放技能
        for i in range(self.level_skill_e_count):
            if self.uiconfig["game_activity_e_saiqi"] == "on":
                combat_left_time = int(self.uiconfig["game_activity_e_saiqi_click_time"])
                self.skill_e_saiqi_0(combat_left_time=combat_left_time)
            else:
                self.skill_e()
        self.level_skill_e_last_time = self.time()

    def level_skill_q(self):
        # 释放大招
        for i in range(self.level_skill_q_count):
            self.skill_q()
            self.sleep(3)
            if self.uiconfig['game_activity_action_crouch'] == "on":
                print("下蹲")
                for i in range(10):
                    res = self.find_my_color(common_color,"角色血条-绿色")
                    if res:
                        break
                    self.sleep(0.1)
                self.action_crouch()
                self.sleep(1)
        self.level_skill_q_last_time = self.time()

        if not self.is_lock_enemy:
            for i in range(2):
                self.skill_e_and_w()
                self.sleep(0.5)
            self.is_lock_enemy = True

    def level_skill_z(self):
        # 释放魔灵
        for i in range(self.level_skill_z_count):
            self.skill_z(after_sleep=0.3)

        self.level_skill_z_last_time = self.time()

    def combat_custom(self):
        # 自定义战斗

        if self.level_skill_q_is_ok():
            self.level_skill_q()
            
        if self.level_skill_e_is_ok():
            self.level_skill_e()

        if self.level_skill_z_is_ok():
            self.level_skill_z()

        if self.rotate_view_to_down_count < 2:
            self.sleep(0.1)
            self.rotate_view_to_down(400,500,0.5)
            self.rotate_view_to_down_count += 1
        
        # for i in range(3):
        #     self.lock_enemy()
        #     self.sleep(0.2)
        
        # self.combat_left_click(dur=1000*2)
        # self.sleep(0.1)
        # self.action_crouch()
        # self.sleep(0.3)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}-{self.game_activity_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}  最高分：{self.level_max_score}"
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
            self.combat_befor()

            res = self.go_to_activate_level()
            if not res:
                self.level_finish_count += 1
                self.level_faile_count += 1
                self.quit_level()
                continue

            res = self.combat()
            if res:
                self.sleep(2)
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                self.level_finish_count += 1
                self.level_faile_count += 1