import json
from PySide6.QtWidgets import QFileIconProvider
from PySide6.QtCore import QAbstractItemModel, Qt, QModelIndex, QSize
from PySide6.QtGui import QIcon, QFont

from PySide6.QtGui import QColor
from srs.parsers.md_file_parser import MarkdownListener
from srs.parsers.st_file_parser import STFileParserWrapper
from srs.models.st_file_tree_item import STFileTreeItem
# Модель данных для дерева
class STFileTreeModel(QAbstractItemModel):
    """Модель данных для отображения структуры ST-файлов в дереве"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = STFileTreeItem(["Root", "root", ""])  # Корневой элемент
        self.parser = STFileParserWrapper()  # Обертка для парсера
        self.md_parser = MarkdownListener()  # Добавляем парсер для MD
        self.icon_provider = QFileIconProvider()  # Провайдер иконок

    # Основные методы модели
    def index(self, row, column, parent=QModelIndex()):
        """Создает индекс для элемента"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        child_item = parent_item.child_items[row]
        return self.createIndex(row, column, child_item)

    def parent(self, index):
        """Возвращает родителя элемента"""
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent_item

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.child_items.index(child_item), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        """Количество строк (дочерних элементов)"""
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        return len(parent_item.child_items)

    def columnCount(self, parent=QModelIndex()):
        """Количество колонок (фиксировано: Имя и Тип)"""
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Возвращает данные для отображения"""
        if not index.isValid():
            return None

        item = index.internalPointer()
        column = index.column()

        if role == Qt.DisplayRole:
            return item.item_data[column]

        elif role == Qt.DecorationRole and column == 0:
            # Возвращаем иконки для разных типов элементов
            if item.item_data[1] == "file":
                return QIcon.fromTheme("text-x-generic")
            elif item.item_data[1] == "folder":
                return QIcon.fromTheme("folder")
            elif item.item_data[1] == "template":
                return QIcon.fromTheme("text-x-script")
            elif item.item_data[1] == "markdown":
                return QIcon.fromTheme("text-markdown")

        elif role == Qt.FontRole:
            # Жирный шрифт для файлов
            font = QFont()
            if item.item_data[1] in ["file", "markdown"]:
                font.setBold(False)
            elif item.item_data[1] == "folder":
                font.setBold(True)
            return font

        elif role == Qt.ForegroundRole:
            # Разные цвета для разных типов элементов
            if item.item_data[1] == "file":
                return QColor("#2a82da")
            elif item.item_data[1] == "folder":
                return QColor("#006400")  # Темно-зеленый для папок
            elif item.item_data[1] == "template":
                return QColor("#00008B")  # Темно-синий для шаблонов
            elif item.item_data[1] == "markdown":
                return QColor("#8B008B")  # Темно-пурпурный для markdown

        elif role == Qt.SizeHintRole:
            return QSize(0, 24)  # Фиксированная высота строк

        # Добавляем пользовательскую роль для определения уровня вложенности
        elif role == Qt.UserRole + 1:
            level = 0
            parent = item.parent_item
            while parent and parent != self.root_item:
                level += 1
                parent = parent.parent_item
            return level
        # Добавляем роль для установки типа элемента (для CSS селекторов)
        elif role == Qt.UserRole + 2:
            return item.item_data[1]  # Возвращаем тип элемента

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Заголовки колонок"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Имя"][section]
        return None

    def add_st_file(self, file_path):
        """Добавляет новый ST-файл в модель"""
        if any(item.item_data[2] == file_path for item in self.root_item.child_items):
            print(f"File {file_path} already exists in tree!")
            return

        # Получаем результат парсинга, который теперь содержит и структуру, и имя корневой папки
        result = self.parser.parse_st_file(file_path)

        print("Parsed structure:")
        print(json.dumps(result['structure'], indent=2, ensure_ascii=False))
        print(f"Root name: {result['root_name']}")  # Отладочный вывод

        # Извлекаем имя корневой папки (например, "Новый1")
        root_name = result['root_name']

        # Извлекаем структуру файла для построения дерева
        structure = result['structure']

        # Начинаем вставку данных в модель
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        # Создаем элемент для корневой папки с именем из файла
        file_item = STFileTreeItem([root_name, "file", file_path], self.root_item)


        # Строим поддерево на основе структуры файла
        self._build_tree(structure, file_item)

        # Добавляем элемент в корневую папку модели
        self.root_item.child_items.append(file_item)

        # Завершаем вставку
        self.endInsertRows()
        # self.print_tree()
        print(f"Структура из парсера: {json.dumps(structure, indent=2)}")

    def _build_tree(self, nodes, parent):
        """
        Рекурсивно строит дерево элементов из переданных данных.

        Аргументы:
            nodes (list): Список словарей, каждый из которых описывает узел дерева.
                Ожидается, что каждый словарь содержит ключи 'name' (имя элемента),
                'type' (тип элемента, например, 'file' или 'folder'),
                и опционально 'content' (содержимое файла) и 'children' (список дочерних элементов).
            parent (STFileTreeItem): Родительский элемент, к которому будут добавляться новые дочерние элементы.

        Описание:
            Для каждого узла из списка nodes создаётся новый экземпляр STFileTreeItem на основе информации из словаря.
            Новый элемент добавляется в список дочерних элементов parent.child_items.
            Если в словаре присутствует ключ 'children', рекурсивно вызывается этот же метод для построения дочерних элементов.
            Таким образом, метод позволяет построить всю иерархию дерева из вложенной структуры данных.
        """
        for node in nodes:
            item = STFileTreeItem([node['name'], node['type'], node.get('content', '')], parent)
            parent.child_items.append(item)
            if 'children' in node:
                self._build_tree(node['children'], item)

    def is_folder(self, index):
        """
        Проверяет, является ли элемент папкой.

        Аргументы:
            index (QModelIndex): Индекс элемента, который требуется проверить.

        Возвращаемое значение:
            bool: True, если элемент является папкой (item.type == "folder"), иначе False.

        Описание:
            Метод проверяет валидность переданного индекса. Если индекс невалиден, возвращает False.
            Затем получает внутренний объект элемента с помощью index.internalPointer().
            Возвращает True, если тип элемента равен "folder", иначе False.
        """
        if not index.isValid():
            return False
        item = index.internalPointer()
        return item.type == "folder"

    def add_markdown_file(self, file_path):
        """Добавляет Markdown файл в модель"""
        #TODO переписать метод
        result = self.md_parser.parse_markdown_file(file_path) # TODO изменить перенести в метод parse_and_get_type

        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        # Создаем элемент для файла
        file_item = STFileTreeItem([result['root_name'], "markdown", file_path], self.root_item)

        # Строим структуру (для MD будет только один корневой элемент)
        #self._build_tree(result['structure'], file_item)

        self.root_item.child_items.append(file_item)
        self.endInsertRows()

    def has_children(self, parent=QModelIndex()):
        """
            Проверяет, есть ли у указанного элемента дочерние элементы.

            Аргументы:
                parent (QModelIndex, необязательный): Индекс родительского элемента.
                    По умолчанию используется корневой элемент (QModelIndex()).

            Возвращаемое значение:
                bool: True, если у элемента есть дочерние элементы, иначе False.

            Описание:
                Если индекс parent невалиден, метод проверяет наличие дочерних элементов у корневого элемента (self.root_item).
                Если индекс валиден, получает соответствующий объект через parent.internalPointer() и проверяет,
                есть ли у него дочерние элементы (элементы в item.child_items).
        """
        if not parent.isValid():
            return len(self.root_item.child_items) > 0
        item = parent.internalPointer()
        return len(item.child_items) > 0

    def canFetchMore(self, parent):
        """
        Проверяет, можно ли загрузить дополнительные дочерние элементы для указанного родительского элемента.

        Аргументы:
            parent (QModelIndex): Индекс родительского элемента, для которого проверяется возможность загрузки дочерних элементов.

        Возвращаемое значение:
            bool: True, если у элемента существуют дочерние элементы, которые можно загрузить; False в противном случае.

        Описание:
            Метод используется в модели для поддержки динамической подгрузки данных (ленивая загрузка).
            Если parent невалиден, возвращается False, так как нельзя загрузить дочерние элементы для несуществующего родителя.
            Если индекс валиден, метод получает соответствующий внутренний объект через parent.internalPointer().
            Затем проверяется наличие дочерних элементов в item.child_items:
            если список не пуст, возвращается True — это сигнал для модели, что можно подгрузить дочерние элементы.
            Если дочерних элементов нет, возвращается False.
        """
        if not parent.isValid():
            return False
        item = parent.internalPointer()
        return bool(item.child_items)

    # необезательный метод создан для проверки данных
    def print_tree(self, item=None, level=0):
        """
        Рекурсивно выводит в консоль структуру дерева начиная с указанного элемента.

        Аргументы:
            item (STFileTreeItem, необязательный): Элемент дерева, с которого начинается печать.
                Если не передан, используется корневой элемент self.root_item.
            level (int, необязательный): Текущий уровень вложенности, используется для визуального отступа при печати.
                На каждом уровне вложенности увеличивается на 1.

        Описание:
            Метод предназначен для отладки структуры дерева.
            Он рекурсивно обходит все дочерние элементы, начиная с заданного item (или с корня, если item не указан).
            Для каждого элемента выводится строка с отступом, соответствующим уровню вложенности,
            а также информацией о названии элемента (item.item_data[0]) и его типе (item.type).
            Далее для каждого дочернего элемента вызывается этот же метод, увеличивая уровень вложенности.
        """
        item = item or self.root_item
        print("  " * level + f"- {item.item_data[0]} ({item.type})")
        for child in item.child_items:
            self.print_tree(child, level + 1)

    def flags(self, index):
        """
        Возвращает флаги, определяющие поведение элемента в модели.

        Аргументы:
            index (QModelIndex): Индекс элемента, для которого необходимо получить флаги.

        Возвращаемое значение:
            Qt.ItemFlags: Набор флагов, указывающих на свойства элемента (например, доступность, выделяемость,
            наличие чекбокса и др.).

        Описание:
            Метод определяет, какие действия разрешены для элемента по переданному индексу.
            Если индекс невалиден, возвращается Qt.NoItemFlags, что означает отсутствие доступных действий.
            Для валидного индекса по умолчанию устанавливаются флаги Qt.ItemIsEnabled (элемент включён) и
            Qt.ItemIsSelectable (элемент можно выделять).
            Если элемент является папкой (item.type == "folder") и содержит дочерние элементы (len(item.child_items) > 0),
            дополнительно устанавливаются флаги Qt.ItemIsAutoTristate (чекбокс может быть в промежуточном состоянии) и
            Qt.ItemIsUserCheckable (отображается чекбокс).
        """
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        item = index.internalPointer()
        if item and item.type == "folder" and len(item.child_items) > 0:
            flags |= Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable

        return flags


    def removeRow(self, row, parent=QModelIndex()):
        """
        Удаляет строку (элемент) из модели.

        Аргументы:
            row (int): Номер строки (индекс элемента), который требуется удалить из родительского элемента.
            parent (QModelIndex, необязательный): Индекс родительского элемента, из которого будет удаляться строка.
            По умолчанию используется корневой элемент (QModelIndex()).

        Возвращаемое значение:
            bool: True, если удаление прошло успешно, иначе False.

        Описание:
            Метод реализует стандартное удаление строки в модели, основанной на QAbstractItemModel.
            Если parent невалиден, используется корневой элемент модели (self.root_item) как родитель.
            Если переданный индекс строки некорректен (отрицательный или превышает количество дочерних элементов),
            возвращается False.

            Для удаления вызываются beginRemoveRows и endRemoveRows для корректного обновления модели и интерфейса.
            После этого соответствующий дочерний элемент удаляется из списка child_items родительского элемента.
            При успешном удалении возвращается True.
        """
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if row < 0 or row >= len(parent_item.child_items):
            return False

        self.beginRemoveRows(parent, row, row)
        parent_item.child_items.pop(row)
        self.endRemoveRows()
        return True

    def get_item_path(self, index):
        """
        Возвращает путь к файлу для указанного элемента дерева.

        Аргументы:
            index (QModelIndex): Индекс элемента, для которого требуется получить путь к файлу.

        Возвращаемое значение:
            str или None: Строка с абсолютным или относительным путем к файлу, если элемент является файлом или markdown-файлом.
            Если элемент не является файлом или индекс невалиден, возвращается None.

        Описание:
            Метод проверяет валидность переданного индекса. Если индекс невалиден, возвращает None.
            Затем получает внутренний объект элемента через index.internalPointer().
            Если тип элемента (item.item_data[1]) равен 'file' или 'markdown', метод возвращает путь к файлу,
            который хранится в item.item_data[2]. Если элемент не является файлом или markdown-файлом, возвращает None.
        """
        if not index.isValid():
            return None

        item = index.internalPointer()
        if item.item_data[1] in ['file', 'markdown']:
            return item.item_data[2]
        return None

    def get_item_type(self, index):
        """
        Возвращает тип элемента файлового дерева.

        Аргументы:
            index (QModelIndex): Индекс элемента, для которого требуется определить тип.

        Возвращаемое значение:
            str: Тип элемента, например, 'file', 'folder' и т.д.

        Описание:
            Метод получает внутренний объект элемента с помощью index.internalPointer(),
            после чего извлекает из его структуры данных значение, определяющее тип элемента.
            Обычно это строка, обозначающая, является ли элемент файлом, папкой и т.д.
            Тип хранится во втором элементе item_data (item.item_data[1]).
        """
        item = index.internalPointer()
        return item.item_data[1]  # 'folder', 'file' и т.д.

    def get_item_level(self, index):
        """
        Возвращает уровень вложенности элемента в дереве файлов.

        Аргументы:
            index (QModelIndex): Индекс элемента, для которого требуется определить уровень вложенности.

        Возвращаемое значение:
            int: Уровень вложенности элемента, где корневой элемент имеет уровень 0.
            Каждый переход к родителю увеличивает уровень на 1.

        Описание:
            Метод вычисляет, на какой глубине относительно корня дерева находится указанный элемент.
            Для этого он проходит по родителям индекса, увеличивая счетчик уровня на каждом шаге,
            пока не дойдет до невалидного родителя (то есть до корня дерева).
        """
        level = 0
        while index.parent().isValid():
            level += 1
            index = index.parent()
        return level
