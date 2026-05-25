from ascript.android import action
from ascript.android.action import Path
from ...res.task.BaseGame import BaseGame

import random
import time


class BaseAction(BaseGame):
    def __init__(self):
        super().__init__()

    def click(self, x, y, dur=20, random_range=2, after_sleep=1):
        # 点击
        click_x = random.randint(x - random_range, x + random_range)
        click_y = random.randint(y - random_range, y + random_range)

        action.click(x=click_x, y=click_y, dur=dur)
        self.sleep(after_sleep)

    def reset_role_view(self):
        # 重置角色视角
        action.slide(self.center_x, 100, self.center_x, 650, 1000)
        self.sleep(1)
        action.slide(self.center_x, 650, self.center_x, 550, 1000)
        self.sleep(1)

    def rotate_view_to_top(self, slide_distance, dur=1000, after_sleep=1):
        # 视角向上滑动
        start_y = 600
        y = start_y - slide_distance
        action.slide(self.center_x+150, start_y, self.center_x+150, y, dur=dur)
        self.sleep(after_sleep)

    def rotate_view_to_down(self, slide_distance, dur=1000, after_sleep=1):
        # 视角向下滑动
        start_y = 150
        y = start_y + slide_distance
        action.slide(self.center_x+150, start_y, self.center_x+150, y, dur=dur)
        self.sleep(after_sleep)

    def rotate_view_to_left(self, slide_distance, dur=1000, after_sleep=1):
        # 视角向左滑动
        start_x = self.center_x
        x = start_x - slide_distance
        action.slide(start_x, self.center_y-150, x, self.center_y-150, dur=dur)
        self.sleep(after_sleep)

    def rotate_view_to_right(self, slide_distance, dur=1000, after_sleep=1):
        # 视角向右滑动
        start_x = self.center_x
        x = start_x + slide_distance
        action.slide(start_x, self.center_y-150, x, self.center_y-150, dur=dur)
        self.sleep(after_sleep)

    def walk_to_w(self, walk_time=1000):
        # 向前走
        x = self.walk_button_center_x
        y = self.walk_button_center_y - 100
        action.slide(
            self.walk_button_center_x, self.walk_button_center_y, x, y, dur=walk_time
        )

    def walk_to_s(self, walk_time=1000):
        # 向后走
        x = self.walk_button_center_x
        y = self.walk_button_center_y + 100
        action.slide(
            self.walk_button_center_x, self.walk_button_center_y, x, y, dur=walk_time
        )

    def walk_to_a(self, walk_time=1000):
        # 向左走
        x = self.walk_button_center_x - 100
        y = self.walk_button_center_y
        action.slide(
            self.walk_button_center_x, self.walk_button_center_y, x, y, dur=walk_time
        )

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

    def walk_to_d(self, walk_time=1000):
        # 向右走
        x = self.walk_button_center_x + 100
        y = self.walk_button_center_y
        action.slide(
            self.walk_button_center_x, self.walk_button_center_y, x, y, dur=walk_time
        )

    def jump(self,after_sleep=1000):
        x = self.action_button_position["跳跃"][0]
        y = self.action_button_position["跳跃"][1]
        self.click(x, y, after_sleep=after_sleep)

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

    def skill_e(self, dur=20, after_sleep=1):
        # 小技能
        x = self.action_button_position["小技能"][0]
        y = self.action_button_position["小技能"][1]
        self.click(x, y, dur=dur, after_sleep=after_sleep)
        self.skill_time['小技能_释放时间'] = time.time()
    
    def skill_e_and_w(self, after_sleep=1):
        # 向前释放e技能
        line1 = Path(0,500)
        line1.moveTo(self.walk_button_center_x,self.walk_button_center_y) 
        line1.lineTo(self.walk_button_center_x,self.walk_button_center_y - 100)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        x = self.action_button_position["小技能"][0]
        y = self.action_button_position["小技能"][1]
        line2 = Path(300,50)
        line2.moveTo(x,y) 
        line2.lineTo(x+1,y+1)
        
        action.gesture([line1,line2])
        self.sleep(500/1000)

    def skill_e_saiqi_0(self,combat_left_time=500):
        # 赛琪e技能（e+平a+飞天）
        x1 = self.action_button_position["近战攻击"][0]
        y1 = self.action_button_position["近战攻击"][1]
        line1 = Path(0,combat_left_time)
        line1.moveTo(x1,y1) 
        line1.lineTo(x1+1,y1+1)

        x2 = self.action_button_position["跳跃"][0]
        y2 = self.action_button_position["跳跃"][1]
        line2 = Path(0,500)
        line2.moveTo(x2,y2)
        line2.lineTo(x2+1,y2+1)

        # 创建另一个新的path路径 模拟 手指2(*第二条路径相对于第一条,会延迟500ms启动)
        x3 = self.action_button_position["小技能"][0]
        y3 = self.action_button_position["小技能"][1]
        line3 = Path(300,50)
        line3.moveTo(x3,y3) 
        line3.lineTo(x3+1,y3+1)

        # x4 = self.center_x
        # y4 = self.center_y
        # line4 = Path(100,400)
        # line4.moveTo(x4,y4) 
        # line4.lineTo(x4,y4+100)
        
        action.gesture([line1,line2,line3])
        self.sleep(combat_left_time/1000)

    def skill_e_saiqi_1(self):
        # 赛琪原地e技能
        x1 = self.action_button_position["下蹲"][0]
        y1 = self.action_button_position["下蹲"][1]
        line1 = Path(0,400)
        line1.moveTo(x1,y1)
        line1.lineTo(x1+1,y1+1)

        x2 = self.action_button_position["小技能"][0]
        y2 = self.action_button_position["小技能"][1]
        line2 = Path(100,300)
        line2.moveTo(x2,y2) 
        line2.lineTo(x2+1,y2+1)
        
        action.gesture([line1,line2])
        self.sleep(0.5)

    def skill_e_suyi_0(self):
        # 苏已边走边a
        x1 = self.walk_button_center_x
        y1 = self.walk_button_center_y
        line1 = Path(0,500)
        line1.moveTo(self.walk_button_center_x - 100,self.walk_button_center_y)
        line1.lineTo(x1+1,y1+1)

        x2 = self.action_button_position["近战攻击"][0]
        y2 = self.action_button_position["近战攻击"][1]
        line2 = Path(200,20)
        line2.moveTo(x2,y2) 
        line2.lineTo(x2+1,y2+1)
        
        action.gesture([line1,line2])
        self.sleep(0.5)

    def skill_e_yuming_0(self):
        # 煜明技能
        x1 = self.center_x
        y1 = self.center_y-250
        line1 = Path(0,200)
        line1.moveTo(x1,y1)
        line1.lineTo(x1-50,y1)

        x2 = self.action_button_position["近战攻击"][0]
        y2 = self.action_button_position["近战攻击"][1]
        line2 = Path(100,20)
        line2.moveTo(x2,y2) 
        line2.lineTo(x2+1,y2+1)
        
        action.gesture([line1,line2])
        self.sleep(0.2)

    def skill_q(self, after_sleep=1):
        # 大招
        x = self.action_button_position["大招"][0]
        y = self.action_button_position["大招"][1]
        self.click(x, y, after_sleep=after_sleep)
        self.skill_time['大招_释放时间'] = time.time()

    def skill_z(self,after_sleep=1):
        # 魔灵技
        x = self.action_button_position["魔灵技"][0]
        y = self.action_button_position["魔灵技"][1]
        self.click(x, y, after_sleep=after_sleep)
        self.skill_time['魔灵技_释放时间'] = time.time()

    def combat_left_click(self,dur=20):
        # 近战攻击
        x = self.action_button_position["近战攻击"][0]
        y = self.action_button_position["近战攻击"][1]
        self.click(x, y, dur=dur, after_sleep=0.1)

    def combat_right_click(self):
        # 远程攻击
        x = self.action_button_position["远程攻击"][0]
        y = self.action_button_position["远程攻击"][1]
        self.click(x, y, after_sleep=0.1)

    def combat_bullet(self):
        # 换弹
        x = self.action_button_position["换弹"][0]
        y = self.action_button_position["换弹"][1]
        self.click(x, y, after_sleep=0.1)

    def action_click_dodge(self):
        # 点击闪避
        x = self.action_button_position["闪避"][0]
        y = self.action_button_position["闪避"][1]
        self.click(x, y, after_sleep=0.1)

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

    def action_jump_fly(self,after_time=1):
        # 螺旋飞跃
        x = self.action_button_position["跳跃"][0]
        y = self.action_button_position["跳跃"][1]
        action.slide(x, y, x, y - 100, dur=200)
        self.sleep(after_time)

    def lock_enemy(self):
        # 锁定敌人
        x = self.action_button_position["锁敌"][0]
        y = self.action_button_position["锁敌"][1]
        self.click(x, y, after_sleep=0.1)
    
    def action_crouch(self):
        # 下蹲
        x = self.action_button_position["下蹲"][0]
        y = self.action_button_position["下蹲"][1]
        self.click(x, y, after_sleep=0.1)

    def slide(self,x,y,x1,y1,dur=20):
        # 滑动
        action.slide(x=x,y=y,x1=x1,y1=y1,dur=dur)

    def fly_spear(self):
        # 飞枪
        x = self.action_button_position["近战攻击"][0]
        y = self.action_button_position["近战攻击"][1]
        self.click(x, y, dur = 500,after_sleep=0.1)
