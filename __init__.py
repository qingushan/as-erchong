# __init__.py 为初始入口文件,工程代码的入口文件.

# 导入动作库常用函数
from ascript.android.action import click,slide,Touch,gesture
# 导入控件检索相关
from ascript.android.node import Selector
# 导入图色相关
from ascript.android.screen import capture,FindColors,FindImages,Ocr
# 导入系统相关
from ascript.android import system
# 环境设备相关
from ascript.android.system import R,Device

from ascript.android.system import R
from ascript.android.ui import WebWindow
from ascript.android.ui import FloatWindow
from ascript.android.system import KeyValue

from .res.config import *
from .res.test.test1 import test11
from .res.test.cloud_test import cloud_test

import json
import time

def tunnel(k,v):
    print(k,v)
    if k =="close":
        print(v) # 用户点X关闭了窗口
    elif k =="submit":
        uiconfig = json.loads(v)
        print(uiconfig)
        print(uiconfig["mod_config_list"])
        # 防止旧缓存或外部调用绕过 UI：委托密函任务与整点刷新机制互斥。
        if uiconfig.get("refresh_time_is_execute_mihan") == "on":
            try:
                task_list = json.loads(uiconfig.get("task_list", "[]"))
            except Exception:
                task_list = []
            if any(item.get("type") == "mihan" for item in task_list if isinstance(item, dict)):
                print("配置冲突：任务列表已添加委托密函，不能同时开启整点刷新执行委托密函")
                return
        test11(uiconfig)
        # cloud_test(uiconfig)

# print(f"启动成功,当前版本：{VERSION}")
name = KeyValue.get('asdata','')
print(name)
formw =  WebWindow(R.ui("form.html"),tunnel)
formw.size("80vw","70vh")
formw.show()
time.sleep(1)
formw.call(f"setVersion('v{VERSION}')")


