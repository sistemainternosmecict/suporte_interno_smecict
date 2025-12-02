from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from garantia_gen import ChamadoGarantiaPDF
from setproctitle import setproctitle
from modulos.termo.modules.data_compiler import DataCompiler
from modulos.termo.modules.pdf_constructor import PdfConstructor
from modulos.devolucao.modules.data_compiler import DataCompiler as DevolucaoDataCompiler
from modulos.devolucao.modules.pdf_constructor import DevolucaoPdfConstructor
from modulos.relatServico.listas import unidades, bairros, distritos
from modulos.relatServico.main import Relatorio_servico_tecnico
from modulos.ponto.models import db, Usuario, RegistroPonto # Import models here for db.create_all()
from modulos.ponto.pdf_generator import PontoPdfGenerator
from modulos.ponto.models import Usuario, RegistroPonto # Import models here for db.create_all()


MODE = "dev" #troque isso para produção

setproctitle("[SERVIDOR_interno]")

app = Flask(__name__, static_url_path="/suporte/static" if MODE == "prod" else "/static")
CORS(app)

# Configuração do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ponto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all() # Cria as tabelas se não existirem
    print("Database initialized.")

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
                           link_url_relatorio_servicos=link_url_relatorio_servicos,
                           link_url_ponto="/suporte/ponto" if MODE == "prod" else "/ponto"
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

# Rotas do Módulo Ponto
@app.route("/ponto")
def ponto_page():
    users = Usuario.query.all()
    # Adicionar o prefixo '/suporte' se estiver em modo de produção
    base_url_for_ponto = "/suporte/ponto" if MODE == "prod" else "/ponto"
    return render_template("ponto.html", usuarios=users, now=datetime.now(), mode=MODE, base_url_for_ponto=base_url_for_ponto)

@app.route("/ponto/cadastrar_usuario", methods=["POST"])
def ponto_cadastrar_usuario():
    data = request.get_json()
    nome = data.get("nome")
    if not nome:
        return jsonify({"success": False, "error": "Nome do usuário é obrigatório"}), 400
    
    # Verifica se o usuário já existe
    if Usuario.query.filter_by(nome=nome).first():
        return jsonify({"success": False, "error": "Usuário já existe"}), 409

    try:
        new_user = Usuario(nome=nome)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True, "user": {"id": new_user.id, "nome": new_user.nome}})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao cadastrar usuário: {e}")
        return jsonify({"success": False, "error": "Erro interno ao cadastrar usuário"}), 500

@app.route("/ponto/registrar", methods=["POST"])
def ponto_registrar():
    data = request.get_json()
    usuario_id = data.get("usuario_id")
    action = data.get("action")
    
    if not usuario_id or not action:
        return jsonify({"success": False, "error": "Usuário e ação são obrigatórios"}), 400
    
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"success": False, "error": "Usuário não encontrado"}), 404

    today = datetime.now().date()
    current_time = datetime.now().time()

    registro = RegistroPonto.query.filter_by(usuario_id=usuario_id, data=today).first()

    if not registro:
        registro = RegistroPonto(usuario_id=usuario_id, data=today)
        db.session.add(registro)

    try:
        if action == "chegada":
            if registro.chegada:
                return jsonify({"success": False, "error": "Chegada já registrada"}), 409
            registro.chegada = current_time
        elif action == "saida_almoco":
            if not registro.chegada:
                return jsonify({"success": False, "error": "Primeiro registre a chegada"}), 400
            if registro.saida_almoco:
                return jsonify({"success": False, "error": "Saída para almoço já registrada"}), 409
            registro.saida_almoco = current_time
        elif action == "retorno_almoco":
            if not registro.saida_almoco:
                return jsonify({"success": False, "error": "Primeiro registre a saída para almoço"}), 400
            if registro.retorno_almoco:
                return jsonify({"success": False, "error": "Retorno do almoço já registrado"}), 409
            registro.retorno_almoco = current_time
        elif action == "saida":
            if not registro.retorno_almoco:
                return jsonify({"success": False, "error": "Primeiro registre o retorno do almoço"}), 400
            if registro.saida:
                return jsonify({"success": False, "error": "Saída já registrada"}), 409
            registro.saida = current_time
        else:
            return jsonify({"success": False, "error": "Ação inválida"}), 400

        db.session.commit()
        return jsonify({"success": True, "registros": registro.to_dict()})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar ponto: {e}")
        return jsonify({"success": False, "error": "Erro interno ao registrar ponto"}), 500

