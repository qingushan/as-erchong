"""后台上报客户端：安装实例登记、运行会话与心跳。

契约来源是《后台开发技术文档.md》（v2 契约修订版）第 6～10、19 节。客户端只做
契约允许的四件事，其余规则一律以服务端为准：

1. **身份**：``install_id`` 是长期随机标识，保存在 ``KeyValue`` 的
   ``backend_identity`` 键里。放在这里而不是 ``asdata``（表单缓存会被重置）或
   ``releases/<release_id>/``（运行时更新即换目录），才能保证重新导入脚本、
   运行时更新、重启 AScript 都不变（文档 6.1）。
   ``run_id`` 每次启动重新生成，全局唯一（``<install_id>-<时间戳>-<6位随机>``）。
2. **会话**：注册 → 开始会话 → 定时心跳 →（尽力而为）停止；时长与排行榜全部由
   服务端计算，客户端**不提交任何时间戳**（文档 8.1 / 9.1）。
3. **线程**：整个上报流程跑在独立守护线程里，与任务线程完全解耦——看门狗会用
   ``ctypes.PyThreadState_SetAsyncExc`` 强杀任务线程（``AppGame.py``），上报线程
   不能被牵连（文档 19.1）。
4. **失败**：后台只是辅助能力。线程内所有异常都吞掉并只打印日志，绝不冒泡到
   ``AppGame.run()``；后台不可用时脚本照常执行任务（文档 19）。

调用方式只有一个入口：``runtime_entry.tunnel`` 收到 ``submit`` 后调 ``start()``，
任务正常跑完后调 ``request_stop()``。
"""

import json
import os
import queue
import random
import re
import string
import threading
import time
from datetime import datetime

import requests
from ascript.android.system import KeyValue

from ...res.config import VERSION, resource_path


# 后台基址。当前部署是阿里云 ECS 的公网 IP + 8443（大陆节点 80/443 对未备案域名
# 做拦截，纯 IP 也拿不到公共可信证书，所以 Caddy 用自签证书，见后台项目 README）。
# 本轮只把后台用于统计上报，运行时清单仍走 OSS/GitHub，因此这个地址即使不可用
# 也不影响脚本更新与任务执行。
BACKEND_BASE_URL = "https://123.57.172.142:8443"

# 自签证书固定校验文件，随运行时 ZIP 一起下发（证书是公开信息，不是密钥）。
TLS_PIN_PATH = resource_path("certs", "backend-ca.crt")

# 身份与注册状态持久化键。禁止放进 ``asdata``（表单缓存）或 release_id 目录。
IDENTITY_KEY = "backend_identity"

API_PREFIX = "/api/v1"

# 文档 19 的超时约定：非启动路径（注册 / 会话 / 心跳）连接 5s、读取 10s，重试 1 次。
# 所有写接口都是幂等的（文档 8.4），所以重试不会产生重复会话或重复时长。
CONNECT_TIMEOUT_SECONDS = 5
READ_TIMEOUT_SECONDS = 10
REQUEST_RETRY_TIMES = 1

# 心跳：服务端在响应里下发 ``next_heartbeat_seconds``（默认 180）；失败后按
# ``30s → 2min → 10min`` 退避（文档 19）。
HEARTBEAT_FALLBACK_SECONDS = 180
HEARTBEAT_MIN_SECONDS = 30
HEARTBEAT_MAX_SECONDS = 3600
HEARTBEAT_BACKOFF_SECONDS = (30, 120, 600)

# 单例命令队列有界，网络异常时不会堆积（文档 19.4）。
COMMAND_QUEUE_SIZE = 8

# 建立会话的最大尝试次数：网络未就绪、限流、后台重启都在这个次数内自愈。
SESSION_MAX_ATTEMPTS = 5

# 结束原因枚举（文档 8.3）。不在枚举内的值会被服务端 400 拒绝，这里先兜底。
END_REASONS = (
    "user_stopped",
    "task_finished",
    "script_exit",
    "replaced_by_new_run",
    "server_closed",
    "heartbeat_timeout",
    "invalid_data",
    "unknown",
)
DEFAULT_END_REASON = "task_finished"

