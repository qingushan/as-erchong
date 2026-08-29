"""AScript 稳定启动入口。

此文件只负责调用远程加载器，业务代码由 ``remote_loader`` 加载，后续可以在
不要求用户重新导入 AScript 工程的情况下独立更新。
"""

from .remote_loader import start


start()
