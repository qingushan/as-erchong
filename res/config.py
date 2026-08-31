import os as _os


VERSION = "2.0.0.1"

# 远程运行时会被解压到原 AScript 工程之外，因此资源路径必须以当前运行时包
# 为基准，不能继续依赖 R.ui/R.res。这样远程下载的 Python 才能与同一发布包
# 中的 HTML、字库、图片等资源保持一致。
PROJECT_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))


def resource_path(*child_paths):
    """返回当前运行时包 ``res`` 目录下资源的绝对路径。"""
    return _os.path.join(PROJECT_ROOT, "res", *child_paths)


def ui_resource(*child_paths):
    """返回当前运行时包 ``res/ui`` 目录下界面资源的绝对路径。"""
    return resource_path("ui", *child_paths)


def image_resource(*child_paths):
    """返回当前运行时包 ``res/img`` 目录下图片资源的绝对路径。"""
    return resource_path("img", *child_paths)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_CENTER_X = 640
SCREEN_CENTER_Y = 360

# 本地游戏位置
WALK_BUTTON_CENTER_X = 209
WALK_BUTTON_CENTER_Y = 553

action_button_position = {
    "小技能": (896,644),
    "大招": (982,643),
    "魔灵技": (1112,643),
    "近战攻击": (1115,504),
    "远程攻击": (976,528),
    "跳跃": (1013,421),
    "闪避": (1125,366),
    "换弹": (895,529),
    "锁敌": (1214, 645),
    "下蹲": (57,590),
}

# 交互文本区域
interaction_text_rect = {
    "单行":[653,324,944,385],
    "多行":[667,296,948,547]
}

# 云游戏位置
CLOUD_WALK_BUTTON_CENTER_X = 208
CLOUD_WALK_BUTTON_CENTER_Y = 551

cloud_action_button_position = {
    "小技能": (858,643),
    "大招": (943,644),
    "魔灵技": (1073,643),
    "近战攻击": (1080,504),
    "远程攻击": (938,527),
    "跳跃": (976,422),
    "闪避": (1090,366),
    "换弹": (858,529),
    "锁敌": (1172,620),
    "下蹲": (86,591),
    "行走": (99,572),
}

# 交互文本区域
cloud_interaction_text_rect = {
    "单行":[673,331,945,380],
    "多行":[670,277,945,555]
}

skill_time = {
    "小技能":10,
    "小技能_释放时间":0,
    "大招":10,
    "大招_释放时间":0,
    "魔灵技":15,
    "魔灵技_释放时间":0
}
