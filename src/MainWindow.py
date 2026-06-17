from datetime import date
import sys
import os
import json
import subprocess
import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QDate
from PyQt6.uic import loadUi
from PyQt6.QtGui import QKeySequence, QShortcut 
from num2words import num2words
from pypdf import PdfReader, PdfWriter


from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib import colors        




def print_cheque(filename: str):
    if sys.platform == "win32":
        os.startfile(filename, "print")
    else:
        try:
            subprocess.run(["evince", "--preview", filename])
        except FileNotFoundError:
            subprocess.run(["xdg-open", filename])

def resource_path(relative_path_dev, relative_path_bundle):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path_bundle)
    return os.path.abspath(relative_path_dev)



def rotate_pdf(filename: str):
    reader = PdfReader(filename)
    writer = PdfWriter()
    
    for page in reader.pages:
        page.rotate(270)
        writer.add_page(page)
    
    with open(filename, 'wb') as f:
        writer.write(f)

def create_cheque_pdf(filename, date, payee, amount, amount_words):
    width  = 215.9 * mm
    height = 88.9  * mm
    c = canvas.Canvas(filename, pagesize=(width, height))

    def y(mm_from_top):
        return height - (mm_from_top * mm)

    c.setFont("Helvetica", 10) 

    # Bounding box (Optional: remove or comment out stroke=1 when printing on real checks)
    c.setStrokeColor(colors.black)
    c.rect(0, 0, width, height, fill=0, stroke=1)

    # 1. Date (UI X: 610, Y: 40) -> 161.4mm from left, 10.6mm from top
    date_digits = date.replace("/", "")
    date_formatted = " ".join(date_digits)
    c.drawString(161.4 * mm, y(10.6), date_formatted)

    # 2. Payee Name (UI X: 110, Y: 90) -> 29.1mm from left, 23.8mm from top
    c.drawString(29.1 * mm, y(23.8), payee.upper())

    # 3. Numeric Amount (UI X: 610, Y: 80) -> 161.4mm from left, 21.2mm from top
    # Added a leading peso sign descriptor structure to match your layout's ₱ indicator
    c.drawString(161.4 * mm, y(21.2), f"{amount}")

    # 4. Amount Words (UI X: 80, Y: 120) -> 21.2mm from left, 31.8mm from top
    c.drawString(21.2 * mm, y(31.8), amount_words)

    c.save()
    #rotate_pdf(filename)
    print_cheque(filename)


def amount_to_words(amount: str) -> str:
    value = float(amount.replace(',', ''))
    
    pesos = int(value)
    centavos = round((value - pesos) * 100)
    
    words = num2words(pesos, lang='en').upper()
    
    if centavos > 0:
        return f"{words} & {centavos}/100 ONLY"
    return f"{words}  ONLY"







class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Check Writer")
        loadUi(resource_path("src/ui/cheque_writer.ui", "src/ui/cheque_writer.ui"), self)
        native_bundle_path = os.path.join("src", "ui", "check.jpeg")
        image_path = resource_path("src/ui/check.jpeg", native_bundle_path)
        clean_qt_path = image_path.replace('\\', '/')

        self.chequeFrame.setStyleSheet(f"""
            #chequeFrame {{
                min-width: 816px;
                max-width: 816px;
                min-height: 336px;
                max-height: 336px;
                border-image: url("{clean_qt_path}") 0 0 0 0 stretch stretch;
            }}
        """)

        self.clearButton.clicked.connect(self.clear_fields)
        self.generatePDFButton.clicked.connect(self.print_cheque_info)
        self.pasteShortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        self.pasteShortcut.activated.connect(self.paste_from_clipboard)


    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard().text()
        cols = clipboard.strip().split('\t')
        
        if len(cols) < 3:
            print("Not enough columns in clipboard")
            return

        raw_date = cols[0].strip()
        raw_payee = cols[1].strip().upper()
        raw_amount = cols[2].strip()

        try:
            calculated_words = amount_to_words(raw_amount)
        except ValueError:
            calculated_words = "INVALID AMOUNT"
            print(f"Could not convert '{raw_amount}' to words.")

        # Map the values to your UI fields
        fields = [
            (self.dateEdit,      raw_date),
            (self.payeeName,     raw_payee),
            (self.paidAmount,    raw_amount),
            (self.amountWords,   calculated_words), # Fills the word box right on paste
        ]
        
        for widget, value in fields:
            if hasattr(widget, 'setDate'):
                val = QDate.fromString(value, "MM/dd/yyyy")
                widget.setDate(val)
            elif hasattr(widget, 'setText'):
                widget.setText(value)

    def clear_fields(self):
        """Clears text from all the input fields."""
        self.payeeName.clear()
        self.paidAmount.clear()
        self.amountWords.clear()
        print("Fields cleared.")

    def print_cheque_info(self):
        """Retrieves and prints the data currently entered in the fields."""
        filename="cheque.pdf"
        payee = self.payeeName.text()
        amount = self.paidAmount.text()
        amount_words = amount_to_words(amount)
        chequeDate = self.dateEdit.date().toString("MM/dd/yyyy")

        create_cheque_pdf(filename,chequeDate,payee,str(amount),amount_words)


