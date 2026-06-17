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

def create_cheque_pdf(filename,date, payee,amount,amount_words):
    c = canvas.Canvas(filename)

    width  = 215.9 * mm
    height = 88.9  * mm
    c = canvas.Canvas(filename, pagesize=(width, height))

    def y(mm_from_top):
        return height - (mm_from_top * mm)
    
    def y_inches(inches_from_top):
        return height - (inches_from_top * inch)
    
    def mark(x, y_pos):
        c.line(x - 10, y_pos, x + 10, y_pos)
        c.line(x, y_pos - 10, x, y_pos + 10)

    c.setStrokeColor(colors.red)
    # mark(5.82 * inch, y_inches(0.60))
    # mark(0.55 * inch, y_inches(0.93))
    # mark(5.82 * inch, y_inches(0.93))
    # mark(0.55 * inch, y_inches(1.25))

    c.setFont("Helvetica", 10) 

    # Bounding box
    c.setStrokeColor(colors.black)
    c.rect(0, 0, width, height, fill=0, stroke=1)

    # Date 
    date_digits = date.replace("/", "")
    date_formatted = " ".join(date_digits)
    print(date)
    print(date_digits)
    print(date_formatted)
    c.drawString(5.82 * inch, y_inches(0.60), date_formatted)
    c.drawString(0.55 * inch, y_inches(0.93), payee.upper())
    c.drawString(5.82 * inch, y_inches(0.93), amount)
    c.drawString(0.55 * inch, y_inches(1.25), amount_words)

    c.save()
    rotate_pdf(filename)
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
        self.setWindowTitle("Check Printer Production Tree")
        loadUi(resource_path("src/ui/cheque_writer.ui", "src/ui/cheque_writer.ui"), self)
        self.clearButton.clicked.connect(self.clear_fields)
        self.generatePDFButton.clicked.connect(self.print_cheque_info)
        self.pasteShortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        self.pasteShortcut.activated.connect(self.paste_from_clipboard)


    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard().text()
        cols = clipboard.strip().split('\t')
        
        if len(cols) < 4:
            print("Not enough columns in clipboard")
            return

        fields = [
            (self.dateEdit,      cols[0].strip()),
            (self.payeeName,     cols[1].strip()),
            (self.paidAmount,    cols[2].strip()),
            (self.amountWords,   cols[3].strip()),
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


