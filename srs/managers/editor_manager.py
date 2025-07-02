class EditorManager:

    def __init__(self):
        pass
    def _clear_viewer(self):
        """Очищает все просмотрщики содержимого"""
        if hasattr(self, 'markdown_viewer'):
            self.markdown_viewer.set_content("")

        if hasattr(self, 'st_content_viewer'):  # Если у вас есть отдельный виджет для ST
            self.st_content_viewer.clear()

        # Или если используется единый виджет:
        if hasattr(self, 'content_view'):
            self.content_view.clear()

    def _change_view_mode(self):
        """Переключение между режимами просмотра ST файла"""
        pass

    def _reset_editors(self):
        """Сбрасывает состояние всех редакторов
         Основное назначение метода - приведение всех редакторов в исходное состояние
         Используется при:
         1. Инициализации окна
         2. Очистке перед загрузкой нового файла
         3. Обработке ошибок
         4. Удалении файла
        """
        pass