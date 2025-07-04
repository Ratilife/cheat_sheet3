"""
    Модуль st_file_parser.py

    Предназначен для парсинга и обработки структурированных текстовых файлов (ST-файлов)
    с использованием ANTLR4. Обеспечивает:
    1. Чтение и анализ структуры ST-файлов
    2. Удаление элементов (шаблонов и папок)
    3. Сохранение изменений обратно в файл

    Основные компоненты:
    - STFileParserWrapper: основной класс для работы с файлами
    - ExceptionErrorListener: обработчик ошибок парсинга
    - StructureListener: слушатель для построения структуры файла
"""

import os
# Импорт компонентов ANTLR
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener
from srs.ANTLR4.STFileLexer import STFileLexer
from srs.ANTLR4.STFileParser import STFileParser
from srs.ANTLR4.STFileListener import STFileListener
# ===================================================================
# КЛАССЫ ДЛЯ ПАРСИНГА ST-ФАЙЛОВ
# ===================================================================

class STFileParserWrapper:
    """
        Основной класс-обертка для работы с ST-файлами.
        Предоставляет высокоуровневый API для операций с файлами.
    """
    def parse_st_file(self, file_path):
        """
                Парсит ST-файл и возвращает его структуру.

                Параметры:
                - file_path: путь к файлу для парсинга

                Возвращает:
                Словарь с ключами:
                - structure: иерархическая структура файла
                - root_name: имя корневого элемента (имя файла без расширения)
        """
        try:
            # Создание входного потока с указанием кодировки
            input_stream = FileStream(file_path, encoding="utf-8")
            # Лексический анализ
            lexer = STFileLexer(input_stream)
            tokens = CommonTokenStream(lexer)
            # Синтаксический анализ
            parser = STFileParser(tokens)

            # Устанавливаем обработчик ошибок
            parser.removeErrorListeners()
            parser.addErrorListener(ExceptionErrorListener())
            # Парсинг структуры файла
            tree = parser.fileStructure()
            # Создание и настройка слушателя
            listener = StructureListener()
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            listener.root_name = file_name  # ИЗМЕНЕНИЕ: Имя файла в listener
            # Обход дерева разбора
            ParseTreeWalker().walk(listener, tree)

            return {
                'structure': listener.get_structure(),
                'root_name': listener.root_name
            }
        except Exception as e:
            # Возвращаем базовую структуру при ошибке парсинга
            return {
                'structure': [],
                'root_name': os.path.splitext(os.path.basename(file_path))[0]
            }

    # Добавляем методы в STFileParserWrapper:
    def remove_template(self, file_path, template_name):
        """
            Удаляет указанный шаблон из ST-файла.
            Параметры:
                - file_path: путь к файлу
                - template_name: имя удаляемого шаблона

            Исключения:
                - ValueError: если файл не может быть прочитан
                - IOError: при ошибках сохранения
        """
        structure = self.parse_st_file(file_path)
        if not structure:
            raise ValueError(f"Не удалось прочитать файл {file_path}")
        # Фильтрация структуры (удаление шаблона)
        new_structure = self._remove_from_structure(
            structure,
            lambda x: not (x['type'] == 'template' and x['name'] == template_name)
        )
        # Сохранение изменений
        self._save_structure(file_path, new_structure)

    def remove_folder(self, file_path, folder_name):
        """
                    Удаляет указанную папку из ST-файла.
                    Параметры:
                        - file_path: путь к файлу
                        - folder_name: имя удаляемой папки
                    Исключения:
                        - ValueError: если файл не может быть прочитан
                        - IOError: при ошибках сохранения
        """
        structure = self.parse_st_file(file_path)
        if not structure:
            raise ValueError(f"Не удалось прочитать файл {file_path}")
        # Фильтрация структуры (удаление папки)
        new_structure = self._remove_from_structure(
            structure,
            lambda x: not (x['type'] == 'folder' and x['name'] == folder_name)
        )
        # Сохранение изменений
        self._save_structure(file_path, new_structure)

    def _remove_from_structure(self, structure, filter_fn):
        """
            Внутренний метод для рекурсивной фильтрации структуры.

            Параметры:
            - structure: текущая структура
            - filter_fn: функция-фильтр (возвращает True для сохраняемых элементов)

            Возвращает:
            Отфильтрованную структуру
        """
        # Фильтрация элементов верхнего уровня
        structure['structure'] = [
            item for item in structure['structure']
            if filter_fn(item)
        ]
        # Рекурсивная обработка вложенных папок
        for item in structure['structure']:
            if item['type'] == 'folder':
                item['children'] = self._remove_from_structure(item, filter_fn)
        return structure

    def _save_structure(self, file_path, structure):
        """
        Внутренний метод для сохранения структуры в файл.

        Параметры:
        - file_path: путь к файлу
        - structure: структура для сохранения

        Исключения:
        - IOError: при ошибках записи в файл
        """
        content = self._generate_st_content(structure)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Ошибка сохранения файла: {str(e)}")

    def parse_and_get_type(self, file_path: str) -> tuple[str, dict]:
        # TODO 🚧 В разработке: 04.07.2025 определится нужен сдесь этот метод
        if file_path.endswith('.st'):
            return "file", self.parse_st_file(file_path)
        elif file_path.endswith('.md'):
            raise ValueError("MD files are not supported by this parser")
        raise ValueError("Unsupported file type")

    def _generate_st_content(self, structure):
        """
        Генерация содержимого ST файла согласно грамматике STFile.g4.
        """

        def build_folder(folder):
            children = []
            for child in folder.get('children', []):
                if child['type'] == 'folder':
                    children.append(
                        f'{{1, {{"{child["name"]}", 1, 0, "", ""}}, [\n'
                        f'{build_folder(child)}\n'
                        ']}'
                    )
                elif child['type'] == 'template':
                    children.append(
                        f'{{0, {{"{child["name"]}", 0, 1, "", "{child["content"]}"}}}}'
                    )
            return ',\n'.join(children)

        root_folder = structure['content']
        return (
            f'{{1, {{"{root_folder["name"]}", 1, 0, "", ""}}, [\n'
            f'{build_folder(root_folder)}\n'
            ']}'
        )
