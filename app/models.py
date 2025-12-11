# app/models.py
# Modelos SQLAlchemy alinhados com o banco de dados diarioapp_db
# Atualizado em 02/12/2025 - Atende 100% à atividade

from . import db
from werkzeug.security import generate_password_hash, check_password_hash

# Tabela: professores
class Professor(db.Model):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

# Tabela: turmas
class Turma(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    serie = db.Column(db.String(1), nullable=False)
    disciplina = db.Column(db.String(50), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)

    professor = db.relationship('Professor', backref='turmas')
    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    aulas = db.relationship('Aula', backref='turma', lazy=True)

# Tabela: alunos
class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    foto_url = db.Column(db.Text)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)

# Tabela: aulas (conteúdo + frequência)
class Aula(db.Model):
    __tablename__ = 'aulas'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, default=db.func.current_date())
    topico = db.Column(db.String(200))
    conteudo_detalhado = db.Column(db.Text)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)

    presencas = db.relationship('Presenca', backref='aula', lazy=True, cascade='all, delete-orphan')

# Tabela: presencas (PK composta)
class Presenca(db.Model):
    __tablename__ = 'presencas'
    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'), primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), primary_key=True)
    presente = db.Column(db.Boolean, default=True)

# Tabela: notas
class Nota(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    bimestre = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Numeric(3,1), nullable=False)

    aluno = db.relationship('Aluno', backref='notas')
    turma = db.relationship('Turma', backref='notas')