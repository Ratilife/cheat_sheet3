import os
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import (QMenu, QMessageBox, QFileDialog, QInputDialog)
from PySide6.QtGui import QAction
from srs.models.st_file_tree_model import STFileTreeModel
from srs.managers.file_manager import FileManager
class TreeModelManager:
    """
    Фасад для работы с моделью дерева файлов. Инкапсулирует:
    - Добавление/удаление элементов
    - Парсинг файлов
    - Взаимодействие с DeleteManager
    """

    def __init__(self, file_manager: FileManager):
        # TODO 🚧 В разработке: 02.07.2025
        self.tree_model = STFileTreeModel()
        self.file_manager = file_manager


    def add_item(self, item_type: str, path: str, parent_index=None) -> bool:
        """
         Добавляет новый элемент (файл, папку, markdown-файл или шаблон) в дерево модели.

         Аргументы:
             item_type (str): Тип добавляемого элемента. Возможные значения:
                 - 'file'      : обычный файл
                 - 'folder'    : папка
                 - 'markdown'  : markdown-файл
                 - 'template'  : шаблон
             path (str): Путь к файлу или имя новой папки/шаблона/markdown-файла.
             parent_index: Индекс родительского элемента в дереве, к которому будет добавлен новый элемент.
                           Если None — элемент добавляется в корень дерева.

         Возвращает:
             bool: True, если элемент был успешно добавлен, иначе False.

         Описание работы:
             В зависимости от значения item_type вызывает соответствующий метод tree_model:
                 - Для 'file' вызывается self.tree_model.add_st_file(path)
                 - Для 'markdown' вызывается self.tree_model.add_markdown_file(path)
                 - Для 'folder' вызывается self.tree_model.add_folder(path, parent_index)
                 - Для 'template' вызывается self.tree_model.add_template(path, parent_index)
             Если тип элемента не распознан, возвращает False.

             В случае возникновения исключения при добавлении элемента — выводит сообщение об ошибке в консоль и возвращает False.

         Исключения:
             Все возможные исключения перехватываются, чтобы предотвратить аварийное завершение работы программы при ошибках добавления.
         """

        try:
            if item_type == "file":
                return self.tree_model.add_st_file(path)
            elif item_type == "markdown":
                return self.tree_model.add_markdown_file(path)
            elif item_type == "folder":
                # Реализация для папок
                return self.tree_model.add_folder(path, parent_index)  # TODO сделать метод
            elif item_type == "template":
                # Реализация для шаблонов
                return self.tree_model.add_template(path, parent_index)  # TODO сделать метод
            return False
        except Exception as e:
            print(f"Ошибка добавления элемента {path}: {str(e)}")
            return False

