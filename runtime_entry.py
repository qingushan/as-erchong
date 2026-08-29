"""Application entry shared by the bundled and downloaded runtimes."""

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

    # Keep the Python-side guard because stale UI caches or external callers
    # can bypass the equivalent validation in form-main.js.
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
    """Show the configuration UI and retain its window globally."""
    global form_window

    print("运行时来源：{}".format(__package__))
    print(KeyValue.get("asdata", ""))
    form_window = WebWindow(ui_resource("form.html"), tunnel)
    form_window.size("80vw", "70vh")
    form_window.show()
    time.sleep(1)
    form_window.call("setVersion('v{}')".format(VERSION))
