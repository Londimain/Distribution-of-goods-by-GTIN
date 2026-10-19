# -*- coding: utf-8 -*-
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.graphics import Color, Rectangle, Line
# Убедитесь, что это есть в widgets.py:
from kivy.uix.textinput import TextInput
from kivy.base import EventLoop
from kivy.core.clipboard import Clipboard

class RightClickTextInput(TextInput):
    def on_touch_down(self, touch):
        # Если нажата правая кнопка мыши и клик был по этому полю
        if touch.button == 'right' and self.collide_point(*touch.pos):
            self.focus = True
            
            # Перемещаем курсор в ту точку, где был совершен клик
            local_x, local_y = self.to_local(*touch.pos)
            self.cursor = self.get_cursor_from_xy(local_x, local_y)
            
            # Получаем текст из буфера обмена
            paste_text = Clipboard.paste()
            if paste_text:
                # Если в поле стоит фильтр только на цифры (как у GTIN), очищаем текст от букв
                if self.input_filter == 'int':
                    paste_text = ''.join(c for c in paste_text if c in '0123456789')
                
                # Вставляем текст
                if paste_text:
                    self.insert_text(paste_text)
            
            # Возвращаем True, чтобы Kivy не пытался показать стандартное меню
            return True 
            
        return super().on_touch_down(touch)

class FeedbackButton(Button):
    def __init__(self, text, color, **kwargs):
        super().__init__(text=text, background_normal='', background_down='', color=(1, 1, 1, 1), bold=True, **kwargs)
        self.set_color(color)
        self.bind(state=self._update_color)

    def set_color(self, color):
        self._normal_color = color
        self._down_color = (max(0, color[0]*0.7), max(0, color[1]*0.7), max(0, color[2]*0.7), color[3])
        if self.state == 'normal':
            self.background_color = self._normal_color
        else:
            self.background_color = self._down_color

    def _update_color(self, instance, value):
        if value == 'down':
            self.background_color = self._down_color
        else:
            self.background_color = self._normal_color

def styled_button(text, color, **kwargs):
    return FeedbackButton(text=text, color=color, **kwargs)

class CustomTab(TabbedPanelHeader):
    def __init__(self, **kwargs):
        super().__init__(background_normal='', background_down='', **kwargs)
        
        # Отключаем стандартный фон Kivy, чтобы рисовать свой
        self.background_color = (0, 0, 0, 0)
        
        with self.canvas.before:
            self.color_inst = Color(0.25, 0.25, 0.3, 1) # Фон вкладки
            self.rect = Rectangle(pos=self.pos, size=self.size)
            
        with self.canvas.after:
            # Разделительная линия справа
            Color(0.1, 0.1, 0.1, 1)
            self.line = Line(points=[], width=1.5)
            
        self.bind(pos=self.update_graphics, size=self.update_graphics, state=self.on_state_change)
        self.on_state_change(self, self.state)

    def update_graphics(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size
        # Рисуем вертикальную линию по правому краю вкладки
        self.line.points = [self.x + self.width, self.y, self.x + self.width, self.y + self.height]

    def on_state_change(self, instance, value):
        if value == 'down':
            # Активная вкладка (синяя)
            self.color_inst.rgba = (0.15, 0.55, 0.85, 1)
            self.color = (1, 1, 1, 1)
        else:
            # Неактивная вкладка (светло-серая)
            self.color_inst.rgba = (0.25, 0.25, 0.3, 1)
            self.color = (0.7, 0.7, 0.7, 1)

class GridCell(Label):
    def __init__(self, bg_color=(0.22, 0.22, 0.22, 1), align='center', **kwargs):
        super().__init__(halign=align, valign='middle', **kwargs)
        if align == 'left':
            self.padding = [dp(10), 0, dp(10), 0]
            
        self.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
        
        with self.canvas.before:
            Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class FilePathBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = [dp(10), 0, dp(10), 0]
        with self.canvas.before:
            Color(0.4, 0.4, 0.4, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        self.label = Label(
            text="Файл не выбран", 
            halign='left', 
            valign='middle', 
            font_size=dp(14),
            color=(1, 1, 1, 1),
            shorten=True,
            shorten_from='right'
        )
        self.label.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
        self.add_widget(self.label)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_text(self, text):
        self.label.text = text
        
# Добавьте этот класс в конец файла widgets.py
class DropZone(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)
        
        with self.canvas.before:
            self.bg_color = Color(0.18, 0.18, 0.18, 1)  # Темный фон
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.border_color = Color(0.3, 0.5, 0.7, 1) # Голубая рамка
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
            
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
        self.label = Label(
            text="[b]Перетащите файл .txt сюда[/b]\n\nили используйте кнопку «Обзор файла»",
            markup=True,
            halign='center',
            valign='middle',
            color=(0.6, 0.6, 0.6, 1),
            font_size=dp(16)
        )
        self.label.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
        self.add_widget(self.label)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rectangle = (self.x, self.y, self.width, self.height)

    def set_text(self, text, color=(0.6, 0.6, 0.6, 1), markup=True):
        self.label.markup = markup
        self.label.text = text
        self.label.color = color