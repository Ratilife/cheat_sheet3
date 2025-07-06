import os
from srs.managers.file_manager import FileManager
from srs.utils.delete_manager import DeleteManager
from srs.parsers.file_parser_service import FileParserService
class FileOperations:
    def __init__(self,  tree_model_manager=None, file_watcher=None):
        self.file_manager = FileManager()
        self.tree_manager = tree_model_manager
        self.file_watcher = file_watcher
        # TODO пока не определился с где будет находится менеджер удаления
        self.delete_manager = DeleteManager()
        self.parser_service = FileParserService()

    def add_file_to_tree(self, file_path: str) -> bool:
        """
        Выполняет полный процесс добавления файла в дерево файлового менеджера.

        Аргументы:
            file_path (str): Путь к файлу, который требуется добавить в дерево.

        Возвращает:
            bool: True, если файл успешно добавлен в дерево, иначе False.

        Описание процесса:
            1. Использует метод self.file_manager.parse_and_get_type, чтобы определить тип файла по переданному пути
               и получить дополнительные данные, если это необходимо.
            2. Добавляет элемент в дерево с помощью self.tree_manager.add_item, передавая тип элемента и путь к файлу.
            3. В случае возникновения исключения печатает сообщение об ошибке и возвращает False.

        Исключения:
            Все исключения перехватываются, чтобы избежать прерывания выполнения программы при ошибках
            (например, если файл не найден или не может быть обработан).
        """
        # TODO 🚧 В разработке: 02.07.2025 нужно переписать метод
        try:
            item_type, parsed_data = self.parser_service.parse_and_get_type(file_path)
            return self.tree_manager.add_item(item_type, file_path) #TODO ?
        except Exception as e:
            print(f"Ошибка добавления файла: {str(e)}")
            return False

    def create_and_add_st_file(self) -> tuple[bool, str]:
        """Полный цикл создания ST-файла"""
        # TODO 🚧 В разработке: 02.07.2025
        path = self.file_manager.get_save_path("Создать ST файл", "ST Files (*.st)")
        if not path:
            return False, "Отменено пользователем"

        try:
            if self.file_manager.create_st_file(path):
                # TODO - tree_manager.add_item("file", path) какой тп элемента создает, нужно передать
                self.tree_manager.add_item("file", path)
                # Обновление состояния
                self.file_watcher.set_current_file(path)  #TODO метод нужно создать
                # TODO функционал(Сигнал) наблюдателя observer не описан
                # TODO Реализовать загрузку данных ново созданного файла в редактор
                return True, f"Файл {os.path.basename(path)} создан"
        except Exception as e:
            return False, str(e)

    def create_and_add_md_file(self) -> tuple[bool, str]:
        """Полный цикл создания MD-файлов"""
        # TODO 🚧 В разработке: 02.07.2025
        path = self.file_manager.get_save_path("Создать MD файл", "Markdown Files (*.md)")
        if not path:
            return False, "Отменено пользователем"
        try:
            if self.file_manager.create_md_file(path):
                self.tree_manager.add_item("markdown", path)
                # Обновление состояния
                self.file_watcher.set_current_file(path)   #TODO метод нужно создать
                # Отправляем сигнал о создании файла
                # TODO функционал(Сигнал) наблюдателя observer не описан
                # TODO Реализовать загрузку данных ново созданного файла в редактор
                return True, f"Файл {os.path.basename(path)} создан"
        except Exception as e:
            return False, str(e)

    def create_folder(self, parent_index=None) -> tuple[bool, str]:
        """Создает папку через единый интерфейс добавления элементов"""
        # ✅ Реализовано: 06.07.2025
        name, ok = self.file_manager.get_text_input(
            title="Создать папку",
            label="Введите имя папки:"
        )
        if not ok:
            return False, "Отменено"
        if not name:
            return False, "Имя папки не может быть пустым"

        return self.tree_manager.add_item(
            item_type="folder",
            path=name,
            parent_index=parent_index
        ), f"Папка '{name}' создана"