from fpdf import FPDF

class PDFHelper:

    def __init__(self):
        pass

    def _create_pdf(self):
        pdf = FPDF()
        pdf.set_font("Arial", size=15)
        pdf.add_page()
        return pdf
    
    def _write_to_pdf(self, pdf, txt):
        pdf.cell(200, 10, txt=txt, ln=1, align = 'S')
        return pdf
    
    def save_pdf(self, pdf, file_name: str):
        pdf.output(file_name)
        