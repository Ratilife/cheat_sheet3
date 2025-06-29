import sys
import os
from PySide6.QtWidgets import (QTreeView, QWidget,
                               QVBoxLayout, QApplication, QMenu,
                               QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject, QRect, QSize
from srs.observers.file_watcher import FileWatcher
from srs.observers.my_base_observer import MyBaseObserver
# Основной класс боковой панели

# Класс для обработки сигналов панели
class SidePanelObserver(MyBaseObserver):
    # ✅ Реализовано: 29.06.2025
    def __init__(self):
        super().__init__()
class SidePanel(QWidget):

    def __init__(self, parent=None):
        # - Всегда поверх других окон (WindowStaysOnTopHint)
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)


if __name__ == "__main__":
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Создаем экземпляр боковой панели
    panel = SidePanel()
    # Устанавливаем заголовок окна
    panel.setWindowTitle("Системная боковая панель")

    # Показываем панель
    panel.show()
    # Запускаем цикл обработки событий
    sys.exit(app.exec())