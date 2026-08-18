#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import ctypes
import faulthandler
import os
import platform
import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
LOCAL_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "EnterpriseKnowledgeRetrieval"
LOG_PATH = LOCAL_DATA / "logs" / "startup_error.log"
FAULT_PATH = LOCAL_DATA / "logs" / "crash_diagnostic.log"


def append_log(title: str, content: str = "") -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write("\n" + "=" * 72 + "\n")
            handle.write(f"[{datetime.now().isoformat(timespec='seconds')}] {title}\n")
            if content:
                handle.write(content.rstrip() + "\n")
    except Exception:
        pass


def show_error(title: str, message: str) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, 0x10 | 0x1000)
        return
    except Exception:
        pass
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror(title, message, parent=root)
        root.destroy()
    except Exception:
        print(f"\n{title}\n{message}\n", file=sys.stderr)


def environment_report() -> str:
    return "\n".join([
        f"Python version: {sys.version}",
        f"System: {platform.platform()}",
        f"Architecture: {platform.architecture()[0]}",
    ])


def install_exception_hook() -> None:
    def hook(exc_type, exc_value, exc_tb):
        details = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        append_log("Unhandled exception", details)
        show_error(
            "企业知识检索系统启动失败",
            "程序发生未处理错误。\n\n"
            f"错误信息：{exc_value}\n\n"
            f"详细日志：\n{LOG_PATH}",
        )
    sys.excepthook = hook


def main() -> int:
    os.chdir(ROOT)
    append_log("Startup environment", environment_report())
    install_exception_hook()

    fault_handle = None
    try:
        FAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        fault_handle = FAULT_PATH.open("a", encoding="utf-8")
        faulthandler.enable(file=fault_handle, all_threads=True)
    except Exception:
        fault_handle = None

    try:
        import PySide6
        append_log("PySide6 import succeeded", f"Version: {getattr(PySide6, '__version__', 'unknown')}")
    except Exception as exc:
        append_log("PySide6 import failed", traceback.format_exc())
        show_error(
            "图形界面组件加载失败",
            "PySide6/Qt 没有正确加载。常见原因是依赖安装不完整、Python 位数不匹配，"
            "或 Windows 缺少 Microsoft Visual C++ 运行库。\n\n"
            f"错误信息：{exc}\n\n详细日志：\n{LOG_PATH}",
        )
        return 2

    try:
        import enterprise_knowledge_retrieval
        append_log("Main module import succeeded")
        return int(enterprise_knowledge_retrieval.main())
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 0
        append_log("Normal exit", f"Exit code: {code}")
        return code
    except BaseException as exc:
        append_log("Application startup failed", traceback.format_exc())
        show_error(
            "企业知识检索系统启动失败",
            f"错误信息：{exc}\n\n详细日志：\n{LOG_PATH}",
        )
        return 1
    finally:
        if fault_handle is not None:
            try:
                fault_handle.flush()
                fault_handle.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
