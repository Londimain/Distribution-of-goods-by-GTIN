# -*- coding: utf-8 -*-
import os
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from widgets import styled_button

def normalize_gtin(gtin):
    gtin = gtin.strip()
    if gtin.isdigit() and len(gtin) < 14:
        gtin = gtin.zfill(14)
    return gtin

def sanitize_filename(name):
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, '')
    return name.strip().rstrip('.')

def read_lines(filepath):
    for enc in ('utf-8', 'cp1251', 'latin-1'):
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return [ln.strip() for ln in f if ln.strip()]
        except UnicodeDecodeError:
            continue
    return []

def show_msg(text, title="Сообщение"):
    """Всплывающее окно с кнопкой 'Хорошо' (требует подтверждения)."""
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(15))
    lbl = Label(text=text, halign='center', valign='middle')
    lbl.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
    content.add_widget(lbl)
    
    ok_btn = styled_button("Хорошо", (0.2, 0.5, 0.8, 1), size_hint_y=None, height=dp(40))
    content.add_widget(ok_btn)
    
    popup = Popup(title=title, content=content, size_hint=(None, None), size=(400, 220), auto_dismiss=False)
    ok_btn.bind(on_release=popup.dismiss)
    popup.open()
    return popup

def show_toast(text, duration=2.5, title="Уведомление"):
    """Всплывающее окно, которое автоматически исчезает через заданное время."""
    lbl = Label(text=text, halign='center', valign='middle', font_size=dp(15))
    lbl.bind(size=lambda s, v: setattr(s, 'text_size', (v[0], v[1])))
    
    popup = Popup(
        title=title, 
        content=lbl, 
        size_hint=(None, None), 
        size=(450, 150), 
        auto_dismiss=True
    )
    popup.open()
    # Автоматически закрываем окно через duration секунд
    Clock.schedule_once(lambda dt: popup.dismiss(), duration)
    return popup