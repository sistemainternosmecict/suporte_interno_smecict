from flask import Blueprint, render_template, request, redirect, url_for, flash
from .model import Session, Registro, engine, Base
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE")

lista_prof_chrome_bp = Blueprint('lista_prof_chrome_bp', __name__, template_folder='templates')

@lista_prof_chrome_bp.route('/lista-prof-chrome')
def lista_prof_chrome():
    session = Session()
    registros = session.query(Registro).all()
    mode = "/suporte" if MODE == "prod" else ""
    return render_template('lista_prof_chrome.html', registros=registros, mode=mode)

@lista_prof_chrome_bp.route('/lista-prof-chrome/add', methods=['POST'])
def add_registro():
    session = Session()
    try:
        nome = request.form['nome']
        cpf = request.form['cpf']
        matricula = request.form['matricula']
        telefone = request.form['telefone']
        obs = request.form.get('obs', '')
        unidade = request.form['unidade']
        assinado = 'assinado' in request.form
        validado = 'validado' in request.form
        declaracao = 'declaracao' in request.form
        em_posse = 'em_posse' in request.form
        devolvido = 'devolvido' in request.form

        novo_registro = Registro(
            nome=nome, cpf=cpf, matricula=matricula, telefone=telefone,
            obs=obs, unidade=unidade, assinado=assinado, validado=validado,
            declaracao=declaracao, em_posse=em_posse, devolvido=devolvido
        )
        session.add(novo_registro)
        session.commit()
        flash('Registro adicionado com sucesso!', 'success')
    except IntegrityError:
        session.rollback()
        flash('Erro: CPF ou Matrícula já existentes.', 'danger')
    except Exception as e:
        session.rollback()
        flash(f'Erro ao adicionar registro: {e}', 'danger')
    finally:
        session.close()
    mode = "/suporte" if MODE == "prod" else ""
    return redirect(f"{mode}/lista-prof-chrome")

@lista_prof_chrome_bp.route('/lista-prof-chrome/update/<int:registro_id>', methods=['POST'])
def update_registro(registro_id):
    session = Session()
    try:
        registro = session.query(Registro).get(registro_id)
        if registro:
            registro.nome = request.form['nome']
            registro.cpf = request.form['cpf']
            registro.matricula = request.form['matricula']
            registro.telefone = request.form['telefone']
            registro.obs = request.form.get('obs', '')
            registro.unidade = request.form['unidade']
            registro.assinado = 'assinado' in request.form
            registro.validado = 'validado' in request.form
            registro.declaracao = 'declaracao' in request.form
            registro.em_posse = 'em_posse' in request.form
            registro.devolvido = 'devolvido' in request.form
            session.commit()
            flash('Registro atualizado com sucesso!', 'success')
        else:
            flash('Registro não encontrado.', 'danger')
    except Exception as e:
        session.rollback()
        flash(f'Erro ao atualizar registro: {e}', 'danger')
    finally:
        session.close()
    return redirect(url_for('lista_prof_chrome_bp.lista_prof_chrome'))

@lista_prof_chrome_bp.route('/lista-prof-chrome/delete/<int:registro_id>', methods=['POST'])
def delete_registro(registro_id):
    session = Session()
    try:
        registro = session.query(Registro).get(registro_id)
        if registro:
            session.delete(registro)
            session.commit()
            flash('Registro excluído com sucesso!', 'success')
        else:
            flash('Registro não encontrado.', 'danger')
    except Exception as e:
        session.rollback()
        flash(f'Erro ao excluir registro: {e}', 'danger')
    finally:
        session.close()
    return redirect(url_for('lista_prof_chrome_bp.lista_prof_chrome'))

# Initialize the database within the blueprint context if not already done
@lista_prof_chrome_bp.before_app_request
def create_tables():
    # Only create tables if running as main app, not in test or other contexts
    # This might need adjustment based on how the main app manages its DB.
    Base.metadata.create_all(engine)
    print("Database for lista_prof_chrome initialized.")
