from ascript.android.screen.gp import run
from ascript.android.screen import Ocr
from ascript.android import action
from ascript.android.screen import Colors
from ascript.android.system import Device

from airscript.intent import Intent 
from ascript.android.system import R
from android.net import Uri
from android.provider import Settings
from ascript.android import system
from ascript.android.screen import FindColors


from ...res.assets.color import *
from ...res.task.AppGame import AppGame
from ...res.task.BaseTask import BaseTask
from ...res.task.AutoMijinTask import AutoMijinTask
from ...res.task.AutoModTask import AutoModTask
from ...res.task.AutoHusongTask import AutoHusongTask
from ...res.task.AutoJjbTask import AutoJjbTask
from ...res.task.AutoRoleBreakthroughTask import AutoRoleBreakthroughTask
from ...res.task.AutoWeituomihanTask import AutoWeituomihanTask
from ...res.task.AutoFishTask import AutoFishTask
from ...res.task.AutoCJSXJTask import AutoCJSXJTask
from ...res.task.AutoRoleExpTask import AutoRoleExpTask
from ...res.task.AutoMozhixieTask import AutoMozhixieTask
from ...res.task.AutoWeaponBreakTask import AutoWeaponBreakTask
from ...res.task.AutoWeaponExpTask import AutoWeaponExpTask
from ...res.task.AutoGameActivityTask import AutoGameActivityTask
from ...res.task.AutoTestTask import AutoTestTask
from ...res.task.AutoDailyTaskTask import AutoDailyTaskTask

# 云游戏
from ...res.assets.cloud_color import *
from ...res.cloud_task.CloudAutoWeaponBreakTask import CloudAutoWeaponBreakTask
from ...res.cloud_task.CloudAutoRoleBreakthroughTask import CloudAutoRoleBreakthroughTask
from ...res.cloud_task.CloudAutoWeaponExpTask import CloudAutoWeaponExpTask
from ...res.cloud_task.CloudAutoGameActivityTask import CloudAutoGameActivityTask
from ...res.cloud_task.CloudAutoFindPropWorldTask import CloudAutoFindPropWorldTask


import time
import threading
from threading import Thread
import json
import ctypes
import inspect


def test11(uiconfig):
    time.sleep(2)
    # 迷津
    # task = AutoMijinTask(uiconfig)
    # task.sleep(1)
    # task.run()

    # 夜航手册
    # task = AutoModTask(uiconfig)
    # task.run()
    # task.go_to_activate_level_50()
    # res = task.find_my_color(common_color,'任务黄色图标')
    # print(res)

    # 护送
    # task = AutoHusongTask(uiconfig)
    # task.run()
    # task.leave_level_70()

    # 角色突破
    # task = AutoRoleBreakthroughTask(uiconfig)
    # task.go_to_capture_moling()

    # 皎皎币
    # task = AutoJjbTask(uiconfig)
    # task.go_to_activate_level_50()
    # task.go_to_activate_level_50_A()

    # 委托密函
    # task = AutoWeituomihanTask(uiconfig)
    # task.run()
    # task.quit_level()

    # 钓鱼
    # task = AutoFishTask(uiconfig)
    # task.run()

    # 沉浸式戏剧
    # task = AutoCJSXJTask(uiconfig)
    # task.run()
    # task.go_to_activate_level()

    # 角色经验
    # task = AutoRoleExpTask(uiconfig)
    # task.run()
    # task.leave_level_60()

    # 魔之楔
    # task = AutoMozhixieTask(uiconfig)
    # task.skill_e_is_ok()
    # task.slide(x,y,x+500,y,1000)

    # 武器突破
    # task = AutoWeaponBreakTask(uiconfig)
    # task.go_to_activate_level_70()

    # 武器经验
    # task = AutoWeaponExpTask(uiconfig)
    # task.go_to_level()
    # task.action_test()

    # 活动
    # task = AutoGameActivityTask(uiconfig)
    # task.level_qiju()
    # task.run()

    # 测试类
    # task = AutoTestTask(uiconfig)
    # task.skill_e(after_sleep=0.5)
    # task.skill_e_yuming_0()
    # task.run()
    # task.skill_e_test()

    # 日常任务
    # task = AutoDailyTaskTask(uiconfig)

    # 云-武器突破
    # task = CloudAutoWeaponBreakTask(uiconfig)
    # task.walk_to_w_new(walk_time=1000*5, after_sleep=0.1, ocr_text="[投喂魔灵]+", is_click_ocr=True)

    # 云-角色突破
    # task = CloudAutoRoleBreakthroughTask(uiconfig)
    # task.go_to_activate_level_10()
    # task.run()

    # 云-武器经验
    # task = CloudAutoWeaponExpTask(uiconfig)

    # 云-活动
    # task = CloudAutoGameActivityTask(uiconfig)
    # res = task.find_my_color(cloud_common_color, "角色血条-绿色")
    # print(res)
    # task.run()

    # 云-锄大地
    # task = CloudAutoFindPropWorldTask(uiconfig)
    # task.test()

    app_game = AppGame(uiconfig)
    app_game.run()