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
        """Добавляет элемент в дерево.
        Args:
            item_type: 'file', 'folder', 'markdown', 'template'
            path: путь к файлу или имя папки/шаблона
            parent_index: родительский индекс (None для корня)
        Returns:
            bool: True если добавление успешно
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

    def _new_st_file(self):
        # TODO 🚧 В разработке: 04.07.2025 Определится нужен file_manager для TreeModelManager
        path, _ = QFileDialog.getSaveFileName(
            self, "Создать ST файл", "", "ST Files (*.st)")
        # Открытие диалогового окна сохранения файла:
        # - Заголовок: "Создать ST файл"
        # - Начальная директория не указана (пустая строка)
        # - Фильтр файлов: только .st расширение
        # Возвращает путь к файлу и выбранный фильтр (который игнорируется)
        if path:
            # Проверка, что пользователь не отменил диалог (путь не пустой)
            # Добавляем расширение, если его нет
            if not path.endswith('.st'):
                path += '.st'

        # Делегируем создание файла FileManager
        try:
            if self.file_manager.create_st_file(path):
                # Добавляем файл в модель
                self.tree_model.add_st_file(path)
                self.file_created.emit(path) # TODO функционал(Сигнал) не описан

        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось создать файл: {str(e)}")