# -*- coding: utf-8 -*-
import sqlite3
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup

# Добавлен импорт RightClickTextInput
from widgets import GridCell, styled_button, RightClickTextInput
from utils import normalize_gtin, show_msg
import db

class ProductsTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        self.editing_id = None

        # --- Форма добавления/редактирования ---
        form = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        form.add_widget(Label(text="Название:", size_hint_x=None, width=dp(80), halign='right', valign='middle', text_size=(dp(80), None)))
        
        # Заменено на RightClickTextInput
        self.name_input = RightClickTextInput(multiline=False, halign='left', font_size=dp(16), padding=[dp(10), dp(13), dp(10), dp(13)])
        form.add_widget(self.name_input)
        
        form.add_widget(Label(text="Объём:", size_hint_x=None, width=dp(60), halign='right', valign='middle', text_size=(dp(60), None)))
        
        # Заменено на RightClickTextInput
        self.vol_input = RightClickTextInput(multiline=False, halign='left', font_size=dp(16), padding=[dp(10), dp(13), dp(10), dp(13)], size_hint_x=None, width=dp(100))
        form.add_widget(self.vol_input)
        
        form.add_widget(Label(text="GTIN:", size_hint_x=None, width=dp(60), halign='right', valign='middle', text_size=(dp(60), None)))
        
        # Заменено на RightClickTextInput (input_filter='int' оставлен для защиты от букв)
        self.gtin_input = RightClickTextInput(multiline=False, input_filter='int', halign='left', font_size=dp(16), padding=[dp(10), dp(13), dp(10), dp(13)], size_hint_x=None, width=dp(180))
        form.add_widget(self.gtin_input)
        
        self.save_btn = styled_button("Добавить", (0.0, 0.4, 0.7, 1), size_hint_x=None, width=dp(120), font_size=dp(16))
        self.save_btn.bind(on_press=self.on_save)
        form.add_widget(self.save_btn)

        self.cancel_btn = styled_button("Отмена", (0.5, 0.5, 0.5, 1), size_hint_x=None, width=dp(100), font_size=dp(16))
        self.cancel_btn.bind(on_press=self.cancel_edit)
        self.cancel_btn.opacity = 0
        self.cancel_btn.disabled = True
        form.add_widget(self.cancel_btn)

        self.add_widget(form)

        # --- Строка поиска ---
        search_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        search_box.add_widget(Label(text="Поиск:", size_hint_x=None, width=dp(80), halign='right', valign='middle', text_size=(dp(80), None)))
        
        # Заменено на RightClickTextInput
        self.search_input = RightClickTextInput(
            multiline=False, 
            halign='left', 
            font_size=dp(16), 
            padding=[dp(10), dp(10), dp(10), dp(10)],
            hint_text="Введите название или GTIN..."
        )
        self.search_input.bind(text=self.on_search)
        search_box.add_widget(self.search_input)
        self.add_widget(search_box)

        # --- Заголовок таблицы ---
        header = BoxLayout(size_hint_y=None, height=dp(40), spacing=1)
        header.add_widget(GridCell(text="№", bg_color=(0.15, 0.15, 0.15, 1), size_hint_x=None, width=dp(50)))
        header.add_widget(GridCell(text="Название товара", bg_color=(0.15, 0.15, 0.15, 1)))
        header.add_widget(GridCell(text="Объём (л)", bg_color=(0.15, 0.15, 0.15, 1), size_hint_x=None, width=dp(80)))
        header.add_widget(GridCell(text="GTIN", bg_color=(0.15, 0.15, 0.15, 1), size_hint_x=None, width=dp(160)))
        header.add_widget(GridCell(text="Действия", bg_color=(0.15, 0.15, 0.15, 1), size_hint_x=None, width=dp(200)))
        self.add_widget(header)

        # --- Список товаров (Таблица) ---
        self.scroll_view = ScrollView()
        self.list_layout = GridLayout(cols=1, size_hint_y=None, spacing=1)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll_view.add_widget(self.list_layout)
        self.add_widget(self.scroll_view)

        self.refresh()

    def on_search(self, instance, value):
        """Вызывается при вводе текста в поисковую строку."""
        self.refresh()

    def refresh(self):
        """Обновляет таблицу с учетом поискового запроса и сквозной нумерацией."""
        self.list_layout.clear_widgets()
        
        search_query = self.search_input.text.strip().lower()
        all_products = db.get_products()
        
        # 1. Сначала фильтруем список товаров
        filtered_products = []
        for pid, name, vol, gtin in all_products:
            if search_query:
                # Ищем только по названию и GTIN (поиск по ID убран, т.к. номер теперь сквозной)
                if (search_query not in name.lower() and 
                    search_query not in gtin.lower()):
                    continue
            filtered_products.append((pid, name, vol, gtin))

        # 2. Выводим отфильтрованный список со сквозной нумерацией
        for display_index, (pid, name, vol, gtin) in enumerate(filtered_products, start=1):
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=1)
            
            # Отображаем сквозной порядковый номер (1, 2, 3...)
            row.add_widget(GridCell(text=str(display_index), size_hint_x=None, width=dp(50)))
            row.add_widget(GridCell(text=name, align='left'))
            row.add_widget(GridCell(text=vol, size_hint_x=None, width=dp(80)))
            row.add_widget(GridCell(text=gtin, size_hint_x=None, width=dp(160)))
            
            btn_box = BoxLayout(spacing=1, size_hint_x=None, width=dp(200))
            eb = styled_button("Изменить", (0.2, 0.5, 0.9, 1))
            # Для действий передаем скрытый настоящий pid
            eb.bind(on_press=lambda b, p=(pid, name, vol, gtin): self.start_edit(*p))
            db_btn = styled_button("Удалить", (0.9, 0.3, 0.3, 1))
            # Для удаления передаем скрытый настоящий pid
            db_btn.bind(on_press=lambda b, p=pid: self.do_delete(p))
            btn_box.add_widget(eb)
            btn_box.add_widget(db_btn)
            
            row.add_widget(btn_box)
            self.list_layout.add_widget(row)
            
        # Принудительно прокручиваем список в самый верх
        self.scroll_view.scroll_y = 1.0

    def start_edit(self, pid, name, vol, gtin):
        self.editing_id = pid
        self.name_input.text = name
        self.vol_input.text = vol
        self.gtin_input.text = gtin
        self.save_btn.text = "Сохранить"
        self.save_btn.set_color((0.9, 0.5, 0.1, 1))
        
        self.cancel_btn.opacity = 1
        self.cancel_btn.disabled = False

    def cancel_edit(self, *args):
        self.editing_id = None
        self.name_input.text = ''
        self.vol_input.text = ''
        self.gtin_input.text = ''
        self.save_btn.text = "Добавить"
        self.save_btn.set_color((0.0, 0.4, 0.7, 1))
        
        self.cancel_btn.opacity = 0
        self.cancel_btn.disabled = True

    def on_save(self, *args):
        name = self.name_input.text.strip()
        vol = self.vol_input.text.strip()
        gtin = normalize_gtin(self.gtin_input.text)
        
        if not name:
            show_msg("Введите название товара")
            return
        if not gtin or not gtin.isdigit():
            show_msg("GTIN должен состоять из цифр")
            return
        try:
            if self.editing_id:
                db.update_product(self.editing_id, name, vol, gtin)
                self.cancel_edit()
            else:
                db.add_product(name, vol, gtin)
        except sqlite3.IntegrityError:
            show_msg("Товар с таким GTIN уже существует")
            return
        
        if not self.editing_id:
            self.name_input.text = ''
            self.vol_input.text = ''
            self.gtin_input.text = ''
        self.refresh()

    def do_delete(self, pid):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        lbl = Label(text="Вы действительно хотите удалить\nэтот товар?", halign='center', valign='middle')
        lbl.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
        content.add_widget(lbl)
        
        btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        no_btn = styled_button("Отмена", (0.5, 0.5, 0.5, 1))
        yes_btn = styled_button("Удалить", (0.9, 0.2, 0.2, 1))
        btns.add_widget(no_btn)
        btns.add_widget(yes_btn)
        content.add_widget(btns)
        
        popup = Popup(title="Подтверждение", content=content, size_hint=(None, None), size=(350, 180), auto_dismiss=False)
        no_btn.bind(on_release=popup.dismiss)
        
        def confirm(*args):
            db.delete_product(pid)
            self.refresh()
            popup.dismiss()
            
        yes_btn.bind(on_release=confirm)
        popup.open()