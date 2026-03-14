"""单例 GUI：通过 Unix socket 与已有进程通信，实现「只唤起一个窗口」。"""

import os
import socket

_SOCKET_PATH = f"/tmp/alfredpy-gui-{os.getuid()}.sock"
_CMD_SHOW = b"show"


def try_show_existing() -> bool:
    """若已有 GUI 进程在监听，则发送 show 并返回 True；否则返回 False。"""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(_SOCKET_PATH)
        s.sendall(_CMD_SHOW)
        s.close()
        return True
    except (FileNotFoundError, ConnectionRefusedError, socket.error, OSError):
        return False


def get_socket_path() -> str:
    return _SOCKET_PATH


def get_show_cmd() -> bytes:
    return _CMD_SHOW
