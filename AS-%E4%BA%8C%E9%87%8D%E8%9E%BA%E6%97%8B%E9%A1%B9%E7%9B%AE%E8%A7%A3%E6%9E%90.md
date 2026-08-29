# AS-二重螺旋项目解析

> 本文档用于跨会话快速了解本项目。**后续代码有更新时，请同步更新本文档**（尤其是「任务清单」「架构」「更新记录」三节）。
>
> 最后同步时间：2026-08-15（版本号由维护者发布时手动调整）

## 一、项目概述

- **项目名**：`erchong`（工作区 `d:\code\Ascript\erchong`）
- **平台**：[AScript](https://www.ascript.cn/)（安卓自动化脚本框架，Python 语法，包名 `ascript.android.*`）
- **目标游戏**：**二重螺旋**（包名 `com.hero.dna.gf`），支持**本地游戏**与**云游戏**两套坐标/流程
- **功能**：全自动日常/刷本挂机脚本。通过 WebWindow 表单配置任务队列，按队列依次执行迷津、委托、突破、钓鱼等任务，并带掉线重连、定时下线、整点密函插队等调度逻辑
- **分辨率强依赖**：脚本只在 **1280x720（横屏）** 下工作，所有坐标、找色、OCR 区域均以此为基准（`AppGame.check_screen` 启动时校验）

## 二、目录结构

```
erchong/
├── __init__.py            # 入口：弹出配置窗体 form.html，submit 后调 test1.test11(uiconfig)
├── build.as               # AS 打包配置：工程名 + pip 依赖(opencv 4.1.2.30/requests/numpy 等)
└── res/
    ├── config.py          # 全局配置：VERSION、屏幕尺寸、本地/云游戏按键坐标、技能CD
    ├── font.t             # 点阵字库（OcrX 用）
    ├── assets/
    │   ├── color.py       # 本地游戏全部找色字典（按任务分组，见下）
    │   └── cloud_color.py # 云游戏找色字典
    ├── task/              # 本地游戏任务（核心目录）
    │   ├── BaseGame.py    # 最底层基类：坐标/技能CD状态、方位判断
    │   ├── BaseAction.py  # 动作层：点击/走位/视角/技能/闪避/多指手势
    │   ├── BaseFind.py    # 识别层：找色/OCR(mlkitocr_v2)/OcrX点阵/等待
    │   ├── BaseTask.py    # 任务基类(继承 Action+Find)：点击跳转、旋转视角寻色、
    │   │                  #   boss识别、密函KeyValue状态、角色复位/回家/前往历练
    │   ├── LogUi.py       # 单例悬浮日志条(log.html) + 打码窗口 MosaicUI(mosaic.html)
    │   ├── AppGame.py     # 总调度器：任务映射、任务线程、看门狗(掉线重连/签到/月卡/定时下线)
    │   └── Auto*Task.py   # 各任务实现（见任务清单）
    ├── cloud_task/        # 云游戏任务（独立的 CloudBaseAction/CloudBaseTask 体系）
    ├── util/
    │   ├── RoleSkillUtil.py      # 角色战斗连招库（按角色编号组合 e/q/z/平A）
    │   └── CloudRoleSkillUtil.py # 云游戏版连招库
    ├── test/
    │   ├── test1.py       # test11(uiconfig)：真实入口，末尾 AppGame(uiconfig).run()
    │   │                  #   （前面大量注释掉的单任务调试代码，调试时取消注释单跑）
    │   └── cloud_test.py  # 云游戏调试入口
    └── ui/                # WebWindow 前端（layui + jQuery）
        ├── form.html      # 主配置窗体（约116KB，所有任务的参数页签都在这里）
        ├── log.html / mosaic.html / updateLogs.json（版本更新日志数据）
        ├── css/form.css
        └── js/
            ├── form-options.js  # 常量：DEFAULT_FORM_DATA、CHECKBOX_FIELDS、TASK_TYPE_NAME_MAP
            ├── form-cache.js    # KeyValue 缓存读写（key: 'asdata'）
            ├── form-main.js     # 表单初始化/提交
            ├── task-list.js     # 任务队列增删/排序，JSON 存隐藏域 #input_task_list
            ├── mod-config.js    # 夜航手册(mod)专用配置
            └── update-log.js    # 更新日志渲染
```

## 三、启动与数据流

1. `__init__.py`（工程入口）→ `WebWindow(R.ui("form.html"), tunnel)` 弹出配置界面（80vw x 70vh），并 `setVersion` 显示版本。
2. 用户在表单里配置全局项 + 任务队列，点击提交 → JS 把整个表单（含 `task_list` JSON 字符串）传给 Python `tunnel("submit", v)`。
3. `tunnel` → `json.loads(v)` 得到 `uiconfig` 字典 → `test1.test11(uiconfig)`。
4. `test11` 末尾 `AppGame(uiconfig).run()` 进入正式调度（前面是注释掉的单任务调试代码）。
5. 表单配置通过 `KeyValue.save('asdata', ...)` 持久化，下次启动自动回填（form-cache.js）。

### uiconfig 关键字段
- `task_list`：JSON 字符串，`[{"type": "mijin"}, ...]`，按顺序执行
- `task_loop`：on/off 是否无限循环整个队列
- `global_check_game_is_offline`：掉线检测开关
- `global_check_month_card` / `global_do_mosaic` / `global_timed_offline`(+`_value` HH:MM:SS) / `global_time_5_offline`
- `refresh_time_is_execute_mihan`：整点插队执行委托密函
- 其余为各任务专属参数（前缀区分：`mijin_*`、`fish_map_*`、`mihan_*`、`lmyy_*` 等，见 form-options.js 的 CHECKBOX_FIELDS）；夜航手册每条配置为 `{grade, num, boci, level}`，其中 `boci` 仅对扼守生效

## 四、类继承体系

```
本地游戏：
BaseGame ──► BaseAction ─┐
BaseGame ──► BaseFind  ──┴─► BaseTask ──► Auto*Task（各任务）
RoleSkillUtil(BaseAction)  由 BaseTask 组合持有（self.role_skill_util）
LogUi / MosaicUI           单例悬浮窗，BaseTask 持有 self.logui

云游戏：
BaseGame ──► CloudBaseAction ─┐
BaseGame ──► BaseFind       ──┴─► CloudBaseTask ──► CloudAuto*Task
CloudRoleSkillUtil(CloudBaseAction)
```

- **BaseGame**：屏幕/按键坐标（区分本地与云）、`skill_time` CD 表、`position_is_left_or_right`（目标在屏幕左/中/右/后）、技能就绪判断（区域颜色计数）。
- **BaseAction**：`click`（带随机偏移）、`walk_to_w/s/a/d`、`rotate_view_to_*`（滑动转视角）、`skill_e/q/z`、闪避/跳跃/锁敌/下蹲，多指手势（`action.gesture + Path`）实现"边走边闪避/跳跃释放技能"以及角色专属连招（赛琪/苏已/煜明）。
- **BaseFind**：`FindColors.find` 找色、`Ocr.mlkitocr_v2` OCR、`OcrX`+font.t 点阵识别；`find_my_color(color_dict, name)` 统一按字典取 colors/rect/diff。
- **BaseTask**：组合动作+识别的通用套路：`click_color_to_color`（点击直到下个界面出现）、`click_until_ocr`、`rotate_view_to_middle_by_color`（转视角把目标转到屏幕中央）、`walk_to_color_disapper`、`ocr_boss`（识别7个boss）、开锁、委托密函执行状态（KeyValue `is_execute_mihan`）、`role_restoration` 角色复位、`go_home`、`go_to_lilian`。

### 任务类通用结构（Auto*Task）
每个任务类基本都有：`init_task`（读 uiconfig 参数）→ `go_to_level`（导航到副本入口）→ `select_level_grade`（选难度）→ `go_in_level` → `go_to_activate_level_XX`（按等级分路线走图，XX=等级，A/B/C 为分支路线）→ `combat`（战斗循环，调 RoleSkillUtil 连招）→ `quit_level`/`level_exit` → `refresh_log`（更新悬浮日志）→ `run`（主循环）。

## 五、AppGame 调度器（res/task/AppGame.py）

- **任务映射** `task_mapping`：type 字符串 → 任务类（注意：`"mijin"` 当前映射到 **AutoTestTask**，而不是 AutoMijinTask——迷津新逻辑在 AutoTestTask 里）。
- **执行模型**：每个任务在独立 Thread 中 `task.run()`；主线程 join 等待。
- **看门狗线程** `watchdog_logic`（每2秒）：
  - 掉线检测：前台应用不是"二重螺旋"或 OCR 到"连接失败"→ `ctypes.PyThreadState_SetAsyncExc` 强杀任务线程 → `close_game`（系统设置页停止应用）→ 等5分钟 → `open_game`（重启并处理更新弹窗/公告/签到）→ 重跑被中断任务。
  - 每日签到/小月卡弹窗处理（5点前后）、定时下线（到点 close_game + system.exit()）、每日5:10回桌面。
- **整点密函插队**：`refresh_time_is_execute_mihan=on` 时，整点先跑 AutoWeituomihanTask 再继续原任务。

## 六、任务清单（type → 名称 → 实现类）

| type | 名称 | 类 |
|---|---|---|
| daily_task | 日常任务 | AutoDailyTaskTask |
| mijin | 迷津 | **AutoTestTask**（旧版 AutoMijinTask 保留） |
| mod | 夜航手册 | AutoModTask |
| jiaojiaobi | 皎皎币 | AutoJjbTask |
| role_tupo | 角色突破 | AutoRoleBreakthroughTask |
| role_exp | 角色经验 | AutoRoleExpTask |
| mozhixie | 魔之楔 | AutoMozhixieTask |
| wuqi_tupo | 武器突破 | AutoWeaponBreakTask |
| wuqi_exp | 武器经验 | AutoWeaponExpTask |
| husong | 护送 | AutoHusongTask |
| mihan | 委托密函 | AutoWeituomihanTask |
| fish | 钓鱼 | AutoFishTask |
| cjsxj | 沉浸式戏剧 | AutoCJSXJTask |
| ze_weapon | 灾厄武器 | AutoZEWeaponTask |
| lmyy | 联袂演绎 | AutoLMYYTask |
| game_activity | 活动 | AutoGameActivityTask |
| cloud_wuqi_tupo | 云-武器突破 | CloudAutoWeaponBreakTask |
| cloud_role_tupo | 云-角色突破 | CloudAutoRoleBreakthroughTask |
| cloud_wuqi_exp | 云-武器经验 | CloudAutoWeaponExpTask |
| cloud_game_activity | 云-活动 | CloudAutoGameActivityTask |
| （未接入调度） | 云-锄大地 | CloudAutoFindPropWorldTask |

> 新增任务的固定改动点：① 写 `res/task/AutoXxxTask.py`（继承 BaseTask）② `AppGame.py` import + `task_mapping` 注册 ③ `form-options.js` 的 `TASK_TYPE_NAME_MAP`（及 CHECKBOX_FIELDS）④ `form.html` 加参数页签 + 任务下拉选项 ⑤ `color.py` 加该任务的找色字典 ⑥ 调试期在 `test1.py` 单跑。

## 七、找色/识别资产（res/assets/color.py）

- 按任务分组的字典：`common_color`（血条/锁敌/BOSS血条/签到界面/退出按钮等公共UI）、`mijin_color`、`mod_color`、`husong_color`、`jjb_color`、`role_tupo_color`、`role_exp_color`、`weapon_tupo`、`mozhixie_color`、`weituomihan_color`、`fish_color`、`cjsxj_color`、`game_activity_color`、`ze_weapon_color`、`lmyy_color`、`test_color`、`daily_task_color`、`app_color`。
- 每项格式：`{"colors": "x,y,#RRGGBB|x,y,#RRGGBB|...", "rect": [x1,y1,x2,y2]|None, "diff": 0.9}`，多点比色（首点+偏移点）。
- 云游戏对应 `cloud_color.py`：`cloud_common_color` 等 6 组。
- **注意**：文件为 UTF-8，键名全是中文；改动时保持 UTF-8 编码。

## 八、角色连招库（res/util/RoleSkillUtil.py）

- 按 `role_type` 编号初始化连招配置，`combat()` 为统一战斗入口；命名如 `combat_skill_7_4_1` = 角色7的某套循环。
- 支持自定义连招 `set_role_skill_config_custom`（来自 UI 的 `mod_config_list`）、追加魔灵技 `add_skill_z`。
- 特殊角色前置：煜明/滞留/苏已/夫人（fll）有专属 `combat_before_*`。
- 云版 `CloudRoleSkillUtil` 与之平行（坐标体系不同）。

## 九、本地 vs 云游戏差异

- 坐标：`config.py` 中两套（`action_button_position` vs `cloud_action_button_position`，行走轮盘中心不同）。
- 动作层：云游戏 `CloudBaseAction` 独立实现（多了 `walk_to_w_new` 边走边OCR、`click_fly`、`action_click_walk` 等）。
- 找色：两套 color 字典；任务类也完全分开（`res/task/` vs `res/cloud_task/`）。
- 云-角色突破：新版主菜单与角色突破图标通过 OCR 定位，副本选择页使用云画面专属属性坐标；进入倍率书弹窗后以角色血条确认成功进本，避免依赖已失效的旧色样。

## 十、开发约定

- 入口只有 `__init__.py`；包内一律相对导入（`from ...res.task.X import X`），不写 `if __name__ == "__main__"`。
- 分辨率 1280x720，坐标写死；找色 diff 默认 0.9。
- 持久化用 `KeyValue`（表单缓存 key=`asdata`；密函状态 key=`is_execute_mihan`）。
- 版本号在 `res/config.py` 的 `VERSION`，同时要更新 `res/ui/updateLogs.json`（界面"更新日志"页签数据源）。
- 调试：在 `res/test/test1.py` 的 `test11` 中注释掉 `AppGame` 两行、取消注释对应任务的单跑代码。

## 十一、更新记录（Devin 维护，代码变更时在此追加）

| 日期 | 版本 | 变更摘要 |
|---|---|---|
| 2026-08-15 | 待发版 | 云-角色突破适配新版主菜单、角色突破入口及属性坐标；关键页面改用 OCR 识别 |
| 2026-08-06 | 待发版 | 夜航手册每条副本配置新增独立扼守轮次；非扼守关卡忽略该字段并保持原逻辑 |
| 2026-08-06 | v1.0.4.5 | 修复夜航手册 70 级第一个扼守关卡被误判为驱离、无法激活的问题 |
| 2026-08-06 | v1.0.4.4 | 初版文档：通读全项目并生成本解析文件（无代码改动） |
