"""工程内置运行时与远程运行时共用的业务入口。"""

import json
import time

from ascript.android.system import KeyValue
from ascript.android.ui import WebWindow

from .res.config import VERSION, ui_resource
from .res.test.test1 import test11


form_window = None


def tunnel(key, value):
    print(key, value)
    if key == "close":
        print(value)
        return

    if key != "submit":
        return

    uiconfig = json.loads(value)
    print(uiconfig)
    print(uiconfig["mod_config_list"])

    # Python 入口必须保留同样的互斥校验，避免旧版 UI 缓存或外部调用绕过
    # form-main.js 中的前端校验后启动冲突任务。
    if uiconfig.get("refresh_time_is_execute_mihan") == "on":
        try:
            task_list = json.loads(uiconfig.get("task_list", "[]"))
        except Exception:
            task_list = []
        if any(
            item.get("type") == "mihan"
            for item in task_list
            if isinstance(item, dict)
        ):
            print(
                "配置冲突：任务列表已添加委托密函，"
                "不能同时开启整点刷新执行委托密函"
            )
            return

    test11(uiconfig)


def start():
    """显示配置界面，并全局持有窗口对象以防被提前回收。"""
    global form_window

    print("运行时来源：{}".format(__package__))
    print(KeyValue.get("asdata", ""))
    form_window = WebWindow(ui_resource("form.html"), tunnel)
    form_window.size("80vw", "70vh")
    form_window.show()
    time.sleep(1)
    form_window.call("setVersion('v{}')".format(VERSION))
