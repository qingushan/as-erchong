# 项目长期约定（erchong / 二重螺旋脚本）

## 文档约定
- `AS-二重螺旋项目解析.md` 只记录项目结构、架构、约定与发布流程，**不记录版本更新记录**。
  - 该文档原有的「十二、更新记录」章节已按用户要求于 2026-10-08 **删除**，**不要重新添加**。
  - 版本变更日志只放在 `res/ui/updateLogs.json`（配置界面"更新日志"页签的数据源），面向玩家。
  - 改代码后同步更新解析文档的「任务清单」「架构」两节。

## 发布约定
- 版本号由维护者手动改 `res/config.py` 的 `VERSION`；`tools/build_runtime_release.py` 只读取、不修改。
- 发布前 `mode.json` 必须为 `remote`，否则构建工具拒绝生成发布包。
- 构建：`python tools/build_runtime_release.py` → 生成内容寻址 ZIP + `dist/latest.json`。
- 清单/ZIP 主源为阿里云 OSS 直链，GitHub Raw（`runtime` 分支）为备用。

## 代码约定
- 入口只有 `__init__.py`；包内一律相对导入，不写 `if __name__ == "__main__"`。
- 分辨率写死 1280x720；找色 diff 默认 0.9；`color.py` 键名为中文，保持 UTF-8。
- 持久化统一用 `KeyValue`：`asdata`（表单缓存）/ `is_execute_mihan`（密函状态）/ `backend_identity`（后台身份）。
- `mijin`（迷津）的实现类是 `AutoMijinTask`（2026-10-08 由 `AutoTestTask` 合并而来，旧版兜底开关 `mijin_run_old` 已移除）。
