# 运行时发布目录

此目录由 AScript 稳定启动器读取。

- 修改业务代码或 UI 后，运行 `python tools/build_runtime_release.py`。
- 提交生成的 `latest.json` 和以内容哈希命名的 ZIP。
- 将发布提交推送到 GitHub 的 `runtime` 分支。
- 将 `dist/latest.json` 和 `dist/releases/` 下对应的 ZIP 上传到阿里云 OSS，
  上传顺序为先 ZIP、后 `latest.json`。
- 不要手动编辑 `latest.json` 或发布 ZIP。

加载器优先访问阿里云 OSS 直链，失败后再尝试 GitHub Raw。GitHub 仓库必须为公开仓库，
设备才能在不携带账号凭据的情况下使用备用地址。OSS Bucket 只允许匿名读取，禁止
匿名写入和删除。
