# -*- coding: utf-8 -*-
import os
import re
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from widgets import GridCell, styled_button, FilePathBox
from utils import sanitize_filename, read_lines
from kivy.core.clipboard import Clipboard
import db

class SplitterTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=[dp(10), dp(40), dp(10), dp(10)], spacing=dp(15), **kwargs)
        self.file_path = None
        self._reset_event = None # Таймер для возврата текста пути

        top_container = BoxLayout(size_hint_y=None, height=dp(45))
        top_box = BoxLayout(size_hint_x=None, width=dp(650), pos_hint={'center_x': 0.5}, spacing=dp(10))
        
        btn_choose = styled_button("Обзор файла", (0.2, 0.6, 0.8, 1), size_hint_x=None, width=dp(120), font_size=dp(14))
        btn_choose.bind(on_press=self.choose_file)
        top_box.add_widget(btn_choose)

        self.file_input = FilePathBox()
        top_box.add_widget(self.file_input)

        split_btn = styled_button("Разделить", (0.85, 0.3, 0.4, 1), size_hint_x=None, width=dp(110), font_size=dp(14))
        split_btn.bind(on_press=self.do_split)
        top_box.add_widget(split_btn)

        top_container.add_widget(top_box)
        self.add_widget(top_container)

        self.summary_label = Label(
            text="Выберите файл и нажмите «Разделить».",
            size_hint_y=None, height=dp(30),
            halign='center', valign='middle',
            font_size=dp(16)
        )
        self.summary_label.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
        self.add_widget(self.summary_label)

        self.results_header = BoxLayout(size_hint_y=None, height=dp(35), spacing=1)
        self.results_header.add_widget(GridCell(text="Название товара", bg_color=(0.15, 0.15, 0.15, 1), align='left'))
        self.results_header.add_widget(GridCell(text="Объём", bg_color=(0.15, 0.15, 0.15, 1), size_hint_x=None, width=dp(100)))
        self.results_header.add_widget(GridCell(text="Кол-во", bg_color=(0.15, 0.15, 0.15, 1), size_hint_x=None, width=dp(100)))
        self.results_header.opacity = 0
        self.add_widget(self.results_header)

        scroll = ScrollView()
        self.results_layout = GridLayout(cols=1, size_hint_y=None, spacing=1)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        scroll.add_widget(self.results_layout)
        self.add_widget(scroll)

    def show_feedback(self, text, is_error=False):
        """Показывает сообщение по центру поля с путем к файлу и скрывает его через 3 секунды."""
        if self._reset_event:
            self._reset_event.cancel()

        self.file_input.label.halign = 'center'
        self.file_input.label.text = text
        self.file_input.label.color = (1, 0.3, 0.3, 1) if is_error else (0.3, 1, 0.3, 1)

        def reset_text(dt):
            self.file_input.label.halign = 'left'
            if self.file_path:
                self.file_input.label.text = self.file_path
            else:
                self.file_input.label.text = "Файл не выбран"
            self.file_input.label.color = (1, 1, 1, 1)

        self._reset_event = Clock.schedule_once(reset_text, 3.0)

    def choose_file(self, *args):
        content = BoxLayout(orientation='vertical')
        fc = FileChooserListView(filters=['*.txt'])
        content.add_widget(fc)
        btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        cancel = styled_button("Отмена", (0.5, 0.5, 0.5, 1)) 
        ok = styled_button("Выбрать", (0.2, 0.7, 0.3, 1))
        
        btns.add_widget(cancel)
        btns.add_widget(ok)
        content.add_widget(btns)
        popup = Popup(title="Выберите .txt файл", content=content, size_hint=(0.9, 0.9), auto_dismiss=False)
        cancel.bind(on_press=popup.dismiss)

        def select(*a):
            if fc.selection:
                self.file_path = fc.selection[0]
                if self._reset_event:
                    self._reset_event.cancel()
                self.file_input.label.halign = 'left'
                self.file_input.label.color = (1, 1, 1, 1)
                self.file_input.set_text(self.file_path)
                popup.dismiss()

        ok.bind(on_press=select)
        popup.open()

    def _show_missing_popup(self, missing_gtins):
        """Показывает прокручиваемое окно со списком GTIN, отсутствующих в базе."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        title_lbl = Label(
            text="В файле обнаружены товары, которых нет в базе:",
            size_hint_y=None, height=dp(35),
            halign='center', valign='middle', font_size=dp(15)
        )
        title_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
        content.add_widget(title_lbl)
        
        # Подсказка для пользователя
        hint_lbl = Label(
            text="(Нажмите на GTIN, чтобы скопировать)",
            size_hint_y=None, height=dp(20),
            halign='center', valign='middle', font_size=dp(12),
            color=(0.7, 0.7, 0.7, 1)
        )
        hint_lbl.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
        content.add_widget(hint_lbl)
        
        scroll = ScrollView()
        list_layout = GridLayout(cols=1, size_hint_y=None, spacing=1)
        list_layout.bind(minimum_height=list_layout.setter('height'))
        
        for gtin in sorted(missing_gtins):
            cell = GridCell(text=gtin, size_hint_y=None, height=dp(30))
            
            # Функция обработки клика
            def copy_to_clipboard(instance, touch):
                if instance.collide_point(*touch.pos):
                    Clipboard.copy(instance.text)  # Копируем GTIN в буфер
                    
                    original_text = instance.text
                    original_color = instance.color
                    
                    # Меняем текст только на "Скопировано" и делаем его зеленым
                    instance.text = "Скопировано"
                    instance.color = (0.3, 1.0, 0.3, 1)
                    
                    # Через 1 секунду возвращаем исходный GTIN и белый цвет
                    def reset_cell(dt):
                        instance.text = original_text
                        instance.color = original_color
                        
                    Clock.schedule_once(reset_cell, 1.0)
                    return True
                return False
                
            cell.bind(on_touch_down=copy_to_clipboard)
            list_layout.add_widget(cell)
            
        scroll.add_widget(list_layout)
        content.add_widget(scroll)
        
        note = Label(
            text="Добавьте эти товары на вкладке «Товары» и повторите попытку.",
            size_hint_y=None, height=dp(35),
            halign='center', valign='middle', font_size=dp(13)
        )
        note.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
        content.add_widget(note)
        
        ok_btn = styled_button("Понятно", (0.2, 0.5, 0.8, 1), size_hint_y=None, height=dp(45))
        content.add_widget(ok_btn)
        
        popup = Popup(
            title="Недостающие товары",
            content=content,
            size_hint=(None, None),
            size=(700, 500),
            auto_dismiss=False
        )
        ok_btn.bind(on_release=popup.dismiss)
        popup.open()

    def do_split(self, *args):
        if not self.file_path or not os.path.exists(self.file_path):
            self.show_feedback("Ошибка: выберите файл!", is_error=True)
            return
        products = db.get_products()
        if not products:
            self.show_feedback("Ошибка: база товаров пуста!", is_error=True)
            return
        lines = read_lines(self.file_path)
        if not lines:
            self.show_feedback("Ошибка: файл пуст!", is_error=True)
            return

        # --- ПРОВЕРКА: есть ли в файле товары, которых нет в базе ---
        db_gtins = {gtin for _pid, _name, _vol, gtin in products if gtin}
        pattern = re.compile(r'01(\d{14})')
        found_gtins = set()
        for line in lines:
            found_gtins.update(pattern.findall(line))

        missing = found_gtins - db_gtins
        if missing:
            self._show_missing_popup(missing)
            self.results_layout.clear_widgets()
            self.results_header.opacity = 0
            self.summary_label.text = "Обнаружены товары, отсутствующие в базе. Файл не был разделён."
            
            # Убрали {len(missing)} из этого сообщения
            self.show_feedback(
                "Ошибка: найдены товары, отсутствующие в базе",
                is_error=True
            )
            return
        # ------------------------------------------------------------

        matched = {}
        for line in lines:
            for _pid, _name, _vol, gtin in products:
                if gtin and ('01' + gtin) in line:
                    matched.setdefault(gtin, []).append(line)
                    break

        if not matched:
            self.results_layout.clear_widgets()
            self.results_header.opacity = 0
            self.summary_label.text = "Ни одного товара из базы не найдено."
            self.show_feedback("Ошибка: коды не найдены!", is_error=True)
            return

        # --- СОЗДАНИЕ ПАПКИ ДЛЯ РЕЗУЛЬТАТОВ ---
        base_dir = os.path.dirname(self.file_path) or "."
        file_name_without_ext = os.path.splitext(os.path.basename(self.file_path))[0]
        out_dir = os.path.join(base_dir, file_name_without_ext)
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        # --------------------------------------

        info_by_gtin = {g: (n, v) for _pid, n, v, g in products}

        self.results_layout.clear_widgets()
        total_codes = 0
        saved = 0

        for gtin, codes in matched.items():
            name, vol = info_by_gtin.get(gtin, (gtin, ""))
            
            if vol:
                vol_str = vol.strip()
                if not vol_str.endswith('л.') and not vol_str.endswith('l.'):
                    vol_str += 'л.'
                display_name = f"{name} - {vol_str}"
            else:
                vol_str = ""
                display_name = name
                
            safe = sanitize_filename(display_name) or gtin
            
            fname = f"{safe} ({len(codes)}) - {gtin}.txt"
            
            path = os.path.join(out_dir, fname)
            
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write('\n'.join(codes))
            saved += 1
            total_codes += len(codes)
            
            row = BoxLayout(size_hint_y=None, height=dp(35), spacing=1)
            row.add_widget(GridCell(text=name, align='left'))
            row.add_widget(GridCell(text=vol_str, size_hint_x=None, width=dp(100)))
            row.add_widget(GridCell(text=str(len(codes)), size_hint_x=None, width=dp(100)))
            self.results_layout.add_widget(row)

        self.results_header.opacity = 1 
        self.summary_label.text = (
            f"Найдено товаров: {saved}. Всего кодов: {total_codes}.\n"
            f"Сохранено в папку: {out_dir}"
        )
        
        self.show_feedback(f"Успешно! Файлов создано: {saved}", is_error=False)