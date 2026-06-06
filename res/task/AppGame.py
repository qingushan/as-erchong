# 自定义
from ...res.assets.color import *
from ...res.task.BaseTask import BaseTask
from ...res.task.LogUi import LogUi,MosaicUI

# 本地游戏
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
from ...res.task.AutoDailyTaskTask import AutoDailyTaskTask

# 云游戏
from ...res.cloud_task.CloudAutoWeaponBreakTask import CloudAutoWeaponBreakTask
from ...res.cloud_task.CloudAutoRoleBreakthroughTask import CloudAutoRoleBreakthroughTask
from ...res.cloud_task.CloudAutoWeaponExpTask import CloudAutoWeaponExpTask
from ...res.cloud_task.CloudAutoGameActivityTask import CloudAutoGameActivityTask

# 测试
from ...res.task.AutoTestTask import AutoTestTask

# as
from ascript.android.system import Device
from airscript.intent import Intent 
from ascript.android.system import R
from android.net import Uri
from android.provider import Settings
from ascript.android import system
from ascript.android.ui import FloatWindow
from ascript.android import action

# python
from threading import Thread
import time
import json
import ctypes
import inspect
import datetime

class Context:
    def __init__(self):
        self.current_thread = None   # 当前正在运行的任务线程
        self.is_game_online = True   # 游戏是否在线
        self.was_interrupted = False # 标记：当前任务是否是因为掉线被强制中断的

