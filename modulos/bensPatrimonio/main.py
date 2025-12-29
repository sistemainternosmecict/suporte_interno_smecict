from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os

class BensPatrimonioGeradorDocumento:
    # Layout Constants
    HEADER_HEIGHT = 3*cm
    FOOTER_HEIGHT = 2*cm
    TOP_MARGIN = 4.5*cm
    TMBP_BOX_HEIGHT = 0.8*cm
    BLOCK_GAP = 0.5*cm
    SECTION_HEIGHT = 2.3*cm
    SOLICITACAO_HEIGHT = 6.5*cm
    SITUACAO_HEIGHT = 2*cm

    def __init__(self, data, file_path):
        self.data = data
        self.file_path = file_path
        self.CANVAS_WIDTH, self.CANVAS_HEIGHT = A4
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

    def _draw_header_and_footer(self, c):
        header_path = os.path.join(self.current_dir, 'header.png')
        footer_path = os.path.join(self.current_dir, 'footer.png')

        if os.path.exists(header_path):
            c.drawImage(header_path, 0, self.CANVAS_HEIGHT - self.HEADER_HEIGHT, width=self.CANVAS_WIDTH, height=self.HEADER_HEIGHT)
        if os.path.exists(footer_path):
            c.drawImage(footer_path, 0, 0, width=self.CANVAS_WIDTH, height=self.FOOTER_HEIGHT)

    def _draw_administrative_unit(self, c, y_pos, title, data_prefix):
        c.rect(1.5*cm, y_pos - self.SECTION_HEIGHT, self.CANVAS_WIDTH - 3*cm, self.SECTION_HEIGHT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(1.7*cm, y_pos - self.SECTION_HEIGHT + 1.6*cm, title)
        c.setFont("Helvetica", 9)
        c.drawString(1.7*cm, y_pos - self.SECTION_HEIGHT + 1*cm, f"ORGÃO/SETOR: {self.data.get(f'{data_prefix}_orgao_setor', '')}")
        c.drawString(1.7*cm, y_pos - self.SECTION_HEIGHT + 0.4*cm, f"RESPONSÁVEL: {self.data.get(f'{data_prefix}_responsavel', '')}")
        c.drawString(self.CANVAS_WIDTH - 8*cm, y_pos - self.SECTION_HEIGHT + 0.3*cm, f"MATRÍCULA: {self.data.get(f'{data_prefix}_matricula', '')}")
        return self.SECTION_HEIGHT

    def _draw_checkbox(self, c, x, y, label, checked=False):
        symbol = "(X)" if checked else "()"
        c.drawString(x, y, f"{symbol} {label}")

    def gerar_pdf(self):
        # gerar um numero unico para documento nao repetivel usando modulo uuid
        import uuid
        self.numero_documento = str(uuid.uuid4().int)[:6]
        c = canvas.Canvas(self.file_path, pagesize=A4)
        self._draw_header_and_footer(c)

        y_cursor = self.CANVAS_HEIGHT

        # Title
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.CANVAS_WIDTH / 2.0, y_cursor - self.TOP_MARGIN, "Termo de Movimentação de Bens Patrimoniais")
        y_cursor -= (self.TOP_MARGIN + 1*cm)

        # TMBP/PMS number
        c.setFont("Helvetica-Bold", 10)
        c.rect(self.CANVAS_WIDTH - 7*cm, y_cursor - self.TMBP_BOX_HEIGHT, 5.5*cm, self.TMBP_BOX_HEIGHT)
        c.drawString(self.CANVAS_WIDTH - 6.8*cm, y_cursor - self.TMBP_BOX_HEIGHT + 0.3*cm, "TMBP/PMS nº")
        c.setFont("Helvetica", 10)
        c.drawString(self.CANVAS_WIDTH - 4.2*cm, y_cursor - self.TMBP_BOX_HEIGHT + 0.3*cm, f"{self.numero_documento} / {self.data.get('ano', '20')}")
        y_cursor -= (self.TMBP_BOX_HEIGHT + self.BLOCK_GAP)

        # Unidade Administrativa Usuária
        drawn_height = self._draw_administrative_unit(c, y_cursor, "UNIDADE ADMINISTRATIVA USUÁRIA", "usuario")
        y_cursor -= (drawn_height + self.BLOCK_GAP)

        # Unidade Administrativa Destino
        drawn_height = self._draw_administrative_unit(c, y_cursor, "UNIDADE ADMINISTRATIVA DESTINO", "destino")
        y_cursor -= (drawn_height + self.BLOCK_GAP)
        
        # Solicitação de Transferência
        c.rect(1.5*cm, y_cursor - self.SOLICITACAO_HEIGHT, self.CANVAS_WIDTH - 3*cm, self.SOLICITACAO_HEIGHT)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.CANVAS_WIDTH/2, y_cursor - 0.8*cm, "SOLICITO A TRANSFERÊNCIA DO(S) BEM(NS) ABAIXO ESPECÍFICADO")
        c.setFont("Helvetica", 9)
        
        y_transferencia = y_cursor - 2*cm
        self._draw_checkbox(c, 2*cm, y_transferencia, "TRANSFERÊNCIA TEMPORÁRIA", 'transferencia_temporaria' in self.data)
        c.drawString(2*cm, y_transferencia - 0.5*cm, f"DEVOLUÇÃO MARCADA PARA {self.data.get('devolucao_data', '')}")
        self._draw_checkbox(c, 7.8*cm, y_transferencia, "TRANSFERÊNCIA PARA CONSERTO", 'transferencia_conserto' in self.data)
        self._draw_checkbox(c, 14*cm, y_transferencia, "OUTROS MOTIVOS", 'outros_motivos' in self.data)
        # c.line(17.5*cm, y_transferencia - 0.1*cm, self.CANVAS_WIDTH - 2*cm, y_transferencia - 0.1*cm)
        
        y_transferencia -= 1.5*cm
        self._draw_checkbox(c, 2*cm, y_transferencia, "TRANSFERÊNCIA DEFINITIVA", 'transferencia_definitiva' in self.data)
        self._draw_checkbox(c, 7.8*cm, y_transferencia, "PARA BAIXA", 'para_baixa' in self.data)
        
        y_transferencia -= 0.5*cm
        self._draw_checkbox(c, 2*cm, y_transferencia, "PARA PMS POR INTERESSE", 'para_pms' in self.data)
        
        y_motivo = y_transferencia - 1.2*cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2*cm, y_motivo, "MOTIVO:")
        c.setFont("Helvetica", 9)
        self._draw_checkbox(c, 2*cm, y_motivo - 0.5*cm, "1- ALIENAÇÃO", self.data.get('motivo') == 'alienacao')
        self._draw_checkbox(c, 2*cm, y_motivo - 1*cm, "5- EXTRAVIO/FURTO", self.data.get('motivo') == 'extravio_furto')
        self._draw_checkbox(c, 7.8*cm, y_motivo - 0.5*cm, "2- ANTI-ECONÔMICO", self.data.get('motivo') == 'anti_economico')
        self._draw_checkbox(c, 7.8*cm, y_motivo - 1*cm, "6- DOAÇÃO", self.data.get('motivo') == 'doacao')
        self._draw_checkbox(c, 12*cm, y_motivo - 0.5*cm, "3- DESCARTE/IRRECUPERÁVEL/INSERVÍVEL", self.data.get('motivo') == 'descarte')
        self._draw_checkbox(c, 12*cm, y_motivo - 1*cm, "7- OUTRO (DISCRIMINAR)", self.data.get('motivo') == 'outro')
        # c.line(17.5*cm, y_motivo - 1.1*cm, self.CANVAS_WIDTH - 2*cm, y_motivo - 1.1*cm)
        y_cursor -= (self.SOLICITACAO_HEIGHT + self.BLOCK_GAP)

        # Situação do Bem
        c.rect(1.5*cm, y_cursor - self.SITUACAO_HEIGHT, self.CANVAS_WIDTH - 3*cm, self.SITUACAO_HEIGHT)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.CANVAS_WIDTH/2, y_cursor - 0.8*cm, "SITUAÇÃO DO BEM(NS)")
        c.setFont("Helvetica", 9)
        y_situacao = y_cursor - 1.5*cm
        
        situacao_bem = self.data.get('situacao_bem', '')
        self._draw_checkbox(c, 2*cm, y_situacao, "NOVO", situacao_bem == 'novo')
        self._draw_checkbox(c, 4.5*cm, y_situacao, "BOM", situacao_bem == 'bom')
        self._draw_checkbox(c, 7.5*cm, y_situacao, "REGULAR", situacao_bem == 'regular')
        self._draw_checkbox(c, 11.5*cm, y_situacao, "RUIM", situacao_bem == 'ruim')
        self._draw_checkbox(c, 14.5*cm, y_situacao, "PÉSSIMO", situacao_bem == 'pessimo')
        self._draw_checkbox(c, 17.5*cm, y_situacao, "OCIOSO", situacao_bem == 'ocioso')

        c.save()

# Example usage:
if __name__ == '__main__':
    dados = {
        'tmbp_pms': '12345',
        'ano': '2025',
        'usuario_orgao_setor': 'SECRETARIA DE EDUCAÇÃO',
        'usuario_responsavel': 'THYEZ DE OLIVEIRA',
        'usuario_matricula': '123456',
        'destino_orgao_setor': 'ESCOLA MUNICIPAL PROFESSORA MARIA DA PENHA',
        'destino_responsavel': 'MARIA DE LURDES',
        'destino_matricula': '654321',
        'transferencia_temporaria': 'on',
        'motivo': 'extravio_furto',
        'situacao_bem': 'ruim'
    }
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'TMBP', 'termo_movimentacao_teste.pdf')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    gerador = BensPatrimonioGeradorDocumento(dados, output_path)
    gerador.gerar_pdf()
    print(f"PDF gerado em: {output_path}")