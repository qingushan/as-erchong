from ...res.task.BaseTask import BaseTask
from ...res.assets.color import *

from ...res.task.AutoModTask import AutoModTask

class AutoDailyTaskTask(BaseTask):
    # 日常任务
    def __init__(self,uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '日常任务'
        self.now_task = '夜航手册'  # 当前执行任务

        self.task_list = []     # 待处理的任务列表

        # 夜航手册、拍照、领取鱼饵、领取玩具气锤、领取每日历练奖励

    def init_level(self):
        # 初始化
        if self.uiconfig['daily_task_mod'] == "on":
            self.task_list.append("夜航手册")

        if self.uiconfig['daily_task_take_a_picture'] == "on":
            self.task_list.append("拍照")

        if self.uiconfig['daily_task_get_fishing_lure'] == "on":
            self.task_list.append("领取鱼饵")

        if self.uiconfig['daily_task_get_wjqc'] == "on":
            self.task_list.append("领取玩具气锤")
        
        if self.uiconfig['daily_task_get_daily_award'] == "on":
            self.task_list.append("领取每日历练奖励")
        
        print(f"任务列表:{self.task_list}")

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}-{self.now_task}"
        self.logui.change_log_text(text)

    def task_mod(self):
        # 夜航手册，40级第一个关卡一次
        task = AutoModTask(self.uiconfig)
        # 修改夜航手册
        task.mod_config_list = [{"grade":"40","num":"3","level":"第一个"}]

        task.run()

    def task_take_a_picture(self):
        print("开始拍照")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        # self.click(49,467,after_sleep=3)
        self.click(49,537,after_sleep=3)

        self.click_until_color(daily_task_color,"拍照-保存",1239,359)
        self.sleep(1)

        self.click(799,677,after_sleep=3)
        self.click(1245,68,after_sleep=3)

        for i in range(3):
            self.click(634,666)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
            print("拍照完成")
        else:
            print("返回主界面失败")

    def task_get_fishing_lure(self):
        # 领取鱼饵
        print("开始领取鱼饵")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=173,y=273)
        self.sleep(3)
        self.click_color_to_color(common_color,"左上角红色退出",daily_task_color,"商店-喧闹卖场-蛋皎的印象商店",x=1204,y=88)
        self.sleep(1)
        self.click(557,424,after_sleep=3)

        # 冰湖城
        res = self.find_my_color(daily_task_color,"通用鱼饵")
        if res:
            print("购买鱼饵-冰湖城")
            self.click_color_to_color(common_color,"左上角红色退出",daily_task_color,"通用鱼饵-购买",x=res.x,y=res.y)
            self.sleep(1)
            self.click(927,424,after_sleep=2)
            self.click(780,511,after_sleep=3)

            self.click(634,687,after_sleep=2)
            self.click(634,687,after_sleep=2)

        # 皓京
        self.click(49,188,after_sleep=3)
        res = self.find_my_color(daily_task_color,"通用鱼饵")
        if res:
            print("购买鱼饵-皓京")
            self.click_color_to_color(common_color,"左上角红色退出",daily_task_color,"通用鱼饵-购买",x=res.x,y=res.y)
            self.sleep(1)
            self.click(927,424,after_sleep=2)
            self.click(780,511,after_sleep=3)

            self.click(634,687,after_sleep=2)
            self.click(634,687,after_sleep=2)
        
        self.click_color_to_color(common_color,"左上角红色退出",daily_task_color,"商店-喧闹卖场-蛋皎的印象商店",x=45,y=34)
        self.sleep(1)

        self.click(45,34,after_sleep=3)

        for i in range(3):
            self.click(634,666)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
            print("领取鱼饵完成")
        else:
            print("返回主界面失败")

    def task_get_wjqc(self):
        # 领取玩具气锤
        print("开始领取玩具气锤")

        # 冰湖城
        self.go_home()
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"左上角红色退出",x=121,y=114)
        self.sleep(1)
        self.click(547,608,after_sleep=3)
        self.click(645,434,after_sleep=3)
        self.click(1071,657,after_sleep=10)
        self.await_color(common_color,"角色血条-绿色",out_time=60*3)
        self.sleep(20)

        res = None
        for i in range(20):
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["多行"],pattern="[拾取]+")
            if res:
                break
            self.walk_to_w(300)
            self.sleep(1)
        
        if res:
            print("拾取-冰湖城")
            self.click(res[0].x,res[0].y,after_sleep=3)

        # 烟津渡
        self.go_home()
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"左上角红色退出",x=121,y=114)
        self.sleep(1)
        # 烟津渡
        self.click(994,664,after_sleep=3)
        self.click(988,555,after_sleep=3)
        self.click(978,391,after_sleep=3)
        self.click(626,700,after_sleep=3)
        # 蛋皎的印象商店
        self.click(1207,239,after_sleep=3)
        self.click(704,336,after_sleep=3)
        self.click(1071,657,after_sleep=10)
        self.await_color(common_color,"角色血条-绿色",out_time=60*3)
        self.sleep(20)

        for i in range(3):
            self.walk_to_d(300)
            self.sleep(1)

        res = None
        for i in range(20):
            res = self.is_text_re_in_ocr(rect=self.interaction_text_rect["多行"],pattern="[拾取]+")
            if res:
                break
            self.walk_to_w(300)
            self.sleep(1)
        
        if res:
            print("拾取-烟津渡")
            self.click(res[0].x,res[0].y,after_sleep=3)

        self.go_home()
        print("领取玩具气锤完成")

    def task_get_daily_award(self):
        # 领取每日历练奖励
        print("开始领取每日历练奖励")
        self.click_color_to_color(common_color,"角色血条-绿色",common_color,"主界面菜单展示",x=38,y=30)
        self.sleep(1)
        self.click_color_to_color(common_color,"主界面菜单展示",common_color,"左上角红色退出",x=124,y=442)
        self.sleep(3)

        self.click(46,116,after_sleep=2)
        self.click(1124,100,after_sleep=3)
        # 全部领取
        self.click(1114,649,after_sleep=3)
        self.click(626,687,after_sleep=3)
        self.click(626,687,after_sleep=3)

        # 领取奖励
        self.click(604,186,after_sleep=3)
        self.click(945,182,after_sleep=3)
        self.click(626,687,after_sleep=3)

        # 返回
        self.click(44,31,after_sleep=3)

        for i in range(3):
            self.click(634,666)

        res = self.find_my_color(common_color,"角色血条-绿色")
        if res:
            print("成功返回主界面")
            print("领取每日历练奖励完成")
        else:
            print("返回主界面失败")

    def run(self):
        self.init_level()
        self.refresh_log()

        for self.now_task in self.task_list:
            print(f"开始执行---{self.now_task}")
            self.refresh_log()

            if self.now_task == "夜航手册":
                self.task_mod()
            elif self.now_task == "拍照":
                self.task_take_a_picture()
            elif self.now_task == "领取鱼饵":
                self.task_get_fishing_lure()
            elif self.now_task == "领取玩具气锤":
                self.task_get_wjqc()
            elif self.now_task == "领取每日历练奖励":
                self.task_get_daily_award()