import os
from srs.managers.file_manager import FileManager
from srs.utils.delete_manager import DeleteManager
class FileOperations:
    def __init__(self,  tree_model_manager=None, file_watcher=None):
        self.file_manager = FileManager()
        self.tree_manager = tree_model_manager
        self.file_watcher = file_watcher
        # TODO пока не определился с где будет находится менеджер удаления
        self.delete_manager = DeleteManager()

    def add_file_to_tree(self, file_path: str) -> bool:
        """Полный процесс добавления файла"""
        # TODO 🚧 В разработке: 02.07.2025
        try:
            item_type, parsed_data = self.file_manager.parse_and_get_type(file_path)
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
                self.file_watcher.set_current_file(path)
                return True, f"Файл {os.path.basename(path)} создан"
        except Exception as e:
            return False, str(e)

    def create_and_add_md_file(self) -> tuple[bool, str]:
        """Полный цикл создания MD-файлов"""
        # ✅ Реализовано: 02.07.2025
        path = self.file_manager.get_save_path("Создать MD файл", "Markdown Files (*.md)")
        if not path:
            return False, "Отменено пользователем"
        try:
            if self.file_manager.create_md_file(path):
                self.tree_manager.add_item("markdown", path)
                # Обновление состояния
                self.file_watcher.set_current_file(path)
                return True, f"Файл {os.path.basename(path)} создан"
        except Exception as e:
            return False, str(e)
