from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm


class ChamadoGarantiaPDF:
    def __init__(self, dados, imagem1=None, imagem2=None, output_file="chamado_garantia.pdf"):
        """
        :param dados: dicionário com os campos do chamado
        :param imagem1: caminho da primeira imagem
        :param imagem2: caminho da segunda imagem
        :param output_file: nome do arquivo PDF de saída
        """
        self.dados = dados
        self.imagem1 = imagem1
        self.imagem2 = imagem2
        self.output_file = output_file

    def gerar_pdf(self):
        doc = SimpleDocTemplate(self.output_file, pagesize=A4,
                                rightMargin=1*cm, leftMargin=1*cm,
                                topMargin=1*cm, bottomMargin=1*cm)

        styles = getSampleStyleSheet()

        doc.title = f"Garantia Daten - Serial {self.dados["numero_serie"]}"
        doc.author = "SMECICT"
        doc.subject = f"Documento de Garantia - {self.dados["defeito"]}"
        doc.creator = "Sistema Garantia Daten"
        doc.keywords = ["garantia", "daten", self.dados["numero_serie"]]

        story = []

        # Cabeçalho
        cabecalho = [["Abertura de chamado"]]
        tabela_cabecalho = Table(cabecalho, colWidths=[19*cm])
        tabela_cabecalho.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#cfe2f3")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(tabela_cabecalho)
        story.append(Spacer(1, 12))

        # Conteúdo em formato de tabela
        data = [
            ["Número de série do equipamento:", self.dados.get("numero_serie", "")],
            ["Cliente:", self.dados.get("cliente", "")],
            ["PIB: (Patrimônio)", self.dados.get("pib", "")],
            ["Chamado Interno (Número):", self.dados.get("chamado_interno", "")],
            ["Nome do operador:", self.dados.get("operador", "")],
            ["Telefone do operador:", self.dados.get("telefone_operador", "")],
            ["E-mail do operador:", self.dados.get("email_operador", "")],
            ["Local do atendimento", ""],
            ["Rua:", self.dados.get("rua", "")],
            ["Número:", self.dados.get("numero", "")],
            ["Departamento, sala ou setor:", self.dados.get("departamento", "")],
            ["Bairro:", self.dados.get("bairro", "")],
            ["CEP:", self.dados.get("cep", "")],
            ["Cidade:", self.dados.get("cidade", "")],
            ["Estado:", self.dados.get("estado", "")],
            ["Nome do usuário:", self.dados.get("usuario", "")],
            ["Telefone do usuário:", self.dados.get("telefone_usuario", "")],
            ["E-mail do usuário:", self.dados.get("email_usuario", "")],
            ["Horário de funcionamento:", self.dados.get("horario", "")],
            ["Intervalo para almoço:", self.dados.get("almoco", "")],
            ["Defeito do equipamento:", self.dados.get("defeito", "")]
        ]

        tabela = Table(data, colWidths=[7*cm, 12*cm])
        tabela.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 7), (1, 7), colors.HexColor("#d9d9d9")),  # Local do atendimento
        ]))

        # Destaque do número de série e defeito em vermelho
        tabela.setStyle(TableStyle([
            ("TEXTCOLOR", (1, 0), (1, 0), colors.red),   # Número de série
            ("TEXTCOLOR", (1, -1), (1, -1), colors.red), # Defeito do equipamento
        ]))

        story.append(tabela)

        # Página de imagens
        # if self.imagem1 or self.imagem2:
        #     # story.append(PageBreak())
        #     if self.imagem1:
        #         img1 = Image(self.imagem1, width=14*cm, height=10*cm)
        #         img1.hAlign = "CENTER"
        #         story.append(img1)
        #         story.append(Spacer(1, 12))
        #     if self.imagem2:
        #         img2 = Image(self.imagem2, width=14*cm, height=10*cm)
        #         img2.hAlign = "CENTER"
        #         story.append(img2)

        story.append(Spacer(1, 12))

        if self.imagem1 or self.imagem2:
            if self.imagem1 and self.imagem2:
                # Duas imagens lado a lado
                img1 = Image(self.imagem1, width=8.5*cm, height=6.5*cm)
                img2 = Image(self.imagem2, width=8.5*cm, height=6.5*cm)
                
                images_table = Table([[img1, img2]], colWidths=[9.5*cm, 9.5*cm])
                images_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(images_table)
            else:
                # Uma imagem só - centralizada e maior
                if self.imagem1:
                    img1 = Image(self.imagem1, width=14*cm, height=10*cm)
                    img1.hAlign = "CENTER"
                    story.append(img1)
                if self.imagem2:
                    img2 = Image(self.imagem2, width=14*cm, height=10*cm)
                    img2.hAlign = "CENTER"
                    story.append(img2)
            
            story.append(Spacer(1, 12))

        doc.build(story)
        print(f"PDF gerado com sucesso em: {self.output_file}")