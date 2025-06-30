from srs.observers.my_base_observer import MyBaseObserver
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QTreeView, QFileDialog,
                               QMessageBox, QSplitter, QStyle, QInputDialog, QApplication, QButtonGroup, QRadioButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
class FileEditorWindowObserver(MyBaseObserver):
    # ✅ Реализовано: 30.06.2025
    def __init__(self):
        super().__init__()

class FileEditorWindow(QMainWindow):
    """
        Главное окно редактора файлов с поддержкой форматов .st и .md.
        Обеспечивает создание, редактирование и сохранение файлов.
    """
    pass
