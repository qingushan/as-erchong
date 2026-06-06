from ...res.task.BaseTask import BaseTask
from ...res.util.RoleSkillUtil import RoleSkillUtil
from ...res.assets.color import *
import datetime
import re

from ascript.android.screen import Colors

class AutoWeituomihanTask(BaseTask):
    # 委托密函
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '委托密函'

        self.task_type = '魔之楔'   # 任务类型：角色/武器/魔之楔
        self.level_type = '扼守'   # 副本类型
        self.level_boci = 1       # 波次    
        self.level_max_count = 2 # 最大探索次数

        self.task_time = 0  # 当前任务的时间（小时）
        
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数

        self.level_skill_e_time = 10  # 技能释放间隔
        self.level_skill_e_count = 1  # 技能释放次数
        self.level_skill_e_last_time = 0  # 最后一次释放技能时间
        self.level_skill_q_time = 10  # 大招释放间隔
        self.level_skill_q_count = 1  # 大招释放次数
        self.level_skill_q_last_time = 0  # 最后一次释放大招时间

        self.use_mihan_counut = 0   # 当前成功使用密函的数量
        self.golden_award = 0       # 当前获得的金色奖励

        self.task_levels = []       # 密函委托执行的类型，角色、武器、魔之楔
        self.level_types = []       # 支持执行的副本类型

        self.set_skill_config()

    def set_skill_config(self):
        # 初始化技能配置
        self.role_skill_util.init_config(self.uiconfig.get('mihan_role_skill', '0'))

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
        self.level_max_count = int(self.uiconfig['mihan_max_num'])
        self.level_boci = int(self.uiconfig['mihan_boci_num'])

        # 构建自定义技能配置传入【角色技能搓招】
        skill_config = {
            "skill_q_max_time": float(self.uiconfig['mihan_skill_q_time']),
            "skill_q_max_count": int(self.uiconfig['mihan_skill_q_count']),
            "skill_e_max_time": float(self.uiconfig['mihan_skill_e_time']),
            "skill_e_max_count": int(self.uiconfig['mihan_skill_e_count']),
            "skill_z_max_time": float(self.uiconfig.get('mihan_skill_z_time', 30)),
            "skill_z_max_count": int(self.uiconfig.get('mihan_skill_z_count', 1)),
        }
        self.role_skill_util.set_role_skill_config_custom(skill_config)

        if self.uiconfig['mihan_level_type_quli'] == "on":
            self.level_types.append("驱离")

        if self.uiconfig['mihan_level_type_tanxian'] == "on":
            self.level_types.append("探险")

        # 避免因为本地数据缓存导致继续能选择扼守
        # if self.uiconfig['mihan_level_type_esho'] == "on":
        #     self.level_types.append("扼守")

        # 委托密函类型
        if self.uiconfig['mihan_task_level_role'] == "on":
            self.task_levels.append("角色")

        if self.uiconfig['mihan_task_level_weapon'] == "on":
            self.task_levels.append("武器")

        if self.uiconfig['mihan_task_level_mod'] == "on":
            self.task_levels.append("魔之楔")
        
        print(f"委托密函类型：{self.task_levels}")

        # if self.uiconfig['mihan_level_type_qianyi'] == "on":
        #     self.level_types.append("迁移")

        # 当前任务时间点
        t = datetime.datetime.now()
        self.task_time = t.hour
        print(f"当前任务时间点：{self.task_time}")
        print(f"当前支持执行的任务类型：{self.level_types}")

    def init_task_level(self):
        # 委托密函每个类型初始化
        self.level_finish_count = 0 # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0 # 探索失败次数
        self.use_mihan_counut = 0   # 当前成功使用密函的数量
        self.golden_award = 0       # 当前获得的金色奖励

    def go_to_level(self):
        # 前往副本
        print(f"开始前往{self.task_name}副本")
        self.click_color_to_color(common_color,"主界面左上角菜单",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=126,y=415)
        self.sleep(1)
        self.click_color_to_color(common_color,"左上角红色退出",common_color,"历练委托菜单",x=47,y=184)
        self.sleep(1)
        self.click_color_to_color(common_color,"历练委托菜单",weituomihan_color,"历练-委托密函界面",x=978,y=99)
        self.sleep(1)
        print(f"成功进入{self.task_name}副本选择界面")

    def select_level_type(self):
        # 筛选副本类型
        res = self.find_my_color(common_color,"副本退出-退出委托")
        if res:
            self.click_color_to_color(common_color,"副本退出-退出委托",common_color,"左上角红色退出",x=1141,y=672,out_time=60)
            self.sleep(3)
        
        res = self.find_my_color(weituomihan_color,"委托密函-选择密函")
        if res:
            self.click_color_to_color(weituomihan_color,"委托密函-选择密函",weituomihan_color,"历练-委托密函界面",x=40,y=29)
            self.sleep(1)

        rect = None
        if self.task_type == "角色":
            rect = [434,385,697,633]
        elif self.task_type == "武器":
            rect = [710,380,966,648]
        elif self.task_type == "魔之楔":
            rect = [984,391,1242,624]

        # level_types = ["驱离","探险","扼守","迁移"]
        # level_types = ["迁移"]
        print("开始识别副本类型")
        for i in self.level_types:
            text = i
            if i == "探险":
                text = "探"
            
            res = None
            for k in range(5):
                res = self.is_text_re_in_ocr(rect=rect,pattern=text)
                print(res)
                if res:
                    break
                self.sleep(0.1)

            if res:
                x = res[0].center_x
                y = res[0].center_y
                self.click_color_to_color(weituomihan_color,"历练-委托密函界面",weituomihan_color,"委托密函-选择密函",x=x,y=y)
                self.sleep(1)
                self.level_type = i
                print(f"当前任务类型:{self.level_type}")
                return True

        print("当前没有符合的任务类型！！！")
        self.level_type = ""
        return False

    def select_mihan(self):
        # 选择密函

        # 判断是否还有密函
        # res = self.find_my_color(weituomihan_color,"选择密函-无密函")
        # if res:
        #     print("没有密函碎片了")
        #     return False

        # 默认选择第一个
        self.click(650,344)
        self.sleep(1)
        # 判断是否还有密函
        status_ = False
        for i in range(10):
            res = self.is_text_re_in_ocr(rect=[534,462,1225,526],pattern="[确认选择]+")
            if res:
                status_ = True
                break

            res = self.is_text_re_in_ocr(rect=[534,462,1225,526],pattern="[购买]+")
            if res:
                print("没有密函碎片了")
                status_ = False
                break

            self.sleep(0.5)

        return status_

    def go_in_level(self):
        # 进入副本
        print(f"开始进入副本---{self.level_type}")
        res = self.find_my_color(weituomihan_color,"委托密函-选择密函")
        if res:
            self.click_color_to_color(weituomihan_color,"委托密函-选择密函",weituomihan_color,"选择密函界面",x=1165,y=675)
            self.sleep(1)

        t = datetime.datetime.now()
        res = self.find_my_color(common_color,"副本退出-退出委托")
        if (res) and (t.hour == self.task_time):
            self.click_color_to_color(common_color,"副本退出-退出委托",weituomihan_color,"选择密函界面",x=894,y=676)
            self.sleep(1)
        elif (res) and (t.hour != self.task_time):
            # 刷新时间了
            print("刷新了，开始重新选择委托")
            self.click_color_to_color(common_color,"副本退出-退出委托",common_color,"左上角红色退出",x=1141,y=672,out_time=60)
            self.sleep(3)
            res = self.select_level_type()
            if not res:
                return False
            self.click_color_to_color(weituomihan_color,"委托密函-选择密函",weituomihan_color,"选择密函界面",x=1165,y=675)
            self.sleep(1)
            self.task_time = t.hour
        
        # 选择密函
        res = self.select_mihan()
        if not res:
            self.click(721,490) # 点击放弃
            self.sleep(3)
            return False

        self.click_color_to_color(weituomihan_color,"选择密函界面",common_color,"角色血条-绿色",x=1012,y=476,out_time=60)
        self.sleep(2)

        # 重置技能时间
        self.role_skill_util.set_role_skill_config()

        print("成功进入副本")
        return True

    def go_to_activate_level(self):
        # 前往激活任务
        if self.level_type == '驱离':
            res = self.go_to_activate_level_quli()
            if res:
                return True
        elif self.level_type == '迁移':
            return True
        elif self.level_type == '扼守':
            res = self.go_to_activate_level_esho()
            if res:
                return True
        elif self.level_type == '探险':
            res = self.go_to_activate_level_tanxian()
            if res:
                return True

        return False

    def check_is_combat(self):
        # 判断是否成功进入战斗
        pattern = ""
        rect = None
        if self.level_type == '扼守':
            pattern = "(波次|轮次|保护|探险家)"
            rect = [4,175,221,325]
        elif self.level_type == '探险':
            pattern="(轮次|血清)"
            rect=[4,166,159,316]
        res = self.await_until_ocr(rect=rect,pattern=pattern,time_out=5)
        if res:
            print("激活副本成功")
            return True
        else:
            print("激活副本失败")
            return False

    def unlocking(self):
        # 开锁
        rect = None
        if self.level_type == '探险':
            rect = [1059,545,1146,606]
        res = self.click_until_ocr(796,360,rect=rect,pattern="快")
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

    def go_to_activate_level_quli(self):
        # 驱离激活，判断是否电梯图即可
        # res = self.find_my_color(weituomihan_color,"驱离电梯图")
        # if res:
        #     print("驱离-电梯图")
        #     self.walk_to_w(1000*10)
        #     self.sleep(5)
        # 驱离，强制向前跳三下
        for i in range(3):
            self.action_jump_fly(after_time=2)
        self.sleep(1)
        self.walk_to_s()
        self.sleep(1)

        return True

    def go_to_activate_level_tanxian(self):
        # 探险激活
        map_type = -1
        # res = self.find_my_color(weituomihan_color,"探险A图")
        # if res:
        #     map_type = 0
        # else:
        #     map_type = 1

        res = None
        for i in range(10):
            res = self.find_my_color(common_color,"任务黄色图标")
            if res:
                break
            self.sleep(1)
        
        if not res:
            return False

        if 570 < res.x < 620:
            map_type = 0
        else:
            map_type = 1

        print(f"当前地图:{map_type}")

        if map_type == 0:
            res = self.go_to_activate_level_tanxian_A()
            if res:
                return True
        elif map_type == 1:
            res = self.go_to_activate_level_tanxian_B()
            if res:
                return True

        return False

    def go_to_activate_level_tanxian_A(self):
        # 探险A图
        for i in range(4):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)
            if i == 1:
                self.skill_z()
                self.sleep(1)
        
        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        self.w_and_jupm(walk_time=500)
        self.sleep(0.5)
        
        for i in range(10):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.walk_to_w(500)
            self.sleep(0.5)
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
            if res:
                break
        
        res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
        if not res:
            print("激活副本失败")
            return False
        
        res = self.unlocking()
        if not res:
            return False

        res = self.check_is_combat()
        return res

    def go_to_activate_level_tanxian_B(self):
        # 探险B图
        self.rotate_view_to_left(20,dur=500)
        self.walk_to_w(1000*3)
        self.sleep(2)
        self.walk_to_w(1000*5)
        self.rotate_view_to_left(50,dur=500)

        for i in range(15):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.walk_to_w(400)
            self.sleep(0.5)
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
            if res:
                break

        res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["单行"],pattern="操作")
        if not res:
            print("激活副本失败")
            return False
        
        res = self.unlocking()
        if not res:
            return False

        res = self.check_is_combat()
        return res
        
    def go_to_activate_level_esho(self):
        # 扼守激活
        map_type = -1

        res = self.find_my_color(weituomihan_color,"扼守A图")
        if res:
            map_type = 0
        else:
            map_type = 1

        print(f"当前地图:{map_type}")

        if map_type == 0:
            res = self.go_to_activate_level_esho_A()
            if res:
                return True
        elif map_type == 1:
            res = self.go_to_activate_level_esho_B()
            if res:
                return True

        return False

    def go_to_activate_level_esho_A(self):
        # 扼守A图
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

        for i in range(17):
            res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            if not res:
                return False
            self.action_jump_fly()
            self.sleep(1)
            res = self.is_text_re_in_ocr(rect=[11,203,252,376],pattern="(波次|保护|探险家)")
            if res:
                print("副本激活成功")
                return True

        return False

    def go_to_activate_level_esho_B(self):
        map_type = -1   # 复位后分几种情况  0:前方  1：右边  2：后面
        self.role_restoration()
        self.sleep(1)

        res = self.find_my_color(common_color,"任务黄色图标")
        if not res:
            return False

        if 600 < res.x < 700:
            map_type = 0    
        elif res.x >= 700:
            map_type = 1
        elif res.x < 500:
            map_type = 2

        print(f"当前详细地图：{map_type}")

        if map_type == 2:
            self.rotate_view_to_left(200,dur=500)
            self.rotate_view_to_left(200,dur=500)
            self.rotate_view_to_left(200,dur=500)

        res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
        if not res:
            return False

        # self.rotate_view_to_top(100,dur=500)
        # self.sleep(0.5)

        if map_type == 2:
            res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,300)
            if not res:
                return False
            self.sleep(0.5)
        elif map_type == 0:
            res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,220)
            if not res:
                return False
            self.sleep(0.5)
        else:
            res = self.rotate_view_direction_range(common_color,"任务黄色图标",0,200)
            if not res:
                return False
            self.sleep(0.5)

        if map_type == 0:
            self.fly_spear_num(5)
            self.sleep(2)
            self.walk_to_s()
            self.sleep(2)
            self.walk_to_w()
            self.sleep(0.5)
        elif map_type == 1:
            self.fly_spear_num(3)
            self.sleep(3)
        elif map_type == 2:
            self.fly_spear_num(5)
            self.sleep(2)
            self.walk_to_s()
            self.sleep(2)
            self.walk_to_w()
            self.sleep(0.5)
        
        # self.rotate_view_to_down(100,dur=500)
        res = self.rotate_view_direction_range(common_color,"任务黄色图标",1,70)
        if not res:
            return False
        self.sleep(0.5)

        for i in range(3):
            self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
            self.fly_spear_num(1)
            self.sleep(1)
        
        self.role_restoration()

        res = self.check_is_combat()
        return res

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"地图esc界面",x=40,y=29)
        self.sleep(1)
        self.click_color_to_color(common_color,"地图esc界面",common_color,"退出委托-确定",x=1189,y=639)
        self.sleep(1)
        self.click_color_to_color(common_color,"退出委托-确定",common_color,"副本退出-退出委托",x=777,y=412,out_time=60)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(common_color,"副本退出-退出委托")
        if res:
            self.click_color_to_color(common_color,"副本退出-退出委托",common_color,"左上角红色退出",x=1141,y=672,out_time=60)
            self.sleep(1)

        res = self.find_my_color(weituomihan_color,"委托密函-选择密函")
        if res:
            self.click_color_to_color(weituomihan_color,"委托密函-选择密函",weituomihan_color,"历练-委托密函界面",x=46,y=32,out_time=60)
            self.sleep(1)

        self.click_color_to_color(weituomihan_color,"历练-委托密函界面",common_color,"主界面左上角菜单",x=43,y=29)
        self.sleep(1)

        for i in range(3):
            self.click(634,666)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def click_award(self,is_golden=False):
        # 自动选择奖励，如果出金则默认选择第一个，不是则选择持有数最少的
        if is_golden:
            self.click(460,310)     # 选择第一个
            self.sleep(1)
            return True
        
        # 持有数位置区域
        rects = [
            [413,452,512,498],
            [591,453,692,492],
            [765,456,866,493]
        ]

        list_ = [0,0,0]     #持有列表
    
        for i in range(3):
            res = self.ocr(rect=rects[i])
            if res:
                text = res[0].text
                print(text)
                result = re.findall(r"\d+",text)
                if len(result) > 0:
                    if len(result) > 0:
                        n = int(result[0])
                        print(f"第{i+1}个持有数：{n}")
                        list_[i] = n

        print(f"持有数情况：{list_}")
        min_index = list_.index(min(list_))

        if min_index == 0:
            self.click(460,310)     # 选择第一个
        elif min_index == 1:
            self.click(637,316)     # 选择第二个
        elif min_index == 2:
            self.click(814,319)     # 选择第三个

        self.sleep(1)
        return True

    def select_award(self):
        # 选择奖励
        # 判断是否出金
        is_golden = False
        self.sleep(3)
        res = Colors.count("#BF8E44-#40688e",rect=[392,255,417,493],sim=0.9)
        if res > 3500:
            print("出金了！！！")
            is_golden = True
            self.golden_award += 1
        
        if self.task_type == "武器":
            self.click_award(is_golden)
        else:
            self.click(460,310)     # 选择第一个
            self.sleep(1)
        self.use_mihan_counut += 1

    def combat(self):
        # 战斗
        res = False

        if self.level_type == '扼守':
            res = self.combat_esho()
        elif self.level_type == '驱离':
            res = self.combat_quli()
        elif self.level_type == '迁移':
            res = self.combat_qianyi()
        elif self.level_type == '探险':
            res = self.combat_tanxian()

        return res

    def combat_esho(self):
        # 扼守战斗
        print("扼守战斗")
        start_time = self.time()

        max_time = 60 * 5

        now_boci = 1  # 当前波次

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.find_my_color(weituomihan_color,"密函报酬选择")
            if res:
                print("密函报酬选择")
                self.select_award()
                self.click_color_to_color(weituomihan_color,"密函报酬选择",common_color,"波次结束界面",x=639,y=638)

            res = self.find_my_color(common_color,"波次结束界面")
            if res:
                print(f"波次完成，当前波次：{now_boci}/{self.level_boci}")
                self.sleep(1)
                if now_boci >= self.level_boci:
                    self.click_color_to_color(common_color,"波次结束界面",common_color,"副本退出-退出委托",x=392,y=526,out_time=20)
                    self.sleep(3)
                    return True
                else:
                    self.click_color_to_color(common_color,"波次结束界面",weituomihan_color,"副本内选择密函界面",x=896,y=526)
                    self.sleep(1)
                    res = self.select_mihan()
                    self.sleep(1)

                    if not res:
                        # 没有密函了
                        self.click(562,346) #不选择密函
                        self.sleep(1)
                        self.click(904,492)
                        self.sleep(3)
                        self.quit_level()
                        return True

                    self.click(904,492)
                    self.sleep(3)

                    start_time = self.time()
                    now_boci += 1
                self.refresh_log()

            # 释放技能
            self.role_skill_util.combat()

            self.sleep(0.1)

    def combat_quli(self):
        # 驱离战斗
        print("驱离战斗")
        start_time = self.time()

        max_time = 60 * 2

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.find_my_color(weituomihan_color,"密函报酬选择")
            if res:
                print("密函报酬选择")
                self.select_award()
                self.click(636,639)
                self.sleep(2)

            res = self.find_my_color(common_color,"副本退出-退出委托")
            if res:
                print("战斗完成")
                return True

            # 释放技能
            self.role_skill_util.combat()

            self.sleep(0.1)

    def combat_qianyi(self):
        # 迁移战斗
        run_status = False  # 载具是否启动

        print("迁移战斗")
        start_time = self.time()

        max_time = 60 * 6

        while 1:
            if self.time() - start_time > max_time:
                return False

            if not run_status:
                # 未启动载具
                res = self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                if res:
                    self.walk_to_w()
                else:
                    self.walk_to_w(500)
                    self.sleep(0.5)
                    res = self.is_text_re_in_ocr(rect=[737,334,939,379],pattern="开启")
                    if res:
                        self.click(786,357)
                        self.sleep(2)
                        run_status = True
                continue

            res = self.find_my_color(weituomihan_color,"密函报酬选择")
            if res:
                print("密函报酬选择")
                self.select_award()
                self.click(636,639)
                self.sleep(2)

            res = self.find_my_color(common_color,"副本退出-退出委托")
            if res:
                print("战斗完成")
                return True

            res = self.find_my_color(common_color,"任务黄色图标")
            if res:
                self.sleep(1)
                self.rotate_view_to_middle_by_color(common_color,"任务黄色图标")
                self.action_jump_fly()
                self.sleep(1)
                continue
            
            r1 = self.is_text_re_in_ocr(rect=[737,334,939,379],pattern="开启")
            r2 = self.find_my_color(weituomihan_color,"迁移-开启-红色")
            if r1 and (not r2):
                print("启动载具")
                self.click(786,357)
                self.sleep(2)

            if r2:
                # 释放技能
                self.role_skill_util.combat()

            self.sleep(0.1)

    def combat_tanxian(self):
        # 探险战斗
        print("探险战斗")
        start_time = self.time()

        max_time = 60 * 5

        now_boci = 1  # 当前波次

        while 1:
            if self.time() - start_time > max_time:
                return False

            res = self.find_my_color(weituomihan_color,"密函报酬选择")
            if res:
                print("密函报酬选择")
                self.select_award()
                self.click_color_to_color(weituomihan_color,"密函报酬选择",common_color,"波次结束界面",x=639,y=638)

            res = self.find_my_color(common_color,"波次结束界面")
            if res:
                print(f"波次完成，当前波次：{now_boci}/{self.level_boci}")
                self.sleep(1)
                if now_boci >= self.level_boci:
                    self.click_color_to_color(common_color,"波次结束界面",common_color,"副本退出-退出委托",x=392,y=526,out_time=20)
                    self.sleep(3)
                    return True
                else:
                    self.click_color_to_color(common_color,"波次结束界面",weituomihan_color,"副本内选择密函界面",x=896,y=524)
                    self.sleep(1)
                    res = self.select_mihan()
                    self.sleep(1)

                    if not res:
                        # 没有密函了
                        self.click(562,346) #不选择密函
                        self.sleep(1)
                        self.click(904,492)
                        self.sleep(3)
                        self.quit_level()
                        return True

                    self.click(904,492)
                    self.sleep(3)

                    start_time = self.time()
                    now_boci += 1
                self.refresh_log()

            # 释放技能
            self.role_skill_util.combat()

            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  成功：{self.level_ok_count}  失败：{self.level_faile_count}   已刷取密函数量：{self.use_mihan_counut}  出金次数：{self.golden_award}"
        self.logui.change_log_text(text)

    def change_log(self,text):
        # 更改指定日志内容
        self.logui.change_log_text(text)

    def run(self):
        self.init_task()
        self.refresh_log()
        self.go_to_level()

        for task_level in self.task_levels:
            self.task_type = task_level
            print(f"开始执行----{self.task_type}")

            self.init_task_level()  # 初始化委托密函

            res = self.select_level_type()
            if not res:
                # self.change_log("未查找到指定类型任务！！！")
                print("未查找到指定类型任务！！！")
                # self.level_exit()
                continue

            while 1:
                self.refresh_log()

                print(f"计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")

                if self.level_finish_count >= self.level_max_count:
                    print(f"任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                    # self.level_exit()
                    # return True
                    break
                
                res = self.go_in_level()
                if not res:
                    # self.change_log("未查找到指定类型任务！！！")
                    print("没有密函或者任务刷新了，没有符合的任务")
                    # self.level_exit()
                    # return False
                    break

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

        self.level_exit()
