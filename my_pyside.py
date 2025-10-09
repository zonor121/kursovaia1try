import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                              QHBoxLayout, QWidget, QPushButton, QLineEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class ModernCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Современный Калькулятор")
        self.setFixedSize(300, 400)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: white;
                border: 2px solid #555;
                border-radius: 10px;
                padding: 10px;
                font-size: 20px;
            }
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                min-width: 50px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QPushButton[special="true"] {
                background-color: #ff9500;
                color: white;
            }
            QPushButton[special="true"]:hover {
                background-color: #ffaa33;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Поле ввода
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        layout.addWidget(self.display)
        
        # Кнопки
        buttons_layout = QVBoxLayout()
        
        # Первый ряд
        row1 = QHBoxLayout()
        buttons = ['7', '8', '9', '/']
        for text in buttons:
            btn = self.create_button(text)
            if text in ['/', '*', '-', '+']:
                btn.setProperty("special", "true")
            row1.addWidget(btn)
        buttons_layout.addLayout(row1)
        
        # Второй ряд
        row2 = QHBoxLayout()
        buttons = ['4', '5', '6', '*']
        for text in buttons:
            btn = self.create_button(text)
            if text in ['/', '*', '-', '+']:
                btn.setProperty("special", "true")
            row2.addWidget(btn)
        buttons_layout.addLayout(row2)
        
        # Третий ряд
        row3 = QHBoxLayout()
        buttons = ['1', '2', '3', '-']
        for text in buttons:
            btn = self.create_button(text)
            if text in ['/', '*', '-', '+']:
                btn.setProperty("special", "true")
            row3.addWidget(btn)
        buttons_layout.addLayout(row3)
        
        # Четвертый ряд
        row4 = QHBoxLayout()
        buttons = ['0', 'C', '=', '+']
        for text in buttons:
            btn = self.create_button(text)
            if text in ['/', '*', '-', '+', '=', 'C']:
                btn.setProperty("special", "true")
            row4.addWidget(btn)
        buttons_layout.addLayout(row4)
        
        layout.addLayout(buttons_layout)
    
    def create_button(self, text):
        button = QPushButton(text)
        button.clicked.connect(lambda: self.on_button_click(text))
        return button
    
    def on_button_click(self, text):
        if text == 'C':
            self.display.clear()
        elif text == '=':
            try:
                result = eval(self.display.text())
                self.display.setText(str(result))
            except:
                self.display.setText("Ошибка")
        else:
            current_text = self.display.text()
            self.display.setText(current_text + text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = ModernCalculator()
    calculator.show()
    sys.exit(app.exec())