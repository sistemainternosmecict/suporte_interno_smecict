from flask import Flask, request, render_template, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from garantia_gen import ChamadoGarantiaPDF

app = Flask(__name__)
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
    return """

  <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Sumário de serviços</title>
    </head>
    <body>
        <h1>Sumário de serviços</h1>
        <a href="/garantia_daten">Gerador - Garantia Daten</a>
    </body>
    </html>
""";

@app.route('/garantia_daten', methods=['GET'])
def garantia_daten():
    # Caminho para a pasta uploads
    uploads_folder = 'static/uploads'
    pdf_files = []
    
    # Verifica se a pasta existe
    if os.path.exists(uploads_folder):
        # Lista todos os arquivos na pasta
        files = os.listdir(uploads_folder)
        
        # Filtra apenas arquivos PDF
        pdf_files = [
            {
                'filename': file,
                'url': url_for('static', filename=f'uploads/{file}')
                # ou se você tiver uma rota específica para servir arquivos:
                # 'url': url_for('download_file', filename=file)
            }
            for file in files 
            if file.lower().endswith('.pdf')
        ]
    return render_template("index.html", pdf_files=enumerate(pdf_files), pdf_files_len=len(pdf_files))

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

        return redirect(url_for("garantia_daten"))
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