class AppGame:
    def __init__(self,uiconfig=None):
        self.uiconfig = uiconfig
        self.ctx = Context()
        self.base_task = BaseTask()

        self.task_list = self.uiconfig['task_list']
        self.task_list = json.loads(self.task_list)
        print(f"任务列表:{self.task_list}")

        # 任务映射表
        self.task_mapping = {
            "daily_task": AutoDailyTaskTask,
            "mijin": AutoTestTask,
            "mod": AutoModTask,
            "jiaojiaobi": AutoJjbTask,
            "role_tupo": AutoRoleBreakthroughTask,
            "role_exp": AutoRoleExpTask,
            "mozhixie": AutoMozhixieTask,
            "wuqi_tupo": AutoWeaponBreakTask,
            "wuqi_exp": AutoWeaponExpTask,
            "husong": AutoHusongTask,
            "mihan": AutoWeituomihanTask,
            "fish": AutoFishTask,
            "cjsxj": AutoCJSXJTask,
            "game_activity": AutoGameActivityTask,
            "cloud_wuqi_tupo": CloudAutoWeaponBreakTask,
            "cloud_role_tupo": CloudAutoRoleBreakthroughTask,
            "cloud_wuqi_exp": CloudAutoWeaponExpTask,
            "cloud_game_activity": CloudAutoGameActivityTask
        }

        # 初始化悬浮窗位置
        self.init_window_postion()

        self.game_name = "二重螺旋"     # 游戏名
        self.pakage_name = "com.hero.dna.gf"    # 游戏包名
        # self.game_name_white_list = ['Quickstep']   # 进程白名单，识别到的时候不会触发重启检测
        self.game_name_white_list = []

        # 打码
        self.mosaic_ui = None

    def init_window_postion(self):
        # 初始化悬浮窗位置
        FloatWindow.show(x=0,y=720,dim=0.3)

    def check_screen(self):
        # 检测屏幕分辨率
        display = Device.display()
        print(f"当前屏幕分辨率：{display.widthPixels}*{display.heightPixels}")

        if (display.widthPixels == 1280 and display.heightPixels == 720) or (display.widthPixels == 720 and display.heightPixels == 1280):
            return True

        text = f"当前分辨率不是720*1280，请先修改分辨率后再启动脚本，当前分辨率：{display.widthPixels}*{display.heightPixels}"
        self.base_task.logui.change_log_text(text)
        return False

    def get_device_info(self):
        # 获取当前设备运行的APP信息
        device_info = Device.current_appinfo()
        print(f"名称：{device_info.name}")
        print(f"包名：{device_info.packageName}")
        print(f"Activity：{device_info.activity}")

        if device_info.name != "二重螺旋":
            text = f"当前前台应用不是二重螺旋，请先启动游戏后再启动脚本，当前前台应用：{device_info.name}"
            self.base_task.logui.change_log_text(text)
            return False
        
        self.game_name = device_info.name
        self.pakage_name = device_info.packageName
        return True

    def _async_raise(self, tid, exctype):
        """向指定线程ID抛出异常"""
        if not isinstance(tid, int):
            tid = tid.ident
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # 如果设置失败，清除状态
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        """强制结束一个线程"""
        if thread is None or not thread.is_alive():
            return
        try:
            self._async_raise(thread, SystemExit)
            print(f"线程 {thread.name} 已被强制发送停止信号")
        except Exception as e:
            print(f"停止线程失败: {e}")

    def game_is_offline(self):
        # 游戏是否掉线
        device_info = Device.current_appinfo()
        if device_info.name != self.game_name:
            print(f"当前前台应用：{device_info.name}")
            # 校验是否白名单
            if device_info.name in self.game_name_white_list:
                print("白名单，跳过检测")
                return False
            return True
        
        if self.base_task.is_text_re_in_ocr(rect=[407,312,872,440],pattern="连接失败"):
            print("游戏网络异常，准备重启游戏！！！")
            return True

        return False

    def close_game(self):
        # 停止游戏
        # 根据需求改变包名,即可跳转,跳转后,可点击停止程序等等.
        intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).setData(Uri.fromParts("package", self.pakage_name, None))
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        R.context.startActivity(intent)
        time.sleep(2)

        self.base_task.await_until_click_ocr(pattern="停止",time_out=20)
        time.sleep(1)
        self.base_task.await_until_click_ocr(pattern="确定",time_out=10)
        time.sleep(5)

        action.Key.back()   # 返回
        time.sleep(5)
    
    def open_game(self):
        # 启动游戏
        system.open(self.pakage_name)
        time.sleep(15)

        while True:
            res = self.base_task.find_my_color(common_color,"角色血条-绿色")
            if res:
                print("成功进入游戏----")
                time.sleep(3)
                return True
            
            res = self.base_task.find_my_color(app_color,"更新确定按钮")
            if res:
                self.base_task.click(640,410)
                time.sleep(1)

            # res = self.base_task.find_my_color(app_color,"公告红色关闭")
            # if res:
            #     self.base_task.click(1054,135)
            #     time.sleep(1)

            res = self.base_task.is_text_re_in_ocr(rect=[26,1,550,77], pattern="公告")
            if res:
                self.base_task.click(1236,33)
                time.sleep(1)
            
            self.base_task.click(630,620)
            time.sleep(3)

    def perform_reconnect(self):
        # 重连游戏
        print("开始重连游戏----")
        
        self.close_game()
        
        text = f"游戏异常闪退，等待五分钟后重启"
        self.base_task.logui.change_log_text(text)
        # self.base_task.sleep(60*5)
        self.base_task.sleep(10)

        self.open_game()

    def watchdog_logic(self):
        #  检测线程
        print("检测线程启动-----")
        while True:
            # 检测掉线
            if self.uiconfig["global_check_game_is_offline"] == "on":
                detected_offline = self.game_is_offline()
                if detected_offline and self.ctx.is_game_online:
                    print("【监控】检测到掉线！准备强杀任务线程...")
                    
                    # 1. 标记状态：这是异常中断
                    self.ctx.is_game_online = False
                    self.ctx.was_interrupted = True 
                    
                    # === 核心：强杀任务线程 ===
                    if self.ctx.current_thread and self.ctx.current_thread.is_alive():
                        self.stop_thread(self.ctx.current_thread)
                        self.ctx.current_thread.join() # 等待线程彻底死透
                        print("【监控】任务线程已终止。")
                    
                    # === 执行重连 ===
                    print("【监控】开始执行重连流程...")
                    self.perform_reconnect()
                    
                    print("【监控】重连成功，通知主流程继续。")
                    self.ctx.is_game_online = True

            # 检测签到页面
            self.check_day_signin()

            # 检测小月卡
            if self.uiconfig["global_check_month_card"] == "on":
                self.check_month_card()

            # 定时下线
            if self.uiconfig["global_timed_offline"] == "on":
                self.timed_offline_detection()

            # 每日五点十分退游戏
            if self.uiconfig["global_time_5_offline"] == "on":
                t = datetime.datetime.now().time()
                if (t.hour == 5) and (t.minute == 10):
                    action.Key.home()

            time.sleep(2)

    def run_task_wrapper(self, task_class):
        """
        这个函数会在单独的线程中运行。
        当收到 stop_thread 信号时，会抛出 SystemExit 异常自动退出。
        """
        try:
            task = task_class(self.uiconfig)
            task.run() # 这里可以是死循环，不需要任何修改
        except SystemExit:
            print("【任务】任务被强制中断！")
        except Exception as e:
            print(f"【任务】运行出错: {e}")

    def check_month_card(self):
        # 小月卡弹窗检测
        t = datetime.datetime.now()
        if (t.hour == 5) or (t.hour==4 and t.minute == 59):
            if self.base_task.find_my_color(common_color,"小月卡弹窗"):
                print("小月卡弹窗")
                self.base_task.click(167,627)

    def check_day_signin(self):
        # 每日签到
        t = datetime.datetime.now()
        if (t.hour == 5) or (t.hour==4 and t.minute == 59):
            if self.base_task.find_my_color(common_color,"签到界面"):
                print("签到界面")
                self.base_task.click(1126,150)
    
    def timed_offline_detection(self):
        # 定时下线检测
        tiem_ = self.uiconfig["global_timed_offline_value"]
        timed_offline_time = datetime.datetime.strptime(tiem_, "%H:%M:%S").time()
        t = datetime.datetime.now().time()
        if t >= timed_offline_time:
            print("满足下线时间")
            # 停止当前执行的任务
            self.ctx.is_game_online = False
            if self.ctx.current_thread and self.ctx.current_thread.is_alive():
                self.stop_thread(self.ctx.current_thread)
                self.ctx.current_thread.join() # 等待线程彻底死透
                print("【监控】任务线程已终止。")

            self.close_game()
            action.Key.home()
            time.sleep(2)
            system.exit()   # 停止脚本

    def is_do_mosaic(self):
        # 是否打码
        if self.uiconfig['global_do_mosaic'] == "on":
            self.mosaic_ui = MosaicUI()

    def run(self):
        # 判断是否打码
        self.is_do_mosaic()

        # 启动监控
        time.sleep(2)

        res = self.check_screen()
        if not res:
            return False

        if self.uiconfig["global_check_game_is_offline"] == "on":
            res = self.get_device_info()
            if not res:
                return False

        if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
            # 初始化是否执行密函信息
            self.base_task.init_is_execute_mihan_info()

        Thread(target=self.watchdog_logic, name="Watchdog").start()

        if self.uiconfig['task_loop'] == "on":
            # 循环任务
            while True:
                for task_info in self.task_list:
                    task_type = task_info['type']
                    if task_type not in self.task_mapping:
                        continue

                    print(f"--- 准备执行任务: {task_type} ---")

                    while True:
                        # 等待游戏在线状态
                        while not self.ctx.is_game_online:
                            time.sleep(1)
                        
                        if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                            # 判断是否需要执行委托密函
                            is_execute_mihan = self.base_task.get_is_execute_mihan()
                            if is_execute_mihan == "执行":
                                print("整点刷新，开始执行委托密函")
                                # 清除中断标记，准备开始新的一次尝试
                                self.ctx.was_interrupted = False
                                
                                # 创建并启动任务线程
                                self.ctx.current_thread = Thread(
                                    target=self.run_task_wrapper, 
                                    args=(AutoWeituomihanTask,),
                                    name=f"Task-{task_type}"
                                )

                                self.ctx.current_thread.start()

                                # 更新执行委托密函时间
                                now_hour = self.base_task.get_time_hour()
                                self.base_task.set_is_execute_mihan_time(str(now_hour))

                                self.ctx.current_thread.join()

                                # 设置是否执行委托密函为不执行
                                self.base_task.set_is_execute_mihan_false()

                                if self.ctx.was_interrupted:
                                    print(f"【整点刷新任务】任务 委托密函 因掉线被中断")
                                    time.sleep(2)
                                else:
                                    print(f"【整点刷新任务】任务 委托密函 正常完成。")

                        # 等待游戏在线状态
                        while not self.ctx.is_game_online:
                            time.sleep(1)

                        print(f"【主调度】启动任务: {task_type}")

                        # 清除中断标记，准备开始新的一次尝试
                        self.ctx.was_interrupted = False
                        
                        # 创建并启动任务线程
                        self.ctx.current_thread = Thread(
                            target=self.run_task_wrapper, 
                            args=(self.task_mapping[task_type],),
                            name=f"Task-{task_type}"
                        )
                        self.ctx.current_thread.start()

                        if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                            # 设置是否执行委托密函为不执行
                            self.base_task.set_is_execute_mihan_false()

                        # 主线程阻塞等待任务结束
                        # 任务结束有两种情况：
                        # A. 正常跑完 -> join结束
                        # B. 被Watchdog杀掉 -> join结束
                        self.ctx.current_thread.join()

                        # 判断是否整点执行委托密函
                        if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                            is_execute_mihan = self.base_task.get_is_execute_mihan()
                            if is_execute_mihan == "执行":
                                time.sleep(2)
                                continue

                        if self.ctx.was_interrupted:
                            print(f"【主调度】任务 {task_type} 因掉线被中断，准备重新执行...")
                            # 这里不 break，continue 会导致重新执行 `while True` 的开头
                            # 从而重新实例化并运行该任务
                            time.sleep(2) # 给一点缓冲时间
                            continue
                        else:
                            print(f"【主调度】任务 {task_type} 正常完成。")
                            break # 跳出 `while True`，继续 `for` 循环的下一个任务
        elif self.uiconfig['task_loop'] == "off":
            # 无需循环
            for task_info in self.task_list:
                task_type = task_info['type']
                if task_type not in self.task_mapping:
                    continue

                print(f"--- 准备执行任务: {task_type} ---")

                while True:
                    # 等待游戏在线状态
                    while not self.ctx.is_game_online:
                        time.sleep(1)

                    if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                        # 判断是否需要执行委托密函
                        is_execute_mihan = self.base_task.get_is_execute_mihan()
                        if is_execute_mihan == "执行":
                            print("整点刷新，开始执行委托密函")
                            # 清除中断标记，准备开始新的一次尝试
                            self.ctx.was_interrupted = False
                            
                            # 创建并启动任务线程
                            self.ctx.current_thread = Thread(
                                target=self.run_task_wrapper, 
                                args=(AutoWeituomihanTask,),
                                name=f"Task-{task_type}"
                            )

                            self.ctx.current_thread.start()

                            # 更新执行委托密函时间
                            now_hour = self.base_task.get_time_hour()
                            self.base_task.set_is_execute_mihan_time(str(now_hour))

                            self.ctx.current_thread.join()

                            # 设置是否执行委托密函为不执行
                            self.base_task.set_is_execute_mihan_false()

                            if self.ctx.was_interrupted:
                                print(f"【整点刷新任务】任务 委托密函 因掉线被中断")
                                time.sleep(2)
                            else:
                                print(f"【整点刷新任务】任务 委托密函 正常完成。")
                    
                    # 等待游戏在线状态
                    while not self.ctx.is_game_online:
                        time.sleep(1)

                    print(f"【主调度】启动任务: {task_type}")

                    # 清除中断标记，准备开始新的一次尝试
                    self.ctx.was_interrupted = False
                    
                    # 创建并启动任务线程
                    self.ctx.current_thread = Thread(
                        target=self.run_task_wrapper, 
                        args=(self.task_mapping[task_type],),
                        name=f"Task-{task_type}"
                    )
                    self.ctx.current_thread.start()

                    if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                        # 设置是否执行委托密函为不执行
                        self.base_task.set_is_execute_mihan_false()


                    # 主线程阻塞等待任务结束
                    # 任务结束有两种情况：
                    # A. 正常跑完 -> join结束
                    # B. 被Watchdog杀掉 -> join结束
                    self.ctx.current_thread.join()

                    # 判断是否整点执行委托密函
                    if self.uiconfig['refresh_time_is_execute_mihan'] == 'on':
                        is_execute_mihan = self.base_task.get_is_execute_mihan()
                        if is_execute_mihan == "执行":
                            time.sleep(2)
                            continue

                    if self.ctx.was_interrupted:
                        print(f"【主调度】任务 {task_type} 因掉线被中断，准备重新执行...")
                        # 这里不 break，continue 会导致重新执行 `while True` 的开头
                        # 从而重新实例化并运行该任务
                        time.sleep(2) # 给一点缓冲时间
                        continue 
                    else:
                        print(f"【主调度】任务 {task_type} 正常完成。")
                        break # 跳出 `while True`，继续 `for` 循环的下一个任务