import json
import os
from PySide6.QtWidgets import QFileDialog
from srs.parsers.file_parser_service import FileParserService
class FileManager:
    def __init__(self, parser_service: FileParserService):
        # TODO 🚧 В разработке: 02.07.2025
        self.tree_model = None
        self.parser_service = parser_service



    @staticmethod
    def get_save_path(title: str, filter: str) -> str | None:
        """Открывает диалог сохранения файла"""
        # ✅ Реализовано: 02.07.2025
        # filter = "Создать ST файл", "", "ST Files (*.st)"
        path, _ = QFileDialog.getSaveFileName(None, title, "", filter)
        return path

    @staticmethod
    def create_md_file(path: str) -> bool:
        """Создает новый MD-файл с базовым заголовком"""
        # ✅ Реализовано: 02.07.2025
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# {os.path.basename(path).replace('.md', '')}\n\n")
            return True
        except Exception as e:
            raise Exception(f"Ошибка создания MD-файла: {str(e)}")

    @staticmethod
    def create_st_file(path: str) -> bool:
        """Создает новый ST-файл с базовой структурой"""
        # ✅ Реализовано: 02.07.2025
        try:
            with open(path, 'w', encoding='utf-8') as f:
                name = os.path.basename(path).replace('.st', '')
                f.write(f"""{{1, {{"{name}", 1, 0, "", ""}}, []}}""")
            return True
        except Exception as e:
            raise Exception(f"Ошибка создания ST-файла: {str(e)}")

    def _get_save_path_json(self):
        """Возвращает путь к файлу сохранения"""
        # ✅ Реализовано: 02.07.2025
        return os.path.join(os.path.dirname(__file__), "saved_files.json")
    def save_files_to_json(self):
        """Сохраняет список загруженных файлов в JSON"""
        # ✅ Реализовано: 02.07.2025
        save_path = self._get_save_path()
        files = []

        # Собираем пути всех загруженных файлов (как st, так и md)
        for i in range(len(self.tree_model.root_item.child_items)):
            item = self.tree_model.root_item.child_items[i]
            if item.item_data[1] in ["file", "markdown"]:  # Изменено условие
                files.append({
                    "path": item.item_data[2],
                    "type": item.item_data[1]  # Сохраняем тип файла
                })

        # Сохраняем в JSON
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=4)


