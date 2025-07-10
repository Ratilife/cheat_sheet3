from PySide6.QtCore import QObject, Signal

class ButtonViewModel(QObject):
    def __init__(self, model):
        super().__init__()
        self._model = model  # Ссылка на Model

    # Сигнал для уведомления View об изменении данных
    buttonsChanged = Signal()

    def add_button(self, name: str, path: str):
        # Добавление новой кнопки через Model
        self._model.add_button(name, path)
        self.buttonsChanged.emit()  # Уведомление View об изменении

    def get_buttons(self):
        # Получение списка кнопок через Model
        return self._model.get_buttons()

    def execute_program(self, index: int):
        # Запуск программы через Model
        button = self._model.get_button(index)
        if button:
            import os
            os.startfile(button.path)  # Запуск программы

    def remove_button(self, index: int):
        self._model.remove_button(index)
        self.buttonsChanged.emit()        

    def edit_button(self, index: int, name: str, path: str):
        if self._model.is_valid_button(name, path):
            self._model.edit_button(index, name, path)
            self.buttonsChanged.emit()    

    def sort_buttons(self):
        self._model.sort_buttons()
        self.buttonsChanged.emit()        

    def is_valid_button(self, name: str, path: str) -> bool:
        return self._model.is_valid_button(name, path)    
    
    def save_buttons(self):
        """
        Сохраняет кнопки через Model.
        """
        self._model.save_buttons()

    def remove_button_list(self, list):
        self._model.remove_button_list(list)