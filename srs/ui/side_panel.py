import sys
import os
from PySide6.QtWidgets import (QTreeView, QWidget,
                               QVBoxLayout, QApplication, QMenu,
                               QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject, QRect, QSize
from PySide6.QtGui import QAction
from srs.observers.file_watcher import FileWatcher
from srs.observers.my_base_observer import MyBaseObserver
from srs.managers.tree_model_manager import TreeModelManager
from srs.operation.file_operations import FileOperations
from srs.widgets.markdown_viewer_widget import MarkdownViewer
from srs.ui.file_editor import FileEditorWindow
from srs.widgets.delegates import TreeItemDelegate
from srs.managers.ui_manager import UIManager
from srs.utils.tree_manager import TreeManager
from srs.managers.toolbar_manager import ToolbarManager
from srs.managers.context_menu_manager import ContextMenuHandler

# Основной класс боковой панели

# Класс для обработки сигналов панели
class SidePanelObserver(MyBaseObserver):
    # ✅ Реализовано: 29.06.2025
    def __init__(self):
        super().__init__()
class SidePanel(QWidget):

    def __init__(self, parent=None):
        # TODO 🚧 В разработке: 30.06.2025
        # - Всегда поверх других окон (WindowStaysOnTopHint)
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 1. Создаем экземпляр класса для сигналов
        self.observer = SidePanelObserver()
        # 2.  Инициализация модели и менеджеров
        # TODO класс TreeModelManager() будет переписан и обращение к нему
        self.tree_model_manager = TreeModelManager()  # Подключаем менеджер
        # TODO проконтролровать, как спользуется
        self.tree_model_manager.delete_manager.removal_complete.connect(self._handle_removal_result)



        # 3. # Инициализация наблюдателя
        self.file_watcher = FileWatcher()
        self.file_watcher.file_updated.connect(self._on_file_updated)
        self.file_watcher.file_deleted.connect(self._on_file_deleted)

        self.file_operations = FileOperations(self.tree_model_manager,self.file_watcher)

        # нижняя панель (отображение данных)
        self.content_viewer = MarkdownViewer()

        # 4. Инициализация пользовательского интерфейса
        self._init_ui()

        # Подключение сигнала
        # TODO проконтролровать, как спользуется
        self.toolbar_manager.editor_toggled.connect(self._open_editor)

        # Инициализация контекстного меню для управления позицией
        self._init_position_menu()
        # Настройка прикрепления к краям экрана
        self._setup_screen_edge_docking()

        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.show()


    # 1. Инициализация и базовый UI
    def _init_ui(self):
        # Создаем дерево для отображения файловой системы
        self.tree_view = QTreeView()
        # Показываем заголовки у дерева
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setIndentation(10)  # Увеличьте это значение
        self.tree_view.setAnimated(True)  # Анимация раскрытия
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setRootIsDecorated(True)  # Показываем декор для корневых элементов
        self.tree_view.setExpandsOnDoubleClick(True)  # Включаем разворачивание по двойному клику
        self.tree_view.setSortingEnabled(False)

        self.ui = UIManager()
        self.tree_manager = TreeManager(self.tree_view)
        self.toolbar_manager = ToolbarManager(self.tree_manager, self.close, self.showMinimized)
        self.toolbar_manager.set_tree_model(self.tree_model_manager)

        self.context_menu_handler = ContextMenuHandler(
           tree_view=self.tree_view,
            delete_manager=self.tree_model_manager.delete_manager
        )
        # Подключение контекстного меню к tree_view
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(
            self.context_menu_handler.show_tree_context_menu
        )

        # Устанавливаем минимальную ширину панели
        self.setMinimumWidth(300)

        # Создаем основной вертикальный layout
        main_layout = QVBoxLayout(self)
        # Убираем отступы у layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем панель заголовка с кнопками управления
        title_layout = self.toolbar_manager.get_title_layout()
        main_layout.addWidget(title_layout)  # Добавляем панель инструментов в основной layout(макет)

        # Создаем разделитель с вертикальной ориентацией
        self.splitter = self.ui.create_splitter(Qt.Vertical,
                                                sizes=[300, 100],
                                                handle_width=5,
                                                handle_style="QSplitter::handle { background: #ccc; }")

        # Устанавливаем делегат с правильной ссылкой на tree_view
        self.delegate = TreeItemDelegate(self.tree_view)
        self.tree_view.setItemDelegate(self.delegate)

        # Подключаем обработчик двойного клика
        self.tree_view.doubleClicked.connect(self._on_tree_item_double_clicked) #TODO ?
        self.tree_manager.setup_double_click_handler(self)

        # Настройка стиля дерева
        self.tree_view.setStyleSheet("""
                            QTreeView {
                                background-color: white;
                                border: 1px solid #ddd;
                            }
                            QTreeView::item {
                                padding: 2px;
                                margin: 0px;
                                height: 20px;
                            }
                            /* Убираем стандартные треугольники */
                            QTreeView::branch {
                                background: transparent;
                                border: 0px;
                            }
                            QTreeView::branch:has-siblings:!adjoins-item {
                                border-image: none;
                                image: none;
                            }
                            QTreeView::branch:has-siblings:adjoins-item {
                                border-image: none;
                                image: none;
                            }
                            QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                                border-image: none;
                                image: none;
                            }
                            QTreeView::branch:has-children:!has-siblings:closed,
                            QTreeView::branch:closed:has-children:has-siblings {
                                border-image: none;
                                image: none;
                            }
                            QTreeView::branch:open:has-children:!has-siblings,
                            QTreeView::branch:open:has-children:has-siblings {
                                border-image: none;
                                image: none;
                            }
                        """)

        # Добавляем само дерево файлов
        main_layout.addWidget(self.tree_view)
        # Текстовое поле (нижняя часть)
        self.splitter.addWidget(self.content_viewer)
        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

    # 2. Позиционирование/размеры
    # Метод настройки прикрепления к краям экрана
    def _setup_screen_edge_docking(self):
        """Настройка прикрепления к краям экрана"""
        # ✅ Реализовано: 30.06.2025
        # Позиция по умолчанию - справа
        self.dock_position = "right"  # left/right/float
        # Отступ от края экрана
        self.dock_margin = 5

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)  # <- ОТКЛЮЧАЕМ поверх всех окон
        # Обновляем позицию
        self.update_dock_position()
        # Устанавливаем прозрачность окна
        self.setWindowOpacity(0.9)

    def _handle_removal_result(self, success, message):
        """Обрабатывает результат операции удаления, показывая пользователю уведомление и сохраняя изменения при успехе.

    Этот метод вызывается после попытки удаления элемента в приложении. В зависимости от результата операции
    он либо сохраняет изменения и показывает сообщение об успехе, либо выводит предупреждение об ошибке.

    Args:
        success (bool): Флаг успешности операции удаления:
            - True: удаление прошло успешно
            - False: возникла ошибка при удалении
        message (str): Текст сообщения, который будет показан пользователю.
                       В случае успеха обычно содержит информацию об удаленном элементе,
                       в случае ошибки - описание проблемы.

    Returns:
        None

    Side Effects:
        - При успешном удалении (success=True):
            * Сохраняет текущее состояние файлов через file_manager.save_files_to_json()
            * Показывает информационное QMessageBox с переданным сообщением
        - При ошибке удаления (success=False):
            * Показывает предупреждающее QMessageBox с сообщением об ошибке

    Examples:
        >>> self._handle_removal_result(True, "Файл успешно удален")
        # Покажет информационное окно и сохранит изменения

        >>> self._handle_removal_result(False, "Не удалось удалить файл")
        # Покажет предупреждающее окно
    """
        # ✅ Реализовано: 02.07.2025
        if success:
            self.file_operations.file_manager.save_files_to_json()
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Ошибка", message)

    def _on_file_updated(self, path):
        """Обрабатывает событие обновления файла, обновляя интерфейс при изменении текущего файла.

        Данный метод вызывается при обнаружении изменений в файловой системе. Если измененный файл
        является текущим открытым файлом (self.current_file), метод:
            1. Отправляет сигнал об изменении файла через observer.file_changed
            2. Пытается перечитать содержимое файла и обновить его в интерфейсе (content_viewer)
            3. В случае ошибок чтения файла отображает сообщение об ошибке
        Args:
            path (str): Абсолютный путь к файлу, который был изменен.
        Returns:
        None
        Side Effects:
            - При совпадении path с current_file:
                * Отправляет сигнал file_changed с путем к файлу
                * Обновляет содержимое в content_viewer:
                    - При успешном чтении: устанавливает новое содержимое файла
                    - При ошибке: устанавливает текст с сообщением об ошибке
            - При несовпадении path с current_file: не выполняет никаких действий

        Raises:
            IOError: Если возникли проблемы с доступом к файлу (перехватывается внутри метода)
            UnicodeDecodeError: Если возникли проблемы с декодированием файла (перехватывается внутри метода)

        Example:
            >>> self._on_file_updated("/path/to/current_file.txt")
            # Если это текущий файл:
            # 1. Будет отправлен сигнал file_changed
            # 2. Содержимое файла будет обновлено в content_viewer
        """
        # TODO 🚧 В разработке: 30.06.2025 (нужно правльно определить переменную self.current_file)
        if path == self.current_file:
            self.observer.file_changed.emit(path)  # Уведомляем о изменении
            # Можно также обновить содержимое просмотра:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    #TODO определить переменную self.content_viewer
                    self.content_viewer.set_content(content)
            except Exception as e:
                self.content_viewer.set_content(f"Ошибка загрузки файла: {str(e)}")

    def _on_file_deleted(self, path):
        """Обрабатывает событие изменения файла, синхронизируя состояние интерфейса с актуальным содержимым.

        Метод выполняет следующие действия при обнаружении изменений в отслеживаемом файле:
            1. Проверяет, относится ли изменение к текущему активному файлу
            2. При совпадении:
                - Отправляет сигнал file_changed через observer для уведомления подписчиков
                - Перечитывает содержимое файла и обновляет отображение в content_viewer
            3. Обрабатывает возможные ошибки ввода-вывода, выводя сообщение в интерфейс

        Логика работы:
            - Изменения игнорируются, если path не соответствует current_file
            - Чтение файла выполняется с явным указанием кодировки UTF-8
            - Все исключения при работе с файлом перехватываются и отображаются пользователю

        Args:
            path (str): Абсолютный путь к измененному файлу в файловой системе.
                    Должен соответствовать формату пути текущей ОС.

        Returns:
            None: Метод не возвращает значений, все изменения происходят через side effects

        Signals:
            Испускает file_changed через observer при обнаружении изменений текущего файла

        UI Effects:
            - Обновляет содержимое content_viewer при успешном чтении
            - Показывает сообщение об ошибке при проблемах с чтением файла

        Error Handling:
            Перехватывает и обрабатывает все исключения при работе с файлом:
            - IOError (отсутствие прав, файл удален)
            - UnicodeDecodeError (проблемы с кодировкой)
            - Другие исключения файловых операций

        Implementation Notes:
            - Использует менеджер контекста для гарантированного закрытия файла
            - Сообщения об ошибках включают оригинальный текст исключения
            - Не блокирует UI при длительных операциях (чтение выполняется синхронно)

        Example:
            При изменении файла '/projects/current.txt':
            >>> self._on_file_updated('/projects/current.txt')
            Если файл является current_file:
                - Сигнал file_changed emitted
                - content_viewer обновит содержимое
            При ошибке доступа:
            - content_viewer покажет "Ошибка загрузки файла: [текст ошибки]"
    """
        if path == self.current_file:
            self.content_viewer.set_content(f"Файл удалён: {path}")
            # TODO 🚧 В разработке: 30.06.2025 (Дополнительные действия, например, убрать файл из tree_view)

    def _open_editor(self):
        """Открыть окно редактора файла"""
        #  TODO 🚧 В разработке: 30.06.2025 (определить метод для сигнала self.editor_window.observer.file_created.connect())
        if not hasattr(self, 'editor_window'):
            # TODO определить переменную self.toolbar_manager
            self.editor_window = FileEditorWindow(self.tree_model_manager, self.toolbar_manager)
            # Подключаем сигналы редактора к панели
            self.editor_window.observer.file_created.connect(self._on_file_created)
        self.editor_window.show()

    def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева с корректной работой FileWatcher"""
        # ✅ Реализовано: 30.06.2025
        item = index.internalPointer()
        if not item:
            return

        # Очищаем предыдущее содержимое
        self.content_viewer.set_content("")

        # Обработка разных типов элементов
        item_type = item.item_data[1]
        item_content = item.item_data[2]

        if item_type == 'template':
            self.content_viewer.set_content(item_content)
            self.content_viewer.set_view_mode("text")

        elif item_type in ['file', 'markdown']:
            file_path = item_content
            self.current_file = file_path
            self.observer.file_selected.emit(file_path)

            # Обновляем FileWatcher
            self._update_file_watcher(file_path)

            # Загружаем содержимое файла
            self._update_file_content(file_path, item_type)

    def _update_file_watcher(self, file_path):
        """Обновляет отслеживаемые файлы в FileWatcher"""
        # ✅ Реализовано: 30.06.2025
        # Удаляем все текущие пути (если есть)
        self.file_watcher.clear_watched_files()  # Очищаем наблюдаемые файлы
        self.file_watcher.watch_file(file_path)  # Добавляем новый файл

    def _update_file_content(self, file_path, file_type):
        """Загружает и отображает содержимое файла с учетом его типа"""
        # ✅ Реализовано: 30.06.2025
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.content_viewer.set_content(content)
                    # Устанавливаем режим просмотра в зависимости от типа файла
                    self.content_viewer.set_view_mode("text" if file_type == 'file' else "markdown")
            else:
                self.content_viewer.set_content(f"Файл не найден: {file_path}")
        except Exception as e:
            self.content_viewer.set_content(f"Ошибка загрузки файла: {str(e)}")

    # Метод инициализации контекстного меню
    def _init_position_menu(self):
        # ✅ Реализовано: 30.06.2025
        # Создаем меню с заголовком
        self.position_menu = QMenu("Позиция панели", self)

        # Создаем действие "Закрепить слева"
        self.pin_left_action = QAction("Закрепить слева", self, checkable=True)
        # Подключаем обработчик
        self.pin_left_action.triggered.connect(self._dock_to_left)

        # Создаем действие "Закрепить справа"
        self.pin_right_action = QAction("Закрепить справа", self, checkable=True)
        # Подключаем обработчик
        self.pin_right_action.triggered.connect(self._dock_to_right)

        # Создаем действие "Свободное перемещение"
        self.float_action = QAction("Свободное перемещение", self, checkable=True)
        # Подключаем обработчик
        self.float_action.triggered.connect(self._enable_floating)

        # Добавляем действия в меню
        self.position_menu.addActions([self.pin_left_action, self.pin_right_action, self.float_action])
        # Устанавливаем политику контекстного меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # Подключаем обработчик показа контекстного меню
        #self.customContextMenuRequested.connect(self.show_context_menu)

    # Метод для закрепления панели слева
    def _dock_to_left(self):
        # ✅ Реализовано: 30.06.2025
        self.dock_position = "left"
        self.update_dock_position()
        self._update_menu_checks()

    # Метод для закрепления панели справа
    def _dock_to_right(self):
        # ✅ Реализовано: 30.06.2025
        self.dock_position = "right"
        self.update_dock_position()
        self._update_menu_checks()

    # Метод для включения свободного перемещения
    def _enable_floating(self):
        # ✅ Реализовано: 30.06.2025
        self.dock_position = "float"
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # <- ВКЛЮЧАЕМ поверх окон
        self.show()
        # self.update_dock_position()  # Обновляем геометрию
        # Устанавливаем начальные размеры и позицию
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(QRect(
            screen.right() - 350,  # X координата (немного левее правого края)
            screen.top() + 100,  # Y координата (немного ниже верхнего края)
            300,  # Ширина
            screen.height() - 200  # Высота (меньше высоты экрана)
        ))
        self._update_menu_checks()

        # Метод обновления позиции панели
    def update_dock_position(self):
        """Обновление позиции относительно края экрана"""
        # ✅ Реализовано: 30.06.2025
        # Получаем геометрию экрана
        screen = QApplication.primaryScreen().availableGeometry()
        # Если панель должна быть слева
        if self.dock_position == "left":
            self.setGeometry(QRect(
                screen.left() + self.dock_margin,  # X координата
                screen.top(),  # Y координата
                300,  # Ширина
                screen.height()  # Высота
                ))
            self.setFixedWidth(300)  # Фиксируем ширину в закрепленном режиме
            self.setFixedHeight(screen.height())  # Фиксируем высоту
            # Если панель должна быть справа
        elif self.dock_position == "right":
            self.setGeometry(QRect(
                screen.right() - 300 - self.dock_margin,  # X координата
                screen.top(),  # Y координата
                300,  # Ширина
                screen.height()  # Высота
                ))
            self.setFixedWidth(300)  # Фиксируем ширину в закрепленном режиме
            self.setFixedHeight(screen.height())  # Фиксируем высоту
            # Для режима float не устанавливаем фиксированные размеры
        elif self.dock_position == "float":
            self.setMinimumSize(200, 200)
            self.setMaximumSize(16777215, 16777215)
            self.setFixedSize(QSize())  # Снимаем фиксированные размеры

    # Метод обновления состояния пунктов меню
    def _update_menu_checks(self):
        # ✅ Реализовано: 30.06.2025
        self.pin_left_action.setChecked(self.dock_position == "left")
        self.pin_right_action.setChecked(self.dock_position == "right")
        self.float_action.setChecked(self.dock_position == "float")




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