#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enterprise Knowledge Retrieval System - Qt Workbench UI

界面结构参考现代编程工具的 Workbench 模型：
Activity Bar -> Primary Sidebar -> Editor Area -> Auxiliary Bar -> Status Bar。
检索、索引和问答核心来自 rag_core.py，界面与核心解耦。
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import sqlite3
import sys
import threading
import traceback
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import (
    QByteArray,
    QEvent,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QThread,
    QTimer,
    QUrl,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QDesktopServices,
    QFont,
    QFontDatabase,
    QIcon,
    QKeySequence,
    QPainter,
    QPixmap,
    QShortcut,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QInputDialog,
    QMenu,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabBar,
    QTabWidget,
    QTextBrowser,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

import rag_core as core


APP_TITLE = "企业知识检索系统"
APP_SUBTITLE = "Enterprise Knowledge Retrieval"


def resource_path(name: str) -> Path:
    """Return a bundled resource path in source and PyInstaller builds."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / name


def application_icon() -> QIcon:
    for name in ("app_icon.png", "app_icon.ico"):
        path = resource_path(name)
        if path.exists():
            icon = QIcon(str(path))
            if not icon.isNull():
                return icon
    return QIcon()


class Theme:
    bg = "#0D1117"
    rail = "#15191F"
    sidebar = "#11161D"
    sidebar_alt = "#151B23"
    editor = "#0D1117"
    surface = "#151B23"
    surface_2 = "#1A212B"
    surface_3 = "#202834"
    border = "#29313D"
    border_soft = "#202732"
    text = "#E6EDF3"
    text_2 = "#C8D1DC"
    muted = "#8B949E"
    muted_2 = "#66707D"
    accent = "#4C8BF5"
    accent_hover = "#5A98FF"
    accent_soft = "#17243A"
    green = "#3FB950"
    orange = "#D29922"
    red = "#F85149"
    user = "#172131"
    user_border = "#2A3C58"
    selection = "#264F78"
    status = "#1B64B0"


# Chat fonts use points instead of pixels.  Points remain visibly consistent under
# Windows DPI scaling, while 19px is only about 14pt at 100% scaling.
CHAT_BODY_FONT_PT = 18
CHAT_INPUT_FONT_PT = 17
CHAT_TITLE_FONT_PT = 14


APP_QSS = f"""
* {{
    font-family: "Segoe UI", "Microsoft YaHei UI";
    font-size: 14px;
    color: {Theme.text};
}}
QWidget {{
    background: {Theme.bg};
}}
QMainWindow {{
    background: {Theme.bg};
}}
QToolTip {{
    background: {Theme.surface_3};
    color: {Theme.text};
    border: 1px solid {Theme.border};
    padding: 5px 7px;
}}
QPushButton, QToolButton {{
    border: 1px solid {Theme.border};
    border-radius: 6px;
    background: {Theme.surface};
    color: {Theme.text_2};
    padding: 6px 10px;
}}
QPushButton:hover, QToolButton:hover {{
    background: {Theme.surface_2};
    border-color: #3A4554;
    color: {Theme.text};
}}
QPushButton:pressed, QToolButton:pressed {{
    background: {Theme.surface_3};
}}
QPushButton:disabled, QToolButton:disabled {{
    color: {Theme.muted_2};
    background: #12171D;
    border-color: {Theme.border_soft};
}}
QPushButton[primary="true"] {{
    background: {Theme.accent};
    color: white;
    border-color: {Theme.accent};
    font-weight: 600;
}}
QPushButton[primary="true"]:hover {{
    background: {Theme.accent_hover};
    border-color: {Theme.accent_hover};
}}
QPushButton[ghost="true"], QToolButton[ghost="true"] {{
    background: transparent;
    border-color: transparent;
    padding: 5px 7px;
}}
QPushButton[ghost="true"]:hover, QToolButton[ghost="true"]:hover {{
    background: {Theme.surface_2};
    border-color: {Theme.border_soft};
}}
QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox {{
    background: {Theme.surface};
    border: 1px solid {Theme.border};
    border-radius: 6px;
    selection-background-color: {Theme.selection};
    color: {Theme.text};
    padding: 6px 8px;
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border-color: {Theme.accent};
}}
QComboBox::drop-down {{
    width: 24px;
    border: none;
}}
QComboBox QAbstractItemView {{
    background: {Theme.surface_2};
    border: 1px solid {Theme.border};
    selection-background-color: {Theme.selection};
    outline: none;
}}
QCheckBox {{
    spacing: 8px;
    color: {Theme.text_2};
}}
QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border-radius: 3px;
    border: 1px solid #4A5564;
    background: {Theme.surface};
}}
QCheckBox::indicator:checked {{
    background: {Theme.accent};
    border-color: {Theme.accent};
}}
QScrollBar:vertical {{
    width: 10px;
    margin: 0;
    background: transparent;
}}
QScrollBar::handle:vertical {{
    background: #374151;
    min-height: 36px;
    border-radius: 4px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: #4B5563;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0;
    background: transparent;
}}
QScrollBar:horizontal {{
    height: 10px;
    background: transparent;
}}
QScrollBar::handle:horizontal {{
    background: #374151;
    min-width: 36px;
    border-radius: 4px;
    margin: 2px;
}}
QSplitter::handle {{
    background: {Theme.border_soft};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:vertical {{
    height: 1px;
}}
QTabWidget::pane {{
    border: none;
    background: {Theme.editor};
}}
QTabBar {{
    background: {Theme.sidebar};
}}
QTabBar::tab {{
    background: {Theme.sidebar};
    color: {Theme.muted};
    min-width: 120px;
    height: 34px;
    padding: 0 14px;
    border-right: 1px solid {Theme.border_soft};
    border-bottom: 1px solid {Theme.border};
}}
QTabBar::tab:selected {{
    color: {Theme.text};
    background: {Theme.editor};
    border-top: 1px solid {Theme.accent};
    border-bottom: 1px solid {Theme.editor};
}}
QTabBar::tab:hover:!selected {{
    background: {Theme.sidebar_alt};
    color: {Theme.text_2};
}}
QTreeWidget {{
    background: {Theme.editor};
    alternate-background-color: #10151C;
    border: none;
    outline: none;
    gridline-color: {Theme.border_soft};
}}
QTreeWidget::item {{
    min-height: 30px;
    padding: 3px 5px;
    border-bottom: 1px solid {Theme.border_soft};
}}
QTreeWidget::item:selected {{
    background: {Theme.selection};
}}
QHeaderView::section {{
    background: {Theme.sidebar_alt};
    color: {Theme.muted};
    padding: 7px 8px;
    border: none;
    border-right: 1px solid {Theme.border_soft};
    border-bottom: 1px solid {Theme.border};
    font-weight: 600;
}}
QProgressBar {{
    border: none;
    background: {Theme.surface_3};
    height: 3px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: {Theme.accent};
}}
"""


ICONS: dict[str, str] = {
    "chat": '<path d="M4 4.5h16v11H9l-5 4v-15z"/><path d="M8 9h8M8 12h5"/>',
    "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1A1.7 1.7 0 0 0 9 4.6 1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1z"/>',
    "new": '<path d="M12 5v14M5 12h14"/>',
    "folder": '<path d="M3 6.5h7l2 2h9v10H3z"/><path d="M3 6.5v-2h7l2 2"/>',
    "index": '<path d="M4 5h16M4 12h16M4 19h16"/><circle cx="7" cy="5" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="17" cy="19" r="1" fill="currentColor"/>',
    "send": '<path d="M4 4l17 8-17 8 3-8z"/><path d="M7 12h14"/>',
    "stop": '<rect x="6" y="6" width="12" height="12" rx="1"/>',
    "copy": '<rect x="8" y="8" width="11" height="11" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
    "sources": '<path d="M4 5h16v4H4zM4 12h16v7H4z"/><path d="M8 7h8M8 15h8"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "collapse": '<path d="M9 5l7 7-7 7"/>',
    "expand": '<path d="M15 5l-7 7 7 7"/>',
    "file": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v5h5"/>',
    "open": '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 13v7H4V6h7"/>',
    "refresh": '<path d="M20 7v5h-5"/><path d="M4 17v-5h5"/><path d="M6.1 8a7 7 0 0 1 11.3-2L20 12M4 12l2.6 6a7 7 0 0 0 11.3-2"/>',
    "trash": '<path d="M5 7h14M9 7V4h6v3M7 7l1 14h8l1-14"/>',
    "chevron": '<path d="M9 5l7 7-7 7"/>',
    "panel": '<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M15 4v16"/>',
}


def svg_icon(name: str, color: str = Theme.muted, size: int = 18) -> QIcon:
    body = ICONS.get(name, ICONS["file"])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{body}</svg>'''
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def set_margins(layout: QVBoxLayout | QHBoxLayout, left: int, top: int, right: int, bottom: int) -> None:
    layout.setContentsMargins(left, top, right, bottom)


def compact_path(path: str, limit: int = 46) -> str:
    path = str(path or "").strip()
    if not path:
        return "未选择"
    if len(path) <= limit:
        return path
    return "…" + path[-(limit - 1):]


def open_local_path(path: str) -> None:
    path = str(path or "").strip()
    if not path:
        return
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    except Exception as exc:
        QMessageBox.warning(None, "打开失败", str(exc))


def ui_state_path() -> Path:
    return core.default_settings_path().with_name("ui_state.json")


def load_ui_state() -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "folder": "",
        "db": str(core.default_db_path()),
        "sidebar_width": 270,
        "inspector_width": 340,
        "window_width": 1500,
        "window_height": 900,
        "window_x": None,
        "window_y": None,
    }
    path = ui_state_path()
    if path.exists():
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                defaults.update(value)
        except Exception:
            pass
    return defaults


def save_ui_state(data: dict[str, Any]) -> None:
    path = ui_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def conversations_path() -> Path:
    return core.default_settings_path().with_name("conversations.json")


def conversation_now() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat(sep=" ")


def make_conversation(title: str = "新对话") -> dict[str, Any]:
    now = conversation_now()
    return {
        "id": uuid.uuid4().hex,
        "title": title.strip() or "新对话",
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }


def conversation_title_from_question(question: str, limit: int = 26) -> str:
    title = " ".join(str(question or "").split()).strip()
    if not title:
        return "新对话"
    if len(title) > limit:
        title = title[: limit - 1].rstrip() + "…"
    return title


def load_conversation_state() -> dict[str, Any]:
    state: dict[str, Any] = {"version": 1, "current_id": "", "conversations": []}
    path = conversations_path()
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                state.update(raw)
        except Exception:
            pass

    cleaned: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in state.get("conversations", []):
        if not isinstance(item, dict):
            continue
        conversation_id = str(item.get("id", "")).strip() or uuid.uuid4().hex
        if conversation_id in seen:
            continue
        seen.add(conversation_id)
        messages = item.get("messages", [])
        if not isinstance(messages, list):
            messages = []
        normalized_messages: list[dict[str, Any]] = []
        for message in messages:
            if not isinstance(message, dict):
                continue
            role = str(message.get("role", "")).strip()
            content = str(message.get("content", ""))
            if role not in {"user", "assistant"} or not content.strip():
                continue
            normalized: dict[str, Any] = {"role": role, "content": content}
            if role == "assistant":
                sources = message.get("source_items", [])
                normalized["source_items"] = list(sources) if isinstance(sources, list) else []
            normalized_messages.append(normalized)
        now = conversation_now()
        cleaned.append(
            {
                "id": conversation_id,
                "title": str(item.get("title", "新对话")).strip() or "新对话",
                "created_at": str(item.get("created_at", now)),
                "updated_at": str(item.get("updated_at", item.get("created_at", now))),
                "messages": normalized_messages,
            }
        )

    if not cleaned:
        cleaned.append(make_conversation())
    cleaned.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    current_id = str(state.get("current_id", ""))
    if current_id not in {str(item["id"]) for item in cleaned}:
        current_id = str(cleaned[0]["id"])
    return {"version": 1, "current_id": current_id, "conversations": cleaned}


def save_conversation_state(state: dict[str, Any]) -> None:
    path = conversations_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "current_id": str(state.get("current_id", "")),
        "conversations": list(state.get("conversations", [])),
    }
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp_path.replace(path)


def db_summary(db_path: Path) -> tuple[int, int]:
    if not db_path.exists():
        return 0, 0
    try:
        conn = sqlite3.connect(str(db_path))
        files = int(conn.execute("SELECT COUNT(*) FROM files WHERE status='indexed'").fetchone()[0])
        chunks = int(conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
        conn.close()
        return files, chunks
    except Exception:
        return 0, 0


@dataclass
class SettingsState:
    api_url: str
    api_key: str
    model: str
    top_k: int
    save_key: bool
    require_all: bool = False
    match_case: bool = False
    phrase: bool = False


class ActivityButton(QToolButton):
    activated = Signal(str)

    def __init__(self, activity: str, icon_name: str, tooltip: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.activity = activity
        self.setToolTip(tooltip)
        self.setIcon(svg_icon(icon_name, Theme.muted, 21))
        self.setIconSize(QSize(21, 21))
        self.setCheckable(True)
        self.setFixedSize(48, 46)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(lambda: self.activated.emit(self.activity))
        self.setStyleSheet(f"""
            QToolButton {{
                background: transparent;
                border: none;
                border-left: 2px solid transparent;
                border-radius: 0;
                padding: 0;
            }}
            QToolButton:hover {{ background: #1E242C; }}
            QToolButton:checked {{
                background: #1B2129;
                border-left-color: {Theme.accent};
            }}
        """)

    def set_active(self, active: bool, icon_name: str) -> None:
        self.setChecked(active)
        self.setIcon(svg_icon(icon_name, Theme.text if active else Theme.muted, 21))


class ActivityRail(QFrame):
    activityChanged = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("activityRail")
        self.setFixedWidth(49)
        self.setStyleSheet(f"QFrame#activityRail {{ background: {Theme.rail}; border-right: 1px solid {Theme.border_soft}; }}")
        layout = QVBoxLayout(self)
        set_margins(layout, 0, 6, 0, 4)
        layout.setSpacing(1)

        brand = QLabel("Y")
        brand.setAlignment(Qt.AlignCenter)
        brand.setFixedSize(48, 38)
        brand.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {Theme.text}; background: transparent;")
        layout.addWidget(brand)

        self.buttons: dict[str, tuple[ActivityButton, str]] = {}
        for activity, icon_name, tooltip in (
            ("chat", "chat", "对话  Ctrl+1"),
            ("knowledge", "database", "知识库  Ctrl+2"),
            ("search", "search", "精确检索  Ctrl+Shift+F"),
        ):
            button = ActivityButton(activity, icon_name, tooltip)
            button.activated.connect(self.select)
            self.buttons[activity] = (button, icon_name)
            layout.addWidget(button)

        layout.addStretch(1)
        settings = ActivityButton("settings", "settings", "设置  Ctrl+, ")
        settings.activated.connect(self.select)
        self.buttons["settings"] = (settings, "settings")
        layout.addWidget(settings)
        self.select("chat")

    @Slot(str)
    def select(self, activity: str) -> None:
        for key, (button, icon_name) in self.buttons.items():
            button.set_active(key == activity, icon_name)
        self.activityChanged.emit(activity)


class SectionTitle(QLabel):
    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text.upper(), parent)
        self.setStyleSheet(f"color: {Theme.muted}; font-size: 10px; font-weight: 700; letter-spacing: 1px; background: transparent;")


class SidebarShell(QFrame):
    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebarShell")
        self.setStyleSheet(f"QFrame#sidebarShell {{ background: {Theme.sidebar}; border-right: 1px solid {Theme.border_soft}; }}")
        self.root = QVBoxLayout(self)
        set_margins(self.root, 0, 0, 0, 0)
        self.root.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(36)
        header.setStyleSheet(f"background: {Theme.sidebar}; border-bottom: 1px solid {Theme.border_soft};")
        header_layout = QHBoxLayout(header)
        set_margins(header_layout, 12, 0, 8, 0)
        label = QLabel(title.upper())
        label.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {Theme.text_2}; background: transparent;")
        header_layout.addWidget(label)
        header_layout.addStretch(1)
        self.root.addWidget(header)

        self.body = QWidget()
        self.body.setStyleSheet(f"background: {Theme.sidebar};")
        self.body_layout = QVBoxLayout(self.body)
        set_margins(self.body_layout, 12, 12, 12, 12)
        self.body_layout.setSpacing(8)
        self.root.addWidget(self.body, 1)


class ChatSidebar(SidebarShell):
    newChatRequested = Signal()
    conversationSelected = Signal(str)
    renameConversationRequested = Signal(str)
    deleteConversationRequested = Signal(str)

    def __init__(self) -> None:
        super().__init__("对话")
        new_button = QPushButton("  新建对话")
        new_button.setIcon(svg_icon("new", Theme.text, 16))
        new_button.setIconSize(QSize(16, 16))
        new_button.setProperty("primary", True)
        new_button.setCursor(Qt.PointingHandCursor)
        new_button.clicked.connect(self.newChatRequested)
        self.body_layout.addWidget(new_button)

        self.body_layout.addSpacing(8)
        self.body_layout.addWidget(SectionTitle("历史会话"))
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setIndentation(0)
        self.tree.setUniformRowHeights(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.setStyleSheet(
            f"QTreeWidget {{ background: transparent; border: none; padding: 0; }}"
            f"QTreeWidget::item {{ height: 34px; padding: 0 7px; border-radius: 5px; color: {Theme.text_2}; }}"
            f"QTreeWidget::item:hover {{ background: {Theme.surface_2}; }}"
            f"QTreeWidget::item:selected {{ background: {Theme.surface_3}; color: {Theme.text}; }}"
        )
        self.tree.itemClicked.connect(self._item_clicked)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.body_layout.addWidget(self.tree, 1)

        hint = QLabel("右键会话可重命名或删除。历史记录保存在本机，不会上传到模型服务。")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {Theme.muted_2}; font-size: 12px; background: transparent;")
        self.body_layout.addWidget(hint)

    def set_conversations(self, conversations: list[dict[str, Any]], current_id: str) -> None:
        self.tree.blockSignals(True)
        self.tree.clear()
        current_item: Optional[QTreeWidgetItem] = None
        for conversation in conversations:
            conversation_id = str(conversation.get("id", ""))
            title = str(conversation.get("title", "新对话"))
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.UserRole, conversation_id)
            item.setIcon(0, svg_icon("chat", Theme.muted, 15))
            updated = str(conversation.get("updated_at", ""))
            item.setToolTip(0, f"{title}\n最后更新：{updated}" if updated else title)
            self.tree.addTopLevelItem(item)
            if conversation_id == current_id:
                current_item = item
        if current_item is not None:
            self.tree.setCurrentItem(current_item)
            self.tree.scrollToItem(current_item)
        self.tree.blockSignals(False)

    @Slot(QTreeWidgetItem, int)
    def _item_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        conversation_id = str(item.data(0, Qt.UserRole) or "")
        if conversation_id:
            self.conversationSelected.emit(conversation_id)

    @Slot(QPoint)
    def _show_context_menu(self, position: QPoint) -> None:
        item = self.tree.itemAt(position)
        if item is None:
            return
        conversation_id = str(item.data(0, Qt.UserRole) or "")
        if not conversation_id:
            return
        menu = QMenu(self)
        rename_action = menu.addAction("重命名")
        delete_action = menu.addAction("删除")
        chosen = menu.exec(self.tree.viewport().mapToGlobal(position))
        if chosen == rename_action:
            self.renameConversationRequested.emit(conversation_id)
        elif chosen == delete_action:
            self.deleteConversationRequested.emit(conversation_id)


class KnowledgeSidebar(SidebarShell):
    chooseFolderRequested = Signal()
    chooseDbRequested = Signal()
    indexRequested = Signal()
    stopIndexRequested = Signal()

    def __init__(self) -> None:
        super().__init__("知识库")
        self.body_layout.addWidget(SectionTitle("工作区"))

        self.folder_title = QLabel("资料文件夹")
        self.folder_title.setStyleSheet(f"color: {Theme.text_2}; font-weight: 600; background: transparent;")
        self.body_layout.addWidget(self.folder_title)
        self.folder_value = QLabel("未选择")
        self.folder_value.setWordWrap(True)
        self.folder_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.folder_value.setStyleSheet(f"color: {Theme.muted}; background: transparent;")
        self.body_layout.addWidget(self.folder_value)

        folder_button = QPushButton("选择文件夹")
        folder_button.setIcon(svg_icon("folder", Theme.text_2, 16))
        folder_button.clicked.connect(self.chooseFolderRequested)
        self.body_layout.addWidget(folder_button)

        self.body_layout.addSpacing(6)
        self.db_title = QLabel("索引库")
        self.db_title.setStyleSheet(f"color: {Theme.text_2}; font-weight: 600; background: transparent;")
        self.body_layout.addWidget(self.db_title)
        self.db_value = QLabel("未选择")
        self.db_value.setWordWrap(True)
        self.db_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.db_value.setStyleSheet(f"color: {Theme.muted}; background: transparent;")
        self.body_layout.addWidget(self.db_value)

        db_button = QPushButton("选择索引库")
        db_button.setIcon(svg_icon("file", Theme.text_2, 16))
        db_button.clicked.connect(self.chooseDbRequested)
        self.body_layout.addWidget(db_button)

        self.body_layout.addSpacing(10)
        self.body_layout.addWidget(SectionTitle("索引"))
        self.summary = QLabel("尚未建立索引")
        self.summary.setStyleSheet(f"color: {Theme.muted}; background: transparent;")
        self.body_layout.addWidget(self.summary)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.body_layout.addWidget(self.progress)
        self.progress_detail = QLabel("就绪")
        self.progress_detail.setWordWrap(True)
        self.progress_detail.setStyleSheet(f"color: {Theme.muted}; font-size: 11px; background: transparent;")
        self.body_layout.addWidget(self.progress_detail)

        self.index_button = QPushButton("建立 / 重建索引")
        self.index_button.setIcon(svg_icon("index", "#FFFFFF", 16))
        self.index_button.setProperty("primary", True)
        self.index_button.clicked.connect(self.indexRequested)
        self.body_layout.addWidget(self.index_button)
        self.stop_button = QPushButton("停止索引")
        self.stop_button.setIcon(svg_icon("stop", Theme.muted, 15))
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stopIndexRequested)
        self.body_layout.addWidget(self.stop_button)
        self.body_layout.addStretch(1)

    def set_workspace(self, folder: str, db: str) -> None:
        self.folder_value.setText(compact_path(folder, 58))
        self.folder_value.setToolTip(folder)
        self.db_value.setText(compact_path(db, 58))
        self.db_value.setToolTip(db)

    def set_summary(self, files: int, chunks: int) -> None:
        self.summary.setText(f"{files} 个文件  ·  {chunks} 个片段" if files else "尚未建立索引")

    def set_indexing(self, active: bool) -> None:
        self.index_button.setEnabled(not active)
        self.stop_button.setEnabled(active)


class SearchSidebar(SidebarShell):
    searchRequested = Signal(str)

    def __init__(self) -> None:
        super().__init__("精确检索")
        self.body_layout.addWidget(SectionTitle("关键词"))
        self.query = QLineEdit()
        self.query.setPlaceholderText("输入关键词或 \"完整短语\"")
        self.query.returnPressed.connect(self._emit_search)
        self.body_layout.addWidget(self.query)

        self.require_all = QCheckBox("同一片段包含全部关键词")
        self.match_case = QCheckBox("区分大小写")
        self.phrase = QCheckBox("按完整短语检索")
        self.body_layout.addWidget(self.require_all)
        self.body_layout.addWidget(self.match_case)
        self.body_layout.addWidget(self.phrase)

        row = QHBoxLayout()
        label = QLabel("最大结果")
        label.setStyleSheet(f"color: {Theme.muted}; background: transparent;")
        self.limit = QSpinBox()
        self.limit.setRange(10, 5000)
        self.limit.setValue(500)
        row.addWidget(label)
        row.addStretch(1)
        row.addWidget(self.limit)
        self.body_layout.addLayout(row)

        search_button = QPushButton("搜索索引")
        search_button.setIcon(svg_icon("search", "#FFFFFF", 16))
        search_button.setProperty("primary", True)
        search_button.clicked.connect(self._emit_search)
        self.body_layout.addWidget(search_button)

        self.body_layout.addSpacing(12)
        tip = QLabel("精确检索不会调用模型，适合定位原文、编号、姓名和固定术语。双击结果可打开文件。")
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color: {Theme.muted}; background: transparent;")
        self.body_layout.addWidget(tip)
        self.body_layout.addStretch(1)

    def _emit_search(self) -> None:
        self.searchRequested.emit(self.query.text().strip())


class SettingsSidebar(SidebarShell):
    saved = Signal()
    modelChanged = Signal(str)

    def __init__(self, settings: SettingsState) -> None:
        super().__init__("设置")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        form = QWidget()
        form.setStyleSheet(f"background: {Theme.sidebar};")
        form_layout = QVBoxLayout(form)
        set_margins(form_layout, 0, 0, 0, 0)
        form_layout.setSpacing(8)

        form_layout.addWidget(SectionTitle("模型"))
        form_layout.addWidget(self._label("API 地址"))
        self.api_url = QLineEdit(settings.api_url)
        form_layout.addWidget(self.api_url)
        form_layout.addWidget(self._label("API Key"))
        self.api_key = QLineEdit(settings.api_key)
        self.api_key.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.api_key)
        form_layout.addWidget(self._label("模型名称"))
        self.model = QComboBox()
        self.model.setEditable(True)
        self.model.addItems(["deepseek-chat", "deepseek-reasoner", "deepseek-v4-pro", "gpt-4o-mini", "gpt-4o"])
        self.model.setCurrentText(settings.model)
        self.model.currentTextChanged.connect(self.modelChanged)
        form_layout.addWidget(self.model)
        self.save_key = QCheckBox("将 API Key 保存到本机")
        self.save_key.setChecked(settings.save_key)
        form_layout.addWidget(self.save_key)

        form_layout.addSpacing(10)
        form_layout.addWidget(SectionTitle("RAG"))
        top_row = QHBoxLayout()
        top_row.addWidget(self._label("引用片段数量"))
        top_row.addStretch(1)
        self.top_k = QSpinBox()
        self.top_k.setRange(1, 20)
        self.top_k.setValue(settings.top_k)
        top_row.addWidget(self.top_k)
        form_layout.addLayout(top_row)
        self.require_all = QCheckBox("同一片段包含全部关键词")
        self.require_all.setChecked(settings.require_all)
        self.match_case = QCheckBox("区分大小写")
        self.match_case.setChecked(settings.match_case)
        self.phrase = QCheckBox("按完整短语检索")
        self.phrase.setChecked(settings.phrase)
        form_layout.addWidget(self.require_all)
        form_layout.addWidget(self.match_case)
        form_layout.addWidget(self.phrase)

        form_layout.addSpacing(10)
        save_button = QPushButton("保存设置")
        save_button.setIcon(svg_icon("settings", "#FFFFFF", 16))
        save_button.setProperty("primary", True)
        save_button.clicked.connect(self.saved)
        form_layout.addWidget(save_button)

        security = QLabel("数据安全：本地资料先在本机检索，但生成回答时会将命中的片段发送给配置的模型接口。请勿处理涉密、客户隐私及未公开经营数据。")
        security.setWordWrap(True)
        security.setStyleSheet(f"color: {Theme.orange}; background: transparent; padding-top: 8px;")
        form_layout.addWidget(security)
        form_layout.addStretch(1)
        scroll.setWidget(form)
        self.body_layout.addWidget(scroll, 1)

    def _label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(f"color: {Theme.muted}; font-size: 11px; background: transparent;")
        return label

    def state(self) -> SettingsState:
        return SettingsState(
            api_url=self.api_url.text().strip(),
            api_key=self.api_key.text(),
            model=self.model.currentText().strip(),
            top_k=int(self.top_k.value()),
            save_key=self.save_key.isChecked(),
            require_all=self.require_all.isChecked(),
            match_case=self.match_case.isChecked(),
            phrase=self.phrase.isChecked(),
        )


class ComposerEdit(QPlainTextEdit):
    sendRequested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setPlaceholderText("询问知识库。可输入姓名、制度、型号、编号或直接追问……")
        self.setTabChangesFocus(True)
        self.setMinimumHeight(92)
        self.setMaximumHeight(190)
        self.setFixedHeight(98)
        composer_font = self.font()
        composer_font.setPointSize(12)
        self.setFont(composer_font)
        self.textChanged.connect(self._adjust_height)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            self.sendRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def _adjust_height(self) -> None:
        doc_height = int(self.document().size().height()) + 24
        self.setFixedHeight(max(92, min(190, doc_height + 6)))


class Composer(QFrame):
    sendRequested = Signal()
    stopRequested = Signal()
    modelChanged = Signal(str)

    def __init__(self, model: str) -> None:
        super().__init__()
        self.setObjectName("composer")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setStyleSheet(f"QFrame#composer {{ background: {Theme.surface}; border: 1px solid {Theme.border}; border-radius: 9px; }}")
        root = QVBoxLayout(self)
        set_margins(root, 10, 9, 10, 8)
        root.setSpacing(7)
        self.editor = ComposerEdit()
        self.editor.setStyleSheet(f"QPlainTextEdit {{ background: transparent; border: none; padding: 7px 7px; color: {Theme.text}; font-size: {CHAT_INPUT_FONT_PT}pt; }}")
        self.editor.sendRequested.connect(self.sendRequested)
        root.addWidget(self.editor)

        tools = QHBoxLayout()
        tools.setContentsMargins(1, 2, 2, 2)
        tools.setSpacing(8)
        self.context_label = QLabel("● 本地知识库")
        self.context_label.setStyleSheet(f"color: {Theme.green}; font-size: 12px; background: transparent;")
        tools.addWidget(self.context_label)
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems(["deepseek-chat", "deepseek-reasoner", "deepseek-v4-pro", "gpt-4o-mini", "gpt-4o"])
        self.model_combo.setCurrentText(model)
        self.model_combo.setFixedWidth(180)
        self.model_combo.setStyleSheet(f"QComboBox {{ background: transparent; border: none; color: {Theme.muted}; padding: 3px 5px; }} QComboBox:hover {{ color: {Theme.text}; background: {Theme.surface_2}; }}")
        self.model_combo.currentTextChanged.connect(self.modelChanged)
        tools.addWidget(self.model_combo)
        tools.addStretch(1)
        hint = QLabel("Enter 发送  ·  Shift+Enter 换行")
        hint.setStyleSheet(f"color: {Theme.muted_2}; font-size: 12px; background: transparent;")
        tools.addWidget(hint)

        self.stop_button = QToolButton()
        self.stop_button.setIcon(svg_icon("stop", Theme.muted, 15))
        self.stop_button.setToolTip("停止生成  Esc")
        self.stop_button.setProperty("ghost", True)
        self.stop_button.setVisible(False)
        self.stop_button.clicked.connect(self.stopRequested)
        tools.addWidget(self.stop_button)

        self.send_button = QPushButton("发送")
        self.send_button.setIcon(svg_icon("send", "#FFFFFF", 16))
        self.send_button.setIconSize(QSize(16, 16))
        self.send_button.setProperty("primary", True)
        self.send_button.setMinimumWidth(104)
        self.send_button.setFixedHeight(40)
        self.send_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.send_button.setStyleSheet(
            f"QPushButton {{ background: {Theme.accent}; color: #FFFFFF; padding: 7px 15px; "
            f"border: 1px solid {Theme.accent}; border-radius: 7px; font-size: 14px; font-weight: 600; }}"
            f"QPushButton:hover {{ background: {Theme.accent_hover}; border: 1px solid {Theme.accent_hover}; }}"
            f"QPushButton:pressed {{ background: #3D78D8; border: 1px solid #3D78D8; }}"
            f"QPushButton:disabled {{ background: #1B2430; color: {Theme.muted_2}; border: 1px solid {Theme.border}; }}"
        )
        self.send_button.clicked.connect(self.sendRequested)
        tools.addWidget(self.send_button, 0, Qt.AlignVCenter)
        root.addLayout(tools)

    def text(self) -> str:
        return self.editor.toPlainText().strip()

    def clear(self) -> None:
        self.editor.clear()

    def set_busy(self, busy: bool) -> None:
        self.send_button.setEnabled(not busy)
        self.model_combo.setEnabled(not busy)
        self.stop_button.setVisible(busy)

    def focus(self) -> None:
        self.editor.setFocus()


class AutoHeightTextBrowser(QTextBrowser):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setOpenExternalLinks(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("QTextBrowser { background: transparent; border: none; padding: 0; margin: 0; }")
        self.document().setDocumentMargin(0)
        self._apply_chat_font()
        self.document().documentLayout().documentSizeChanged.connect(self._sync_height)

    def _chat_font(self) -> QFont:
        font = QFont(self.font())
        if not font.family():
            font.setFamily("Microsoft YaHei UI")
        font.setPointSizeF(float(CHAT_BODY_FONT_PT))
        return font

    def _apply_chat_font(self) -> None:
        # QTextDocument has its own default font. Setting only QWidget/QSS is not
        # enough because setMarkdown() creates paragraph/list formats internally.
        font = self._chat_font()
        self.setFont(font)
        self.document().setDefaultFont(font)

    def _enforce_document_font_sizes(self) -> None:
        """Force real point sizes onto Markdown-created text fragments.

        Qt's Markdown importer may create explicit fragment fonts that ignore the
        document stylesheet. Applying a point size per block makes the visible
        result deterministic on Windows at 100%-200% DPI scaling.
        """
        block = self.document().begin()
        while block.isValid():
            level = int(block.blockFormat().headingLevel())
            if level == 1:
                size = 25.0
            elif level == 2:
                size = 21.0
            elif level == 3:
                size = 18.0
            else:
                size = float(CHAT_BODY_FONT_PT)
            cursor = QTextCursor(block)
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            char_format = QTextCharFormat()
            char_format.setFontPointSize(size)
            cursor.mergeCharFormat(char_format)
            block = block.next()

    def _document_css(self) -> str:
        return f"""
            html, body, p, div, span, li, ul, ol, table, tr, td, th {{
                color: {Theme.text_2};
                font-family: 'Segoe UI', 'Microsoft YaHei UI';
                font-size: {CHAT_BODY_FONT_PT}pt;
                line-height: 1.62;
            }}
            p {{ margin: 0 0 16px 0; }}
            h1, h2, h3 {{ color: {Theme.text}; margin: 14px 0 8px 0; font-weight: 700; }}
            h1 {{ font-size: 25pt; }}
            h2 {{ font-size: 21pt; }}
            h3 {{ font-size: 18pt; }}
            ul, ol {{ margin-top: 5px; margin-bottom: 10px; }}
            li {{ margin-bottom: 7px; }}
            code {{ background: {Theme.surface_3}; color: #D2E4FF; font-family: 'Cascadia Mono', 'Consolas'; font-size: 14pt; padding: 1px 4px; }}
            pre {{ background: #0A0E13; border: 1px solid {Theme.border}; padding: 11px; margin: 9px 0; white-space: pre-wrap; font-size: 14pt; }}
            blockquote {{ color: {Theme.muted}; border-left: 3px solid {Theme.border}; margin-left: 0; padding-left: 11px; }}
            a {{ color: {Theme.accent}; }}
        """

    def set_markdown_text(self, text: str) -> None:
        self._apply_chat_font()
        css = self._document_css()
        self.document().setDefaultStyleSheet(css)
        try:
            self.setMarkdown(text)
        except Exception:
            self.setHtml("<p>" + html.escape(text).replace("\n", "<br>") + "</p>")
        # Re-apply after setMarkdown: on some Qt builds the generated block formats
        # otherwise fall back to QApplication's 11pt default font.
        self._apply_chat_font()
        self.document().setDefaultStyleSheet(css)
        self._enforce_document_font_sizes()
        QTimer.singleShot(0, self._sync_height)

    def set_typewriter_text(self, text: str, cursor: bool = True) -> None:
        """Render partial output at the same real point size as final Markdown."""
        self._apply_chat_font()
        css = self._document_css() + f"""
            .stream {{ white-space: pre-wrap; margin: 0; font-size: {CHAT_BODY_FONT_PT}pt; line-height: 1.62; }}
            .cursor {{ color: {Theme.accent}; font-weight: 700; font-size: {CHAT_BODY_FONT_PT}pt; }}
        """
        self.document().setDefaultStyleSheet(css)
        safe = html.escape(text).replace("\n", "<br>")
        caret = '<span class="cursor">▍</span>' if cursor else ''
        self.setHtml(
            f'<div class="stream" style="font-size:{CHAT_BODY_FONT_PT}pt; line-height:1.62;">{safe}{caret}</div>'
        )
        self._apply_chat_font()
        self._enforce_document_font_sizes()
        QTimer.singleShot(0, self._sync_height)

    def _sync_height(self, *_args) -> None:
        width = max(240, self.viewport().width())
        self.document().setTextWidth(width)
        height = int(self.document().size().height()) + 6
        self.setFixedHeight(max(34, height))

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        QTimer.singleShot(0, self._sync_height)


class MessageWidget(QFrame):
    sourcesRequested = Signal(object)

    def __init__(
        self,
        role: str,
        text: str,
        citations: Optional[list[dict[str, str]]] = None,
        pending: bool = False,
        error: bool = False,
    ) -> None:
        super().__init__()
        self.role = role
        self.raw_text = text
        self.citations = citations or []
        self.pending = pending
        self.error = error
        if role == "user":
            self.setMinimumWidth(260)
            self.setMaximumWidth(760)
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        else:
            self.setMaximumWidth(1060)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setObjectName("message")

        if role == "user":
            self.setStyleSheet(f"QFrame#message {{ background: {Theme.user}; border: 1px solid {Theme.user_border}; border-radius: 8px; }}")
        else:
            self.setStyleSheet(f"QFrame#message {{ background: transparent; border: none; border-bottom: 1px solid {Theme.border_soft}; }}")

        root = QVBoxLayout(self)
        set_margins(root, 16, 13, 16, 14)
        root.setSpacing(8)

        header = QHBoxLayout()
        avatar = QLabel("你" if role == "user" else "AI")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(30, 30)
        avatar_bg = "#294766" if role == "user" else Theme.accent_soft
        avatar_color = "#DCEBFF" if role == "user" else "#9EC5FF"
        avatar.setStyleSheet(f"background: {avatar_bg}; color: {avatar_color}; border-radius: 6px; font-size: 14pt; font-weight: 700;")
        header.addWidget(avatar)
        # 用户消息只保留头像中的“你”，避免头像和名称重复显示。
        self.title_label = QLabel(f"{APP_TITLE} · 正在处理" if pending else APP_TITLE)
        self.title_label.setStyleSheet(f"color: {Theme.text_2}; font-size: {CHAT_TITLE_FONT_PT}pt; font-weight: 600; background: transparent;")
        if role == "assistant":
            header.addWidget(self.title_label)
        else:
            self.title_label.hide()
        header.addStretch(1)

        # 不再显示消息复制按钮。此前图标既占用空间，又容易让用户误以为
        # 可以选择并复制局部文本；需要引用时仍可通过右侧来源面板查看。
        root.addLayout(header)

        self.body = AutoHeightTextBrowser()
        self.body.setStyleSheet("QTextBrowser { background: transparent; border: none; padding: 0; margin: 0; }")
        self.set_text(text, pending=pending, error=error)
        root.addWidget(self.body)

        self.source_row = QHBoxLayout()
        self.source_row.addStretch(1)
        self.source_button = QPushButton()
        self.source_button.setIcon(svg_icon("sources", Theme.muted, 14))
        self.source_button.setProperty("ghost", True)
        self.source_button.clicked.connect(lambda: self.sourcesRequested.emit(self.citations))
        self.source_row.addWidget(self.source_button)
        root.addLayout(self.source_row)
        self._sync_sources_button()

    def set_text(self, text: str, pending: bool = False, error: bool = False) -> None:
        self.raw_text = text
        self.pending = pending
        self.error = error
        if self.role == "assistant":
            self.title_label.setText(f"{APP_TITLE} · 正在处理" if pending else APP_TITLE)
        if error:
            self.body.document().setDefaultStyleSheet(f"body {{ color: {Theme.red}; }}")
        self.body.set_markdown_text(text)

    def set_typewriter_text(self, text: str) -> None:
        self.raw_text = text
        self.pending = True
        if self.role == "assistant":
            self.title_label.setText(f"{APP_TITLE} · 正在输出")
        self.body.set_typewriter_text(text, cursor=True)

    def set_citations(self, citations: list[dict[str, str]]) -> None:
        self.citations = citations
        self._sync_sources_button()

    def _sync_sources_button(self) -> None:
        count = len(self.citations)
        self.source_button.setVisible(count > 0)
        self.source_button.setText(f"查看 {count} 条来源")
        self.source_button.setStyleSheet(f"font-size: 12pt; color: {Theme.text_2};")

class PromptCard(QFrame):
    clicked = Signal()

    def __init__(self, icon_name: str, icon_color: str, text: str) -> None:
        super().__init__()
        self.setObjectName("promptCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(116)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            f"QFrame#promptCard {{ background: {Theme.surface}; "
            f"border: 1px solid {Theme.border}; border-radius: 18px; }} "
            f"QFrame#promptCard:hover {{ background: {Theme.surface_2}; "
            f"border-color: #3A4554; }}"
        )

        layout = QVBoxLayout(self)
        set_margins(layout, 18, 16, 18, 16)
        layout.setSpacing(12)

        icon = QLabel()
        icon.setPixmap(svg_icon(icon_name, icon_color, 23).pixmap(23, 23))
        icon.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(icon, 0, Qt.AlignLeft)
        layout.addStretch(1)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label.setStyleSheet(
            f"color: {Theme.text}; font-size: 15pt; font-weight: 600; "
            "line-height: 1.35; background: transparent; border: none;"
        )
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(label)

    def mouseReleaseEvent(self, event: object) -> None:
        button = getattr(event, "button", lambda: None)()
        if button == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)  # type: ignore[arg-type]


class EmptyChatState(QWidget):
    promptSelected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        # 新建页的文字比正式回答略小一档，避免喧宾夺主；示例卡片采用
        # 彩色线性图标点缀，接近现代编程智能体的空白工作区。
        self.setMaximumWidth(1080)
        root = QVBoxLayout(self)
        set_margins(root, 20, 42, 20, 26)
        root.setSpacing(13)

        icon = QLabel()
        icon.setPixmap(svg_icon("database", "#79AFFF", 44).pixmap(44, 44))
        icon.setAlignment(Qt.AlignCenter)
        root.addWidget(icon)

        title = QLabel("须知尽知，谋略既成")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {Theme.text}; font-size: 23pt; font-weight: 700; "
            "background: transparent;"
        )
        root.addWidget(title)

        desc = QLabel(
            "输入人员、制度、流程、型号等问题。"
            "系统会理解语义，检索原文总结答案并给出标注。"
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)

        desc.setMinimumWidth(900)
        desc.setMaximumWidth(900)
        desc.setMinimumHeight(70)
        desc.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.MinimumExpanding,
        )

        desc.setStyleSheet(
            f"color: {Theme.muted}; "
            "font-size: 14pt; "
            "background: transparent;"
        )

        root.addWidget(desc, 0, Qt.AlignHCenter)
        root.addSpacing(14)

        card_row = QHBoxLayout()
        card_row.setSpacing(14)
        prompts = (
            ("search", "#2F9CF4", "年假制度有哪些关键规定？"),
            ("settings", "#A970FF", "XX制度的审批流程是什么？"),
            ("refresh", "#3FB950", "XX设备点检由谁负责，周期是多少？"),
            ("index", "#F0883E", "把XX文件的关键要求整理出来。"),
        )
        for icon_name, icon_color, prompt in prompts:
            card = PromptCard(icon_name, icon_color, prompt)
            card.clicked.connect(lambda value=prompt: self.promptSelected.emit(value))
            card_row.addWidget(card, 1)
        root.addLayout(card_row)
        root.addStretch(1)


class ChatView(QWidget):
    sourcesRequested = Signal(object)
    typewriterFinished = Signal()
    sendRequested = Signal()
    stopRequested = Signal()
    modelChanged = Signal(str)
    promptSelected = Signal(str)
    clearRequested = Signal()
    toggleInspectorRequested = Signal()

    def __init__(self, model: str) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        set_margins(root, 0, 0, 0, 0)
        root.setSpacing(0)

        toolbar = QFrame()
        toolbar.setFixedHeight(46)
        toolbar.setStyleSheet(f"background: {Theme.editor}; border-bottom: 1px solid {Theme.border_soft};")
        toolbar_layout = QHBoxLayout(toolbar)
        set_margins(toolbar_layout, 14, 0, 8, 0)
        self.title_label = QLabel("当前对话")
        self.title_label.setStyleSheet(f"font-weight: 600; color: {Theme.text_2}; background: transparent;")
        toolbar_layout.addWidget(self.title_label)
        self.stage_label = QLabel("就绪")
        self.stage_label.setStyleSheet(f"color: {Theme.muted}; font-size: 11px; background: transparent;")
        toolbar_layout.addWidget(self.stage_label)
        toolbar_layout.addStretch(1)
        inspector_button = QToolButton()
        inspector_button.setIcon(svg_icon("panel", Theme.muted, 16))
        inspector_button.setToolTip("显示 / 隐藏来源面板")
        inspector_button.setProperty("ghost", True)
        inspector_button.clicked.connect(self.toggleInspectorRequested)
        toolbar_layout.addWidget(inspector_button)
        clear_button = QToolButton()
        clear_button.setIcon(svg_icon("trash", Theme.muted, 16))
        clear_button.setToolTip("清空当前对话")
        clear_button.setProperty("ghost", True)
        clear_button.clicked.connect(self.clearRequested)
        toolbar_layout.addWidget(clear_button)
        root.addWidget(toolbar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet(f"background: {Theme.editor};")
        self.scroll.viewport().setStyleSheet(f"background: {Theme.editor};")
        self.content = QWidget()
        self.content.setStyleSheet(f"background: {Theme.editor};")
        self.content_layout = QVBoxLayout(self.content)
        set_margins(self.content_layout, 72, 12, 72, 24)
        self.content_layout.setSpacing(0)
        self.content_layout.addStretch(1)
        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll, 1)

        composer_wrap = QFrame()
        composer_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        composer_wrap.setStyleSheet(f"background: {Theme.editor}; border-top: 1px solid {Theme.border_soft};")
        composer_layout = QVBoxLayout(composer_wrap)
        set_margins(composer_layout, 24, 12, 24, 14)
        self.composer = Composer(model)
        self.composer.setMaximumWidth(1080)
        self.composer.sendRequested.connect(self.sendRequested)
        self.composer.stopRequested.connect(self.stopRequested)
        self.composer.modelChanged.connect(self.modelChanged)
        row = QHBoxLayout()
        set_margins(row, 48, 0, 48, 0)
        row.addWidget(self.composer, 1)
        composer_layout.addLayout(row)
        root.addWidget(composer_wrap)

        self.empty_state: Optional[EmptyChatState] = None
        self.empty_row: Optional[QWidget] = None
        self.pending_message: Optional[MessageWidget] = None
        self.message_rows: list[QWidget] = []
        self.typewriter_timer = QTimer(self)
        self.typewriter_timer.setSingleShot(False)
        self.typewriter_timer.timeout.connect(self._advance_typewriter)
        self.typewriter_message: Optional[MessageWidget] = None
        self.typewriter_full_text = ""
        self.typewriter_index = 0
        self.typewriter_citations: list[dict[str, str]] = []
        self.show_empty_state()

    def set_conversation_title(self, title: str) -> None:
        self.title_label.setText(title.strip() or "新对话")

    def render_history(self, history: list[dict[str, Any]], title: str, pending_text: str = "") -> None:
        self.set_conversation_title(title)
        self.clear_messages()
        if not history and not pending_text:
            self.show_empty_state()
            return
        for item in history:
            role = str(item.get("role", ""))
            content = str(item.get("content", ""))
            if role not in {"user", "assistant"} or not content.strip():
                continue
            citations = item.get("source_items", []) if role == "assistant" else []
            self.add_message(role, content, citations=list(citations) if isinstance(citations, list) else [])
        if pending_text:
            self.start_pending(pending_text)
        QTimer.singleShot(80, self.scroll_to_bottom)

    def scroll_to_bottom(self) -> None:
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def show_empty_state(self) -> None:
        self.clear_messages()
        state = EmptyChatState()
        state.promptSelected.connect(self.promptSelected)
        row = QWidget()
        row_layout = QHBoxLayout(row)
        set_margins(row_layout, 0, 0, 0, 0)
        row_layout.addStretch(1)
        row_layout.addWidget(state)
        row_layout.addStretch(1)
        self.content_layout.insertWidget(self.content_layout.count() - 1, row)
        self.message_rows.append(row)
        self.empty_row = row
        self.empty_state = state

    def hide_empty_state(self) -> None:
        if self.empty_row is not None:
            self.content_layout.removeWidget(self.empty_row)
            if self.empty_row in self.message_rows:
                self.message_rows.remove(self.empty_row)
            self.empty_row.hide()
            self.empty_row.setParent(None)
            self.empty_row.deleteLater()
        self.empty_row = None
        self.empty_state = None

    def clear_messages(self) -> None:
        self.cancel_typewriter(notify=True)
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.message_rows.clear()
        self.pending_message = None
        self.empty_state = None
        self.empty_row = None

    def add_message(
        self,
        role: str,
        text: str,
        citations: Optional[list[dict[str, str]]] = None,
        pending: bool = False,
        error: bool = False,
    ) -> MessageWidget:
        self.hide_empty_state()
        message = MessageWidget(role, text, citations=citations, pending=pending, error=error)
        message.sourcesRequested.connect(self.sourcesRequested)
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        set_margins(row_layout, 0, 0, 0, 0)
        if role == "user":
            row_layout.addStretch(1)
            row_layout.addWidget(message, 0)
        else:
            row_layout.addWidget(message, 1)
        self.content_layout.insertWidget(self.content_layout.count() - 1, row)
        self.message_rows.append(row)
        if pending:
            self.pending_message = message
        QTimer.singleShot(60, lambda: self.scroll_to_widget_top(row))
        return message

    def start_pending(self, text: str) -> MessageWidget:
        return self.add_message("assistant", text, pending=True)

    def update_pending(self, text: str, error: bool = False) -> None:
        if self.pending_message:
            self.pending_message.set_text(text, pending=not error, error=error)
            self.stage_label.setText(text.splitlines()[0][:70])

    def finish_pending(self, answer: str, citations: list[dict[str, str]]) -> Optional[MessageWidget]:
        """Immediately finish a pending answer (used by non-animated paths)."""
        self.cancel_typewriter(notify=False)
        message = self.pending_message
        if message:
            message.set_text(answer, pending=False, error=False)
            message.set_citations(citations)
        self.pending_message = None
        self.stage_label.setText("完成")
        return message

    def is_typewriting(self) -> bool:
        return self.typewriter_timer.isActive()

    def start_typewriter(self, answer: str, citations: list[dict[str, str]]) -> Optional[MessageWidget]:
        """Animate a completed model answer without blocking the Qt event loop."""
        self.cancel_typewriter(notify=False)
        message = self.pending_message
        if message is None:
            message = self.add_message("assistant", "", pending=True)
        self.typewriter_message = message
        self.typewriter_full_text = str(answer or "")
        self.typewriter_index = 0
        self.typewriter_citations = [dict(item) for item in citations if isinstance(item, dict)]
        message.set_citations([])
        message.set_typewriter_text("")
        self.stage_label.setText("正在输出回答…")
        self.typewriter_timer.setInterval(22)
        self.typewriter_timer.start()
        return message

    def finish_typewriter_immediately(self) -> bool:
        if not self.typewriter_timer.isActive() or self.typewriter_message is None:
            return False
        self.typewriter_timer.stop()
        message = self.typewriter_message
        full = self.typewriter_full_text
        citations = self.typewriter_citations
        message.set_text(full, pending=False, error=False)
        message.set_citations(citations)
        self.pending_message = None
        self.typewriter_message = None
        self.typewriter_full_text = ""
        self.typewriter_index = 0
        self.typewriter_citations = []
        self.stage_label.setText("完成")
        QTimer.singleShot(0, self.scroll_to_bottom)
        self.typewriterFinished.emit()
        return True

    def cancel_typewriter(self, notify: bool = True) -> None:
        was_active = self.typewriter_timer.isActive()
        if was_active:
            self.typewriter_timer.stop()
        self.typewriter_message = None
        self.typewriter_full_text = ""
        self.typewriter_index = 0
        self.typewriter_citations = []
        if was_active and notify:
            self.typewriterFinished.emit()

    def _advance_typewriter(self) -> None:
        message = self.typewriter_message
        full = self.typewriter_full_text
        if message is None:
            self.cancel_typewriter(notify=True)
            return
        if self.typewriter_index >= len(full):
            self.typewriter_timer.stop()
            message.set_text(full, pending=False, error=False)
            message.set_citations(self.typewriter_citations)
            self.pending_message = None
            self.typewriter_message = None
            self.typewriter_full_text = ""
            self.typewriter_index = 0
            self.typewriter_citations = []
            self.stage_label.setText("完成")
            QTimer.singleShot(0, self.scroll_to_bottom)
            self.typewriterFinished.emit()
            return

        remaining = len(full) - self.typewriter_index
        total = len(full)
        if total <= 280:
            batch = 1
        elif total <= 900:
            batch = 2
        elif total <= 2200:
            batch = 4
        else:
            batch = 7
        batch = min(batch, remaining)
        end = self.typewriter_index + batch
        # Do not jump over punctuation: punctuation gets a small human-like pause.
        punctuation = "，。！？；：,.!?;:\n"
        for pos in range(self.typewriter_index, end):
            if full[pos] in punctuation:
                end = pos + 1
                break
        self.typewriter_index = end
        partial = full[:end]
        message.set_typewriter_text(partial)
        last = partial[-1:]
        if last in "。！？.!?":
            self.typewriter_timer.setInterval(95)
        elif last in "，；：,;:\n":
            self.typewriter_timer.setInterval(52)
        else:
            self.typewriter_timer.setInterval(22 if total < 900 else 18)
        if end % 24 == 0 or last in punctuation:
            QTimer.singleShot(0, self.scroll_to_bottom)

    def fail_pending(self, error_text: str) -> None:
        self.update_pending(error_text, error=True)
        self.pending_message = None
        self.stage_label.setText("失败")

    def scroll_to_widget_top(self, widget: QWidget) -> None:
        bar = self.scroll.verticalScrollBar()
        pos = widget.mapTo(self.content, QPoint(0, 0)).y()
        bar.setValue(max(0, pos - 8))

    def set_busy(self, busy: bool) -> None:
        self.composer.set_busy(busy)


class SourceCard(QFrame):
    def __init__(self, item: dict[str, str]) -> None:
        super().__init__()
        self.item = item
        self.setObjectName("sourceCard")
        self.setStyleSheet(f"QFrame#sourceCard {{ background: {Theme.surface}; border: 1px solid {Theme.border}; border-radius: 6px; }}")
        root = QVBoxLayout(self)
        set_margins(root, 10, 9, 10, 9)
        root.setSpacing(5)
        index = item.get("index", "")
        file_name = item.get("file", "未知文件")
        title = QLabel(f"[{index}] {file_name}" if index else file_name)
        title.setWordWrap(True)
        title.setStyleSheet(f"color: {Theme.text}; font-weight: 600; background: transparent;")
        root.addWidget(title)
        meta = " · ".join(value for value in (item.get("position", ""), item.get("origin", "")) if value)
        if meta:
            meta_label = QLabel(meta)
            meta_label.setWordWrap(True)
            meta_label.setStyleSheet(f"color: {Theme.muted}; font-size: 11px; background: transparent;")
            root.addWidget(meta_label)
        snippet = item.get("snippet", "")
        if snippet:
            snippet_label = QLabel(snippet)
            snippet_label.setWordWrap(True)
            snippet_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            snippet_label.setStyleSheet(f"color: {Theme.text_2}; background: transparent; line-height: 1.4;")
            root.addWidget(snippet_label)
        actions = QHBoxLayout()
        open_button = QPushButton("打开")
        open_button.setIcon(svg_icon("open", Theme.muted, 13))
        open_button.setProperty("ghost", True)
        open_button.clicked.connect(lambda: open_local_path(item.get("path", "")))
        actions.addWidget(open_button)
        copy_button = QPushButton("复制路径")
        copy_button.setIcon(svg_icon("copy", Theme.muted, 13))
        copy_button.setProperty("ghost", True)
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(item.get("path", "")))
        actions.addWidget(copy_button)
        actions.addStretch(1)
        root.addLayout(actions)


class SourcesInspector(QFrame):
    closeRequested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sourcesInspector")
        self.setMinimumWidth(280)
        self.setStyleSheet(f"QFrame#sourcesInspector {{ background: {Theme.sidebar}; border-left: 1px solid {Theme.border_soft}; }}")
        root = QVBoxLayout(self)
        set_margins(root, 0, 0, 0, 0)
        root.setSpacing(0)
        header = QFrame()
        header.setFixedHeight(36)
        header.setStyleSheet(f"background: {Theme.sidebar}; border-bottom: 1px solid {Theme.border_soft};")
        header_layout = QHBoxLayout(header)
        set_margins(header_layout, 12, 0, 6, 0)
        label = QLabel("来源")
        label.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {Theme.text_2}; background: transparent;")
        header_layout.addWidget(label)
        header_layout.addStretch(1)
        close_button = QToolButton()
        close_button.setIcon(svg_icon("close", Theme.muted, 14))
        close_button.setProperty("ghost", True)
        close_button.clicked.connect(self.closeRequested)
        header_layout.addWidget(close_button)
        root.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.container = QWidget()
        self.container.setStyleSheet(f"background: {Theme.sidebar};")
        self.container_layout = QVBoxLayout(self.container)
        set_margins(self.container_layout, 10, 10, 10, 10)
        self.container_layout.setSpacing(8)
        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll, 1)
        self.set_sources([])

    def set_sources(self, items: list[dict[str, str]]) -> None:
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if not items:
            empty = QLabel("本轮回答尚无来源。\n完成一次知识库问答后，这里会显示文件、位置和证据摘录。")
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            empty.setStyleSheet(f"color: {Theme.muted}; background: transparent; padding: 6px;")
            self.container_layout.addWidget(empty)
            self.container_layout.addStretch(1)
            return
        for item in items:
            self.container_layout.addWidget(SourceCard(item))
        self.container_layout.addStretch(1)


class SearchResultsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        set_margins(root, 0, 0, 0, 0)
        root.setSpacing(0)
        toolbar = QFrame()
        toolbar.setFixedHeight(46)
        toolbar.setStyleSheet(f"background: {Theme.editor}; border-bottom: 1px solid {Theme.border_soft};")
        toolbar_layout = QHBoxLayout(toolbar)
        set_margins(toolbar_layout, 14, 0, 10, 0)
        title = QLabel("精确检索")
        title.setStyleSheet(f"color: {Theme.text_2}; font-weight: 600; background: transparent;")
        toolbar_layout.addWidget(title)
        self.summary = QLabel("输入关键词开始检索")
        self.summary.setStyleSheet(f"color: {Theme.muted}; font-size: 11px; background: transparent;")
        toolbar_layout.addWidget(self.summary)
        toolbar_layout.addStretch(1)
        root.addWidget(toolbar)

        splitter = QSplitter(Qt.Vertical)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["文件", "位置", "关键词", "上下文"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setUniformRowHeights(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.header().setStretchLastSection(True)
        self.tree.setColumnWidth(0, 320)
        self.tree.setColumnWidth(1, 160)
        self.tree.setColumnWidth(2, 120)
        self.tree.itemSelectionChanged.connect(self._show_selected)
        self.tree.itemDoubleClicked.connect(self._open_selected)
        splitter.addWidget(self.tree)

        preview_frame = QFrame()
        preview_frame.setStyleSheet(f"background: {Theme.sidebar}; border-top: 1px solid {Theme.border_soft};")
        preview_layout = QVBoxLayout(preview_frame)
        set_margins(preview_layout, 12, 9, 12, 10)
        preview_title = QLabel("上下文预览")
        preview_title.setStyleSheet(f"color: {Theme.muted}; font-size: 11px; font-weight: 600; background: transparent;")
        preview_layout.addWidget(preview_title)
        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(False)
        self.preview.setStyleSheet(f"background: {Theme.sidebar}; border: none; color: {Theme.text_2};")
        preview_layout.addWidget(self.preview, 1)
        splitter.addWidget(preview_frame)
        splitter.setSizes([540, 210])
        root.addWidget(splitter, 1)
        self.hits: list[core.SearchHit] = []

    def set_loading(self, query: str) -> None:
        self.summary.setText(f"正在搜索：{query}")
        self.tree.clear()
        self.preview.clear()

    def set_results(self, query: str, hits: list[core.SearchHit]) -> None:
        self.hits = hits
        self.tree.clear()
        for index, hit in enumerate(hits):
            item = QTreeWidgetItem([
                hit.path,
                hit.position,
                hit.keyword,
                hit.snippet,
            ])
            item.setData(0, Qt.UserRole, index)
            item.setToolTip(0, hit.path)
            self.tree.addTopLevelItem(item)
        self.summary.setText(f"“{query}” · {len(hits)} 条结果")
        if hits:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))
        else:
            self.preview.setPlainText("没有找到匹配内容。")

    def _selected_hit(self) -> Optional[core.SearchHit]:
        items = self.tree.selectedItems()
        if not items:
            return None
        index = items[0].data(0, Qt.UserRole)
        try:
            return self.hits[int(index)]
        except Exception:
            return None

    def _show_selected(self) -> None:
        hit = self._selected_hit()
        if not hit:
            self.preview.clear()
            return
        self.preview.setPlainText(f"文件：{hit.path}\n位置：{hit.position}\n关键词：{hit.keyword}\n\n{hit.snippet}")

    def _open_selected(self, *_args) -> None:
        hit = self._selected_hit()
        if not hit:
            return
        try:
            core.open_hit_target(hit)
        except Exception:
            open_local_path(hit.path)


class WorkbenchStatusBar(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(24)
        self.setStyleSheet(f"background: {Theme.status};")
        layout = QHBoxLayout(self)
        set_margins(layout, 8, 0, 8, 0)
        layout.setSpacing(14)
        self.state = QLabel("就绪")
        self.state.setStyleSheet("color: white; font-size: 11px; background: transparent;")
        layout.addWidget(self.state)
        self.index = QLabel("索引：未建立")
        self.index.setStyleSheet("color: white; font-size: 11px; background: transparent;")
        layout.addWidget(self.index)
        layout.addStretch(1)
        self.model = QLabel("")
        self.model.setStyleSheet("color: white; font-size: 11px; background: transparent;")
        layout.addWidget(self.model)
        self.safety = QLabel("本地检索优先")
        self.safety.setStyleSheet("color: white; font-size: 11px; background: transparent;")
        layout.addWidget(self.safety)


class IndexWorker(QObject):
    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, folder: Path, db_path: Path) -> None:
        super().__init__()
        self.folder = folder
        self.db_path = db_path
        self.stop_event = threading.Event()

    @Slot()
    def run(self) -> None:
        try:
            stats = core.index_folder(
                self.folder,
                self.db_path,
                progress=lambda payload: self.progress.emit(dict(payload)),
                should_stop=self.stop_event.is_set,
            )
            self.finished.emit(stats)
        except Exception as exc:
            self.failed.emit(str(exc))

    def stop(self) -> None:
        self.stop_event.set()


class SearchWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        query: str,
        require_all: bool,
        match_case: bool,
        phrase: bool,
        limit: int,
    ) -> None:
        super().__init__()
        self.db_path = db_path
        self.query = query
        self.require_all = require_all
        self.match_case = match_case
        self.phrase = phrase
        self.limit = limit

    @Slot()
    def run(self) -> None:
        try:
            hits = core.search_index(
                self.db_path,
                self.query,
                require_all_terms=self.require_all,
                match_case=self.match_case,
                phrase=self.phrase,
                limit=self.limit,
            )
            self.finished.emit(hits)
        except Exception as exc:
            self.failed.emit(str(exc))


class RagWorker(QObject):
    stage = Signal(str)
    finished = Signal(str, str, object)
    failed = Signal(str, str)
    cancelled = Signal(str)

    def __init__(
        self,
        db_path: Path,
        question: str,
        settings: SettingsState,
        history: list[dict[str, str]],
    ) -> None:
        super().__init__()
        self.db_path = db_path
        self.question = question
        self.settings = settings
        self.history = history
        self._cancel = threading.Event()

    def stop(self) -> None:
        self._cancel.set()

    def _check_cancel(self) -> bool:
        if self._cancel.is_set():
            self.cancelled.emit(self.question)
            return True
        return False

    @Slot()
    def run(self) -> None:
        try:
            q = self.question
            s = self.settings
            context_only = core.should_skip_local_retrieval(q, self.history)
            if context_only:
                self.stage.emit("正在结合最近对话生成回答…")
                answer = core.call_context_completion(
                    s.api_url,
                    s.api_key,
                    s.model,
                    q,
                    chat_history=self.history,
                )
                if self._check_cancel():
                    return
                self.finished.emit(q, answer, [])
                return

            # 完全采用用户提供的 win_keyword_search(3).py 检索流程：
            # 追问改写 -> 文件候选 -> 候选内精确搜索 -> 全库补检 ->
            # fetch_rag_contexts 多通道合并 -> 原版提示词生成回答。
            self.stage.emit("正在检索本地知识库…")
            retrieval_query = core.retrieval_query_for_question(q, self.history)
            file_candidates = core.rank_candidate_files(
                self.db_path,
                retrieval_query,
                match_case=s.match_case,
                limit=max(s.top_k * 8, 32),
            )
            preferred_file_paths = {item.path for item in file_candidates}
            if preferred_file_paths:
                self.stage.emit(
                    f"已按文件名和内容线索筛选 {len(preferred_file_paths)} 个候选文件，正在检索内容…"
                )

            priority_hits: list[core.SearchHit] = []
            seen_hits: set[tuple[str, str, int]] = set()
            for candidate in core.rag_search_candidates(retrieval_query):
                candidate_hits = core.search_index(
                    self.db_path,
                    candidate,
                    require_all_terms=s.require_all,
                    match_case=s.match_case,
                    phrase=s.phrase,
                    limit=max(s.top_k * 4, s.top_k),
                    file_paths=preferred_file_paths if preferred_file_paths else None,
                )
                for hit in candidate_hits:
                    key = (
                        hit.path,
                        hit.keyword.casefold() if not s.match_case else hit.keyword,
                        hit.offset,
                    )
                    if key in seen_hits:
                        continue
                    seen_hits.add(key)
                    priority_hits.append(hit)
                    if len(priority_hits) >= max(s.top_k * 4, s.top_k):
                        break
                if len(priority_hits) >= max(s.top_k * 8, s.top_k):
                    break

            if not priority_hits and preferred_file_paths:
                self.stage.emit("候选文件内未找到精确命中，正在全库补充检索…")
                for candidate in core.rag_search_candidates(retrieval_query):
                    candidate_hits = core.search_index(
                        self.db_path,
                        candidate,
                        require_all_terms=s.require_all,
                        match_case=s.match_case,
                        phrase=s.phrase,
                        limit=max(s.top_k * 4, s.top_k),
                    )
                    for hit in candidate_hits:
                        key = (
                            hit.path,
                            hit.keyword.casefold() if not s.match_case else hit.keyword,
                            hit.offset,
                        )
                        if key in seen_hits:
                            continue
                        seen_hits.add(key)
                        priority_hits.append(hit)
                        if len(priority_hits) >= max(s.top_k * 4, s.top_k):
                            break
                    if len(priority_hits) >= max(s.top_k * 8, s.top_k):
                        break

            if self._check_cancel():
                return

            contexts = core.fetch_rag_contexts(
                self.db_path,
                q,
                require_all_terms=s.require_all,
                match_case=s.match_case,
                phrase=s.phrase,
                limit=s.top_k,
                chat_history=self.history,
                priority_hits=priority_hits,
                preferred_file_paths=preferred_file_paths,
            )
            self.stage.emit(f"已找到 {len(contexts)} 条相关资料，正在生成回答…")
            if self._check_cancel():
                return

            answer = core.call_chat_completion(
                s.api_url,
                s.api_key,
                s.model,
                q,
                contexts,
                chat_history=self.history,
            )
            if self._check_cancel():
                return

            source_items: list[dict[str, str]] = []
            for index, context in enumerate(contexts, start=1):
                focus_terms = core.unique_keep_order(
                    [context.keyword, *context.matched_terms, *core.rag_question_terms(q)]
                )
                source_items.append(
                    {
                        "index": str(index),
                        "file": Path(context.path).name,
                        "path": context.path,
                        "position": context.position,
                        "origin": context.origin or "本地检索",
                        "snippet": core.focused_context_text(context.text, focus_terms, 220),
                    }
                )
            self.finished.emit(q, answer, source_items)
        except Exception as exc:
            self.failed.emit(self.question, str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        icon = application_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        self.setMinimumSize(1180, 720)
        self.ui_state = load_ui_state()
        self.resize(int(self.ui_state.get("window_width", 1500)), int(self.ui_state.get("window_height", 900)))
        if self.ui_state.get("window_x") is not None and self.ui_state.get("window_y") is not None:
            self.move(int(self.ui_state["window_x"]), int(self.ui_state["window_y"]))

        settings_raw = core.load_rag_settings()
        self.settings_state = SettingsState(
            api_url=str(settings_raw.get("api_url", core.DEFAULT_RAG_API_URL)),
            api_key=str(settings_raw.get("api_key", "")),
            model=str(settings_raw.get("model", core.DEFAULT_RAG_MODEL)),
            top_k=int(settings_raw.get("top_k", core.DEFAULT_RAG_TOP_K) or core.DEFAULT_RAG_TOP_K),
            save_key=bool(settings_raw.get("save_key", False)),
        )
        self.folder_path = str(self.ui_state.get("folder", ""))
        self.db_path = str(self.ui_state.get("db", core.default_db_path()))
        self.conversation_state = load_conversation_state()
        self.conversations: dict[str, dict[str, Any]] = {
            str(item["id"]): item for item in self.conversation_state.get("conversations", [])
        }
        self.current_conversation_id = str(self.conversation_state.get("current_id", ""))
        if self.current_conversation_id not in self.conversations:
            first = make_conversation()
            self.conversations[str(first["id"])] = first
            self.current_conversation_id = str(first["id"])
        self.history: list[dict[str, Any]] = [
            dict(item) for item in self.conversations[self.current_conversation_id].get("messages", [])
        ]
        self.current_sources: list[dict[str, str]] = []
        self.active_rag_conversation_id = ""
        self.active_rag_stage = ""
        self.index_thread: Optional[QThread] = None
        self.index_worker: Optional[IndexWorker] = None
        self.rag_thread: Optional[QThread] = None
        self.rag_worker: Optional[RagWorker] = None
        self.search_thread: Optional[QThread] = None
        self.search_worker: Optional[SearchWorker] = None
        self.sidebar_visible = True
        self.inspector_visible = False

        self._build_ui()
        self._install_shortcuts()
        self._refresh_workspace()
        self._refresh_conversation_sidebar()
        self._render_current_conversation()
        self._set_status("就绪")
        QTimer.singleShot(120, self.chat_view.composer.focus)

    def _build_ui(self) -> None:
        central = QWidget()
        central_layout = QVBoxLayout(central)
        set_margins(central_layout, 0, 0, 0, 0)
        central_layout.setSpacing(0)

        workbench = QWidget()
        workbench_layout = QHBoxLayout(workbench)
        set_margins(workbench_layout, 0, 0, 0, 0)
        workbench_layout.setSpacing(0)

        self.activity_rail = ActivityRail()
        self.activity_rail.activityChanged.connect(self.switch_activity)
        workbench_layout.addWidget(self.activity_rail)

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        workbench_layout.addWidget(self.main_splitter, 1)

        self.sidebar_stack = QStackedWidget()
        self.sidebar_stack.setMinimumWidth(220)
        self.chat_sidebar = ChatSidebar()
        self.knowledge_sidebar = KnowledgeSidebar()
        self.search_sidebar = SearchSidebar()
        self.settings_sidebar = SettingsSidebar(self.settings_state)
        for widget in (self.chat_sidebar, self.knowledge_sidebar, self.search_sidebar, self.settings_sidebar):
            self.sidebar_stack.addWidget(widget)
        self.main_splitter.addWidget(self.sidebar_stack)

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        self.chat_view = ChatView(self.settings_state.model)
        self.chat_view.sourcesRequested.connect(self.show_sources)
        self.chat_view.sendRequested.connect(self.send_question)
        self.chat_view.stopRequested.connect(self.stop_generation)
        self.chat_view.modelChanged.connect(self.model_changed_from_composer)
        self.chat_view.promptSelected.connect(self.use_prompt)
        self.chat_view.clearRequested.connect(self.clear_current_chat)
        self.chat_view.toggleInspectorRequested.connect(self.toggle_inspector)
        self.chat_view.typewriterFinished.connect(self.on_typewriter_finished)
        self.chat_tab_index = self.editor_tabs.addTab(self.chat_view, svg_icon("chat", Theme.muted, 14), "对话")
        self._hide_tab_close_button(self.chat_tab_index)
        self.search_view: Optional[SearchResultsView] = None
        self.main_splitter.addWidget(self.editor_tabs)

        self.sources_inspector = SourcesInspector()
        self.sources_inspector.closeRequested.connect(self.hide_inspector)
        self.sources_inspector.setVisible(False)
        self.main_splitter.addWidget(self.sources_inspector)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setStretchFactor(2, 0)
        self.main_splitter.setSizes([int(self.ui_state.get("sidebar_width", 270)), 1000, 0])

        central_layout.addWidget(workbench, 1)
        self.status_bar_widget = WorkbenchStatusBar()
        central_layout.addWidget(self.status_bar_widget)
        self.setCentralWidget(central)

        self.chat_sidebar.newChatRequested.connect(self.new_chat)
        self.chat_sidebar.conversationSelected.connect(self.switch_conversation)
        self.chat_sidebar.renameConversationRequested.connect(self.rename_conversation)
        self.chat_sidebar.deleteConversationRequested.connect(self.delete_conversation)
        self.knowledge_sidebar.chooseFolderRequested.connect(self.choose_folder)
        self.knowledge_sidebar.chooseDbRequested.connect(self.choose_db)
        self.knowledge_sidebar.indexRequested.connect(self.start_index)
        self.knowledge_sidebar.stopIndexRequested.connect(self.stop_index)
        self.search_sidebar.searchRequested.connect(self.run_search)
        self.settings_sidebar.saved.connect(self.save_settings)
        self.settings_sidebar.modelChanged.connect(self.model_changed_from_settings)

    def _hide_tab_close_button(self, index: int) -> None:
        tab_bar = self.editor_tabs.tabBar()
        for side in (QTabBar.LeftSide, QTabBar.RightSide):
            button = tab_bar.tabButton(index, side)
            if button:
                button.resize(0, 0)
                button.hide()

    def _install_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self.activity_rail.select("chat"))
        QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self.activity_rail.select("knowledge"))
        QShortcut(QKeySequence("Ctrl+Shift+F"), self, activated=self.focus_search)
        QShortcut(QKeySequence("Ctrl+,"), self, activated=lambda: self.activity_rail.select("settings"))
        QShortcut(QKeySequence("Ctrl+B"), self, activated=self.toggle_sidebar)
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.new_chat)
        QShortcut(QKeySequence("Escape"), self, activated=self.stop_generation)

    @Slot(str)
    def switch_activity(self, activity: str) -> None:
        mapping = {"chat": 0, "knowledge": 1, "search": 2, "settings": 3}
        self.sidebar_stack.setCurrentIndex(mapping.get(activity, 0))
        if not self.sidebar_visible:
            self.toggle_sidebar()
        if activity == "chat":
            self.editor_tabs.setCurrentIndex(self.chat_tab_index)
        elif activity == "search":
            self.search_sidebar.query.setFocus()
        elif activity == "settings":
            self.settings_sidebar.api_url.setFocus()

    def focus_search(self) -> None:
        self.activity_rail.select("search")
        self.search_sidebar.query.selectAll()
        self.search_sidebar.query.setFocus()

    def toggle_sidebar(self) -> None:
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar_stack.setVisible(self.sidebar_visible)
        if self.sidebar_visible:
            sizes = self.main_splitter.sizes()
            sidebar_width = int(self.ui_state.get("sidebar_width", 270))
            self.main_splitter.setSizes([sidebar_width, max(600, sum(sizes)), sizes[2] if len(sizes) > 2 else 0])

    def toggle_inspector(self) -> None:
        if self.inspector_visible:
            self.hide_inspector()
        else:
            self.show_sources(self.current_sources)

    @Slot(object)
    def show_sources(self, items: object) -> None:
        sources = list(items) if isinstance(items, list) else []
        self.current_sources = sources
        self.sources_inspector.set_sources(sources)
        self.sources_inspector.setVisible(True)
        self.inspector_visible = True
        sizes = self.main_splitter.sizes()
        width = int(self.ui_state.get("inspector_width", 340))
        if len(sizes) == 3:
            self.main_splitter.setSizes([sizes[0], max(560, sizes[1] - width), width])

    def hide_inspector(self) -> None:
        sizes = self.main_splitter.sizes()
        if len(sizes) == 3 and sizes[2] > 0:
            self.ui_state["inspector_width"] = sizes[2]
        self.sources_inspector.setVisible(False)
        self.inspector_visible = False

    def close_editor_tab(self, index: int) -> None:
        if index == self.chat_tab_index:
            return
        widget = self.editor_tabs.widget(index)
        self.editor_tabs.removeTab(index)
        if widget:
            widget.deleteLater()
        self.search_view = None

    def choose_folder(self) -> None:
        initial = self.folder_path if self.folder_path and Path(self.folder_path).exists() else str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "选择知识库文件夹", initial)
        if folder:
            self.folder_path = folder
            self._refresh_workspace()
            self._set_status(f"已选择资料文件夹：{Path(folder).name}")

    def choose_db(self) -> None:
        initial = self.db_path or str(core.default_db_path())
        path, _ = QFileDialog.getSaveFileName(self, "选择索引库", initial, "SQLite 数据库 (*.sqlite);;所有文件 (*.*)")
        if path:
            if not Path(path).suffix:
                path += ".sqlite"
            self.db_path = path
            self._refresh_workspace()
            self._set_status(f"索引库：{Path(path).name}")

    def _refresh_workspace(self) -> None:
        self.knowledge_sidebar.set_workspace(self.folder_path, self.db_path)
        files, chunks = db_summary(Path(self.db_path))
        self.knowledge_sidebar.set_summary(files, chunks)
        self.status_bar_widget.index.setText(f"索引：{files} 文件 / {chunks} 片段" if files else "索引：未建立")
        self.status_bar_widget.model.setText(self.settings_state.model)
        context_name = Path(self.folder_path).name if self.folder_path else "未选择知识库"
        self.chat_view.composer.context_label.setText(f"● {context_name}")
        self.chat_view.composer.context_label.setStyleSheet(
            f"color: {Theme.green if self.folder_path else Theme.muted}; font-size: 11px; background: transparent;"
        )

    def start_index(self) -> None:
        if self.index_thread and self.index_thread.isRunning():
            return
        folder = Path(self.folder_path)
        db_path = Path(self.db_path)
        if not folder.exists() or not folder.is_dir():
            QMessageBox.information(self, "请选择资料文件夹", "请先在左侧知识库面板选择要建立索引的文件夹。")
            return
        self.knowledge_sidebar.set_indexing(True)
        self.knowledge_sidebar.progress.setValue(0)
        self.knowledge_sidebar.progress_detail.setText("正在统计文件…")
        self._set_status("正在建立索引…")
        self.index_thread = QThread(self)
        self.index_worker = IndexWorker(folder, db_path)
        self.index_worker.moveToThread(self.index_thread)
        self.index_thread.started.connect(self.index_worker.run)
        self.index_worker.progress.connect(self.on_index_progress)
        self.index_worker.finished.connect(self.on_index_finished)
        self.index_worker.failed.connect(self.on_index_failed)
        self.index_worker.finished.connect(self.index_thread.quit)
        self.index_worker.failed.connect(self.index_thread.quit)
        self.index_thread.finished.connect(self._cleanup_index_thread)
        self.index_thread.start()

    def stop_index(self) -> None:
        if self.index_worker:
            self.index_worker.stop()
            self.knowledge_sidebar.progress_detail.setText("正在停止索引…")
            self._set_status("已请求停止索引")

    @Slot(object)
    def on_index_progress(self, payload: object) -> None:
        data = dict(payload) if isinstance(payload, dict) else {}
        event = str(data.get("event", ""))
        total = max(1, int(data.get("total", 0) or 1))
        seen = int(data.get("seen", 0) or 0)
        if event == "counting":
            self.knowledge_sidebar.progress.setRange(0, 0)
            self.knowledge_sidebar.progress_detail.setText(f"正在统计文件：{data.get('total', 0)}")
            return
        self.knowledge_sidebar.progress.setRange(0, 100)
        percent = min(100, int(seen / total * 100))
        self.knowledge_sidebar.progress.setValue(percent)
        path = str(data.get("path", ""))
        detail = f"{seen}/{total}  ·  已索引 {data.get('indexed', 0)}"
        if path:
            detail += f"\n{compact_path(path, 50)}"
        self.knowledge_sidebar.progress_detail.setText(detail)

    @Slot(object)
    def on_index_finished(self, stats: object) -> None:
        data = dict(stats) if isinstance(stats, dict) else {}
        cancelled = bool(data.get("cancelled"))
        self.knowledge_sidebar.set_indexing(False)
        self.knowledge_sidebar.progress.setRange(0, 100)
        self.knowledge_sidebar.progress.setValue(100 if not cancelled else int(self.knowledge_sidebar.progress.value()))
        self.knowledge_sidebar.progress_detail.setText(
            f"{'已停止' if cancelled else '完成'}：索引 {data.get('indexed', 0)}，跳过 {data.get('skipped', 0)}，失败 {data.get('failed', 0)}"
        )
        self._refresh_workspace()
        self._set_status("索引已停止" if cancelled else "索引建立完成")

    @Slot(str)
    def on_index_failed(self, error: str) -> None:
        self.knowledge_sidebar.set_indexing(False)
        self.knowledge_sidebar.progress.setRange(0, 100)
        self.knowledge_sidebar.progress_detail.setText("索引失败")
        self._set_status("索引失败")
        QMessageBox.critical(self, "索引失败", error)

    def _cleanup_index_thread(self) -> None:
        if self.index_worker:
            self.index_worker.deleteLater()
        if self.index_thread:
            self.index_thread.deleteLater()
        self.index_worker = None
        self.index_thread = None

    @Slot(str)
    def run_search(self, query: str) -> None:
        query = query.strip()
        if not query:
            return
        db_path = Path(self.db_path)
        if not db_path.exists():
            QMessageBox.information(self, "缺少索引", "请先建立索引。")
            return
        if self.search_thread and self.search_thread.isRunning():
            return
        if self.search_view is None:
            self.search_view = SearchResultsView()
            index = self.editor_tabs.addTab(self.search_view, svg_icon("search", Theme.muted, 14), "精确检索")
        else:
            index = self.editor_tabs.indexOf(self.search_view)
        self.editor_tabs.setCurrentIndex(index)
        self.search_view.set_loading(query)
        self._set_status(f"正在搜索：{query}")

        self.search_thread = QThread(self)
        self.search_worker = SearchWorker(
            db_path,
            query,
            self.search_sidebar.require_all.isChecked(),
            self.search_sidebar.match_case.isChecked(),
            self.search_sidebar.phrase.isChecked(),
            int(self.search_sidebar.limit.value()),
        )
        self.search_worker.moveToThread(self.search_thread)
        self.search_thread.started.connect(self.search_worker.run)
        self.search_worker.finished.connect(lambda hits, q=query: self.on_search_finished(q, hits))
        self.search_worker.failed.connect(self.on_search_failed)
        self.search_worker.finished.connect(self.search_thread.quit)
        self.search_worker.failed.connect(self.search_thread.quit)
        self.search_thread.finished.connect(self._cleanup_search_thread)
        self.search_thread.start()

    @Slot(str, object)
    def on_search_finished(self, query: str, hits: object) -> None:
        results = list(hits) if isinstance(hits, list) else []
        if self.search_view:
            self.search_view.set_results(query, results)
        self._set_status(f"精确检索完成：{len(results)} 条结果")

    @Slot(str)
    def on_search_failed(self, error: str) -> None:
        self._set_status("精确检索失败")
        QMessageBox.critical(self, "检索失败", error)

    def _cleanup_search_thread(self) -> None:
        if self.search_worker:
            self.search_worker.deleteLater()
        if self.search_thread:
            self.search_thread.deleteLater()
        self.search_worker = None
        self.search_thread = None

    def use_prompt(self, prompt: str) -> None:
        self.chat_view.composer.editor.setPlainText(prompt)
        self.chat_view.composer.focus()

    def _sorted_conversations(self) -> list[dict[str, Any]]:
        return sorted(
            self.conversations.values(),
            key=lambda item: str(item.get("updated_at", "")),
            reverse=True,
        )

    def _current_conversation(self) -> dict[str, Any]:
        conversation = self.conversations.get(self.current_conversation_id)
        if conversation is None:
            conversation = make_conversation()
            self.current_conversation_id = str(conversation["id"])
            self.conversations[self.current_conversation_id] = conversation
        return conversation

    def _persist_conversations(self) -> None:
        conversation = self._current_conversation()
        conversation["messages"] = [dict(item) for item in self.history]
        state = {
            "version": 1,
            "current_id": self.current_conversation_id,
            "conversations": self._sorted_conversations(),
        }
        self.conversation_state = state
        try:
            save_conversation_state(state)
        except Exception as exc:
            self._write_error_log(f"保存会话失败：{exc}")

    def _refresh_conversation_sidebar(self) -> None:
        self.chat_sidebar.set_conversations(self._sorted_conversations(), self.current_conversation_id)

    def _latest_sources_from_history(self) -> list[dict[str, str]]:
        for item in reversed(self.history):
            if item.get("role") != "assistant":
                continue
            sources = item.get("source_items", [])
            if isinstance(sources, list):
                return [dict(source) for source in sources if isinstance(source, dict)]
        return []

    def _render_current_conversation(self) -> None:
        conversation = self._current_conversation()
        self.history = [dict(item) for item in conversation.get("messages", [])]
        pending = ""
        if (
            self.rag_thread
            and self.rag_thread.isRunning()
            and self.active_rag_conversation_id == self.current_conversation_id
        ):
            pending = self.active_rag_stage or "正在处理…"
        self.chat_view.render_history(self.history, str(conversation.get("title", "新对话")), pending_text=pending)
        self.current_sources = self._latest_sources_from_history()
        self.sources_inspector.set_sources(self.current_sources)
        self.chat_view.set_busy(bool(self.rag_thread and self.rag_thread.isRunning()) or self.chat_view.is_typewriting())
        self.editor_tabs.setCurrentIndex(self.chat_tab_index)

    @Slot(str)
    def switch_conversation(self, conversation_id: str) -> None:
        conversation_id = str(conversation_id or "")
        if not conversation_id or conversation_id == self.current_conversation_id:
            return
        if conversation_id not in self.conversations:
            return
        self._persist_conversations()
        self.current_conversation_id = conversation_id
        self.conversation_state["current_id"] = conversation_id
        self._render_current_conversation()
        self._refresh_conversation_sidebar()
        self._persist_conversations()
        self._set_status(f"已切换：{self._current_conversation().get('title', '新对话')}")
        self.chat_view.composer.focus()

    @Slot(str)
    def rename_conversation(self, conversation_id: str) -> None:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            return
        current_title = str(conversation.get("title", "新对话"))
        title, accepted = QInputDialog.getText(self, "重命名会话", "会话名称：", text=current_title)
        title = title.strip()
        if not accepted or not title:
            return
        conversation["title"] = title[:80]
        conversation["updated_at"] = conversation_now()
        self._refresh_conversation_sidebar()
        if conversation_id == self.current_conversation_id:
            self.chat_view.set_conversation_title(title)
        self._persist_conversations()
        self._set_status("会话已重命名")

    @Slot(str)
    def delete_conversation(self, conversation_id: str) -> None:
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            return
        if conversation_id == self.active_rag_conversation_id and self.rag_thread and self.rag_thread.isRunning():
            QMessageBox.information(self, "正在生成", "该会话正在生成回答，请先停止生成后再删除。")
            return
        title = str(conversation.get("title", "新对话"))
        result = QMessageBox.question(
            self,
            "删除会话",
            f"确定删除“{title}”吗？\n删除后无法恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if result != QMessageBox.Yes:
            return
        self.conversations.pop(conversation_id, None)
        if not self.conversations:
            replacement = make_conversation()
            self.conversations[str(replacement["id"])] = replacement
        if conversation_id == self.current_conversation_id:
            self.current_conversation_id = str(self._sorted_conversations()[0]["id"])
            self._render_current_conversation()
        self._refresh_conversation_sidebar()
        self._persist_conversations()
        self._set_status("会话已删除")

    def clear_current_chat(self) -> None:
        conversation = self._current_conversation()
        if not self.history:
            return
        result = QMessageBox.question(
            self,
            "清空当前对话",
            "确定清空当前会话中的全部消息吗？\n会话本身会保留。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if result != QMessageBox.Yes:
            return
        self.history.clear()
        conversation["messages"] = []
        conversation["updated_at"] = conversation_now()
        self.current_sources = []
        self.sources_inspector.set_sources([])
        self.hide_inspector()
        self._persist_conversations()
        self._refresh_conversation_sidebar()
        self._render_current_conversation()
        self._set_status("当前对话已清空")

    def current_settings(self) -> SettingsState:
        state = self.settings_sidebar.state()
        state.model = self.chat_view.composer.model_combo.currentText().strip() or state.model
        return state

    def send_question(self) -> None:
        if self.rag_thread and self.rag_thread.isRunning():
            return
        if self.chat_view.is_typewriting():
            self._set_status("当前回答仍在输出，请等待输出完成")
            return
        question = self.chat_view.composer.text()
        if not question:
            return
        settings = self.current_settings()
        if not settings.model:
            QMessageBox.information(self, "缺少模型", "请在设置中填写模型名称。")
            return
        if not settings.api_key and "localhost" not in settings.api_url and "127.0.0.1" not in settings.api_url:
            self.activity_rail.select("settings")
            QMessageBox.information(self, "缺少 API Key", "请先在设置中填写 API Key。")
            return
        history_snapshot = [dict(item) for item in self.history]
        context_only = core.should_skip_local_retrieval(question, history_snapshot)
        if not context_only and not Path(self.db_path).exists():
            self.activity_rail.select("knowledge")
            QMessageBox.information(self, "缺少索引", "请先选择资料文件夹并建立索引。")
            return

        try:
            core.save_rag_settings(settings.api_url, settings.model, settings.api_key, settings.top_k, settings.save_key)
        except Exception:
            pass
        self.settings_state = settings
        self.status_bar_widget.model.setText(settings.model)

        self.chat_view.add_message("user", question)
        self.history.append({"role": "user", "content": question})
        conversation = self._current_conversation()
        if not conversation.get("messages") and str(conversation.get("title", "新对话")) == "新对话":
            conversation["title"] = conversation_title_from_question(question)
            self.chat_view.set_conversation_title(str(conversation["title"]))
        conversation["messages"] = [dict(item) for item in self.history]
        conversation["updated_at"] = conversation_now()
        self._persist_conversations()
        self._refresh_conversation_sidebar()

        initial = "正在结合最近对话生成回答…" if context_only else "正在理解问题…"
        self.active_rag_conversation_id = self.current_conversation_id
        self.active_rag_stage = initial
        self.chat_view.start_pending(initial)
        self.chat_view.composer.clear()
        self.chat_view.set_busy(True)
        self._set_status(initial)

        self.rag_thread = QThread(self)
        self.rag_worker = RagWorker(Path(self.db_path), question, settings, history_snapshot)
        self.rag_worker.moveToThread(self.rag_thread)
        self.rag_thread.started.connect(self.rag_worker.run)
        self.rag_worker.stage.connect(self.on_rag_stage)
        self.rag_worker.finished.connect(self.on_rag_finished)
        self.rag_worker.failed.connect(self.on_rag_failed)
        self.rag_worker.cancelled.connect(self.on_rag_cancelled)
        self.rag_worker.finished.connect(self.rag_thread.quit)
        self.rag_worker.failed.connect(self.rag_thread.quit)
        self.rag_worker.cancelled.connect(self.rag_thread.quit)
        self.rag_thread.finished.connect(self._cleanup_rag_thread)
        self.rag_thread.start()

    @Slot(str)
    def on_rag_stage(self, message: str) -> None:
        self.active_rag_stage = message
        if self.current_conversation_id == self.active_rag_conversation_id:
            self.chat_view.update_pending(message)
        self._set_status(message)

    @Slot(str, str, object)
    def on_rag_finished(self, question: str, answer: str, source_items: object) -> None:
        sources = list(source_items) if isinstance(source_items, list) else []
        target_id = self.active_rag_conversation_id or self.current_conversation_id
        target = self.conversations.get(target_id)
        if target is None:
            target = make_conversation(conversation_title_from_question(question))
            target_id = str(target["id"])
            self.conversations[target_id] = target
        messages = [dict(item) for item in target.get("messages", [])]
        if not messages or messages[-1].get("role") != "user" or messages[-1].get("content") != question:
            messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer, "source_items": sources})
        target["messages"] = messages[-40:]
        target["updated_at"] = conversation_now()
        self.active_rag_conversation_id = ""
        self.active_rag_stage = ""
        if target_id == self.current_conversation_id:
            self.history = [dict(item) for item in target["messages"]]
            self.current_sources = sources
            if self.inspector_visible:
                self.sources_inspector.set_sources(sources)
            self.chat_view.start_typewriter(answer, sources)
            self._set_status("正在逐字输出回答…")
        else:
            self.chat_view.set_busy(False)
            self._set_status("回答已保存到原会话")
        self._persist_conversations()
        self._refresh_conversation_sidebar()

    @Slot()
    def on_typewriter_finished(self) -> None:
        self.chat_view.set_busy(False)
        self.chat_view.composer.focus()
        if self.current_sources and self.inspector_visible:
            self.sources_inspector.set_sources(self.current_sources)
        self._set_status("回答完成")

    @Slot(str, str)
    def on_rag_failed(self, question: str, error: str) -> None:
        target_id = self.active_rag_conversation_id
        self.active_rag_conversation_id = ""
        self.active_rag_stage = ""
        if target_id == self.current_conversation_id:
            self.chat_view.fail_pending(f"回答失败：{error}")
            self.chat_view.composer.focus()
        self.chat_view.set_busy(False)
        self._set_status("回答失败")
        self._write_error_log(error)

    @Slot(str)
    def on_rag_cancelled(self, _question: str) -> None:
        target_id = self.active_rag_conversation_id
        self.active_rag_conversation_id = ""
        self.active_rag_stage = ""
        if target_id == self.current_conversation_id:
            self.chat_view.fail_pending("已停止生成。用户问题已保存在当前会话中。")
            self.chat_view.composer.focus()
        self.chat_view.set_busy(False)
        self._set_status("已停止生成")

    def stop_generation(self) -> None:
        if self.chat_view.finish_typewriter_immediately():
            self._set_status("已显示完整回答")
            return
        if self.rag_worker:
            self.rag_worker.stop()
            self._set_status("已请求停止生成")

    def _cleanup_rag_thread(self) -> None:
        if self.rag_worker:
            self.rag_worker.deleteLater()
        if self.rag_thread:
            self.rag_thread.deleteLater()
        self.rag_worker = None
        self.rag_thread = None
        if not self.chat_view.is_typewriting():
            self.chat_view.set_busy(False)

    def new_chat(self) -> None:
        current = self._current_conversation()
        if not self.history and not (
            self.rag_thread
            and self.rag_thread.isRunning()
            and self.active_rag_conversation_id == self.current_conversation_id
        ):
            self._render_current_conversation()
            self._set_status("当前已是空白新对话")
            self.chat_view.composer.focus()
            return
        self._persist_conversations()
        conversation = make_conversation()
        conversation_id = str(conversation["id"])
        self.conversations[conversation_id] = conversation
        self.current_conversation_id = conversation_id
        self.history = []
        self.current_sources = []
        self.sources_inspector.set_sources([])
        self.hide_inspector()
        self._persist_conversations()
        self._refresh_conversation_sidebar()
        self._render_current_conversation()
        if self.rag_thread and self.rag_thread.isRunning():
            self._set_status("已新建对话；上一会话仍在生成")
        else:
            self._set_status("已新建对话")
        self.chat_view.composer.focus()


    def save_settings(self) -> None:
        state = self.settings_sidebar.state()
        try:
            core.save_rag_settings(state.api_url, state.model, state.api_key, state.top_k, state.save_key)
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", str(exc))
            return
        self.settings_state = state
        self.chat_view.composer.model_combo.setCurrentText(state.model)
        self.status_bar_widget.model.setText(state.model)
        self._set_status("设置已保存")

    def model_changed_from_composer(self, model: str) -> None:
        if model and self.settings_sidebar.model.currentText() != model:
            self.settings_sidebar.model.blockSignals(True)
            self.settings_sidebar.model.setCurrentText(model)
            self.settings_sidebar.model.blockSignals(False)
        self.status_bar_widget.model.setText(model)

    def model_changed_from_settings(self, model: str) -> None:
        if model and self.chat_view.composer.model_combo.currentText() != model:
            self.chat_view.composer.model_combo.blockSignals(True)
            self.chat_view.composer.model_combo.setCurrentText(model)
            self.chat_view.composer.model_combo.blockSignals(False)
        self.status_bar_widget.model.setText(model)

    def _set_status(self, text: str) -> None:
        self.status_bar_widget.state.setText(text)
        self.chat_view.stage_label.setText(text)

    def _write_error_log(self, message: str) -> None:
        try:
            path = core.default_db_path().with_name("rag_error.log")
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(f"[{core.now_iso()}] {message}\n")
                handle.write(traceback.format_exc() + "\n")
        except Exception:
            pass

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.index_worker:
            self.index_worker.stop()
        if self.rag_worker:
            self.rag_worker.stop()
        sizes = self.main_splitter.sizes()
        if len(sizes) == 3:
            if sizes[0] > 0:
                self.ui_state["sidebar_width"] = sizes[0]
            if sizes[2] > 0:
                self.ui_state["inspector_width"] = sizes[2]
        geometry = self.geometry()
        self.ui_state.update(
            {
                "folder": self.folder_path,
                "db": self.db_path,
                "window_width": geometry.width(),
                "window_height": geometry.height(),
                "window_x": geometry.x(),
                "window_y": geometry.y(),
            }
        )
        try:
            save_ui_state(self.ui_state)
        except Exception:
            pass
        try:
            self._persist_conversations()
        except Exception:
            pass
        super().closeEvent(event)


def apply_application_font(app: QApplication) -> None:
    families = set(QFontDatabase.families())
    family = next((name for name in ("Segoe UI Variable Text", "Segoe UI", "Microsoft YaHei UI") if name in families), "Microsoft YaHei UI")
    font = QFont(family, 12)
    font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(font)


def main() -> int:
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EnterpriseKnowledge.Retrieval")
        except Exception:
            pass
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    icon = application_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    app.setOrganizationName("EnterpriseKnowledge")
    apply_application_font(app)
    app.setStyleSheet(APP_QSS)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
