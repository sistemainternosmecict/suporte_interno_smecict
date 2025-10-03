from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os, sys

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class Relatorio_servico_tecnico:
    image_path = resource_path("header.png")
    footer = resource_path("footer.png")
    PAGE_WIDTH, PAGE_HEIGHT = A4
    LEFT_MARGIN = 40
    RIGHT_MARGIN = PAGE_WIDTH - 40
    current_y = PAGE_HEIGHT - 110

    header_image = ImageReader(image_path)
    img_width = PAGE_WIDTH
    img_original_width, img_original_height = header_image.getSize()
    aspect = img_original_height / img_original_width
    img_height = img_width * aspect

    def __init__(self, dados):
        self.filename = f"Relatório de Serviço Técnico - {dados['protocolo']}.pdf"
        self.export_dir = os.path.join(os.getcwd(), "export_relatorio")
        self.definir_diretorio_exportacao(self.export_dir)
        self.c = canvas.Canvas(self.pdf_path, pagesize=A4)
        self.c.drawImage(
            self.header_image,
            0,                          # x: início da imagem à esquerda
            self.PAGE_HEIGHT - self.img_height,  # y: topo da página menos altura da imagem
            width=self.img_width,
            height=self.img_height,
            preserveAspectRatio=True,
            mask='auto'
        )

        self.escrever_dados(dados)

    def definir_diretorio_exportacao(self, dir):
        dir = os.path.join(dir, self.filename)
        self.pdf_path = dir

    def escrever_dados(self, dados):
        c = self.c

        c.setTitle(f"Relatório de Serviço Técnico - {dados['protocolo']}")

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y, "RELATÓRIO DE SERVIÇO TÉCNICO")
        
        self.inserir_protocolo_ao_lado(dados['protocolo'], self.current_y)
        self.current_y -= 35

        # Seção: Informações da Unidade (fundo cinza)
        c.setFillColor(colors.grey)
        c.rect(self.LEFT_MARGIN, self.current_y - 5, self.RIGHT_MARGIN - self.LEFT_MARGIN, 12, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y - 2, "Informações da Unidade")
        self.current_y -= 20

        # Campo: Unidade Escola
        c.setFont("Helvetica", 10)
        c.drawString(self.LEFT_MARGIN, self.current_y, "Unidade Escolar:")

        c.drawString(self.LEFT_MARGIN + 85, self.current_y, dados['unidade_escolar'])
        c.line(self.LEFT_MARGIN + 85, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)
        self.current_y -= 20

        # Campo: Bairro / Distrito / CEP
        c.drawString(self.LEFT_MARGIN, self.current_y, "Bairro:")
        c.drawString(self.LEFT_MARGIN + 38, self.current_y, dados['unidade_bairro'])
        c.line(self.LEFT_MARGIN + 38, self.current_y - 2, self.LEFT_MARGIN + 200, self.current_y - 2)

        c.drawString(self.LEFT_MARGIN + 210, self.current_y, "Distrito:")
        c.drawString(self.LEFT_MARGIN + 250, self.current_y, dados['unidade_distrito'])
        c.line(self.LEFT_MARGIN + 250, self.current_y - 2, self.LEFT_MARGIN + 370, self.current_y - 2)

        c.drawString(self.LEFT_MARGIN + 390, self.current_y, "CEP.:")
        c.drawString(self.LEFT_MARGIN + 430, self.current_y, dados['unidade_cep'])
        c.line(self.LEFT_MARGIN + 430, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)
        self.current_y -= 25

        # Seção: Dados do Solicitante (fundo cinza)
        self.current_y -= -5
        c.setFillColor(colors.grey)
        c.rect(self.LEFT_MARGIN, self.current_y - 5, self.RIGHT_MARGIN - self.LEFT_MARGIN, 12, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y - 2, "Dados do Solicitante")
        self.current_y -= 20

        # Campo: Nome do solicitante
        c.setFont("Helvetica", 10)
        c.drawString(self.LEFT_MARGIN, self.current_y, "Nome do solicitante:")
        c.drawString(self.LEFT_MARGIN + 95, self.current_y, dados['solicitante_nome'])
        c.line(self.LEFT_MARGIN + 95, self.current_y - 2, self.LEFT_MARGIN + 295, self.current_y - 2)
        c.drawString(self.LEFT_MARGIN + 300, self.current_y, "Cargo:")
        c.line(self.LEFT_MARGIN + 335, self.current_y - 2, self.LEFT_MARGIN + 435, self.current_y - 2)
        c.drawString(self.LEFT_MARGIN + 335, self.current_y, dados['solicitante_cargo'])
        c.drawString(self.LEFT_MARGIN + 440, self.current_y, "Mat:")
        c.line(self.LEFT_MARGIN + 460, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)
        c.drawString(self.LEFT_MARGIN + 460, self.current_y, dados['solicitante_matricula'])
        self.current_y -= 20

        # Campo: Cargo / Matrícula / Telefone
        c.drawString(self.LEFT_MARGIN, self.current_y, "Horário do chamado:")
        c.drawString(self.LEFT_MARGIN + 100, self.current_y, dados['horario_chamado'])
        c.line(self.LEFT_MARGIN + 100, self.current_y - 2, self.LEFT_MARGIN + 200, self.current_y - 2)

        c.drawString(self.LEFT_MARGIN + 220, self.current_y, "Data:")
        c.drawString(self.LEFT_MARGIN + 255, self.current_y, dados['data_chamado'])
        c.line(self.LEFT_MARGIN + 255, self.current_y - 2, self.LEFT_MARGIN + 320, self.current_y - 2)

        c.drawString(self.LEFT_MARGIN + 340, self.current_y, "Telefone:")
        c.drawString(self.LEFT_MARGIN + 395, self.current_y, dados['solicitante_telefone'])
        c.line(self.LEFT_MARGIN + 395, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)

        print(f"PDF gerado em: {self.pdf_path}")
    
    def escrever_dados_tecnico(self, dados_tecnico):
        c = self.c

        self.current_y -= 25
        self.current_y -= -5
        # Seção: Dados do Técnico
        c.setFillColor(colors.grey)
        c.rect(self.LEFT_MARGIN, self.current_y - 5, self.RIGHT_MARGIN - self.LEFT_MARGIN, 12, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y - 2, "Dados do Técnico")
        self.current_y -= 20

        c.setFont("Helvetica", 10)
        c.drawString(self.LEFT_MARGIN, self.current_y, "Nome do Técnico:")
        c.drawString(self.LEFT_MARGIN + 85, self.current_y, dados_tecnico['nome_tecnico'])
        c.line(self.LEFT_MARGIN + 85, self.current_y - 2, self.LEFT_MARGIN + 295, self.current_y - 2)
        c.drawString(self.LEFT_MARGIN + 300, self.current_y, "Cargo:")
        c.line(self.LEFT_MARGIN + 335, self.current_y - 2, self.LEFT_MARGIN + 435, self.current_y - 2)
        c.drawString(self.LEFT_MARGIN + 335, self.current_y, dados_tecnico['tecnico_cargo'])
        c.drawString(self.LEFT_MARGIN + 440, self.current_y, "Mat:")
        c.line(self.LEFT_MARGIN + 460, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)
        c.drawString(self.LEFT_MARGIN + 460, self.current_y, dados_tecnico['tecnico_matricula'])
        self.current_y -= 20

        c.drawString(self.LEFT_MARGIN, self.current_y, "Horário de Atendimento:")
        c.drawString(self.LEFT_MARGIN + 120, self.current_y, dados_tecnico['horario_atendimento'])
        c.line(self.LEFT_MARGIN + 120, self.current_y - 2, self.LEFT_MARGIN + 200, self.current_y - 2)

        c.drawString(self.LEFT_MARGIN + 220, self.current_y, "Data:")
        c.drawString(self.LEFT_MARGIN + 255, self.current_y, dados_tecnico['data'])
        c.line(self.LEFT_MARGIN + 255, self.current_y - 2, self.LEFT_MARGIN + 320, self.current_y - 2)

        c.drawString(self.LEFT_MARGIN + 340, self.current_y, "Telefone:")
        c.drawString(self.LEFT_MARGIN + 395, self.current_y, dados_tecnico['telefone'])
        c.line(self.LEFT_MARGIN + 395, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)
        self.current_y -= 25

        # Seção: Causas ou Problemas Técnicos Relacionados
        self.current_y -= -5
        c.setFillColor(colors.grey)
        c.rect(self.LEFT_MARGIN, self.current_y - 5, self.RIGHT_MARGIN - self.LEFT_MARGIN, 12, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y - 2, "Causas ou Problemas Técnicos Relacionados")
        self.current_y -= 20

        c.setFont("Helvetica", 11)
        causas = [
            "Computador não liga", "Monitor não liga ou piscando", "Mouse ou teclado com defeito", "Cabos com defeito", "Configuração de sistema",
            "Entrega de equipamentos", "Substituição de equipamentos", "Manutenção de equipamentos", "Garantia de equipamentos", "Vistoria de equipamentos",
            "Remoção de equipamentos", "Rede e Internet", "Backup de arquivos", "Avaliação de Carência", "Outro"
        ]

        # Quebra as causas em 3 colunas
        col_x = [self.LEFT_MARGIN, self.LEFT_MARGIN + 180, self.LEFT_MARGIN + 360]
        line_height = 16
        itens_por_coluna = 5

        for i, causa in enumerate(causas):
            col = i // itens_por_coluna
            row = i % itens_por_coluna
            x = col_x[col]
            y = self.current_y - (row * line_height)
            marcado = "x" if causa in dados_tecnico['causas_marcadas'] else " "
            if causa == "Outro":
                outro_valor = dados_tecnico.get('causa_outro', "")
                causa += f": {outro_valor}"
            c.drawString(x, y, f"(  {marcado}  ) {causa}", None, -0.5)

        self.current_y -= (itens_por_coluna * line_height + 20)
    
    def escrever_procedimentos_observacoes_avaliacao(self, dados_final):
        c = self.c

        self.current_y -= -10
        # Seção: Procedimentos Realizados
        c.setFillColor(colors.grey)
        c.rect(self.LEFT_MARGIN, self.current_y - 5, self.RIGHT_MARGIN - self.LEFT_MARGIN, 12, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y - 2, "Procedimentos Realizados")
        self.current_y -= 20

        c.setFont("Helvetica", 9)
        linhas_procedimentos = dados_final.get("procedimentos_realizados", ["", "", ""])
        for linha in linhas_procedimentos:
            c.drawString(self.LEFT_MARGIN, self.current_y, linha)
            c.line(self.LEFT_MARGIN, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)
            self.current_y -= 20

        # Seção: Observações
        c.setFillColor(colors.grey)
        c.rect(self.LEFT_MARGIN, self.current_y - 5, self.RIGHT_MARGIN - self.LEFT_MARGIN, 12, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y - 2, "Observações")
        self.current_y -= 20

        c.setFont("Helvetica", 9)
        linhas_observacoes = dados_final.get("observacoes", ["", "", ""])
        for linha in linhas_observacoes:
            c.drawString(self.LEFT_MARGIN, self.current_y, linha)
            c.line(self.LEFT_MARGIN, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)
            self.current_y -= 20

        # Seção: Avaliação do Atendimento
        c.setFillColor(colors.grey)
        c.rect(self.LEFT_MARGIN, self.current_y - 5, self.RIGHT_MARGIN - self.LEFT_MARGIN, 12, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y - 2, "Avaliação do Atendimento")
        self.current_y -= 20

        c.setFont("Helvetica", 9)

        opcoes = ["Ótimo", "Bom", "Regular", "Ruim"]
        avaliacao = dados_final.get("avaliacao", "")
        obs_avaliacao = dados_final.get("obs_avaliacao", "")
        x_pos = self.LEFT_MARGIN
        for opcao in opcoes:
            marcado = "X" if opcao.lower() == avaliacao.lower() else " "
            c.drawString(x_pos, self.current_y, f"( {marcado} ) {opcao}")
            x_pos += 70

        c.drawString(x_pos + 10, self.current_y, "Obs.:")
        c.drawString(x_pos + 45, self.current_y, obs_avaliacao)
        c.line(x_pos + 45, self.current_y - 2, self.RIGHT_MARGIN, self.current_y - 2)

        self.current_y -= 25

    def escrever_assinaturas_e_rodape(self):
        c = self.c

        # Seção: Aceite do Serviço Técnico
        self.current_y -= -5
        c.setFillColor(colors.grey)
        c.rect(self.LEFT_MARGIN, self.current_y - 5, self.RIGHT_MARGIN - self.LEFT_MARGIN, 12, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.PAGE_WIDTH / 2, self.current_y - 2, "Aceite do Serviço Técnico")
        self.current_y -= 55

        # Linhas de assinatura
        c.setFont("Helvetica", 9)
        linha_y = self.current_y

        # Linhas
        largura_linha = 180
        espacamento = 80
        c.line(self.LEFT_MARGIN, linha_y, self.LEFT_MARGIN + largura_linha, linha_y)
        c.line(self.RIGHT_MARGIN - largura_linha, linha_y, self.RIGHT_MARGIN, linha_y)

        # Legendas
        c.drawCentredString(self.LEFT_MARGIN + largura_linha / 2, linha_y - 12, "Responsável Técnico")
        c.drawCentredString(self.RIGHT_MARGIN - largura_linha / 2, linha_y - 12, "Gestor da Unidade Escolar")

        self.current_y = linha_y - 50

        # Inserção do rodapé com imagem
        from reportlab.platypus import Image

        try:
            imagem = Image(self.footer)
            largura_imagem = self.PAGE_WIDTH
            altura_imagem = 60  # ajuste se necessário

            c.drawImage(self.footer, -1, 0, width=largura_imagem + 1, height=altura_imagem)
        except Exception as e:
            print("Erro ao inserir imagem de rodapé:", e)

    def inserir_protocolo_ao_lado(self, protocolo, altura_titulo):
        if not protocolo:
            return

        c = self.c

        texto_inicial = "Ordem de Serviço/Protocolo nº "
        fonte_normal = "Helvetica"
        fonte_negrito = "Helvetica-Bold"
        tamanho_fonte = 10

        c.setFont(fonte_normal, tamanho_fonte)
        largura_inicial = c.stringWidth(texto_inicial, fonte_normal, tamanho_fonte)
        largura_protocolo = c.stringWidth(protocolo, fonte_negrito, tamanho_fonte)
        largura_total = largura_inicial + largura_protocolo

        # Calcula o ponto inicial para centralizar as duas partes
        x_inicio = (self.PAGE_WIDTH - largura_total) / 2
        y = altura_titulo - 15

        # Desenha parte normal
        c.setFont(fonte_normal, tamanho_fonte)
        c.drawString(x_inicio, y, texto_inicial)

        # Desenha número do protocolo em negrito
        c.setFont(fonte_negrito, tamanho_fonte)
        c.drawString(x_inicio + largura_inicial, y, protocolo)

    def salvar(self):
        self.c.save()