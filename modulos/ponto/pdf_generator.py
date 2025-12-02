from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime, timedelta, time, date
import os
import calendar

class PontoPdfGenerator:
    def __init__(self, usuario, mes, ano, registros_ponto):
        self.usuario = usuario
        self.mes = int(mes)
        self.ano = int(ano)
        self.registros_ponto = registros_ponto # List of RegistroPonto objects
        self.export_folder = "static/ponto_relatorios"
        self.template_pdf = "modulos/termo/template.pdf" # Reusing existing template
        self.temp_pdf = os.path.join(self.export_folder, f"temp_ponto_{usuario.id}_{self.mes}_{self.ano}.pdf")
        self.output_filename = f"Folha_Ponto_{usuario.nome}_{self.mes:02d}-{self.ano}.pdf"
        self.export_pdf_path = os.path.join(self.export_folder, self.output_filename)

        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)

        self.gerado = {"path": self.output_filename, "gerado": self._generate_pdf()}

    def _generate_pdf(self):
        try:
            self._create_content_pdf(self.temp_pdf)
            merged = self._merge_pdf(self.template_pdf, self.temp_pdf, self.export_pdf_path)
            self._delete_temp_pdf()
            return merged
        except Exception as e:
            print(f"Erro ao gerar PDF de ponto: {e}")
            return False

    def _create_content_pdf(self, output_path):
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle", parent=styles["h2"], alignment=1, fontSize=18, spaceAfter=20, leading=22)
        
        header_style = ParagraphStyle(
            "HeaderStyle", parent=styles["Normal"], alignment=1, fontSize=12, spaceAfter=10)

        # Title
        title_text = f"FOLHA DE PONTO"
        p_title = Paragraph(title_text, title_style)
        p_title.wrapOn(c, width - 2*cm, height)
        p_title.drawOn(c, 1*cm, height - 15*cm) # Ajustado para baixo

        # User and Period Info
        period_name = datetime(self.ano, self.mes, 1).strftime("%B de %Y").capitalize()
        header_text = f"<b>Funcionário:</b> {self.usuario.nome}<br/><b>Mês/Ano:</b> {period_name}"
        p_header = Paragraph(header_text, header_style)
        p_header.wrapOn(c, width - 2*cm, height)
        p_header.drawOn(c, 1*cm, height - 16.5*cm) # Ajustado para baixo

        # Prepare table data
        table_data = [['Dia', 'Chegada', 'Saída Almoço', 'Retorno Almoço', 'Saída', 'Total Diário']]
        
        # Create a dictionary for easier access to records by date
        records_by_date = {r.data: r for r in self.registros_ponto}
        
        total_month_duration = timedelta(0)
        
        for day in range(1, calendar.monthrange(self.ano, self.mes)[1] + 1):
            current_date = date(self.ano, self.mes, day)
            registro = records_by_date.get(current_date)

            chegada = registro.chegada.strftime('%H:%M') if registro and registro.chegada else '--:--'
            saida_almoco = registro.saida_almoco.strftime('%H:%M') if registro and registro.saida_almoco else '--:--'
            retorno_almoco = registro.retorno_almoco.strftime('%H:%M') if registro and registro.retorno_almoco else '--:--'
            saida = registro.saida.strftime('%H:%M') if registro and registro.saida else '--:--'
            
            daily_total = '--:--h'
            if registro and registro.chegada and registro.saida_almoco and registro.retorno_almoco and registro.saida:
                duration = self._calculate_daily_duration(registro)
                daily_total = self._format_timedelta(duration)
                total_month_duration += duration
            
            table_data.append([str(day), chegada, saida_almoco, retorno_almoco, saida, daily_total])

        # Add total for the month
        table_data.append(['', '', '', '', 'Total do Mês:', self._format_timedelta(total_month_duration)])

        # Table style
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#008080')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('FONTNAME', (4, -1), (4, -1), 'Helvetica-Bold'), # Total do mês label
            ('FONTNAME', (5, -1), (5, -1), 'Helvetica-Bold'), # Total do mês value
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0e0d0')), # Fundo da linha de total
        ])

        # Create the table
        table = Table(table_data, colWidths=[1.5*cm, 2.5*cm, 3.0*cm, 3.0*cm, 2.5*cm, 3.0*cm])
        table.setStyle(table_style)
        
        # Draw table
        table.wrapOn(c, width - 2*cm, height)
        table.drawOn(c, 1*cm, height - (p_title.height + p_header.height + 24.5*cm)) # Ajustar posição Y

        c.save()

    def _calculate_daily_duration(self, registro):
        if not all([registro.chegada, registro.saida_almoco, registro.retorno_almoco, registro.saida]):
            return timedelta(0)

        chegada_dt = datetime.combine(registro.data, registro.chegada)
        saida_almoco_dt = datetime.combine(registro.data, registro.saida_almoco)
        retorno_almoco_dt = datetime.combine(registro.data, registro.retorno_almoco)
        saida_dt = datetime.combine(registro.data, registro.saida)

        # Work before lunch
        work_before_lunch = saida_almoco_dt - chegada_dt
        # Work after lunch
        work_after_lunch = saida_dt - retorno_almoco_dt
        
        return work_before_lunch + work_after_lunch

    def _format_timedelta(self, td):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes:02d}m"

    def _merge_pdf(self, template_path, content_path, output_path) -> bool:
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

    def _delete_temp_pdf(self):
        if os.path.exists(self.temp_pdf):
            os.remove(self.temp_pdf)
