# -*- coding: utf-8 -*-
import webbrowser
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from widgets import styled_button

class AboutTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(20), spacing=dp(10), **kwargs)

        # Обновленный текст описания программы
        about_text = """
[b][size=24][color=55aaff]Распределение кодов маркировки по товарам[/color][/size][/b]

Данная программа предназначена для автоматического распределения отсканированных кодов маркировки (GS1 DataMatrix) по отдельным текстовым файлам в зависимости от товара.

[b][size=18]Инструкция по использованию:[/size][/b]

[b]1. Вкладка «Товары»[/b]
• Внесите в базу данных информацию о ваших товарах: Название, Объём (необязательно) и GTIN (14 цифр).
• Для удобного поиска используйте строку «Поиск» над таблицей (ищет по названию, GTIN и номеру).
• Вы всегда можете отредактировать или удалить товар, используя кнопки в таблице.

[b]2. Вкладка «Разделить файл»[/b]
• Нажмите кнопку [b]«Обзор файла»[/b] и выберите текстовый файл (`.txt`), содержащий отсканированные коды.
• Нажмите кнопку [b]«Разделить»[/b].

[b]3. Результат[/b]
• Программа проанализирует файл, найдет коды, соответствующие GTIN из вашей базы, и создаст отдельные файлы для каждого товара.
• Рядом с исходным файлом создастся папка с его именем, внутри которой появятся файлы вида: [i]Название - Объём (Количество) - GTIN.txt[/i]
• Если файлы уже существуют, они будут перезаписаны.

[b][size=18]Особенности:[/size][/b]
• Поддерживаются файлы в кодировках UTF-8, Windows-1251 и Latin-1.
• Программа автоматически определяет GTIN в строке по стандартному префиксу `01`.
• Объём в названии файла автоматически дополняется символом `л.`, если вы не указали его вручную.

[b][size=18]Исходный код[/size][/b]
Проект распространяется свободно. Полный исходный код, история изменений и возможность сообщить о проблемах - в репозитории на GitHub.
"""
        
        # Создаем метку с текстом
        lbl = Label(
            text=about_text,
            markup=True,          # Включаем поддержку разметки (тегов)
            halign='left',        # Выравнивание по левому краю
            valign='top',         # Выравнивание по верху
            size_hint_y=None,     # Высота будет зависеть от текста
            font_size=dp(15)
        )
        # Привязываем размер текста к ширине окна для переноса строк
        lbl.bind(width=lambda *x: lbl.setter('text_size')(lbl, (lbl.width, None)))
        lbl.bind(texture_size=lambda *x: lbl.setter('height')(lbl, lbl.texture_size[1]))
        
        # Оборачиваем текст в ScrollView, чтобы можно было прокручивать
        scroll = ScrollView()
        scroll.add_widget(lbl)
        self.add_widget(scroll)

        # --- БЛОК С ССЫЛКОЙ НА GITHUB ---
        link_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Пустой виджет для отступа слева
        link_box.add_widget(Label(size_hint_x=0.2))
        
        # Кнопка-ссылка с новым названием
        github_btn = styled_button(
            "Перейти на репозиторий на GitHub", 
            (0.2, 0.2, 0.2, 1), # Темно-серый цвет
            size_hint_x=0.6,
            font_size=dp(14)
        )
        # Открываем ссылку в браузере при нажатии
        github_btn.bind(on_release=lambda x: webbrowser.open("https://github.com/Londimain/Work-schedule"))
        
        link_box.add_widget(github_btn)
        link_box.add_widget(Label(size_hint_x=0.2)) # Пустой виджет для отступа справа
        
        self.add_widget(link_box)