# widgets.py (или custom_widgets.py)
from kivy.uix.textinput import TextInput
from kivy.base import EventLoop

class RightClickTextInput(TextInput):
    def on_touch_down(self, touch):
        # Сначала даем стандартной логике TextInput обработать касание
        super().on_touch_down(touch)
        
        # Если нажата правая кнопка мыши
        if touch.button == 'right':
            # Вызываем встроенное меню вставки
            pos = super().to_local(*self._long_touch_pos, relative=True)
            self._show_cut_copy_paste(pos, EventLoop.window, mode='paste')
            return True  # Событие обработано
        return super().on_touch_down(touch)