# 与后台 services/identity.py 保持一致的校验规则（文档 6.1 / 6.2 / 6.3）。
INSTALL_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{16,96}$")
DISPLAY_NAME_MAX_LENGTH = 20
DISPLAY_NAME_EXTRA_CHARS = " _-."
RESERVED_DISPLAY_NAMES = frozenset(
    {
        "admin",
        "administrator",
        "root",
        "support",
        "system",
        "official",
        "管理员",
        "系统",
        "官方",
        "客服",
    }
)


class BackendError(Exception):
    """后台返回了非 2xx 响应。"""

    def __init__(self, status_code, code, message):
        super().__init__("HTTP {} {} {}".format(status_code, code, message))
        self.status_code = status_code
        self.code = code
        self.message = message


class BackendOffline(Exception):
    """网络层不可达（超时、DNS、TLS 握手失败等）。"""

    pass


class InstallationDisabled(BackendError):
    """实例被后台禁用：注册与写接口都会被拒，重试没有意义。"""

    pass


def _sanitize_display_name(value):
    """把界面输入规范化为后台接受的昵称；不合法时返回空串（表示不上报昵称）。

    规范与后台 ``normalize_display_name`` 一致：去首尾空格、压缩连续空格、最长
    20 个码点、只允许中文/字母/数字与空格 ``_ - .``、禁止保留名。这里**不做报错**
    ——昵称只是显示属性，不能因为它让整个会话上报失败（文档 19）。
    """
    if not isinstance(value, str):
        return ""
    text = re.sub(r"\s+", " ", value.strip())
    if not text:
        return ""
    kept = [
        char
        for char in text
        if char.isalnum() or char in DISPLAY_NAME_EXTRA_CHARS
    ]
    text = "".join(kept)[:DISPLAY_NAME_MAX_LENGTH].strip()
    if not text or text.casefold() in RESERVED_DISPLAY_NAMES:
        return ""
    return text


def _valid_install_id(value):
    """校验 ``install_id``；损坏或手工改坏的值会被重新生成（文档 6.1）。"""
    return isinstance(value, str) and bool(INSTALL_ID_PATTERN.match(value))


def _valid_run_id(value):
    """校验 ``run_id`` 是否符合全局唯一格式（文档 6.2）。"""
    return isinstance(value, str) and bool(RUN_ID_PATTERN.match(value))


def _new_install_id():
    """生成 ``ER-XXXX-XXXX-XXXX`` 形式的安装实例标识（推荐形式，文档 6.1）。"""
    groups = [
        "".join(random.choice("0123456789ABCDEF") for _ in range(4))
        for _ in range(3)
    ]
    return "ER-{}".format("-".join(groups))


def _new_run_id(install_id):
    """生成全局唯一的会话标识：``<install_id>-<yyyyMMddTHHmmss>-<6位随机>``。

    带上 ``install_id`` 前缀是为了跨设备不撞车（文档 7 的 C7）；同秒内重复启动
    由随机后缀区分。
    """
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    suffix = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
    )
    run_id = "{}-{}-{}".format(install_id, stamp, suffix)
    if not _valid_run_id(run_id):
        run_id = "{}-{}-{}".format(install_id, int(time.time()), suffix)
    return run_id


def _error_code(body):
    """从 ``{"error": {"code": ...}}`` 里取错误码；格式不符时返回空串。"""
    if not isinstance(body, dict):
        return ""
    error = body.get("error")
    if not isinstance(error, dict):
        return ""
    code = error.get("code")
    return code if isinstance(code, str) else ""


def _error_message(body):
    """取错误描述，取不到时给出空串，避免日志里出现 None。"""
    if not isinstance(body, dict):
        return ""
    error = body.get("error")
    if not isinstance(error, dict):
        return ""
    message = error.get("message")
    return message if isinstance(message, str) else ""


