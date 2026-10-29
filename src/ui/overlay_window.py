from typing import Callable, Optional
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QCursor, QKeyEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QProgressBar
)
from src.ai_service import ImprovementResult


class SuggestionCard(QFrame):
    clicked = Signal(str)

    def __init__(self, key_shortcut: str, tag: str, tag_color: str, text: str, parent=None):
        super().__init__(parent)
        self.text_content = text
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setObjectName("SuggestionCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(8)

        # Shortcut badge (e.g. "[1]")
        key_lbl = QLabel(f"[{key_shortcut}]")
        key_lbl.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px;")
        header.addWidget(key_lbl)

        # Category Tag
        tag_lbl = QLabel(tag)
        tag_lbl.setStyleSheet(f"color: {tag_color}; font-weight: bold; font-size: 12px;")
        header.addWidget(tag_lbl)
        header.addStretch()

        layout.addLayout(header)

        # Content text
        self.content_lbl = QLabel(text)
        self.content_lbl.setWordWrap(True)
        self.content_lbl.setStyleSheet("color: #f8fafc; font-size: 13px; line-height: 1.4;")
        layout.addWidget(self.content_lbl)

        self.setStyleSheet("""
            QFrame#SuggestionCard {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QFrame#SuggestionCard:hover {
                background-color: #334155;
                border: 1px solid #38bdf8;
            }
        """)

    def mousePressEvent(self, event):
        self.clicked.emit(self.text_content)


class OverlayWindow(QWidget):
    suggestion_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(520, 360)

        self.cards: list[SuggestionCard] = []

        # Shadow & Main Container
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(16, 16, 16, 16)

        self.container = QFrame()
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
            QFrame#Container {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 12px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)

        self.inner_layout = QVBoxLayout(self.container)
        self.inner_layout.setContentsMargins(16, 14, 16, 14)
        self.inner_layout.setSpacing(10)

        # Title bar
        title_bar = QHBoxLayout()
        title = QLabel("🐭 SprachMaus")
        title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 14px;")
        title_bar.addWidget(title)

        hint = QLabel("Drücke [1-4] oder klicke zum Einfügen | [Esc] zum Abbrechen")
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        title_bar.addStretch()
        title_bar.addWidget(hint)
        self.inner_layout.addLayout(title_bar)

        # Original text preview
        self.orig_lbl = QLabel("")
        self.orig_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-style: italic;")
        self.orig_lbl.setWordWrap(True)
        self.inner_layout.addWidget(self.orig_lbl)

        # Explanation badge
        self.explanation_lbl = QLabel("")
        self.explanation_lbl.setStyleSheet("""
            background-color: #172554;
            color: #93c5fd;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 500;
        """)
        self.explanation_lbl.setWordWrap(True)
        self.inner_layout.addWidget(self.explanation_lbl)

        # Loading bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #38bdf8;
                border-radius: 2px;
            }
        """)
        self.inner_layout.addWidget(self.progress)

        # Container for suggestions
        self.suggestions_layout = QVBoxLayout()
        self.suggestions_layout.setSpacing(8)
        self.inner_layout.addLayout(self.suggestions_layout)

        outer_layout.addWidget(self.container)

    def show_loading(self, original_text: str):
        self.cards.clear()
        # Clear layout
        while self.suggestions_layout.count():
            item = self.suggestions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        preview = original_text if len(original_text) <= 80 else original_text[:77] + "..."
        self.orig_lbl.setText(f'Original: "{preview}"')
        self.explanation_lbl.setText("💡 SprachMaus denkt nach...")
        self.progress.setVisible(True)

        self._position_near_cursor()
        self.show()
        self.raise_()
        self.activateWindow()

    def show_results(self, result: ImprovementResult):
        self.progress.setVisible(False)
        self.explanation_lbl.setText(f"💡 {result.explanation}")

        items = [
            ("1", "🟢 Korrigiert (Grammatik & Artikel)", "#4ade80", result.corrected),
            ("2", "👔 Formell & Büro", "#60a5fa", result.formal),
            ("3", "💬 Locker / Chat", "#f472b6", result.casual),
        ]
        if result.english:
            items.append(("4", "🇬🇧 Englisch", "#fbbf24", result.english))

        for key_num, tag, color, text in items:
            card = SuggestionCard(key_num, tag, color, text, self)
            card.clicked.connect(self._on_card_clicked)
            self.cards.append(card)
            self.suggestions_layout.addWidget(card)

        self.adjustSize()
        self._position_near_cursor()

    def _on_card_clicked(self, text: str):
        self.hide()
        self.suggestion_selected.emit(text)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.hide()
        elif key == Qt.Key.Key_1 and len(self.cards) >= 1:
            self._on_card_clicked(self.cards[0].text_content)
        elif key == Qt.Key.Key_2 and len(self.cards) >= 2:
            self._on_card_clicked(self.cards[1].text_content)
        elif key == Qt.Key.Key_3 and len(self.cards) >= 3:
            self._on_card_clicked(self.cards[2].text_content)
        elif key == Qt.Key.Key_4 and len(self.cards) >= 4:
            self._on_card_clicked(self.cards[3].text_content)
        else:
            super().keyPressEvent(event)

    def _position_near_cursor(self):
        cursor_pos = QCursor.pos()
        screen = self.screen().availableGeometry()

        x = cursor_pos.x() + 10
        y = cursor_pos.y() + 10

        # Boundary checks so it doesn't open off-screen
        if x + self.width() > screen.right():
            x = max(screen.left(), screen.right() - self.width() - 10)
        if y + self.height() > screen.bottom():
            y = max(screen.top(), cursor_pos.y() - self.height() - 10)

        self.move(x, y)

