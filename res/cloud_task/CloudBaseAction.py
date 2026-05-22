from ascript.android import action
from ascript.android.action import Path
from ...res.task.BaseGame import BaseGame

import random

class CloudBaseAction(BaseGame):
    # 云游戏动作

    def __init__(self):
        super().__init__()

    def click(self, x, y, dur=20, random_range=2, after_sleep=1):
        # 点击
        click_x = random.randint(x - random_range, x + random_range)
        click_y = random.randint(y - random_range, y + random_range)

        action.click(x=click_x, y=click_y, dur=dur)
        self.sleep(after_sleep)

    def slide(self,x,y,x1,y1,dur=20,after_sleep=1):
        # 滑动
        action.slide(x=x,y=y,x1=x1,y1=y1,dur=dur)
        self.sleep(after_sleep)

    def rotate_view_to_top(self, slide_distance, dur=1000, after_sleep=1):
        # 视角向上滑动
        y = self.center_y - slide_distance
        self.slide(self.center_x+60, self.center_y, self.center_x+60, y, dur=dur, after_sleep=after_sleep)

    def rotate_view_to_down(self, slide_distance, dur=1000, after_sleep=1):
        # 视角向下滑动
        y = self.center_y + slide_distance
        self.slide(self.center_x+60, self.center_y, self.center_x+60, y, dur=dur, after_sleep=after_sleep)

    def rotate_view_to_left(self, slide_distance, dur=1000, after_sleep=1):
        # 视角向左滑动
        x = self.center_x+60 - slide_distance
        self.slide(self.center_x+60, self.center_y, x, self.center_y, dur=dur, after_sleep=after_sleep)

    def rotate_view_to_right(self, slide_distance, dur=1000, after_sleep=1):
        # 视角向右滑动
        x = self.center_x+60 + slide_distance
        self.slide(self.center_x+60, self.center_y, x, self.center_y, dur=dur, after_sleep=after_sleep)

    def walk_to_w(self, walk_time=1000, after_sleep=1):
        # 向前走
        x = self.cloud_walk_button_center_x
        y = self.cloud_walk_button_center_y - 100
        self.slide(self.cloud_walk_button_center_x, self.cloud_walk_button_center_y, x, y, dur=walk_time, after_sleep=after_sleep)

    def walk_to_w_new(self, walk_time=1000, after_sleep=1):
        # 向前冲刺
        line1 = Path(0,walk_time)
        x1 = self.cloud_walk_button_center_x
        y1 = self.cloud_walk_button_center_y
        line1.moveTo(x1,y1) 
        line1.lineTo(x1,y1 - 100)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(500,walk_time)
        line2.moveTo(self.action_button_position["闪避"][0],self.action_button_position["闪避"][1]) 
        line2.lineTo(self.action_button_position["闪避"][0] +10,self.action_button_position["闪避"][1]+10)
        
        action.gesture([line1,line2])
        self.sleep(walk_time/1000)

    def walk_to_s(self, walk_time=1000, after_sleep=1):
        # 向后走
        x = self.cloud_walk_button_center_x
        y = self.cloud_walk_button_center_y + 100
        self.slide(self.cloud_walk_button_center_x, self.cloud_walk_button_center_y, x, y, dur=walk_time, after_sleep=after_sleep)

    def walk_to_a(self, walk_time=1000, after_sleep=1):
        # 向左走
        x = self.cloud_walk_button_center_x - 100
        y = self.cloud_walk_button_center_y
        self.slide(self.cloud_walk_button_center_x, self.cloud_walk_button_center_y, x, y, dur=walk_time, after_sleep=after_sleep)

    def walk_to_d(self, walk_time=1000, after_sleep=1):
        # 向右走
        x = self.cloud_walk_button_center_x + 100
        y = self.cloud_walk_button_center_y
        self.slide(self.cloud_walk_button_center_x, self.cloud_walk_button_center_y, x, y, dur=walk_time, after_sleep=after_sleep)

    def skill_e(self, dur=20, after_sleep=1):
        # 小技能
        x = self.cloud_action_button_position["小技能"][0]
        y = self.cloud_action_button_position["小技能"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def skill_q(self, after_sleep=1):
        # 大招
        x = self.cloud_action_button_position["大招"][0]
        y = self.cloud_action_button_position["大招"][1]
        self.click(x, y, after_sleep=after_sleep)

    def skill_z(self,after_sleep=1):
        # 魔灵技
        x = self.cloud_action_button_position["魔灵技"][0]
        y = self.cloud_action_button_position["魔灵技"][1]
        self.click(x, y, after_sleep=after_sleep)

    def combat_left_click(self,dur=20,after_sleep=0.1):
        # 近战攻击
        x = self.cloud_action_button_position["近战攻击"][0]
        y = self.cloud_action_button_position["近战攻击"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def combat_right_click(self,dur=20,after_sleep=0.1):
        # 远程攻击
        x = self.cloud_action_button_position["远程攻击"][0]
        y = self.cloud_action_button_position["远程攻击"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def combat_bullet(self,dur=20,after_sleep=0.1):
        # 换弹
        x = self.cloud_action_button_position["换弹"][0]
        y = self.cloud_action_button_position["换弹"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def action_click_dodge(self,dur=20,after_sleep=0.1):
        # 点击闪避
        x = self.cloud_action_button_position["闪避"][0]
        y = self.cloud_action_button_position["闪避"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def lock_enemy(self,dur=20,after_sleep=0.1):
        # 锁定敌人
        x = self.cloud_action_button_position["锁敌"][0]
        y = self.cloud_action_button_position["锁敌"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def action_crouch(self,dur=20,after_sleep=0.1):
        # 下蹲
        x = self.cloud_action_button_position["下蹲"][0]
        y = self.cloud_action_button_position["下蹲"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def action_click_walk(self,dur=20,after_sleep=0.1):
        # 行走
        x = self.cloud_action_button_position["行走"][0]
        y = self.cloud_action_button_position["行走"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def jump(self,dur=20,after_sleep=0.1):
        x = self.cloud_action_button_position["跳跃"][0]
        y = self.cloud_action_button_position["跳跃"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def click_fly(self,dur=20,after_sleep=1):
        # 点击副本内的飞索
        x = 946
        y = 296
        self.click(x, y, dur=dur, after_sleep=after_sleep)

    def action_jump_fly(self,after_time=1):
        # 螺旋飞跃
        x = self.cloud_action_button_position["跳跃"][0]
        y = self.cloud_action_button_position["跳跃"][1]
        self.slide(x, y, x, y - 100, dur=200, after_sleep=after_sleep)

    def fly_spear(self,dur=300,after_sleep=0.3,count=1):
        # 飞枪
        for i in range(count):
            self.combat_left_click(dur=dur,after_sleep=after_sleep)

    def walk_shift_to_w(self,walk_time=1000):
        # 向前冲刺
        line1 = Path(0,walk_time)
        line1.moveTo(self.walk_button_center_x,self.walk_button_center_y) 
        line1.lineTo(self.walk_button_center_x,self.walk_button_center_y - 100)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(500,walk_time)
        line2.moveTo(self.action_button_position["闪避"][0],self.action_button_position["闪避"][1]) 
        line2.lineTo(self.action_button_position["闪避"][0] +10,self.action_button_position["闪避"][1]+10)
        
        action.gesture([line1,line2])
        self.sleep(walk_time/1000)

    def walk_shift_to_a(self,walk_time=1000):
        # 向左冲刺
        line1 = Path(0,walk_time)
        line1.moveTo(self.walk_button_center_x,self.walk_button_center_y) 
        line1.lineTo(self.walk_button_center_x - 100,self.walk_button_center_y)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(500,walk_time)
        line2.moveTo(self.action_button_position["闪避"][0],self.action_button_position["闪避"][1]) 
        line2.lineTo(self.action_button_position["闪避"][0] +10,self.action_button_position["闪避"][1]+10)
        
        action.gesture([line1,line2])
        self.sleep(walk_time/1000)

    def action_test(self,walk_time=1000):
        # 向左冲刺
        line1 = Path(0,walk_time)
        x = self.action_button_position["下蹲"][0]
        y = self.action_button_position["下蹲"][1]
        line1.moveTo(x,y) 
        line1.lineTo(x,y+1)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(500,walk_time)
        line2.moveTo(self.action_button_position["小技能"][0],self.action_button_position["小技能"][1]) 
        line2.lineTo(self.action_button_position["小技能"][0] +1,self.action_button_position["小技能"][1])
        
        action.gesture([line1,line2])
        self.sleep(walk_time/1000)

    def walk_shift_to_d(self,walk_time=1000):
        # 向右冲刺
        line1 = Path(0,walk_time)
        line1.moveTo(self.walk_button_center_x,self.walk_button_center_y) 
        line1.lineTo(self.walk_button_center_x + 100,self.walk_button_center_y)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(500,walk_time)
        line2.moveTo(self.action_button_position["闪避"][0],self.action_button_position["闪避"][1]) 
        line2.lineTo(self.action_button_position["闪避"][0] +10,self.action_button_position["闪避"][1]+10)
        
        action.gesture([line1,line2])
        self.sleep(walk_time/1000)

    def w_and_jupm(self,walk_time=500):
        # 向前跳跃
        line1 = Path(0,walk_time)
        line1.moveTo(self.walk_button_center_x,self.walk_button_center_y) 
        line1.lineTo(self.walk_button_center_x,self.walk_button_center_y - 100)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(300,50)
        line2.moveTo(self.action_button_position["跳跃"][0],self.action_button_position["跳跃"][1]) 
        line2.lineTo(self.action_button_position["跳跃"][0] +10,self.action_button_position["跳跃"][1]+10)
        
        action.gesture([line1,line2])
        self.sleep(walk_time/1000)
    
    def d_and_jupm(self,walk_time=500):
        # 向右跳跃
        line1 = Path(0,walk_time)
        line1.moveTo(self.walk_button_center_x,self.walk_button_center_y) 
        line1.lineTo(self.walk_button_center_x + 100,self.walk_button_center_y)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(300,50)
        line2.moveTo(self.action_button_position["跳跃"][0],self.action_button_position["跳跃"][1]) 
        line2.lineTo(self.action_button_position["跳跃"][0] +10,self.action_button_position["跳跃"][1]+10)
        
        action.gesture([line1,line2])
        self.sleep(walk_time/1000)

    def action_dodge_to_w(self):
        # 向前闪避
        line1 = Path(0,500)
        line1.moveTo(self.walk_button_center_x,self.walk_button_center_y) 
        line1.lineTo(self.walk_button_center_x,self.walk_button_center_y - 100)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(250,100)
        line2.moveTo(self.action_button_position["闪避"][0],self.action_button_position["闪避"][1]) 
        line2.lineTo(self.action_button_position["闪避"][0] +10,self.action_button_position["闪避"][1]+10)

        action.gesture([line1,line2])

    def action_dodge_to_s(self):
        # 向后闪避
        line1 = Path(0,500)
        line1.moveTo(self.walk_button_center_x,self.walk_button_center_y) 
        line1.lineTo(self.walk_button_center_x,self.walk_button_center_y + 100)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        line2 = Path(250,100)
        line2.moveTo(self.action_button_position["闪避"][0],self.action_button_position["闪避"][1]) 
        line2.lineTo(self.action_button_position["闪避"][0] +10,self.action_button_position["闪避"][1]+10)

        action.gesture([line1,line2])


    # 下面是技能搓招
    def skill_e_saiqi_1(self):
        # 赛琪原地e技能
        x1 = self.cloud_action_button_position["下蹲"][0]
        y1 = self.cloud_action_button_position["下蹲"][1]
        line1 = Path(0, 400)
        line1.moveTo(x1, y1)
        line1.lineTo(x1 + 1, y1 + 1)

        x2 = self.cloud_action_button_position["小技能"][0]
        y2 = self.cloud_action_button_position["小技能"][1]
        line2 = Path(100, 300)
        line2.moveTo(x2, y2)
        line2.lineTo(x2 + 1, y2 + 1)

        action.gesture([line1, line2])
        self.sleep(0.5)
