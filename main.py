# -*- coding: utf-8 -*-
import os
import sys
import ctypes
from ctypes import wintypes

# --- Отключаем масштабирование Windows ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.tabbedpanel import TabbedPanel

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from widgets import CustomTab, styled_button
from tab_products import ProductsTab
from tab_splitter import SplitterTab
from tab_about import AboutTab
import db

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SplitterApp(App):
    title = "Распределение кодов по товарам v1.2.0"

    def build(self):
        # Запуск во весь экран
        Window.maximize()
        
        try:
            Window.set_icon(resource_path(os.path.join('ico', 'distribution.ico')))
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")

        db.init_db()
        self.last_db_mtime = db.get_db_mtime()
        
        root = FloatLayout()
        
        tp = TabbedPanel(do_default_tab=False, tab_width=dp(180), tab_height=dp(45), padding=[0, 0, 0, 0])
        tp.size_hint = (1, 0.998) 
        
        t1 = CustomTab(text="Товары", font_size=dp(16), bold=True)
        self.products_tab = ProductsTab()
        t1.content = self.products_tab
        
        t2 = CustomTab(text="Разделить файл", font_size=dp(16), bold=True)
        t2.content = SplitterTab()

        t3 = CustomTab(text="О программе", font_size=dp(16), bold=True)
        t3.content = AboutTab()
        
        tp.add_widget(t1)
        tp.add_widget(t2)
        tp.add_widget(t3)
        
        root.add_widget(tp)
        
        exit_btn = styled_button(
            "Выход", (0.55, 0.25, 0.25, 1), 
            size_hint=(None, None), 
            size=(dp(160), dp(40)), 
            pos_hint={'right': 0.99, 'center_y': 0.973}, 
            font_size=dp(17)
        )
        exit_btn.bind(on_release=lambda x: self.stop())
        root.add_widget(exit_btn)
        
        # --- ЗАПУСК АВТООБНОВЛЕНИЯ ---
        Clock.schedule_interval(self.check_sync, 2.0)
        
        return root

    def check_sync(self, dt):
        current_mtime = db.get_db_mtime()
        if current_mtime > self.last_db_mtime:
            self.last_db_mtime = current_mtime
            if hasattr(self, 'products_tab'):
                # Передаем reset_scroll=False, чтобы прокрутка не сбрасывалась
                self.products_tab.refresh(reset_scroll=False)
                print("База данных обновлена извне.")

if __name__ == '__main__':
    SplitterApp().run()