class BackendClient:
    """后台会话上报客户端（单例）。

    ``start()`` 只负责拉起线程，真正的注册、开始会话、心跳都在后台线程里完成，
    因此后台慢或不可达都不会拖慢脚本启动（后台在启动路径之外）。
    """

    _instance = None
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls):
        """返回全局唯一实例。"""
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        self._commands = queue.Queue(maxsize=COMMAND_QUEUE_SIZE)
        self._thread = None
        self._thread_lock = threading.Lock()
        # None = 还没决定；False = 本次运行降级为不校验；字符串 = 固定证书路径
        self._tls_verify = None
        self._ui_display_name = ""

    # ------------------------------------------------------------------ 对外接口

    def start(self, uiconfig, app_version="", release_id=""):
        """启动上报线程。重复调用（线程还活着）时直接忽略，不阻塞调用方。"""
        try:
            self._ui_display_name = _sanitize_display_name(
                (uiconfig or {}).get("backend_display_name")
            )
        except Exception as exc:
            self._ui_display_name = ""
            print("读取排行榜昵称失败：{}".format(exc))

        with self._thread_lock:
            if self._thread is not None and self._thread.is_alive():
                print("后台上报线程已在运行，忽略重复启动")
                return False
            self._thread = threading.Thread(
                target=self._worker,
                args=(app_version, release_id),
                name="BackendReport",
                daemon=True,
            )
            self._thread.start()
        print("后台上报线程已启动")
        return True

    def request_stop(self, reason=DEFAULT_END_REASON):
        """请求结束会话。只投递命令，不阻塞、不等待网络。

        ``system.exit()`` 强杀进程时不会有停止请求，服务端会按
        ``last_heartbeat_at + 120s`` 结算（文档 8.3），所以这里是"尽力而为"。
        """
        if reason not in END_REASONS:
            reason = "unknown"
        try:
            self._commands.put_nowait(reason)
        except queue.Full:
            print("后台上报命令队列已满，忽略停止请求")
        except Exception as exc:
            print("投递后台停止请求失败：{}".format(exc))

    def is_running(self):
        """上报线程是否仍在运行（排障用）。"""
        return self._thread is not None and self._thread.is_alive()

    def wait_stopped(self, timeout=0):
        """等待上报线程收尾，最多 ``timeout`` 秒。

        脚本正常结束前调用，给停止请求一个发出去的机会；定时下线等强杀路径没有
        这个机会，服务端会按超时容差结算，所以这里只是"尽力而为"。
        """
        thread = self._thread
        if thread is None or not thread.is_alive() or timeout <= 0:
            return
        try:
            thread.join(timeout)
        except Exception as exc:
            print("等待后台上报线程结束失败：{}".format(exc))

    # ------------------------------------------------------------------ 线程主体

    def _worker(self, app_version, release_id):
        """线程入口：吞掉一切异常，只打印日志（文档 19.2）。"""
        try:
            self._run(app_version, release_id)
        except InstallationDisabled as exc:
            print("后台已禁用该安装实例，停止上报：{}".format(exc))
        except Exception as exc:
            print("后台上报线程结束：{}".format(exc))

    def _run(self, app_version, release_id):
        """注册 → 开始会话 → 心跳循环 → 停止。

        设备刚开机时网络可能还没就绪，因此"建立会话"这一步允许有限次重试：网络
        不可达按退避重试，注册/开始会话失败（限流、实例尚未登记等）也隔一个间隔
        再试。重试全部失败就安静退出——后台是辅助能力，不能因为统计失败影响挂机。
        """
        identity = self._load_identity()

        for attempt in range(1, SESSION_MAX_ATTEMPTS + 1):
            try:
                self._register(identity, app_version, release_id)
                run_id = _new_run_id(identity["install_id"])
                if not self._start_run(identity, run_id, app_version, release_id):
                    time.sleep(HEARTBEAT_MIN_SECONDS)
                    continue

                outcome, reason = self._heartbeat_loop(
                    identity, run_id, app_version, release_id
                )
                if outcome == "stopped":
                    self._stop_run(identity, run_id, reason)
                    return
                # outcome == "expired"：会话已被服务端结束（多为超时扫描或后台重启），
                # 换新的 run_id 重新开始（文档 10.3：已结束的会话不得复活）。
                print("后台会话已结束，准备用新的 run_id 重新开始")
                time.sleep(2)
            except BackendOffline as exc:
                wait = HEARTBEAT_BACKOFF_SECONDS[
                    min(attempt - 1, len(HEARTBEAT_BACKOFF_SECONDS) - 1)
                ]
                print(
                    "后台暂时不可达（第 {} 次），{} 秒后重试：{}".format(
                        attempt, wait, exc
                    )
                )
                time.sleep(wait)

        print("后台会话未能建立，本轮不再上报")

    # ------------------------------------------------------------------ 各步骤

    def _register(self, identity, app_version, release_id, force=False):
        """注册 / 刷新安装实例（幂等，文档 8.4）。

        注册接口对同一 ``install_id`` 有 **10 次/天** 的限流（文档 10.4），而脚本
        一天内可能被重启很多次，所以默认只在「今天还没注册过」或「昵称变了」时才
        调用；确实需要（例如后台没有这个实例）时才用 ``force`` 跳过判断。
        """
        name = identity.get("display_name", "")
        today = time.strftime("%Y-%m-%d")
        if not force:
            already_today = identity.get("last_register_date") == today
            name_synced = name == identity.get("synced_display_name", "")
            if already_today and name_synced:
                return True

        # 候选昵称：先按界面/本地记录的值注册，被拒时再退一步不带昵称。
        candidates = []
        for candidate in (name, ""):
            if candidate in candidates:
                continue
            if candidate and candidate == identity.get("rejected_display_name"):
                continue
            candidates.append(candidate)

        for attempt_name in candidates:
            status, body = self._request(
                "POST",
                API_PREFIX + "/installations/register",
                {
                    "install_id": identity["install_id"],
                    "display_name": attempt_name,
                    "app_version": app_version,
                    "release_id": release_id,
                    "update_channel": "stable",
                },
            )
            if 200 <= status < 300:
                identity["last_register_date"] = today
                identity["synced_display_name"] = attempt_name
                identity.pop("rejected_display_name", None)
                self._save_identity(identity)
                print(
                    "后台注册成功：{}（昵称：{}）".format(
                        identity["install_id"],
                        attempt_name or "沿用后台当前值",
                    )
                )
                return True

            code = _error_code(body)
            if code == "INSTALLATION_DISABLED":
                raise InstallationDisabled(status, code, _error_message(body))
            if attempt_name and code == "INVALID_ARGUMENT":
                # 昵称被拒（保留名/字符集等）时退一步：不带昵称再注册一次，
                # 会话统计比昵称重要。
                print("后台拒绝昵称，改为不上报昵称：{}".format(_error_message(body)))
                identity["rejected_display_name"] = attempt_name
                self._save_identity(identity)
                continue
            print(
                "后台注册失败：HTTP {} {} {}".format(
                    status, code, _error_message(body)
                )
            )
            return False
        return False

    def _start_run(self, identity, run_id, app_version, release_id):
        """开始会话；成功返回 True。"""
        payload = {
            "install_id": identity["install_id"],
            "run_id": run_id,
            "app_version": app_version,
            "release_id": release_id,
        }
        status, body = self._request("POST", API_PREFIX + "/runs", payload)
        if 200 <= status < 300:
            if body.get("replaced_run_id"):
                print("后台已关闭同一实例的上一个会话：{}".format(body["replaced_run_id"]))
            print("后台会话已开始：{}".format(run_id))
            return True

        code = _error_code(body)
        if code == "INSTALLATION_DISABLED":
            raise InstallationDisabled(status, code, _error_message(body))
        if code == "CONFLICT":
            # run_id 撞车（概率极低）或并发冲突，换一个 run_id 让上层重试。
            print("后台会话冲突，将使用新的 run_id 重试")
            return False
        if code == "NOT_FOUND":
            # 后台没有这个实例：补一次注册再试。
            if self._register(identity, app_version, release_id, force=True):
                status, body = self._request("POST", API_PREFIX + "/runs", payload)
                if 200 <= status < 300:
                    print("后台会话已开始：{}".format(run_id))
                    return True
        print(
            "后台开始会话失败：HTTP {} {} {}".format(
                status, code, _error_message(body)
            )
        )
        return False

    def _heartbeat_loop(self, identity, run_id, app_version, release_id):
        """心跳循环。返回 ``("stopped", reason)`` 或 ``("expired", None)``。

        先立刻发一次心跳（确认会话、顺便取回服务端下发的间隔），之后按间隔发送；
        等待心跳间隔期间同时等待停止命令，停止请求最迟一个间隔内被处理。
        """
        interval = HEARTBEAT_FALLBACK_SECONDS
        failures = 0
        client_seq = 0

        while True:
            client_seq += 1
            try:
                status, body = self._request(
                    "POST",
                    "{}/runs/{}/heartbeat".format(API_PREFIX, run_id),
                    {
                        "install_id": identity["install_id"],
                        "client_seq": client_seq,
                        "app_version": app_version,
                        "release_id": release_id,
                    },
                )
                if 200 <= status < 300:
                    failures = 0
                    interval = self._next_interval(body)
                else:
                    code = _error_code(body)
                    if code == "RUN_ALREADY_STOPPED":
                        return "expired", None
                    if code == "INSTALLATION_DISABLED":
                        raise InstallationDisabled(
                            status, code, _error_message(body)
                        )
                    failures += 1
                    print(
                        "后台心跳失败：HTTP {} {} {}".format(
                            status, code, _error_message(body)
                        )
                    )
            except InstallationDisabled:
                raise
            except Exception as exc:
                failures += 1
                print("后台心跳失败：{}".format(exc))

            if failures:
                interval = HEARTBEAT_BACKOFF_SECONDS[
                    min(failures, len(HEARTBEAT_BACKOFF_SECONDS)) - 1
                ]

            reason = self._wait_command(interval)
            if reason is not None:
                return "stopped", reason

    def _next_interval(self, body):
        """读取服务端下发的下次心跳间隔，异常值回落到默认 180 秒。"""
        try:
            value = int(body.get("next_heartbeat_seconds"))
        except Exception:
            return HEARTBEAT_FALLBACK_SECONDS
        if value <= 0:
            return HEARTBEAT_FALLBACK_SECONDS
        return max(HEARTBEAT_MIN_SECONDS, min(value, HEARTBEAT_MAX_SECONDS))

    def _stop_run(self, identity, run_id, reason):
        """尽力而为地结束会话；失败只打印（服务端会按超时容差结算）。"""
        try:
            status, body = self._request(
                "POST",
                "{}/runs/{}/stop".format(API_PREFIX, run_id),
                {"install_id": identity["install_id"], "reason": reason},
            )
            if 200 <= status < 300:
                print("后台会话已结束：{}（{}）".format(run_id, reason))
            else:
                print(
                    "后台停止会话失败：HTTP {} {} {}".format(
                        status, _error_code(body), _error_message(body)
                    )
                )
        except Exception as exc:
            print("后台停止会话失败：{}".format(exc))

    def _wait_command(self, timeout):
        """等待停止命令；超时返回 None。"""
        try:
            return self._commands.get(timeout=max(1, int(timeout)))
        except queue.Empty:
            return None
        except Exception as exc:
            print("读取后台命令失败：{}".format(exc))
            time.sleep(1)
            return None

    # ------------------------------------------------------------------ 身份持久化

    def _load_identity(self):
        """读取本地身份；缺失或损坏时生成新的 ``install_id``。

        界面里填的昵称优先于本地记录，且写回本地，下次启动无需重新填写。
        """
        data = {}
        try:
            raw = KeyValue.get(IDENTITY_KEY, "")
        except Exception as exc:
            raw = ""
            print("读取后台身份失败：{}".format(exc))
        if isinstance(raw, str) and raw.strip():
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    data = parsed
            except Exception:
                print("后台身份数据损坏，重新生成")

        changed = False
        if not _valid_install_id(data.get("install_id")):
            data["install_id"] = _new_install_id()
            data["last_register_date"] = ""
            data["synced_display_name"] = ""
            data.pop("rejected_display_name", None)
            changed = True
            print("生成后台安装实例标识：{}".format(data["install_id"]))

        sanitized = _sanitize_display_name(data.get("display_name"))
        if sanitized != data.get("display_name"):
            data["display_name"] = sanitized
            changed = True
        if self._ui_display_name and self._ui_display_name != data.get("display_name"):
            data["display_name"] = self._ui_display_name
            changed = True

        if changed:
            self._save_identity(data)
        return data

    def _save_identity(self, data):
        """写回身份。失败不影响会话上报（只是下次启动会重新生成或重填）。"""
        try:
            KeyValue.save(
                IDENTITY_KEY, json.dumps(data, ensure_ascii=False)
            )
        except Exception as exc:
            print("保存后台身份失败：{}".format(exc))

    # ------------------------------------------------------------------ HTTP

    def _verify_argument(self):
        """返回 ``requests`` 的 ``verify`` 参数。

        后台是自签证书，用系统信任库校验必然失败，因此固定校验随运行时下发的
        证书文件；一旦固定校验失败或证书缺失，降级为不校验并打印告警——后台这
        条链路只承载统计上报，不承载可执行代码（清单与 ZIP 仍走 OSS/GitHub 的
        合法证书），所以降级不会让设备执行到不可信代码。
        """
        if self._tls_verify is not None:
            return self._tls_verify
        if os.path.isfile(TLS_PIN_PATH):
            # 记住这次决定：后面请求（含固定校验失败后的降级）都以它为准。
            self._tls_verify = TLS_PIN_PATH
            return self._tls_verify
        print("后台证书文件缺失，本次改为不校验 TLS：{}".format(TLS_PIN_PATH))
        self._tls_verify = False
        return False

    def _request(self, method, path, payload=None):
        """发送一次后台请求，返回 ``(status_code, body_dict)``。

        网络层异常（超时、连接失败）按文档 19 重试 1 次后抛 ``BackendOffline``；
        HTTP 错误码不抛异常，交给调用方按 ``error.code`` 分支处理。
        """
        url = BACKEND_BASE_URL.rstrip("/") + path

        for _ in range(REQUEST_RETRY_TIMES + 1):
            last_error = None
            try:
                response = requests.request(
                    method,
                    url,
                    json=payload,
                    timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
                    verify=self._verify_argument(),
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "Accept": "application/json",
                    },
                )
            except requests.exceptions.SSLError as exc:
                last_error = exc
                if isinstance(self._tls_verify, str):
                    print("后台证书固定校验失败，降级为不校验 TLS：{}".format(exc))
                    self._tls_verify = False
                    continue
            except requests.exceptions.RequestException as exc:
                last_error = exc
            except Exception as exc:
                last_error = exc

            if last_error is None:
                try:
                    body = response.json()
                except Exception:
                    body = {}
                if not isinstance(body, dict):
                    body = {}
                return response.status_code, body

            print("后台请求失败（{}）：{}".format(path, last_error))
            time.sleep(1)

        raise BackendOffline(str(last_error))


def start_reporting(uiconfig, release_id=""):
    """便捷入口：按当前脚本版本启动上报（失败绝不影响任务执行）。"""
    try:
        BackendClient.instance().start(
            uiconfig,
            app_version=VERSION,
            release_id=release_id,
        )
    except Exception as exc:
        print("启动后台上报失败：{}".format(exc))


def stop_reporting(reason=DEFAULT_END_REASON, wait_seconds=8):
    """便捷入口：请求结束会话，并短暂等待线程把请求发出去。

    脚本主体已经结束，这里等几秒不会影响任务执行，却能显著提高"会话被正常
    结束而不是靠超时兜底"的比例。等待时间有上限，后台慢也不会拖住脚本退出。
    """
    try:
        client = BackendClient.instance()
        client.request_stop(reason)
        client.wait_stopped(wait_seconds)
    except Exception as exc:
        print("结束后台上报失败：{}".format(exc))