@app.route("/ponto/registros_dia", methods=["GET"])
def ponto_registros_dia():
    usuario_id = request.args.get("usuario_id")
    date_str = request.args.get("data") # YYYY-MM-DD
    
    if not usuario_id or not date_str:
        return jsonify({"success": False, "error": "ID do usuário e data são obrigatórios"}), 400

    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"success": False, "error": "Formato de data inválido. Use YYYY-MM-DD"}), 400

    registro = RegistroPonto.query.filter_by(usuario_id=usuario_id, data=query_date).first()

    if registro:
        return jsonify({"success": True, "registros": registro.to_dict()})
    else:
        return jsonify({"success": True, "registros": {}}) # Retorna vazio se não houver registro para o dia

@app.route("/ponto/gerar_pdf", methods=["POST"])
def ponto_gerar_pdf():
    usuario_id = request.form.get("usuario_id")
    mes = request.form.get("mes")
    ano = request.form.get("ano")

    if not usuario_id or not mes or not ano:
        return "Dados incompletos para gerar o PDF.", 400

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return "Usuário não encontrado.", 404

    try:
        mes = int(mes)
        ano = int(ano)
    except ValueError:
        return "Mês ou ano inválido.", 400

    from sqlalchemy import extract
    registros = RegistroPonto.query.filter(
        RegistroPonto.usuario_id == usuario_id,
        extract('month', RegistroPonto.data) == mes,
        extract('year', RegistroPonto.data) == ano
    ).order_by(RegistroPonto.data).all()

    pdf_generator = PontoPdfGenerator(usuario, mes, ano, registros)
    if pdf_generator.gerado["gerado"]:
        base_prefix = "/suporte" if MODE == "prod" else ""
        return redirect(base_prefix + url_for("baixar_ponto_relatorio", filename=pdf_generator.gerado["path"]))
    else:
        return "Erro ao gerar o relatório de ponto.", 500

@app.route("/ponto/relatorios/<path:filename>")
@app.route("/suporte/ponto/relatorios/<path:filename>")
def baixar_ponto_relatorio(filename):
    directory = os.path.join(app.static_folder, 'ponto_relatorios')
    return send_from_directory(
        directory=directory,
        path=filename,
        as_attachment=True
    )

@app.route("/gerar_termo_chromebook", methods=["POST"])
def gerar_termo_chromebook():
    data = request.form.to_dict()

    data_comp = DataCompiler()
    data_comp.set_data(data)
    data_from_compiler = data_comp.define_first_paragraph()
    pdf_con = PdfConstructor(data_from_compiler, "Termo de responsabilidade", data_comp.get_data())
    
    base_prefix = "/suporte" if MODE == "prod" else ""
    if pdf_con.gerado["gerado"]:
        return redirect(base_prefix + url_for("baixar_termo", filename=pdf_con.gerado["path"]))

@app.route("/gerar_termo_devolucao", methods=["POST"])
def gerar_termo_devolucao():
    data = request.form.to_dict()
    data_comp = DevolucaoDataCompiler()
    data_comp.set_data(data)

    if isinstance(data_comp.get_data(), str):
        return "Erro: Dados inválidos.", 400

    pdf_con = DevolucaoPdfConstructor(data_comp.get_data())
    
    base_prefix = "/suporte" if MODE == "prod" else ""
    if pdf_con.gerado["gerado"]:
        return redirect(base_prefix + url_for("baixar_termo", filename=pdf_con.gerado["path"]))
    else:
        return "Erro ao gerar o PDF de devolução.", 500

@app.route("/obter_termo/<path:filename>")
@app.route("/suporte/obter_termo/<path:filename>")
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
