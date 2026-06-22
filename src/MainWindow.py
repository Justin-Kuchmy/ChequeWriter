from datetime import date
import sys
import os
import json
import subprocess
import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableWidgetItem, QMessageBox
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

############################################
    # width  = 215.9 * mm
    # height = 88.9  * mm

    # c = canvas.Canvas(filename, pagesize=(width, height))

    # def y(mm_from_top):
    #     return height - (mm_from_top * mm)

    # c.setFont("Helvetica", 10) 

    # # Bounding box
    # c.setStrokeColor(colors.black)
    # c.rect(0, 0, width, height, fill=0, stroke=1)

    # #date
    # date_digits = date.toString("MM/dd/yyyy").replace("/", " ")
    # date_formatted = "   ".join(date_digits)
    # c.drawString(160 * mm, y(19), date_formatted)

    # # 2. Payee Name
    # c.drawString(32 * mm, y(30.5), payee.upper())


    # # 3. Amount Words
    # c.drawString(25.2 * mm, y(39.5), amount_words)

    # # 4. Numeric Amount 
    # c.drawString(152.4 * mm, y(28.0), f"{amount}")

############################################

    width  = 203.2 * mm
    height = 76.2  * mm
    c = canvas.Canvas(filename, pagesize=(width, height))

    def y(mm_from_top):
        return height - (mm_from_top * mm)

    c.setFont("Helvetica", 9)

    c.setStrokeColor(colors.black)
    c.rect(0, 0, width, height, fill=0, stroke=1)

    # Date  (was 160, 19)
    date_digits = date.toString("MM/dd/yyyy").replace("/", " ")
    date_formatted = "   ".join(date_digits)
    c.drawString(150* mm, y(16.5), date_formatted)

    # Payee Name  (was 32, 30.5)
    c.drawString(32 * mm, y(26), payee.upper())

    # Numeric Amount  (was 152.4, 28.0)
    c.drawString(147.4 * mm, y(24.5), f"{amount}")

    # Amount Words  (was 25.2, 39.5)
    c.drawString(25.2 * mm, y(34), amount_words)
    

    c.save()
    rotate_pdf(filename)
    print_cheque(filename)


#for debugging purposes, to overlay the generated PDF on the check image
# from pdf2image import convert_from_path
# from PIL import Image
# def overlay_pdf_on_cheque_image(pdf_path, cheque_image_path, output_path="overlay_check.png"):
    
#     pdf_pages = convert_from_path(pdf_path, dpi=150) 
#     pdf_image = pdf_pages[0].convert("RGBA")

#     cheque_image = Image.open(cheque_image_path).convert("RGBA")

#     pdf_image = pdf_image.resize(cheque_image.size)

#     alpha = pdf_image.split()[3].point(lambda p: p * 0.5)
#     pdf_image.putalpha(alpha)
    
#     combined = Image.alpha_composite(cheque_image, pdf_image)
#     combined.save(output_path)

def amount_to_words(amount: str) -> str:
    #value = float(amount.replace(',', ''))
    value = float(amount.replace(',', ''))
    formatted_amount = f"{value:,.2f}"
    
    pesos = int(value)
    centavos = round((value - pesos) * 100)
    
    words = num2words(pesos, lang='en').upper()
    words = words.replace("AND ", "")  # Remove "AND" if it exists
    words = words.replace(',', '')  # Remove "AND" if it exists
    
    if centavos > 0:
        return f"{words} AND {centavos}/100 ONLY", formatted_amount
    return f"{words} ONLY", formatted_amount

def parse_flexible_date(date_str: str) -> QDate:
    date = QDate.fromString(date_str, "MM/dd/yyyy")
    if not date.isValid():
        messagebox = QMessageBox()
        messagebox.setIcon(QMessageBox.Icon.Warning)
        messagebox.setWindowTitle("Invalid Date Format")
        messagebox.setText(f"Could not parse date: '{date_str}'. Please use MM/dd/yyyy format.")
        messagebox.exec()
        return QDate() 
    return date

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Check Writer")
        loadUi(resource_path("src/ui/cheque_writer.ui", "src/ui/cheque_writer.ui"), self)
        native_bundle_path = os.path.join("src", "ui", "check.jpg")
        image_path = resource_path("src/ui/check.jpg", native_bundle_path)
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

        self.clearCheckButton.clicked.connect(self.clear_check_fields)
        self.clearTableButton.clicked.connect(self.clear_table_fields)
        self.generatePDFButton.clicked.connect(self.print_cheque_info)
        self.pasteShortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        self.pasteShortcut.activated.connect(self.paste_from_excel)
        self.excelTableData.horizontalHeader().setStretchLastSection(False)
        self.excelTableData.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.excelTableData.cellClicked.connect(self.on_row_clicked)

    def on_row_clicked(self, row, column):
        date_item = self.excelTableData.item(row, 0)
        payee_item = self.excelTableData.item(row, 1)
        amount_item = self.excelTableData.item(row, 2)

        if date_item and payee_item and amount_item:
            raw_date = date_item.text()
            raw_payee = payee_item.text().upper()
            raw_amount = amount_item.text()

            try:
                calculated_words, self.formatted_amount = amount_to_words(raw_amount)
                raw_amount = self.formatted_amount  # Update raw_amount to the formatted version
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

    def paste_from_excel(self):
        clipboard = QApplication.clipboard().text()
        rows = clipboard.strip().split('\n')
        self.formatted_amount = None
        
        for row in rows:
            cols = row.split('\t')
            if len(cols) < 3:
                print("Not enough columns in clipboard")
                continue

            raw_date = cols[0].strip()
            raw_payee = cols[1].strip().upper()
            raw_amount = cols[2].strip()

            raw_date = parse_flexible_date(raw_date)
            
            print(f"Pasting: Date: {raw_date}, Payee: {raw_payee}, Amount: {raw_amount}")
            newRowCol1 = QTableWidgetItem(raw_date.toString("MM/dd/yyyy"))
            newRowCol2 = QTableWidgetItem(raw_payee)
            newRowCol3 = QTableWidgetItem(raw_amount)

            row_index = self.excelTableData.rowCount()
            self.excelTableData.insertRow(row_index)
            self.excelTableData.setItem(row_index, 0, newRowCol1)
            self.excelTableData.setItem(row_index, 1, newRowCol2)
            self.excelTableData.setItem(row_index, 2, newRowCol3)

    def clear_check_fields(self):
        """Clears text from all the input fields."""
        self.payeeName.clear()
        self.paidAmount.clear()
        self.amountWords.clear()
        print("Fields cleared.")

    def clear_table_fields(self):
        """Clears all rows from the Excel table."""
        self.excelTableData.setRowCount(0)
        print("Table fields cleared.")

    def print_cheque_info(self):
        """Retrieves and prints the data currently entered in the fields."""
        payee = self.payeeName.text().strip()
        amount = self.paidAmount.text().strip()

        if not payee or not amount:
                print("Missing payee or amount — nothing to print.")
                return

        try:
            amount_words, self.formatted_amount = amount_to_words(amount)
        except ValueError:
            print(f"Invalid amount: '{amount}'")
            return

        filename = "cheque.pdf"
        chequeDate = parse_flexible_date(self.dateEdit.date().toString("MM/dd/yyyy"))

        create_cheque_pdf(filename, chequeDate, payee, str(self.formatted_amount), amount_words)
        
        #overlay_pdf_on_cheque_image(filename, "src/ui/check.jpg")
        input("Press Enter to Exit...")


