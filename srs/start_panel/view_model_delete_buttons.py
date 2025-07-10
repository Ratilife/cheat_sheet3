from typing import Dict, List
from PySide6.QtCore import QObject, Signal
from model_delete_buttons import DeleteButtonsModel

class DeleteButtonsViewModel(QObject):
    def __init__(self, model):
        super().__init__()
        self._model = model  # Ссылка на ButtonListModel (model)
        self._delete_model = DeleteButtonsModel(model)  # Создаем DeleteButtonsModel (model_delete_buttons)
    # Сигнал для уведомления View об изменении данных
    buttonsUpdated = Signal()

    def get_buttons(self) -> List[Dict[str, str]]:
        """
        Возвращает список кнопок.
        """
        return [{"name": button.name, "path": button.path} for button in self._model.get_buttons()]


    def set_selected(self, name: str, selected: bool):
        """
        Устанавливает отметку для кнопки.
        """
        self._delete_model.set_selected(name, selected)
        self.buttonsUpdated.emit()

    def get_selected_buttons(self) -> List[str]:
        """
        Возвращает список имен кнопок, которые были отмечены для удаления.
        """
        return self._delete_model.get_selected_buttons()
    
    def get_selected_buttons_index(self) -> List[str]:
        # возможно удалить
        return self._delete_model.get_selected_buttons_index()

    #описать метод на удаление 
    def remove_button_list(self,list):
        return self._model.remove_button_list(list)