from ascript.android.ui import WebWindow

from ...res.config import VERSION, ui_resource


import time

def a():
    ui.call()
    

class LogUi:
    _instance = None
    _is_initialized = False # 增加一个标记，防止重复初始化

    def __new__(cls, *args, **kwargs):
        # 如果实例还不存在，就创建一个新的
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        # 如果已存在，直接返回该实例
        return cls._instance

    def __init__(self):
        # 确保只初始化一次 UI (init 每次实例化都会被调用，所以要加锁)
        if not self._is_initialized:
            self.init_show()
            self._is_initialized = True

    def init_show(self):
        self.logui = WebWindow(ui_resource("log.html"))
        self.logui.size(1280,30)
        self.logui.mode(2)
        self.logui.gravity(80|1)
        self.logui.background("#00000000")
        self.logui.dim_amount(0)
        self.logui.show()
        time.sleep(1)
        self.logui.call(f"setVersion('v{VERSION}')")
        print("日志初始化展示完成")

    def change_log_text(self,text):
        if self.logui:
            self.logui.call(f"updateFooter('{text}')")

class MosaicUI:
    # 打码区域
    _instance = None
    _is_initialized = False # 增加一个标记，防止重复初始化

    def __new__(cls, *args, **kwargs):
        # 如果实例还不存在，就创建一个新的
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        # 如果已存在，直接返回该实例
        return cls._instance

    def __init__(self):
        # 确保只初始化一次 UI (init 每次实例化都会被调用，所以要加锁)
        if not self._is_initialized:
            self.init_show()
            self._is_initialized = True

    def init_show(self):
        self.logui = WebWindow(ui_resource("mosaic.html"))
        self.logui.size(110,20)
        self.logui.mode(2)
        self.logui.gravity(80|3)
        self.logui.background("#000000")
        self.logui.dim_amount(0)
        self.logui.show()
        print("日志初始化展示完成")

