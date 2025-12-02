from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# Configuração do banco de dados
engine = create_engine("sqlite:///instance/lista_profe_chrome.db", echo=True)
Session = sessionmaker(bind=engine)


class Registro(Base):
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(Integer, nullable=False)
    matricula = Column(Integer, nullable=False)
    telefone = Column(Integer, nullable=False)
    obs = Column(String)
    unidade = Column(String)
    assinado = Column(Boolean)
    validado = Column(Boolean)
    declaracao = Column(Boolean, default=False)
    em_posse = Column(Boolean, default=False)      # Novo campo: professor está em posse
    devolvido = Column(Boolean, default=False)     # Novo campo: professor devolveu
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self):
        self.session = Session()
        Base.metadata.create_all(engine)