class ExceptionErrorListener(ErrorListener):
    """
        Кастомный обработчик ошибок парсинга для ANTLR.
        Преобразует ошибки синтаксиса в исключения Python с подробным описанием.
    """
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
                Вызывается при обнаружении синтаксической ошибки.

                Параметры:
                - recognizer: распознаватель, обнаруживший ошибку
                - offendingSymbol: ошибочный символ
                - line: номер строки с ошибкой
                - column: позиция в строке
                - msg: сообщение об ошибке
                - e: исключение (если есть)
        """
        raise Exception(f"Ошибка парсинга в строке {line}:{column} - {msg}")

class StructureListener(STFileListener):
    """
        Слушатель для построения структуры ST-файла в виде дерева объектов.
        Наследуется от сгенерированного ANTLR listener'а.
    """
    def __init__(self):
        """Инициализация слушателя с пустой структурой."""
        self.stack = [{'children': []}]             # Стек для хранения иерархии элементов
        self.current_parent = self.stack[0]         # Текущий родительский элемент
        self.root_name = "Unnamed"                  # Имя корневого элемента (по умолчанию)
        self.found_root = False                     # Флаг обнаружения корневого элемента


    def get_structure(self):
        """Возвращает полную структуру файла."""
        return self.stack[0]['children']


    def enterEntry(self, ctx):
        """
            Обрабатывает вход в элемент структуры (папку или шаблон).

            Параметры:
              - ctx: контекст элемента (от ANTLR)
        """
        if ctx.folderHeader():
            # Обработка папки
            header = ctx.folderHeader()
            name = header.STRING(0).getText()[1:-1]   # Извлечение имени (удаляем кавычки)

            # Создание элемента папки
            new_item = {
                'name': name,
                'type': 'folder',
                'children': []
            }
            # Добавление в текущего родителя и обновление стека
            self.current_parent['children'].append(new_item)
            self.stack.append(new_item)
            self.current_parent = new_item



        elif ctx.templateHeader():
            # Обработка шаблона
            header = ctx.templateHeader()
            name = header.STRING(0).getText()[1:-1]    # Имя шаблона
            # Содержимое шаблона (если есть)
            content = header.STRING(2).getText()[1:-1] if len(header.STRING()) > 1 else ""

            # Добавление шаблона в текущего родителя
            self.current_parent['children'].append({
                'name': name,
                'type': 'template',
                'content': content
            })

    def exitEntry(self, ctx):
        """
            Обрабатывает выход из элемента структуры.

            Параметры:
             - ctx: контекст элемента (от ANTLR)
        """
        if ctx.folderHeader() and len(self.stack) > 1:
            # Для папки: возвращаемся к предыдущему родителю
            self.stack.pop()
            self.current_parent = self.stack[-1]

