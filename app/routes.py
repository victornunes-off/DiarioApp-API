# app/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import db
from .models import Professor, Turma, Aluno, Aula, Presenca, Nota
from werkzeug.security import check_password_hash
from sqlalchemy import text
from datetime import date

# ←←← Nome correto e único do Blueprint
bp = Blueprint('api', __name__)


# ========================================
# 1. LOGIN (POST /api/login)
# ========================================
@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')

        professor = Professor.query.filter_by(email=email).first()

        if professor and check_password_hash(professor.senha_hash, senha):
            token = create_access_token(identity=professor.id)
            return jsonify({
                "token": token,
                "professor": {
                    "id": professor.id,
                    "nome": professor.nome,
                    "email": professor.email
                }
            }), 200

        return jsonify({"erro": "Credenciais inválidas"}), 401
    except Exception as e:
        return jsonify({"erro": "Erro no login", "detalhes": str(e)}), 500


# ========================================
# 2. TURMAS (GET /api/turmas)
# ========================================
@bp.route('/turmas', methods=['GET'])
@jwt_required()
def get_turmas():
    prof_id = get_jwt_identity()
    turmas = Turma.query.filter_by(professor_id=prof_id).all()
    lista = [{
        "id": t.id,
        "ano": t.ano,
        "serie": t.serie,
        "disciplina": t.disciplina,
        "progresso": 75
    } for t in turmas]
    return jsonify({"turmas": lista}), 200


# ========================================
# 3. ALUNOS DA TURMA (GET /api/turmas/<id>/alunos)
# ========================================
@bp.route('/turmas/<int:turma_id>/alunos', methods=['GET'])
@jwt_required()
def get_alunos_turma(turma_id):
    alunos = Aluno.query.filter_by(turma_id=turma_id).all()
    lista = [{
        "id": a.id,
        "nome": a.nome,
        "foto_url": a.foto_url or ""
    } for a in alunos]
    return jsonify({"alunos": lista}), 200


# ========================================
# 4. LANÇAR AULA + FREQUÊNCIA (POST /api/aulas)
# ========================================
@bp.route('/aulas', methods=['POST'])
@jwt_required()
def create_aula():
    data = request.get_json()
    nova_aula = Aula(
        data=data.get('data', date.today()),
        topico=data.get('topico'),
        conteudo_detalhado=data.get('conteudo_detalhado'),
        turma_id=data['turma_id']
    )
    db.session.add(nova_aula)
    db.session.flush()

    for p in data.get('presencas', []):
        presenca = Presenca(
            aula_id=nova_aula.id,
            aluno_id=p['aluno_id'],
            presente=p.get('presente', True)
        )
        db.session.add(presenca)

    db.session.commit()
    return jsonify({"mensagem": "Aula e frequência lançadas", "aula_id": nova_aula.id}), 201


# ========================================
# 5. CRUD DE NOTAS
# ========================================
@bp.route('/notas', methods=['POST'])
@jwt_required()
def create_nota():
    data = request.get_json()
    nota = Nota(
        aluno_id=data['aluno_id'],
        turma_id=data['turma_id'],
        bimestre=data['bimestre'],
        valor=data['valor']
    )
    db.session.add(nota)
    db.session.commit()
    return jsonify({"mensagem": "Nota lançada", "nota_id": nota.id}), 201


@bp.route('/notas/<int:aluno_id>', methods=['GET'])
@jwt_required()
def get_notas_aluno(aluno_id):
    notas = Nota.query.filter_by(aluno_id=aluno_id).all()
    lista = []
    for n in notas:
        media = db.session.execute(
            text("SELECT calcular_media_final(:aluno, :turma)"),
            {"aluno": aluno_id, "turma": n.turma_id}
        ).scalar() or 0.0

        lista.append({
            "id": n.id,
            "bimestre": n.bimestre,
            "valor": float(n.valor),
            "media_final": round(float(media), 1)
        })
    return jsonify({"notas": lista}), 200


@bp.route('/notas/<int:nota_id>', methods=['PUT'])
@jwt_required()
def update_nota(nota_id):
    nota = Nota.query.get_or_404(nota_id)
    data = request.get_json()
    nota.valor = data.get('valor', nota.valor)
    db.session.commit()
    return jsonify({"mensagem": "Nota atualizada"}), 200


@bp.route('/notas/<int:nota_id>', methods=['DELETE'])
@jwt_required()
def delete_nota(nota_id):
    nota = Nota.query.get_or_404(nota_id)
    db.session.delete(nota)
    db.session.commit()
    return jsonify({"mensagem": "Nota deletada"}), 200


# ========================================
# 6. RELATÓRIOS
# ========================================
@bp.route('/relatorios/boletim/<int:aluno_id>', methods=['GET'])
@jwt_required()
def get_boletim(aluno_id):
    result = db.session.execute(
        text("SELECT * FROM vw_boletim_completo WHERE aluno_id = :id"),
        {"id": aluno_id}
    )
    boletim = [dict(row) for row in result]
    return jsonify({"boletim": boletim}), 200


@bp.route('/relatorios/frequencia/<int:turma_id>', methods=['GET'])
@jwt_required()
def get_frequencia_turma(turma_id):
    aulas = Aula.query.filter_by(turma_id=turma_id).order_by(Aula.data).all()
    relatorio = []
    for aula in aulas:
        presencas = Presenca.query.filter_by(aula_id=aula.id).all()
        lista_presenca = [{"aluno_id": p.aluno_id, "presente": p.presente} for p in presencas]
        relatorio.append({
            "aula_id": aula.id,
            "data": aula.data.isoformat(),
            "topico": aula.topico,
            "presencas": lista_presenca
        })
    return jsonify({"frequencia": relatorio}), 200


@bp.route('/relatorios/conteudos/<int:turma_id>', methods=['GET'])
@jwt_required()
def get_conteudos_turma(turma_id):
    aulas = Aula.query.filter_by(turma_id=turma_id).order_by(Aula.data.desc()).all()
    conteudos = [{
        "data": a.data.isoformat(),
        "topico": a.topico,
        "conteudo_detalhado": a.conteudo_detalhado
    } for a in aulas]
    return jsonify({"conteudos": conteudos}), 200


# ========================================
# 7. CALENDÁRIO DO PROFESSOR
# ========================================
@bp.route('/calendario', methods=['GET'])
@jwt_required()
def get_calendario():
    prof_id = get_jwt_identity()
    aulas = Aula.query.join(Turma).filter(Turma.professor_id == prof_id).order_by(Aula.data).all()
    eventos = [{
        "data": a.data.isoformat(),
        "topico": a.topico or "Sem título",
        "turma": a.turma.disciplina
    } for a in aulas]
    return jsonify({"eventos": eventos}), 200