"""工程内置运行时与远程运行时共用的业务入口。"""

import json
import os

from ascript.android.system import KeyValue, R
from ascript.android.ui import WebWindow

from .res.config import VERSION, ui_resource
from .res.test.test1 import test11


# WebWindow 必须由模块级变量持续引用。如果只保存在 start() 的局部变量中，函数
# 返回后对象可能被 Python 回收，导致配置窗口意外关闭或 tunnel 回调失效。
form_window = None
form_release_id = ""
form_should_show_update_log = False
form_ui_initialized = False

# 更新日志展示状态放在在线运行时的稳定缓存目录中，不能放进具体 release_id
# 目录，否则每次更新后旧状态都会随运行时路径变化而失效。
UPDATE_LOG_STATE_PATH = os.path.join(
    R.sd("AScript/erchong_runtime"),
    "update-log-state.json",
)


def _current_release_id():
    """返回当前运行时的稳定身份，用于判断是否首次打开这个发布包。"""
    if __package__ == "erchong_runtime":
        package_root = os.path.dirname(os.path.abspath(__file__))
        return os.path.basename(os.path.dirname(package_root))
    return "bundled-v{}".format(VERSION)


def _last_shown_release_id():
    """读取上次成功展示更新日志的发布标识，损坏状态按未展示处理。"""
    try:
        with open(UPDATE_LOG_STATE_PATH, "r", encoding="utf-8") as file_obj:
            state = json.load(file_obj)
        release_id = state.get("release_id")
        return release_id if isinstance(release_id, str) else ""
    except Exception:
        return ""


def _mark_update_log_shown(release_id):
    """在前端确认弹窗已打开后，原子记录本次已展示的发布标识。"""
    os.makedirs(os.path.dirname(UPDATE_LOG_STATE_PATH), exist_ok=True)
    temporary_path = UPDATE_LOG_STATE_PATH + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as file_obj:
        json.dump(
            {"release_id": release_id, "app_version": VERSION},
            file_obj,
            ensure_ascii=False,
            indent=2,
        )
    os.replace(temporary_path, UPDATE_LOG_STATE_PATH)


def tunnel(key, value):
    """处理配置界面通过 WebWindow 通道发回的事件。

    ``close`` 只记录窗口返回值；``submit`` 会解析完整表单、执行后端互斥校验，
    再把配置交给正式任务入口。其他未知事件直接忽略，避免误触发游戏任务。
    """
    print(key, value)
    if key == "ui_ready":
        _initialize_form_ui()
        return

    if key == "close":
        print(value)
        return

    if key == "update_log_shown":
        current_release_id = _current_release_id()
        if value != current_release_id:
            print("忽略非当前版本的更新日志回调：{}".format(value))
            return
        try:
            _mark_update_log_shown(current_release_id)
        except Exception as exc:
            # 状态写入失败不影响脚本使用；下次启动会再次尝试展示更新日志。
            print("记录更新日志展示状态失败：{}".format(exc))
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


def _initialize_form_ui():
    """在 WebView 主动确认页面加载完成后注入版本并按需展示更新日志。"""
    global form_ui_initialized

    if form_ui_initialized or form_window is None:
        return

    form_window.call("setVersion({})".format(json.dumps("v{}".format(VERSION))))
    if form_should_show_update_log:
        form_window.call(
            "showUpdateLogAutomatically({}, {})".format(
                json.dumps(form_release_id),
                json.dumps("v{}".format(VERSION)),
            )
        )
    form_ui_initialized = True


def start():
    """显示配置界面，并全局持有窗口对象以防被提前回收。

    这里通过 ``ui_resource`` 获取当前运行时包中的 HTML：远程运行时会使用远程
    ZIP 内的 UI，工程内置回退则使用最初导入的 UI。WebView 完成加载并发送
    ``ui_ready`` 后再设置版本文字和更新日志，避免依赖固定等待时间。
    """
    global form_release_id, form_should_show_update_log, form_ui_initialized, form_window

    form_release_id = _current_release_id()
    form_should_show_update_log = (
        _last_shown_release_id() != form_release_id
    )
    form_ui_initialized = False
    print("运行时来源：{}".format(__package__))
    print(KeyValue.get("asdata", ""))
    form_window = WebWindow(ui_resource("form.html"), tunnel)
    form_window.size("80vw", "70vh")
    form_window.show()
