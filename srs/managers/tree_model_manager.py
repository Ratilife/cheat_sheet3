import os
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import (QMenu, QMessageBox, QFileDialog, QInputDialog)
from PySide6.QtGui import QAction

class TreeModelManager:
    """
    Фасад для работы с моделью дерева файлов. Инкапсулирует:
    - Добавление/удаление элементов
    - Парсинг файлов
    - Взаимодействие с DeleteManager
    """
    pass