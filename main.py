# -*- coding: utf-8 -*-
import os
import sys
import ctypes
from ctypes import wintypes

# --- Отключаем масштабирование Windows для корректного центрирования ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
# ----------------------------------------------------------------------

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.tabbedpanel import TabbedPanel
# main.py
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from widgets import CustomTab, styled_button
from tab_products import ProductsTab
from tab_splitter import SplitterTab
from tab_about import AboutTab
import db

# Функция для правильного пути к ресурсам (работает и в .py, и в .exe)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SplitterApp(App):
    title = "Распределение кодов по товарам v1.2.0"

    def build(self):
        # Устанавливаем иконку для окна и панели задач
        try:
            Window.set_icon(resource_path(os.path.join('ico', 'distribution.ico')))
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")

        Clock.schedule_once(self.center_window, 0.2)
        db.init_db()
        
        root = FloatLayout()
        
        tp = TabbedPanel(do_default_tab=False, tab_width=dp(180), tab_height=dp(45), padding=[0, 0, 0, 0])
        
        # --- НАСТРОЙКА ПОЛОЖЕНИЯ ВКЛАДОК ПО ВЕРТИКАЛИ ---
        tp.size_hint = (1, 0.998) 
        
        t1 = CustomTab(text="Товары", font_size=dp(16), bold=True)
        t1.content = ProductsTab()
        
        t2 = CustomTab(text="Разделить файл", font_size=dp(16), bold=True)
        t2.content = SplitterTab()

        t3 = CustomTab(text="О программе", font_size=dp(16), bold=True)
        t3.content = AboutTab()
        
        tp.add_widget(t1)
        tp.add_widget(t2)
        tp.add_widget(t3)
        
        root.add_widget(tp)
        
        # --- НАСТРОЙКА КНОПКИ ВЫХОД ---
        exit_btn = styled_button(
            "Выход", (0.55, 0.25, 0.25, 1), 
            size_hint=(None, None), 
            size=(dp(160), dp(40)), 
            pos_hint={'right': 0.99, 'center_y': 0.966}, 
            font_size=dp(17)
        )
        exit_btn.bind(on_release=lambda x: self.stop())
        root.add_widget(exit_btn)
        
        return root

    def center_window(self, dt):
        Window.size = (1200, 800)
        Clock.schedule_once(self.force_center, 0.1)

    def force_center(self, dt):
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, self.title)
            if hwnd:
                user32 = ctypes.windll.user32
                user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
                user32.GetWindowRect.restype = wintypes.BOOL
                
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                w = rect.right - rect.left
                h = rect.bottom - rect.top
                
                screen_w = user32.GetSystemMetrics(0)
                screen_h = user32.GetSystemMetrics(1)
                
                x = (screen_w - w) // 2 - 50
                y = (screen_h - h) // 2
                
                user32.SetWindowPos(hwnd, 0, x, y, 0, 0, 0x0001 | 0x0004)
        except Exception as e:
            print("Ошибка центрирования:", e)
            Window.left = (Window.system_size[0] - Window.size[0]) // 2 - 50
            Window.top = (Window.system_size[1] - Window.size[1]) // 2

if __name__ == '__main__':
    SplitterApp().run()