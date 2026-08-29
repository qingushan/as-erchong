# 运行时发布目录

此目录由 AScript 稳定启动器读取。

- 修改业务代码或 UI 后，运行 `python tools/build_runtime_release.py`。
- 提交生成的 `latest.json` 和以内容哈希命名的 ZIP。
- 将发布提交推送到 GitHub 的 `runtime` 分支。
- 推送完成后，运行 `python tools/build_runtime_release.py --purge` 清理清单缓存，
  并确认 jsDelivr 返回新的 `release_id`。不要在推送前执行 `--purge`。
- 不要手动编辑 `latest.json` 或发布 ZIP。

加载器优先访问 jsDelivr，失败后再尝试 GitHub Raw。GitHub 仓库必须为公开仓库，
设备才能在不携带账号凭据的情况下下载这两个地址。
