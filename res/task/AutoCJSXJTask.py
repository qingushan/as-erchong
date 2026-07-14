from ...res.task.BaseTask import BaseTask
from ...res.util.RoleSkillUtil import RoleSkillUtil
from ...res.assets.color import *
import re

class AutoCJSXJTask(BaseTask):
    # 沉浸式戏剧
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '沉浸式戏剧'

        self.moling_boss_max_time = 5   # boss战斗魔灵最大释放间隔
        self.moling_boss_last_time = 0  # boss战斗魔灵最后一次释放时间

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

        self.isfail = False      # 任务失败

        self.role = "赛琪"

        self.boss = None      # 当前boss
        self.boss_dodge_to_w_time = 5   # boss战向boss冲刺时间
        self.boss_dodge_to_w_last_time = 0  # 最后一次释放技能时间

        self.set_skill_config()

    def set_skill_config(self):
        # 初始化技能配置
        self.role_skill_util.init_config(self.uiconfig.get('cjsxj_role_skill', '0'))

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
        self.level_max_count = int(self.uiconfig['cjsxj_max_num'])

        # 构建自定义技能配置传入【角色技能搓招】
        skill_config = {
            "skill_q_max_time": float(self.uiconfig['cjsxj_skill_q_time']),
            "skill_q_max_count": int(self.uiconfig['cjsxj_skill_q_count']),
            "skill_e_max_time": float(self.uiconfig['cjsxj_skill_e_time']),
            "skill_e_max_count": int(self.uiconfig['cjsxj_skill_e_count']),
            "skill_z_max_time": float(self.uiconfig['cjsxj_skill_z_time']),
            "skill_z_max_count": int(self.uiconfig['cjsxj_skill_z_count']),
        }
        self.role_skill_util.set_role_skill_config_custom(skill_config)
        self.isfail = False

    def init_skill_time(self):
        # 重置技能时间
        self.level_skill_e_last_time = 0
        self.level_skill_q_last_time = 0
        self.level_skill_z_last_time = 0
        self.boss_dodge_to_w_last_time = 0

        self.role_skill_util.set_role_skill_config()
        self.role_skill_util.set_combat_options(None)

    def add_moling_skill(self):
        """
        添加魔灵技能
        """
        skill_config = {
            "skill_z_max_time": float(self.uiconfig.get('cjsxj_skill_z_time', 30)),
            "skill_z_max_count": int(self.uiconfig.get('cjsxj_skill_z_count', 1))
        }
        self.role_skill_util.add_skill_z(skill_config)

    def go_to_level(self):
        # 前往副本
        print("开始前往沉浸式戏剧")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=126,y=415)
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",cjsxj_color,"历练-迷津前往",x=47,y=325)
        self.sleep(2)
        for i in range(3):
            self.click(758,617)
        self.sleep(2)
        self.click_until_color(cjsxj_color,"沉浸式戏剧-右上角深渊票",x=1107,y=513)
        self.sleep(1)
        self.click(144,508)
        # self.sleep(2)
        self.sleep(10)
        print("成功进入沉浸式戏剧")
        return True

    def go_in_level(self):
        # 进入副本
        self.boss = None

        self.init_skill_time()

        # 添加魔灵技能
        self.add_moling_skill()

        print(f"开始进入副本---")
        res = self.find_my_color(cjsxj_color,"挑战完成-下一层")
        if res:
            self.click_color_to_color(cjsxj_color,"挑战完成-下一层",common_color,"角色血条-绿色",x=1146,y=679,out_time=60)
            self.sleep(2)
            print("成功进入副本")
            return True

        res = self.find_my_color(cjsxj_color,"挑战完成-失败")
        if res:
            self.click_color_to_color(cjsxj_color,"挑战完成-失败",common_color,"角色血条-绿色",x=865,y=679,out_time=60)
            self.sleep(2)
            print("成功进入副本")
            return True
        
        res = self.find_my_color(cjsxj_color,"未完成的关卡星星")
        if res:
            self.click_color_to_color(cjsxj_color,"未完成的关卡星星",cjsxj_color,"具体关卡-星星",x=res.x,y=res.y)
            self.sleep(1)
            self.click(1169,682)
            self.sleep(3)
            res = self.find_my_color(cjsxj_color,"确认进入副本")
            if res:
                self.click_color_to_color(cjsxj_color,"确认进入副本",common_color,"角色血条-绿色",x=779,y=413,out_time=60)
            res = self.await_color(common_color,"角色血条-绿色",out_time=40)
            if res:
                self.sleep(2)
                print("成功进入副本")
                return True
            else:
                return False
        
        return False

    def unlocking(self):
        # 开锁
        for i in range(10):
            res = self.find_my_color(common_color,'角色血条-绿色')
            if res:
                self.click(796,360)
                self.sleep(1)
            res = self.find_my_color(cjsxj_color,'副本战斗中')
            if res:
                break
            self.sleep(0.5)
        
        res = self.find_my_color(cjsxj_color,'副本战斗中')
        if res:
            print("开锁成功")
            return True
        else:
            print("开锁失败")
            return False

    def go_to_activate_level(self):
        # 前往激活任务
        map_type = -1   # 第一关地图

        # res = self.find_my_color(cjsxj_color,"A图")
        # if res:
        #     map_type = 0
        
        # res = self.find_my_color(cjsxj_color,"B图")
        # if res:
        #     map_type = 1

        # res = self.find_my_color(cjsxj_color,"C图")
        # if res:
        #     map_type = 2

        for i in range(10):
            res = self.find_my_color(common_color,"任务黄色图标")
            if res:
                break
            self.sleep(1)
        
        if res:
            if (420 < res.x < 455) and (300 < res.y < 330):
                map_type = 0
            elif (570 < res.x < 615):
                map_type = 1
            elif (390 < res.x < 430) and (390 < res.y < 420):
                map_type = 2
            elif (890 < res.x < 920) and (310 < res.y < 340):
                map_type = 3
        
        print(f"地图类型：{map_type}")
        if map_type == -1:
            print("未识别到地图")
            return False
        
        if map_type == 0:
            res = self.go_to_activate_level_common()
            return res
        elif map_type == 1:
            res = self.go_to_activate_level_B()
            return res
        elif map_type == 2:
            res = self.go_to_activate_level_C()
            return res
        elif map_type == 3:
            res = self.go_to_activate_level_D()
            if res:
                self.walk_to_a(walk_time=1000)
                self.sleep(0.5)
                # self.action_jump_fly()
                self.action_jump_fly()
            return res

        return False

    def go_to_activate_level_common(self):
        # 普通激活，不需要其他额外路线
        for i in range(20):
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
            if res:
                break
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.walk_to_w(300)
            self.sleep(0.5)

        res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
        if not res:
            print("激活副本失败")
            return False
        
        res = self.unlocking()
        return res

    def go_to_activate_level_B(self):
        self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        self.sleep(1)
        for i in range(4):
            self.action_jump_fly()
            self.sleep(0.5)
        
        return self.go_to_activate_level_common()
    
    def go_to_activate_level_C(self):
        self.rotate_view_to_left(20,dur=500)
        self.walk_to_w(1000*3)
        self.sleep(2)
        self.walk_to_w(1000*5)
        self.rotate_view_direction_to_front(common_color,"任务黄色图标",2)
        self.sleep(1)
        return self.go_to_activate_level_common()

    def go_to_activate_level_D(self):
        self.walk_to_d(1000)
        self.sleep(2)
        return self.go_to_activate_level_common()

    def role_restoration(self):
        # 角色复位
        print("角色复位")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"地图esc界面",x=40,y=29)
        self.sleep(1)
        self.click_color_to_color(common_color,"地图esc界面",common_color,"左上角红色退出",x=936,y=636)
        self.sleep(1)
        self.click_until_ocr(x=49,y=395,rect=[941,211,1254,267],pattern="复位角色")
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"设置-重置位置-确定",x=1092,y=240)
        self.sleep(1)
        self.click_color_to_color(common_color,"设置-重置位置-确定",common_color,"任务黄色图标",x=774,y=412)
        self.sleep(1)
        print("角色复位成功")

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"地图esc界面",x=40,y=29)
        self.sleep(1)
        self.click_color_to_color(common_color,"地图esc界面",common_color,"退出委托-确定",x=1189,y=639)
        self.sleep(1)
        self.click_color_to_color(common_color,"退出委托-确定",cjsxj_color,"挑战完成-失败",x=777,y=412)
        self.sleep(1)
        self.click_color_to_color(cjsxj_color,"挑战完成-失败",cjsxj_color,"具体关卡-星星",x=1131,y=681,out_time=20)
        self.sleep(1)
        self.click_color_to_color(cjsxj_color,"具体关卡-星星",cjsxj_color,"沉浸式戏剧主页",x=44,y=32,out_time=20)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(cjsxj_color,"挑战完成-下一层")
        if res:
            self.click_color_to_color(cjsxj_color,"挑战完成-下一层",cjsxj_color,"具体关卡-星星",x=905,y=679,out_time=20)
            self.sleep(1)
            self.click_color_to_color(cjsxj_color,"具体关卡-星星",cjsxj_color,"沉浸式戏剧主页",x=44,y=32,out_time=20)
            self.sleep(1)

        res = self.find_my_color(cjsxj_color,"挑战完成-失败")
        if res:
            self.click_color_to_color(cjsxj_color,"挑战完成-失败",cjsxj_color,"具体关卡-星星",x=1131,y=681,out_time=20)
            self.sleep(1)
            self.click_color_to_color(cjsxj_color,"具体关卡-星星",cjsxj_color,"沉浸式戏剧主页",x=44,y=32,out_time=20)
            self.sleep(1)

        self.click_color_to_color(cjsxj_color,"沉浸式戏剧-右上角深渊票",common_color,"角色血条-绿色",x=43,y=34)
        self.sleep(2)

        res = self.find_my_color(common_color, "角色血条-绿色")
        if not res:
            self.click_color_to_color(cjsxj_color, "历练-迷津前往", common_color, "角色血条-绿色", x=43, y=34)
            self.sleep(2)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def auot_lock_enemy(self):
        self.lock_enemy()

    def combat(self):
        # 战斗
        print("开始战斗")
        while 1:
            res = self.find_my_color(cjsxj_color,"挑战完成-下一层")
            if res:
                print("挑战成功,开始校验")
                self.sleep(1)
                res = self.find_my_color(cjsxj_color,"挑战完成-下一层")
                if res:
                    print("校验成功,挑战成功")
                    return True
                else:
                    print("校验失败")

            res = self.find_my_color(cjsxj_color,"挑战完成-失败")
            if res:
                print("挑战失败,开始校验")
                self.sleep(1)
                res = self.find_my_color(cjsxj_color,"挑战完成-失败")
                if res:
                    print("校验成功,挑战失败")
                    self.isfail = True
                    return False
                else:
                    print("校验失败")

            # self.role_combat_0()
            self.combat_custom()
            # self.role_combat_1()
            self.sleep(0.1)

    def moling_boss(self):
        # boss战斗是否释放魔灵
        if self.time() - self.moling_boss_last_time >= self.moling_boss_max_time:
            self.skill_z()
            self.moling_boss_last_time = self.time()

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

    def level_skill_z_is_ok(self):
        # 魔灵是否可以释放
        if self.level_skill_z_time < 0:
            return False

        if self.time() - self.level_skill_z_last_time >= self.level_skill_z_time:
            return True
        else:
            return False

    def boss_dodge_to_w_is_ok(self):
        # 是否向boss冲刺
        if self.boss_dodge_to_w_time < 0:
            return False

        if self.time() - self.boss_dodge_to_w_last_time >= self.boss_dodge_to_w_time:
            return True
        else:
            return False

    def boss_dodge_to_w(self):
        # 向boss冲刺
        self.action_dodge_to_w()
        self.sleep(1)
        self.boss_dodge_to_w_last_time = self.time()

    def level_skill_e(self):
        # 释放技能
        for i in range(self.level_skill_e_count):
            if self.boss == "狼人":
                if not self.find_my_color(common_color,"BOSS_血条_红色"):
                    return False
            self.skill_e()
        self.level_skill_e_last_time = self.time()

    def level_skill_q(self):
        # 释放大招
        for i in range(self.level_skill_q_count):
            if self.boss == "狼人":
                if not self.find_my_color(common_color,"BOSS_血条_红色"):
                    return False
            self.skill_q()
            self.sleep(3)
        self.level_skill_q_last_time = self.time()

    def level_skill_z(self):
        # 释放魔灵
        for i in range(self.level_skill_z_count):
            self.skill_z()
        self.level_skill_z_last_time = self.time()

    def ocr_boss(self):
        # 识别boss
        boss_name = "其他"
        res = self.ocr(rect=[411,10,869,71])
        if res:
            for r in res:
                if (re.findall(re.compile(r'\?|？'), r.text)):
                    boss_name = "狼人"
                    break
                if (re.findall(re.compile(r'雪国'), r.text)):
                    boss_name = "雪国的野兽"
                    break
                if (re.findall(re.compile('(炼火|典狱长)'), r.text)):
                    boss_name = "典狱长"
                    break
                if (re.findall(re.compile('西比尔'), r.text)):
                    boss_name = "西比尔"
                    break
        print(f"当前boss：{boss_name}")

        if boss_name != "其他":
            text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}  当前BOSS：{boss_name}"
            self.logui.change_log_text(text)

        return boss_name

    def is_boss(self):
        # 判断当前是否BOSS
        res = self.is_text_re_in_ocr(rect=[10,216,226,318],pattern="(最终|高危)")
        if res:
            return True
        else:
            return False

    def combat_custom(self):
        # 自定义战斗

        if self.uiconfig.get('cjsxj_role_skill', '0') == "8-1":
            if self.is_boss():
                # 识别boss
                if (self.boss == "其他") or(self.boss is None):
                    self.boss = self.ocr_boss()

            # 传入当前当前boss
            combat_options = {
                "CJSXJ_BOSS": self.boss
            }
            self.role_skill_util.set_combat_options(combat_options)

            # 释放技能
            self.role_skill_util.combat()


            return True

        if self.is_boss():
            # self.auot_lock_enemy()
            self.lock_enemy()
            self.sleep(0.2)

            # 识别boss
            if self.boss == "其他":
                self.boss = self.ocr_boss()
            
            if self.boss == "狼人":
                if not self.find_my_color(common_color,"BOSS_血条_红色"):
                    # 狼人技能
                    print("狼人技能")
                    # self.auot_lock_enemy()
                    self.lock_enemy()
                    self.sleep(0.2)
                    for i in range(3):
                        self.action_dodge_to_s()
                        self.sleep(0.5)
                    # self.skill_e()
                    # self.skill_q()
                    return True
                else:
                    self.action_dodge_to_w()
                    self.sleep(1)
                    self.lock_enemy()
                    self.sleep(0.2)
            else:
                if self.boss_dodge_to_w_is_ok():
                    self.boss_dodge_to_w()
                    for i in range(3):
                        self.lock_enemy()
                        self.sleep(0.1)

        # 传入当前当前boss
        combat_options = {
            "CJSXJ_BOSS":self.boss
        }
        self.role_skill_util.set_combat_options(combat_options)

        # 释放技能
        self.role_skill_util.combat()

    def role_combat_0(self):
        # 夫人战斗
        if self.is_boss():
            if self.find_my_color(common_color,"BOSS处决"):
                print("boss处决")
                self.click(996,248)

            for i in range(3):
                self.auot_lock_enemy()
                self.sleep(0.2)

            self.action_dodge_to_w()
            self.sleep(1)

            if self.skill_q_mp_is_ok():
                self.skill_q()
                self.sleep(2)
            
            self.auot_lock_enemy()
            self.sleep(0.2)
            for i in range(7):
                self.moling_boss()    # 魔灵
                if self.skill_e_mp_is_ok():
                    self.skill_e()
                else:
                    break
            
            # boss还在
            if self.is_boss():
                self.auot_lock_enemy()
                self.sleep(0.5)
                res = self.find_my_color(common_color,"没有子弹")
                if res:
                    print("没有子弹了")
                    for i in range(50):
                        self.moling_boss()    # 魔灵
                        self.combat_left_click()
                else:
                    for i in range(50):
                        self.moling_boss()    # 魔灵
                        self.combat_right_click()
        else:
            if self.skill_q_is_ok():
                self.skill_q()
            if self.skill_z_is_ok():
                self.skill_z()
            for i in range(6):
                # 判断是否还在战斗
                r = self.find_my_color(common_color,"角色血条-绿色")
                if not r:
                    break
                if self.is_boss():
                    break
                self.skill_e(after_sleep=0.5)
                self.skill_e(after_sleep=0.5)
                x = self.action_button_position["远程攻击"][0]
                y = self.action_button_position["远程攻击"][1]
                self.combat_bullet()
                self.slide(x,y,x+500,y,1000)

    def role_combat_1(self):
        # 赛琪战斗
        if self.is_boss():
            print("boss")
            self.auot_lock_enemy()
            self.sleep(0.2)

            x = self.action_button_position["跳跃"][0]
            y = self.action_button_position["跳跃"][1]
            self.click(x, y, dur=500,after_sleep=0.1)

            x = self.action_button_position["近战攻击"][0]
            y = self.action_button_position["近战攻击"][1]
            self.click(x, y, dur=2000,after_sleep=0.1)

            # self.jump(100)

            # 识别boss
            # if self.boss == "其他":
            #     self.boss = self.ocr_boss()
            
            # if self.boss == "狼人":
            #     if not self.find_my_color(common_color,"BOSS_血条_红色"):
            #         # 狼人技能
            #         print("狼人技能")
            #         self.auot_lock_enemy()
            #         self.sleep(0.2)
            #         self.action_dodge_to_s()
            #         self.sleep(1)
            #         if self.level_skill_q_is_ok():
            #             self.skill_q()
            #         return True
            #     else:
            #         self.action_dodge_to_w()
            #         self.sleep(1)

        if self.level_skill_q_is_ok():
            self.level_skill_q()
            
        if self.level_skill_e_is_ok():
            self.level_skill_e()
            self.walk_to_w()
            self.sleep(1)

        if self.level_skill_z_is_ok():
            self.level_skill_z()

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
                self.sleep(3)
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                self.level_finish_count += 1
                self.level_faile_count += 1

            # 是否任务失败
            # if self.isfail:
            #     self.level_exit()
            #     return False
