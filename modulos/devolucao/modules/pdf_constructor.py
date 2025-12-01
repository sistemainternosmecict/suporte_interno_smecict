from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, gray
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.units import cm
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
import os, random

class DevolucaoPdfConstructor:
    def __init__(self, data: dict):
        self.numero = random.randint(1000000, 9999999)
        self.title = "TERMO DE DEVOLUÇÃO DO CHROMEBOOK"
        self.base_color = Color(0.0, 0.50196, 0.50196)
        self.template_pdf = "modulos/termo/template.pdf"  # Reutilizando o template do termo
        self.temp_pdf = f"modulos/devolucao/temp_{self.numero}.pdf"
        self.export_folder = "static/termos"
        
        self.user_name = self.extract_first_and_second_name(data["nome"])
        self.first_name = data["nome"].split()[0]
        self.export_pdf = os.path.join(self.export_folder, f"devolucao_{self.first_name.lower()}_{self.numero}.pdf")

        self.main_paragraph = self.construct_main_paragraph(data)

        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
        
        self.criar_pdf_temp(self.temp_pdf)
        
        self.gerado = {
            "path": os.path.basename(self.export_pdf),
            "gerado": self.merge_pdf(self.template_pdf, self.temp_pdf, self.export_pdf)
        }
        self.delete_temp_pdf()

    def construct_main_paragraph(self, data: dict):
        # Usando <br/> para forçar quebras de linha e controlar o espaçamento
        return f"""
        Unidade Escolar: <b>{data.get('unidade', '___________________________')}</b>
        <br/><br/><br/>
        Conforme estabelecido no termo de responsabilidade, e considerando o
        desligamento do professor <b>{data.get('nome', '___________________________')}</b> da
        Unidade Escolar da Rede Municipal de Ensino de Saquarema, procedemos à
        devolução do Chromebook, identificado pelo número de série:
        <b>{data.get('serial', '___________________________')}</b>, matrícula n° <b>{data.get('matricula', '___________________________')}</b>, CPF
        n° <b>{data.get('cpf', '___________________________')}</b>.
        <br/><br/>
        Dessa forma, cumprimos com as disposições estabelecidas no termo de
        responsabilidade.
        """

    def extract_first_and_second_name(self, full_name):
        parts = full_name.split()
        if len(parts) > 1:
            return f"{parts[0]} {parts[1]}"
        return full_name

    def get_current_date(self):
        meses = {
            "January": "Janeiro", "February": "Fevereiro", "March": "Março",
            "April": "Abril", "May": "Maio", "June": "Junho",
            "July": "Julho", "August": "Agosto", "September": "Setembro",
            "October": "Outubro", "November": "Novembro", "December": "Dezembro"
        }
        data_atual = datetime.now()
        mes_em_portugues = meses[data_atual.strftime("%B")]
        return data_atual.strftime(f"%d de {mes_em_portugues} de %Y")

    def criar_pdf_temp(self, nome_arquivo):
        largura, altura = A4
        c = canvas.Canvas(nome_arquivo, pagesize=A4)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle", parent=styles["h2"], alignment=1, fontSize=16, spaceAfter=20)
        
        body_style = ParagraphStyle(
            "BodyStyle", parent=styles["Normal"], fontSize=12, alignment=4, leading=18)
        
        date_style = ParagraphStyle(
            "DateStyle", parent=styles["Normal"], fontSize=12, alignment=1, spaceBefore=40)

        title_paragraph = Paragraph(self.title, title_style)
        text_paragraph = Paragraph(self.main_paragraph, body_style)
        timestamp = Paragraph(f"Saquarema, {self.get_current_date()}", date_style)

        frame = Frame(2 * cm, 10 * cm, 17 * cm, 15 * cm, showBoundary=0)
        frame.addFromList([title_paragraph, Spacer(1, 20), text_paragraph, timestamp], c)

        # Linhas de Assinatura
        signature_y_user = 8 * cm
        c.line(4 * cm, signature_y_user, 10 * cm, signature_y_user)
        c.drawCentredString(7 * cm, signature_y_user - 0.5 * cm, "Usuário")

        signature_y_director = 6 * cm
        c.line(11 * cm, signature_y_director, 17 * cm, signature_y_director)
        c.drawCentredString(14 * cm, signature_y_director - 0.5 * cm, "Assinatura do Diretor")
        
        # Campo OBS
        obs_y = 4 * cm
        c.drawString(2 * cm, obs_y, "OBS.:")
        c.line(3 * cm, obs_y - 0.1 * cm, 19 * cm, obs_y - 0.1 * cm)


        c.save()

    def merge_pdf(self, template_path, content_path, output_path) -> bool:
        try:
            template_reader = PdfReader(template_path)
            content_reader = PdfReader(content_path)
            writer = PdfWriter()

            if len(template_reader.pages) > 0 and len(content_reader.pages) > 0:
                template_page = template_reader.pages[0]
                content_page = content_reader.pages[0]
                template_page.merge_page(content_page)
                writer.add_page(template_page)
                
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)
                return True
            return False
        except Exception as e:
            print(f"Erro ao mesclar PDF: {e}")
            return False

    def delete_temp_pdf(self):
        if os.path.exists(self.temp_pdf):
            os.remove(self.temp_pdf)
