# AS-二重螺旋项目解析

> 本文档用于跨会话快速了解本项目。**后续代码有更新时，请同步更新本文档**（尤其是「任务清单」「架构」「更新记录」三节）。
>
> 最后同步时间：2026-09-02（版本号由维护者发布时手动调整）

## 一、项目概述

- **项目名**：`erchong`（工作区 `d:\code\Ascript\erchong`）
- **平台**：[AScript](https://www.ascript.cn/)（安卓自动化脚本框架，Python 语法，包名 `ascript.android.*`）
- **目标游戏**：**二重螺旋**（包名 `com.hero.dna.gf`），支持**本地游戏**与**云游戏**两套坐标/流程
- **功能**：全自动日常/刷本挂机脚本。通过 WebWindow 表单配置任务队列，按队列依次执行迷津、委托、突破、钓鱼等任务，并带掉线重连、定时下线、整点密函插队等调度逻辑
- **分辨率强依赖**：脚本只在 **1280x720（横屏）** 下工作，所有坐标、找色、OCR 区域均以此为基准（`AppGame.check_screen` 启动时校验）

## 二、目录结构

```
erchong/
├── __init__.py            # 稳定入口：只调用 remote_loader.start()
├── remote_loader.py       # 运行模式选择、远程运行时检查、下载、校验、缓存及回退
├── runtime_entry.py       # 业务入口：配置窗体 + submit 后调 test1.test11(uiconfig)
├── mode.json              # 可提交的运行模式配置：remote/local/cache
├── build.as               # AS 打包配置：工程名 + pip 依赖(opencv 4.1.2.30/requests/numpy 等)
├── tools/
│   └── build_runtime_release.py # 生成内容寻址运行时 ZIP 与 dist/latest.json
├── dist/
│   ├── latest.json        # 当前远程运行时发布清单
│   └── releases/          # 按 release_id 保存的运行时 ZIP 发布包
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
    ├── combat/            # 战斗技能控制器（按本地/云游戏隔离）
    │   ├── local/
    │   │   ├── CombatSkillController.py # 普通副本技能 + 共享动作委托/计时/角色展示
    │   │   ├── CJSXJCombatController.py # 沉浸式戏剧技能策略
    │   │   ├── LMYYCombatController.py  # 联袂演绎技能策略
    │   │   └── ActivityCombatController.py # 活动技能策略
    │   └── cloud/         # 云游戏技能控制器预留包，当前尚未迁移
    ├── util/
    │   └── CloudRoleSkillUtil.py # 云游戏版连招库（暂未迁入 combat/cloud）
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
            └── update-log.js    # 更新日志渲染及自动更新日志弹窗
```

## 三、启动与数据流

1. `__init__.py`（稳定入口）只调用 `remote_loader.start()`，不直接导入业务任务，确保用户首次导入的启动器可以长期保留。
2. 加载器读取项目根目录 `mode.json` 的 `mode`：缺失或非法时默认为 `remote`；`local` 直接加载工程内置代码，`cache` 只加载活动缓存。
3. `remote` 模式检查 `dist/latest.json`：云手机优先访问阿里云 OSS 直链，GitHub Raw 作为备用；查询参数用于区分设备请求，OSS 直链不依赖缓存清理。
4. 新发布包下载到 `/storage/emulated/0/AScript/erchong_runtime`，必须同时通过清单大小限制和 SHA-256 校验，随后解压到独立 `release_id` 目录并动态导入 `erchong_runtime.runtime_entry`。
5. `remote` 模式在线更新失败时先加载 `active.json` 指向的上一次成功缓存；没有有效缓存时加载工程自带的 `.runtime_entry`，所以首次断网也能打开脚本。
6. `runtime_entry.py` 使用运行时包自己的 `res/ui/form.html` 弹出配置界面（80vw x 70vh），并 `setVersion` 显示版本。资源不再依赖原工程的 `R.ui/R.res`，远程包中的 UI、字库和图片可随 Python 同步更新。
7. 用户在表单里配置全局项 + 任务队列，点击提交 → JS 把整个表单（含 `task_list` JSON 字符串）传给 Python `tunnel("submit", v)`。
8. `tunnel` → `json.loads(v)` 得到 `uiconfig` 字典 → `test1.test11(uiconfig)` → `AppGame(uiconfig).run()` 进入正式调度。
9. 表单配置通过 `KeyValue.save('asdata', ...)` 持久化，下次启动自动回填（form-cache.js）。

### uiconfig 关键字段
- `task_list`：JSON 字符串，`[{"type": "mijin"}, ...]`，按顺序执行
- `task_loop`：on/off 是否无限循环整个队列
- `global_check_game_is_offline`：掉线检测开关
- `global_check_month_card` / `global_do_mosaic` / `global_timed_offline`(+`_value` HH:MM:SS) / `global_time_5_offline`
- `refresh_time_is_execute_mihan`：整点插队执行委托密函
- 配置校验：任务列表包含 `mihan`（委托密函）时，不允许同时开启 `refresh_time_is_execute_mihan=on`；前端提交和 Python 入口均会拦截。
- 其余为各任务专属参数（前缀区分：`mijin_*`、`fish_map_*`、`mihan_*`、`lmyy_*` 等，见 form-options.js 的 CHECKBOX_FIELDS）；夜航手册每条配置为 `{grade, num, boci, level}`，其中 `boci` 仅对扼守生效

## 四、类继承体系

```
本地游戏：
BaseGame ──► BaseAction ─┐
BaseGame ──► BaseFind  ──┴─► BaseTask ──► Auto*Task（各任务）
CombatSkillController      由需要战斗技能的普通任务组合持有（self.combat_skill）
                         ├─► CJSXJCombatController
                         ├─► LMYYCombatController
                         └─► ActivityCombatController
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
每个任务类基本都有：`init_task`（读 uiconfig 参数）→ `go_to_level`（导航到副本入口）→ `select_level_grade`（选难度）→ `go_in_level` → `go_to_activate_level_XX`（按等级分路线走图，XX=等级，A/B/C 为分支路线）→ `combat`（战斗循环，普通任务调 `CombatSkillController`，沉浸式戏剧/联袂演绎/活动调各自专用控制器）→ `quit_level`/`level_exit` → `refresh_log`（更新悬浮日志）→ `run`（主循环）。

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

## 八、本地战斗技能控制器

- 本地技能代码统一位于 `res/combat/local/`。旧 `RoleSkillUtil` 已删除；`BaseTask` 不再无条件创建技能对象，只有实际需要普通技能循环的任务才组合持有 `CombatSkillController(self)`。
- `CombatSkillController` 同时承担普通副本技能策略和四个控制器共享的基础能力：通过 `__getattr__` 将动作/识别委托给任务对象，统一提供 `_ready`、`_cast`、`_cast_z`、`reset` 等计时方法。
- 普通控制器保留自定义技能以及赛琪、止流、灾厄武器角色等普通副本模组；沉浸式戏剧、联袂演绎、活动技能分别位于 `CJSXJCombatController`、`LMYYCombatController`、`ActivityCombatController`，不再混入普通控制器。
- 四个控制器根据 `skill_type` 第一段统一映射并打印角色展示名称，例如 `8-1`、`8-2-2`、`8-4-1` 均显示“芙洛拉”；该名称只用于日志展示，不参与战斗分支判断。
- 三个专用控制器继承 `CombatSkillController` 的公共能力并各自维护技能状态；活动任务调用 `before()`、`start()`、`tick()`，沉浸式戏剧和联袂演绎调用各自的 `tick()`。
- 活动芙洛拉（`8-4-1`/`8-4-2`）开场跳跃后，会在释放大招前调用 `rotate_view_to_middle_by_color(common_color, "任务黄色图标")`，把任务目标调整到视野中央。
- 活动芙洛拉分组赛（`8-4-1`）以正式战斗循环开始时间计时，15 秒后切换第二阶段，重击间隔由 2 秒缩短为 0.8 秒、E 技能间隔改为 99999 秒；当前战斗循环中的自动右转处于关闭状态，进入下一局时恢复第一阶段参数。
- `res/combat/cloud/` 已预留云游戏控制器包，但本次仅重构本地游戏；云任务仍使用 `res/util/CloudRoleSkillUtil.py`，调用路径和行为均未改变。
- 支持各任务从 UI 注入自定义连招 `set_role_skill_config_custom`；该方法同时登记魔灵覆盖配置。控制器提供统一的 `apply_skill_z(max_time, max_count)`，并在每次技能模组重建或重置后自动恢复，因此任务层不再保留重复的 `add_moling_skill()` 中转方法。
- 发布工具会把 `res/combat`、`res/combat/local`、`res/combat/cloud` 作为标准 Python 包写入运行时 ZIP；已有 `__init__.py` 使用源码文件，缺失时才补空文件，避免 ZIP 出现重复成员。

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

### 远程运行时发布（OSS 主源）

- 仓库与分支：`main` 是日常开发和正式发布分支，`runtime` 仅用于在线更新测试及已验证版本备份。当前设备主更新源为 OSS；匿名备用下载要求 GitHub 仓库公开，脚本中禁止保存 GitHub Token 或 SSH 私钥。
- 下载顺序：清单和 ZIP 优先读取阿里云 OSS 直链 `https://as-erchong.oss-cn-beijing.aliyuncs.com/`，失败后尝试公开 GitHub Raw。OSS 对象名与仓库 `dist/` 目录保持一致，设备不保存阿里云访问密钥；GitHub 仓库必须公开才能作为匿名备用源。
- 缓存目录：`/storage/emulated/0/AScript/erchong_runtime`；调用时必须使用 `R.sd("AScript/erchong_runtime")` 单个相对路径，当前 Android AScript 实测 `R.sd("AScript", "erchong_runtime")` 会返回两个路径组成的列表而非拼接字符串。`active.json` 仅在远程包解压且 Python 导入成功后更新，因此坏包不会替换当前可用缓存。
- 完整性保护：清单限制 ZIP 不超过 20 MiB，并记录精确字节数和 SHA-256；加载器防止 ZIP 路径穿越。SHA-256 用于发现传输/缓存损坏，不等同于独立数字签名，GitHub 仓库写权限仍需严格保护并开启 2FA。
- 启动日志区分三种来源：`已下载并加载远程运行时` 表示本次首次下载该 `release_id`；`已加载已缓存的远程运行时` 表示在线清单正常但设备已有对应缓存，跳过 ZIP 下载；`已加载上次成功缓存的远程运行时` 表示在线检查失败后使用 `active.json` 回退。
- 资源边界：运行时 ZIP 包含 `runtime_entry.py` 与整个 `res/`（Python、HTML、JS、CSS、JSON、字库和图片）；稳定启动器 `__init__.py`、`remote_loader.py` 和 `build.as` 不放进远程包。
- 发布命令：`python tools/build_runtime_release.py`。工具读取当前 `VERSION` 但不修改它，生成 `dist/releases/erchong-runtime-v版本-内容哈希.zip` 和 `dist/latest.json`。
- 远程发布使用 OSS 直链，不需要执行缓存清理。`build_runtime_release.py --purge` 仅保留兼容提示并立即退出，不会发起网络请求；发布时应直接上传 ZIP，再上传 `dist/latest.json`。GitHub Raw 备用地址目前仍指向 `runtime`，如需改为 `main`，必须先修改 `remote_loader.py` 中的 `RELEASE_BRANCH` 并重新发布。
- 项目根目录的 `mode.json` 纳入 Git，仓库默认设置为 `{"mode": "remote"}`；本地开发时可改为 `local`。正式构建前必须恢复为 `remote`，否则构建工具会拒绝生成发布包。

#### 标准发布流程

1. 完成 Python、UI、找色资源或其他 `res/` 文件修改，同时更新本文档和 `res/ui/updateLogs.json`；不要在发布工具中自动修改 `res/config.py` 的版本号。
2. 在项目根目录执行构建：

   ```powershell
   python tools/build_runtime_release.py
   ```

   工具会生成内容寻址 ZIP 和 `dist/latest.json`。如果源码内容没有变化，发布包的 `release_id`、文件名和 SHA-256 应保持不变。

3. 检查 `dist/latest.json` 中的 `release_id`、ZIP 路径、文件大小和 SHA-256，并确认 ZIP 包含 `erchong_runtime/runtime_entry.py`、完整 `res/`，且没有 `__pycache__`、`.pyc` 或稳定加载器文件。
4. 本地验证通过后，使用以下 Git 命令提交构建产物、源码和文档，并推送到远程 `main` 分支。`runtime` 仅在需要单独测试在线更新时使用；禁止使用 `git push --force`。

   ```powershell
   # 查看待提交文件，确认没有混入密钥、缓存或无关改动
   git status --short

   # 暂存本次发布需要的文件；也可以按文件逐个 git add
   git add .

   # 提交本地发布版本，提交说明按实际改动调整
   git commit -m "feat: update runtime release"

   # 将当前提交推送到日常开发和正式发布使用的 main 分支
   git push origin HEAD:main

   # 核对远程 main 的提交是否与本地 HEAD 一致
   git ls-remote --heads origin main
   git rev-parse HEAD
   ```

   如果 `git status --short` 显示了不应发布的文件，不要直接执行 `git add .`，先使用 `git reset` 取消暂存，再按路径精确执行 `git add`。如果 `git commit` 提示没有变更，说明当前内容已经提交，不要为了触发更新重复生成发布包。
5. 确认推送成功后，将构建产物上传到 OSS Bucket：

   ```powershell
   # 先上传版本化 ZIP，路径必须保留 dist/releases/ 前缀
   # 再上传清单，覆盖 OSS 中的 dist/latest.json
   ```

   上传后请求 `https://as-erchong.oss-cn-beijing.aliyuncs.com/dist/latest.json`，确认返回新的 `release_id`；再检查清单中的 ZIP URL 为 HTTP 200 且大小一致。OSS 直链不依赖分支缓存传播。
6. 让设备重新启动脚本。检查日志出现“已加载远程运行时”，并读取 `/storage/emulated/0/AScript/erchong_runtime/active.json`，确认 `release_id` 和 `sha256` 与 `dist/latest.json` 一致；配置 UI 能正常显示后才算发布完成。
7. 如果清单下载、ZIP 校验或导入失败，加载器会自动使用设备上一次成功缓存；设备没有缓存时使用工程内置版本。回滚时将 OSS 中的 `dist/latest.json` 恢复为上一个已验证包的信息，并同步推送 GitHub `runtime` 分支作为备用源。

## 十一、更新记录（Devin 维护，代码变更时在此追加）

| 日期 | 版本 | 变更摘要 |
|---|---|---|
| 2026-08-31 | 待发版 | 新增项目 `mode.json` 运行模式配置；配置页面改为通过 `ui_ready` 通知 Python 完成加载，再设置版本并自动展示更新日志，修复慢设备上函数未定义的问题；未修改版本号 |
| 2026-08-30 | 待发版 | 远程运行时改用阿里云 OSS 直链作为主源、GitHub Raw 作为备用，移除公共缓存服务依赖；保留大小与 SHA-256 校验、内容寻址缓存及离线回退；脚本更新后首次打开配置界面自动展示“关于脚本”中的本次更新日志，每个发布包只展示一次；同步更新发布目录说明和上传顺序；未修改版本号 |
| 2026-08-29 | 待发版 | 新增远程运行时加载、大小与 SHA-256 校验、内容寻址缓存、上次成功缓存及工程内置版本双重回退；Python 与 UI/字库/图片可同步更新；增加可重复发布构建工具；详细补充在线更新与构建流程的中文代码注释；未修改版本号 |
| 2026-08-28 | 待发版 | 调整活动芙洛拉分组赛战斗节奏：前 30 秒保持循环旋转，满 30 秒后加快重击并停止自动释放 E 和旋转，同时支持每局重置阶段 |
| 2026-08-26 | 待发版 | 本地游戏将沉浸式戏剧、联袂演绎、活动技能策略迁移到独立控制器；活动芙洛拉开场在放大招前自动对准黄色任务图标；云游戏暂不调整 |
| 2026-08-22 | 待发版 | 增加委托密函任务与整点刷新执行委托密函互斥校验，冲突配置禁止启动 |
| 2026-08-15 | 待发版 | 云-角色突破适配新版主菜单、角色突破入口及属性坐标；关键页面改用 OCR 识别 |
| 2026-08-06 | 待发版 | 夜航手册每条副本配置新增独立扼守轮次；非扼守关卡忽略该字段并保持原逻辑 |
| 2026-08-06 | v1.0.4.5 | 修复夜航手册 70 级第一个扼守关卡被误判为驱离、无法激活的问题 |
| 2026-08-06 | v1.0.4.4 | 初版文档：通读全项目并生成本解析文件（无代码改动） |
