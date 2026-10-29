from typing import Optional
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QCursor, QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGraphicsDropShadowEffect, QProgressBar,
    QScrollArea
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
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        header = QHBoxLayout()
        header.setSpacing(6)

        # Shortcut badge (e.g. "[1]")
        key_lbl = QLabel(f"[{key_shortcut}]")
        key_lbl.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        header.addWidget(key_lbl)

        # Category Tag
        tag_lbl = QLabel(tag)
        tag_lbl.setStyleSheet(f"color: {tag_color}; font-weight: bold; font-size: 11px;")
        header.addWidget(tag_lbl)
        header.addStretch()

        action_hint = QLabel("Klick / Taste")
        action_hint.setStyleSheet("color: #475569; font-size: 10px;")
        header.addWidget(action_hint)

        layout.addLayout(header)

        # Content text
        self.content_lbl = QLabel(text)
        self.content_lbl.setWordWrap(True)
        self.content_lbl.setStyleSheet("color: #f8fafc; font-size: 12px; line-height: 1.3;")
        layout.addWidget(self.content_lbl)

        self.setStyleSheet("""
            QFrame#SuggestionCard {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
            }
            QFrame#SuggestionCard:hover {
                background-color: #334155;
                border: 1px solid #38bdf8;
            }
        """)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
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
        self.setFixedWidth(480)

        self.cards: list[SuggestionCard] = []
        self._drag_pos: Optional[QPoint] = None

        # Main Layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        self.container = QFrame()
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
            QFrame#Container {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 10px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(0, 6)
        self.container.setGraphicsEffect(shadow)

        self.inner_layout = QVBoxLayout(self.container)
        self.inner_layout.setContentsMargins(12, 10, 12, 10)
        self.inner_layout.setSpacing(6)

        # Title bar (draggable)
        self.title_bar = QWidget()
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("🐭 SprachMaus")
        title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 13px;")
        title_layout.addWidget(title)

        hint = QLabel("Taste [1-4] oder [Esc] zum Schließen")
        hint.setStyleSheet("color: #64748b; font-size: 10px;")
        title_layout.addStretch()
        title_layout.addWidget(hint)
        self.inner_layout.addWidget(self.title_bar)

        # Original text preview
        self.orig_lbl = QLabel("")
        self.orig_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-style: italic;")
        self.orig_lbl.setWordWrap(True)
        self.orig_lbl.setMaximumHeight(36)
        self.inner_layout.addWidget(self.orig_lbl)

        # Explanation badge
        self.explanation_lbl = QLabel("")
        self.explanation_lbl.setStyleSheet("""
            background-color: #172554;
            color: #93c5fd;
            padding: 4px 8px;
            border-radius: 5px;
            font-size: 11px;
            font-weight: 500;
        """)
        self.explanation_lbl.setWordWrap(True)
        self.inner_layout.addWidget(self.explanation_lbl)

        # Loading bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(3)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border: none;
                border-radius: 1px;
            }
            QProgressBar::chunk {
                background-color: #38bdf8;
                border-radius: 1px;
            }
        """)
        self.inner_layout.addWidget(self.progress)

        # Scroll area for suggestions (so it never overflows screen height)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: #1e293b;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #475569;
                border-radius: 3px;
            }
        """)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.suggestions_layout = QVBoxLayout(self.scroll_content)
        self.suggestions_layout.setContentsMargins(0, 2, 0, 2)
        self.suggestions_layout.setSpacing(6)
        self.scroll.setWidget(self.scroll_content)

        self.inner_layout.addWidget(self.scroll)
        outer_layout.addWidget(self.container)

    def show_loading(self, original_text: str):
        self.cards.clear()
        while self.suggestions_layout.count():
            item = self.suggestions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        preview = original_text if len(original_text) <= 70 else original_text[:67] + "..."
        self.orig_lbl.setText(f'Original: "{preview}"')
        self.explanation_lbl.setText("💡 SprachMaus denkt nach...")
        self.progress.setVisible(True)
        self.scroll.setVisible(False)

        self.adjustSize()
        self._position_smart(estimated_height=140)
        self.show()
        self.raise_()
        self.activateWindow()

    def show_results(self, result: ImprovementResult):
        self.progress.setVisible(False)
        self.explanation_lbl.setText(f"💡 {result.explanation}")
        self.scroll.setVisible(True)

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

        # Compact height calculation
        screen = self.screen().availableGeometry()
        max_height = min(460, screen.height() - 80)
        self.scroll.setMaximumHeight(max_height - 130)

        self.adjustSize()
        self._position_smart()

    def _position_smart(self, estimated_height: Optional[int] = None):
        cursor_pos = QCursor.pos()
        screen = self.screen().availableGeometry()

        win_width = self.width() if self.width() > 0 else 480
        win_height = estimated_height or max(self.sizeHint().height(), self.height())

        x = cursor_pos.x() + 10

        # Wenn der Cursor in der unteren Bildschirmhälfte ist (z.B. Teams/Outlook Chat unten):
        # Zeige das Fenster OBERHALB des Cursors, damit die Hebel/Optionen voll sichtbar sind!
        if cursor_pos.y() > (screen.top() + screen.height() * 0.55):
            y = cursor_pos.y() - win_height - 15
        else:
            y = cursor_pos.y() + 25

        # Sicherstellen, dass das Fenster immer innerhalb des sichtbaren Bildschirms bleibt
        if x + win_width > screen.right() - 10:
            x = screen.right() - win_width - 10
        if x < screen.left() + 10:
            x = screen.left() + 10

        if y + win_height > screen.bottom() - 10:
            y = screen.bottom() - win_height - 10
        if y < screen.top() + 10:
            y = screen.top() + 10

        self.move(int(x), int(y))

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

    # Fenster per Maus verschiebbar machen
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
