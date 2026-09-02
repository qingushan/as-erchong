# Git 命令说明

本文档适用于 `qingushan/as-erchong` 项目。

## 一、项目分支约定

- `main`：日常开发和正式发布分支，后续默认使用这个分支。
- `runtime`：在线更新方案测试和已验证版本的备用分支，不作为日常开发分支。
- 远程仓库：`git@github.com:qingushan/as-erchong.git`

当前设备的主更新源是 OSS。代码中的 GitHub Raw 备用地址仍指向 `runtime` 分支；如果以后要把备用源也切换到 `main`，需要先修改 `remote_loader.py` 中的 `RELEASE_BRANCH`，再重新打包和发布。

## 二、首次获取项目

```bash
# 从 GitHub 克隆日常使用的 main 分支
git clone -b main git@github.com:qingushan/as-erchong.git

# 进入克隆出来的项目目录
cd as-erchong
```

没有 SSH 密钥时可以使用 HTTPS：

```bash
# 通过 HTTPS 克隆 main 分支
git clone -b main https://github.com/qingushan/as-erchong.git
cd as-erchong
```

## 三、查看状态和分支

```bash
# 进入本地项目目录
cd /d/code/Ascript/erchong

# 查看当前分支、未提交修改和未跟踪文件
git status

# 简短显示修改文件；没有输出表示工作区干净
git status --short

# 查看本地分支及其跟踪的远程分支
git branch -vv

# 查看所有本地和远程分支
git branch -a
```

如果看到本地在 `main`，但提示跟踪 `origin/runtime`，表示分支名称和跟踪关系不一致。应重新设置 `main` 跟踪 `origin/main`：

```bash
# 让本地 main 分支跟踪远程 origin/main
git branch --set-upstream-to=origin/main main
```

## 四、切换到 main 分支

```bash
# 获取远程最新提交和分支信息，不修改当前工作文件
git fetch origin
```

如果本地还没有 `main` 分支：

```bash
# 创建本地 main 分支，并关联远程 origin/main
git switch -c main --track origin/main
```

如果本地已经有 `main` 分支：

```bash
# 切换到已有的本地 main 分支
git switch main
```

确认切换结果：

```bash
# 查看当前分支和远程跟踪关系
git branch -vv

# 查看工作区状态
git status
```

## 五、拉取最新代码

```bash
# 从远程 main 分支拉取最新提交，只允许快进更新
git pull --ff-only origin main
```

说明：

- `git pull`：下载远程提交并更新本地分支。
- `--ff-only`：只允许快进更新，发现本地和远程分叉时直接停止。
- `origin main`：明确指定远程仓库和 `main` 分支。
- 有未提交修改时，Git 通常会拒绝拉取，不会直接覆盖本地文件。

本地 `main` 已设置跟踪关系时，也可以使用：

```bash
# 按当前分支已经配置的远程跟踪关系拉取
git pull --ff-only
```

拉取后检查：

```bash
# 查看拉取后的最新提交
git log -1 --oneline --decorate

# 没有输出表示工作区没有未提交修改
git status --short
```

## 六、提交本地修改

```bash
# 查看修改、新增和删除的文件
git status --short

# 查看尚未暂存的具体代码差异
git diff
```

推荐按文件暂存：

```bash
# 只暂存本次需要提交的文件
git add remote_loader.py
git add runtime_entry.py
git add res/
git add dist/latest.json
git add dist/releases/你的发布包.zip
```

确认所有修改都属于本次提交时：

```bash
# 暂存当前目录下所有新增、修改和删除的文件
git add .
```

检查暂存区：

```bash
# 查看已经暂存的文件
git status

# 查看准备提交的具体差异
git diff --cached
```

创建提交：

```bash
# 使用中文说明创建本地提交
git commit -m "更新远程运行时发布版本"
```

说明：`git add` 只把文件放入暂存区；`git commit` 只修改本地 Git 历史，不会上传到 GitHub。

## 七、推送到 GitHub main 分支

本地分支名称为 `main` 时：

```bash
# 将本地 main 推送到远程 main，并建立跟踪关系
git push -u origin main
```

本地分支名称不是 `main`，但确认当前提交需要发布到远程 `main` 时：

```bash
# 将当前分支提交推送到远程 main
git push origin HEAD:main
```

推送后核对：

```bash
# 查看远程 main 当前指向的提交
git ls-remote --heads origin main

# 查看本地当前提交
git rev-parse HEAD
```

两条命令输出的提交哈希应一致。

## 八、标准发布流程

```bash
# 1. 进入项目目录
cd /d/code/Ascript/erchong

# 2. 切换到日常使用的 main 分支
git switch main

# 3. 基于远程最新代码进行修改
git pull --ff-only origin main

# 4. 修改 Python、UI、资源或文档

# 5. 构建运行时 ZIP 和 dist/latest.json
python tools/build_runtime_release.py

# 6. 检查待提交文件，确认没有密钥、缓存或无关文件
git status --short

# 7. 暂存本次发布文件
git add .

# 8. 查看暂存区摘要
git diff --cached --stat

# 9. 创建中文提交
git commit -m "更新远程运行时发布版本"

# 10. 推送到正式发布使用的 main 分支
git push -u origin main

# 11. 核对远程 main 分支提交
git ls-remote --heads origin main
```

推送完成后，再把以下文件上传到 OSS。必须先上传 ZIP，最后覆盖清单：

```text
dist/releases/erchong-runtime-版本-内容哈希.zip
dist/latest.json
```

OSS 地址：

```text
https://as-erchong.oss-cn-beijing.aliyuncs.com/
```

## 九、拉取前有本地修改时

```bash
# 查看本地修改
git status --short

# 临时保存已跟踪和未跟踪文件，并记录原因
git stash push -u -m "拉取最新 main 代码前临时保存"

# 拉取远程 main 分支
git pull --ff-only origin main

# 恢复刚才临时保存的本地修改
git stash pop
```

如果恢复时发生冲突：

```bash
# 查看冲突文件和处理状态
git status

# 查看冲突位置
git diff
```

手动解决冲突标记后：

```bash
# 将已解决的文件重新加入暂存区
git add 冲突文件路径

# 确认冲突已经解决
git status
```

## 十、常见命令

```bash
# 查看本地和远程提交关系
git log --oneline --graph --decorate --all -20

# 取消暂存但保留工作区代码
git restore --staged .

# 查看最近一次提交的说明和文件变化
git show --stat --oneline HEAD

# 查看远程仓库地址
git remote -v

# 查看当前仓库的提交用户名和邮箱
git config user.name; git config user.email

# 查看全局配置的提交用户名和邮箱
git config --global user.name; git config --global user.email
```

如果 `git pull --ff-only` 提示无法快进，说明本地和远程发生了分叉。先查看提交历史，不要直接使用 `git push --force` 或覆盖本地文件的命令。

## 十一、安全注意事项

- 不要提交 SSH 私钥、GitHub Token、阿里云 AccessKey 或 SecretKey。
- 提交前检查 `git status --short`，不要把缓存、临时文件或无关压缩包加入 AScript 工程。
- AScript 工程导出包中不要嵌套远程运行时 ZIP；运行时 ZIP 应单独上传 OSS。
- 不要使用 `git push --force` 覆盖远程分支。
- 不确定某个文件是否应该提交时，先查看 `git diff` 和 `git diff --cached`。
