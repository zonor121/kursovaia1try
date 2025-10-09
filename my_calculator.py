from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle

Window.clearcolor = (0.1, 0.1, 0.1, 1)

class ModernButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = 20
        self.bold = True
        
        with self.canvas.before:
            Color(0.25, 0.25, 0.25, 1)
            self.rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[15]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class SpecialButton(ModernButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1.0, 0.58, 0.0, 1)
            self.rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[15]
            )

class Display(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "0"
        self.font_size = 32
        self.color = (1, 1, 1, 1)
        self.halign = 'right'
        self.valign = 'middle'
        self.text_size = self.size
        self.bind(size=self.on_size)
        
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[10]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def on_size(self, *args):
        self.text_size = self.size
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ModernCalculator(App):
    def build(self):
        self.title = "Современный Калькулятор"
        self.current_text = "0"
        
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Дисплей
        self.display = Display(size_hint=(1, 0.2))
        main_layout.add_widget(self.display)
        
        # Кнопки
        grid = GridLayout(cols=4, spacing=10, size_hint=(1, 0.8))
        
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]
        
        for text in buttons:
            if text in ['/', '*', '-', '+', '=', 'C']:
                btn = SpecialButton(text=text)
            else:
                btn = ModernButton(text=text)
            btn.bind(on_press=self.on_button_press)
            grid.add_widget(btn)
        
        main_layout.add_widget(grid)
        return main_layout
    
    def on_button_press(self, instance):
        text = instance.text
        
        if text == 'C':
            self.current_text = "0"
            self.display.text = self.current_text
        elif text == '=':
            try:
                result = str(eval(self.current_text))
                self.current_text = result
                self.display.text = result
            except:
                self.current_text = "0"
                self.display.text = "Ошибка"
        else:
            if self.current_text == "0" or self.current_text == "Ошибка":
                self.current_text = text
            else:
                self.current_text += text
            self.display.text = self.current_text

if __name__ == "__main__":
    ModernCalculator().run()