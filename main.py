from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from garantia_gen import ChamadoGarantiaPDF
from setproctitle import setproctitle
from modulos.termo.modules.data_compiler import DataCompiler
from modulos.termo.modules.pdf_constructor import PdfConstructor
from modulos.relatServico.listas import unidades, bairros, distritos
from modulos.relatServico.main import Relatorio_servico_tecnico

MODE = "dev" #troque isso para produção

setproctitle("[SERVIDOR_interno]")

app = Flask(__name__, static_url_path="/suporte/static" if MODE == "prod" else "/static")
CORS(app)

# Configurações
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Criar pasta uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    css_url = url_for("static", filename="style.css")
    link_url_garantia_daten = "/suporte/garantia_daten" if MODE == "prod" else "/garantia_daten"
    link_url_termo_chromebooks = "/suporte/termo_chromebooks" if MODE == "prod" else "/termo_chromebooks"
    link_url_relatorio_servicos = "/suporte/relatorio_servicos" if MODE == "prod" else "/relatorio_servicos"
    return render_template("menu.html", 
                           css_url=css_url, 
                           link_url_garantia_daten=link_url_garantia_daten, 
                           link_url_termo_chromebooks=link_url_termo_chromebooks,
                           link_url_relatorio_servicos=link_url_relatorio_servicos
                           )

@app.route('/garantia_daten', methods=['GET'])
def garantia_daten():
    uploads_folder = 'static/uploads'
    pdf_files = []
    
    if os.path.exists(uploads_folder):
        files = os.listdir(uploads_folder)
        
        # Filtra apenas arquivos PDF
        pdf_files = [
            {
                'filename': file,
                'url': url_for('static', filename=f'uploads/{file}'),
                'link':f"/daten/{file}"
                # ou se você tiver uma rota específica para servir arquivos:
                # 'url': url_for('download_file', filename=file)
            }
            for file in files 
            if file.lower().endswith('.pdf')
        ]
    return render_template("index.html", mode=MODE, pdf_files=enumerate(pdf_files), pdf_files_len=len(pdf_files))

@app.route("/termo_chromebooks")
def termo_chromebooks():
    return render_template("form_termo_chromebooks.html", mode=MODE)

@app.route("/relatorio_servicos")
def relatorio_servicos():
    return render_template("relatorioServico.html", unidades=unidades, bairros=bairros, distritos=distritos, mode=MODE)

@app.route("/gerar_termo_chromebook", methods=["POST"])
def gerar_termo_chromebook():
    data = request.form.to_dict()

    data_comp = DataCompiler()
    data_comp.set_data(data)
    data_from_compiler = data_comp.define_first_paragraph()
    pdf_con = PdfConstructor(data_from_compiler, "Termo de responsabilidade", data_comp.get_data())
    if pdf_con.gerado["gerado"]:
        return redirect(url_for("baixar_termo", filename=pdf_con.gerado["path"]))

@app.route("/obter_termo/<path:filename>")
def baixar_termo(filename):
    return send_from_directory(
        os.path.join(app.static_folder, "termos"),
        filename,
        as_attachment=True
    )

@app.route('/upload', methods=['POST'])
def upload_image():
    if request.method == "POST":
        numero_serial = request.form['serial']
        problema_relatado = request.form['problema']
        imagem_1 = request.files['imagem_1']
        imagem_2 = request.files['imagem_2']

        original_filename_1 = secure_filename(imagem_1.filename)
        extensao_1 = os.path.splitext(original_filename_1)[1]
        new_filename_1 = f"{numero_serial}_img1{extensao_1}"
        filepath_1 = os.path.join(UPLOAD_FOLDER, new_filename_1)
        imagem_1.save(filepath_1)

        original_filename_2 = secure_filename(imagem_2.filename)
        extensao_2 = os.path.splitext(original_filename_2)[1]
        new_filename_2 = f"{numero_serial}_img2{extensao_2}"
        filepath_2 = os.path.join(UPLOAD_FOLDER, new_filename_2)
        imagem_2.save(filepath_2)

        dados_chamado = {
            "numero_serie": numero_serial,
            "cliente": "SMECICT",
            "pib": "",
            "chamado_interno": "",
            "operador": "Angel Daumas Pereira Lopez",
            "telefone_operador": "(22)98844-2429",
            "email_operador": "angeldaumaslopez@smec.saquarema.rj.gov.br",
            "rua": "Avenida Saquarema",
            "numero": "4299",
            "departamento": "TI - Sala 25",
            "bairro": "Bacaxá",
            "cep": "28991-350",
            "cidade": "Saquarema",
            "estado": "Rio de Janeiro",
            "usuario": "Angel Daumas Pereira Lopez",
            "telefone_usuario": "(22)98844-2429",
            "email_usuario": "angeldaumaslopez@smec.saquarema.rj.gov.br",
            "horario": "9h - 17h",
            "almoco": "12h - 13h",
            "defeito": problema_relatado
        }

        pdf_filename = f"SN-{numero_serial}_pedido_{datetime.now().strftime('%d-%m-%Y')}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)

        chamado_pdf = ChamadoGarantiaPDF(
                dados=dados_chamado,
                imagem1=filepath_1,
                imagem2=filepath_2,
                output_file=pdf_path
            )
        chamado_pdf.gerar_pdf()

        base_prefix = "/suporte" if MODE == "prod" else ""
        return redirect(base_prefix + url_for("garantia_daten"))

@app.route('/remover_garantia/<path:filename>', methods=['DELETE'])
def remover_garantia(filename):
    # Prevenção contra Directory Traversal
    if '..' in filename or filename.startswith('/'):
        return jsonify({'success': False, 'error': 'Nome de arquivo inválido'}), 400
    
    try:
        pdf_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Arquivo não encontrado'}), 404
    except Exception as e:
        print(f"Erro ao remover o arquivo {filename}: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@app.route("/gerar_relatorio_servico", methods=["POST"])
def gerar_relatorio_servico():
    data = request.form.to_dict(flat=False)

    data = {
        k: v if len(v) > 1 else v[0]
        for k, v in request.form.lists()
    }

    rs = Relatorio_servico_tecnico(data)
    filename = rs.salvar()
    print("PATH > ", filename)

    base_prefix = "/suporte" if MODE == "prod" else ""
    return redirect(f"{base_prefix}/acessar_relatorio/{filename}")

@app.route("/acessar_relatorio/<filename>")
def acessar_relatorio(filename):
    directory = os.path.join(app.static_folder, 'export_relatorio')
    return send_from_directory(
        directory=directory,
        path=filename,
        as_attachment=False  # False = abre no navegador (se for PDF), True = força download
    )

if __name__ == '__main__':
    app.run(port=5001) if MODE == "prod" else app.run(host="0.0.0.0", debug=True, port=5001)
