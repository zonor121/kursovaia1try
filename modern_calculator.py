import customtkinter as ctk
import tkinter as tk

class ModernCalculator:
    def __init__(self):
        # Настройка темы ДО создания окна
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Современный Калькулятор")
        self.root.geometry("300x400")
        self.root.resizable(False, False)
        
        self.current_expression = ""
        self.create_widgets()
    
    def create_widgets(self):
        # Поле ввода
        self.display = ctk.CTkEntry(
            self.root,
            width=280,
            height=60,
            font=("Arial", 20),
            justify="right"
        )
        self.display.pack(pady=20)
        
        # Фрейм для кнопок
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Расположение кнопок
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+']
        ]
        
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                # Определяем цвет кнопки
                if text in ['/', '*', '-', '+']:
                    fg_color = "#FF9500"
                    hover_color = "#FFAA33"
                elif text in ['=', 'C']:
                    fg_color = "#FF2D55"
                    hover_color = "#FF4C6B"
                else:
                    fg_color = "#404040"
                    hover_color = "#505050"
                
                btn = ctk.CTkButton(
                    button_frame,
                    text=text,
                    width=60,
                    height=50,
                    font=("Arial", 18),
                    fg_color=fg_color,
                    hover_color=hover_color,
                    command=lambda t=text: self.on_button_click(t)
                )
                btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
        
        # Настройка веса строк и столбцов
        for i in range(4):
            button_frame.grid_rowconfigure(i, weight=1)
            button_frame.grid_columnconfigure(i, weight=1)
    
    def on_button_click(self, text):
        if text == 'C':
            self.display.delete(0, tk.END)
            self.current_expression = ""
        elif text == '=':
            try:
                result = eval(self.current_expression)
                self.display.delete(0, tk.END)
                self.display.insert(0, str(result))
                self.current_expression = str(result)
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Ошибка")
                self.current_expression = ""
        else:
            self.current_expression += text
            self.display.delete(0, tk.END)
            self.display.insert(0, self.current_expression)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernCalculator()
    app.run()