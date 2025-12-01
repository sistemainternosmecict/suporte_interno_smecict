from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    registros = db.relationship('RegistroPonto', backref='usuario', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class RegistroPonto(db.Model):
    __tablename__ = 'registros_ponto'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    
    chegada = db.Column(db.Time, nullable=True)
    saida_almoco = db.Column(db.Time, nullable=True)
    retorno_almoco = db.Column(db.Time, nullable=True)
    saida = db.Column(db.Time, nullable=True)

    def __repr__(self):
        return f'<RegistroPonto {self.usuario.nome} - {self.data}>'

    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.strftime('%Y-%m-%d'),
            'chegada': self.chegada.strftime('%H:%M:%S') if self.chegada else None,
            'saida_almoco': self.saida_almoco.strftime('%H:%M:%S') if self.saida_almoco else None,
            'retorno_almoco': self.retorno_almoco.strftime('%H:%M:%S') if self.retorno_almoco else None,
            'saida': self.saida.strftime('%H:%M:%S') if self.saida else None,
        }
