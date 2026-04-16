from datetime import date, datetime, timedelta
from functools import wraps
from typing import Optional

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from sqlalchemy import inspect, text

from config import Config
from luma import reply as luma_reply
from models import (
    BloodPressureLog,
    MedicalAppointment,
    Medication,
    PregnancyProfile,
    Reminder,
    WeightLog,
    db,
)
from pregnancy_data import (
    EDUCATION_SECTIONS,
    fecha_probable_parto,
    info_for_week,
    mensaje_del_dia_payload,
)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)


def migrate_sqlite_profile_columns():
    """Añade columnas nuevas si la base ya existía (SQLite)."""
    try:
        if db.engine.dialect.name != "sqlite":
            return
        insp = inspect(db.engine)
        cols = {c["name"] for c in insp.get_columns("pregnancy_profile")}
        with db.engine.connect() as conn:
            if "nombre_bebe" not in cols:
                conn.execute(text("ALTER TABLE pregnancy_profile ADD COLUMN nombre_bebe VARCHAR(120) DEFAULT ''"))
                conn.commit()
            if "sexo_bebe" not in cols:
                conn.execute(
                    text("ALTER TABLE pregnancy_profile ADD COLUMN sexo_bebe VARCHAR(20) DEFAULT 'desconocido'")
                )
                conn.commit()
            if "suscripcion_activa" not in cols:
                conn.execute(text("ALTER TABLE pregnancy_profile ADD COLUMN suscripcion_activa BOOLEAN DEFAULT 0"))
                conn.commit()
            if "suscripcion_hasta" not in cols:
                conn.execute(text("ALTER TABLE pregnancy_profile ADD COLUMN suscripcion_hasta DATE"))
                conn.commit()
            if "plan_suscripcion" not in cols:
                conn.execute(text("ALTER TABLE pregnancy_profile ADD COLUMN plan_suscripcion VARCHAR(30) DEFAULT ''"))
                conn.commit()
    except Exception:
        pass


def get_or_create_profile():
    p = PregnancyProfile.query.first()
    if not p:
        p = PregnancyProfile(
            nombre_madre="",
            fecha_fum=None,
            nombre_bebe="",
            sexo_bebe="desconocido",
            suscripcion_activa=False,
            suscripcion_hasta=None,
            plan_suscripcion="",
        )
        db.session.add(p)
        db.session.commit()
    return p


def gestational_week(fum: Optional[date]) -> Optional[int]:
    if not fum:
        return None
    today = date.today()
    days = (today - fum).days
    if days < 0:
        return None
    return min(42, max(1, days // 7))


def subscription_ok(p: PregnancyProfile) -> bool:
    if not p.suscripcion_activa:
        return False
    if p.suscripcion_hasta and date.today() > p.suscripcion_hasta:
        p.suscripcion_activa = False
        db.session.commit()
        return False
    return True


def require_subscription(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        p = get_or_create_profile()
        if not subscription_ok(p):
            return jsonify({"ok": False, "error": "subscription_required"}), 403
        return f(*args, **kwargs)

    return wrapped


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/suscripcion", methods=["GET"])
def api_suscripcion_get():
    p = get_or_create_profile()
    ok = subscription_ok(p)
    return jsonify(
        {
            "activa": ok,
            "hasta": p.suscripcion_hasta.isoformat() if p.suscripcion_hasta else None,
            "plan": p.plan_suscripcion or None,
            "es_demo": True,
        }
    )


@app.route("/api/suscripcion/pagar", methods=["POST"])
def api_suscripcion_pagar():
    """Registra el pago de suscripción (entorno académico, sin pasarela externa)."""
    p = get_or_create_profile()
    data = request.get_json(silent=True) or {}
    plan = (data.get("plan") or "mensual").strip().lower()
    plan_dias = {
        "mensual": 30,
        "trimestral": 90,
        "semestral": 180,
        "embarazo_completo": 270,
        "anual": 365,
    }
    if plan not in plan_dias:
        return jsonify({"ok": False, "error": "Elige un plan válido"}), 400
    titular = (data.get("titular_tarjeta") or "").strip()
    if len(titular) < 3:
        return jsonify({"ok": False, "error": "Indica el nombre del titular de la tarjeta"}), 400
    digitos = (data.get("ultimos_4_digitos") or "").strip()
    if not digitos.isdigit() or len(digitos) != 4:
        return jsonify({"ok": False, "error": "Últimos 4 dígitos deben ser 4 números"}), 400

    dias = plan_dias[plan]
    p.suscripcion_activa = True
    p.suscripcion_hasta = date.today() + timedelta(days=dias)
    p.plan_suscripcion = plan
    db.session.commit()
    return jsonify(
        {
            "ok": True,
            "hasta": p.suscripcion_hasta.isoformat(),
            "plan": plan,
            "mensaje": "Suscripción activada correctamente.",
        }
    )


@app.route("/api/profile", methods=["GET", "POST"])
def api_profile():
    p = get_or_create_profile()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        if "nombre_madre" in data:
            nombre = (data.get("nombre_madre") or "").strip()[:120]
            if not nombre:
                return jsonify({"ok": False, "error": "El nombre es obligatorio"}), 400
            p.nombre_madre = nombre
        if "fecha_fum" in data and data["fecha_fum"]:
            try:
                p.fecha_fum = datetime.strptime(data["fecha_fum"][:10], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"ok": False, "error": "fecha_fum inválida (YYYY-MM-DD)"}), 400
        elif "fecha_fum" in data and data["fecha_fum"] is None:
            p.fecha_fum = None
        if "nombre_bebe" in data:
            p.nombre_bebe = (data.get("nombre_bebe") or "").strip()[:120]
        if "sexo_bebe" in data:
            sx = (data.get("sexo_bebe") or "desconocido").strip().lower()
            if sx not in ("desconocido", "nina", "nino"):
                return jsonify({"ok": False, "error": "sexo_bebe debe ser desconocido, nina o nino"}), 400
            p.sexo_bebe = sx
        db.session.commit()
    week = gestational_week(p.fecha_fum)
    return jsonify(
        {
            "nombre_madre": p.nombre_madre,
            "fecha_fum": p.fecha_fum.isoformat() if p.fecha_fum else None,
            "semana_gestacional": week,
            "nombre_bebe": p.nombre_bebe or "",
            "sexo_bebe": p.sexo_bebe or "desconocido",
        }
    )


@app.route("/api/seguimiento", methods=["GET"])
@require_subscription
def api_seguimiento():
    p = get_or_create_profile()
    week = gestational_week(p.fecha_fum)
    if week is None:
        info = {
            "bebe": "Registra tu FUM en el perfil para ver cómo va tu bebé semana a semana.",
            "madre": "—",
            "tamaño_cm": None,
            "peso_aprox_g": None,
            "comparacion_fruta": None,
            "semana_referencia": None,
        }
    else:
        info = info_for_week(week)

    fpp_iso = None
    dias_restantes = None
    if p.fecha_fum:
        fpp = fecha_probable_parto(p.fecha_fum)
        fpp_iso = fpp.isoformat()
        dias_restantes = (fpp - date.today()).days

    msg = mensaje_del_dia_payload(week, p.nombre_bebe or "", p.sexo_bebe or "desconocido")

    return jsonify(
        {
            "semana": week,
            "desarrollo_bebe": info["bebe"],
            "cambios_madre": info["madre"],
            "bloque_referencia_semana": info.get("semana_referencia"),
            "tamaño_aprox": info.get("tamaño_cm"),
            "peso_aprox_g": info.get("peso_aprox_g"),
            "comparacion_fruta": info.get("comparacion_fruta"),
            "fecha_probable_parto": fpp_iso,
            "dias_hasta_parto_aprox": dias_restantes,
            "mensaje_diario": msg["mensaje_diario"],
            "mensaje_etapa": msg["mensaje_etapa"],
            "nombre_bebe": p.nombre_bebe or "",
            "sexo_bebe": p.sexo_bebe or "desconocido",
        }
    )


@app.route("/api/pesos", methods=["GET", "POST"])
@require_subscription
def api_pesos():
    p = get_or_create_profile()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        try:
            fecha = datetime.strptime((data.get("fecha") or "")[:10], "%Y-%m-%d").date()
            peso = float(data.get("peso_kg"))
        except (ValueError, TypeError):
            return jsonify({"ok": False, "error": "fecha (YYYY-MM-DD) y peso_kg numérico requeridos"}), 400
        row = WeightLog(profile_id=p.id, fecha=fecha, peso_kg=peso)
        db.session.add(row)
        db.session.commit()
        return jsonify({"ok": True, "id": row.id})
    rows = (
        WeightLog.query.filter_by(profile_id=p.id).order_by(WeightLog.fecha.desc()).limit(100).all()
    )
    return jsonify(
        [
            {"id": r.id, "fecha": r.fecha.isoformat(), "peso_kg": r.peso_kg}
            for r in rows
        ]
    )


@app.route("/api/presion", methods=["GET", "POST"])
@require_subscription
def api_presion():
    p = get_or_create_profile()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        try:
            fecha = datetime.strptime((data.get("fecha") or "")[:10], "%Y-%m-%d").date()
            sis = int(data.get("sistolica"))
            dia = int(data.get("diastolica"))
        except (ValueError, TypeError):
            return jsonify({"ok": False, "error": "fecha, sistolica y diastolica requeridos"}), 400
        row = BloodPressureLog(profile_id=p.id, fecha=fecha, sistolica=sis, diastolica=dia)
        db.session.add(row)
        db.session.commit()
        return jsonify({"ok": True, "id": row.id})
    rows = (
        BloodPressureLog.query.filter_by(profile_id=p.id)
        .order_by(BloodPressureLog.fecha.desc())
        .limit(100)
        .all()
    )
    return jsonify(
        [
            {
                "id": r.id,
                "fecha": r.fecha.isoformat(),
                "sistolica": r.sistolica,
                "diastolica": r.diastolica,
            }
            for r in rows
        ]
    )


@app.route("/api/citas", methods=["GET", "POST"])
@require_subscription
def api_citas():
    p = get_or_create_profile()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        try:
            fh = datetime.fromisoformat(data.get("fecha_hora").replace("Z", "+00:00"))
            if fh.tzinfo:
                fh = fh.replace(tzinfo=None)
        except (ValueError, TypeError, AttributeError):
            return jsonify({"ok": False, "error": "fecha_hora ISO requerida"}), 400
        titulo = (data.get("titulo") or "Cita")[:200]
        notas = data.get("notas") or ""
        tipo = (data.get("tipo") or "cita")[:50]
        row = MedicalAppointment(
            profile_id=p.id, fecha_hora=fh, titulo=titulo, notas=notas, tipo=tipo
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({"ok": True, "id": row.id})
    rows = (
        MedicalAppointment.query.filter_by(profile_id=p.id)
        .order_by(MedicalAppointment.fecha_hora.asc())
        .limit(200)
        .all()
    )
    return jsonify(
        [
            {
                "id": r.id,
                "fecha_hora": r.fecha_hora.isoformat(),
                "titulo": r.titulo,
                "notas": r.notas,
                "tipo": r.tipo,
            }
            for r in rows
        ]
    )


@app.route("/api/medicamentos", methods=["GET", "POST"])
@require_subscription
def api_medicamentos():
    p = get_or_create_profile()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        nombre = (data.get("nombre") or "").strip()[:200]
        if not nombre:
            return jsonify({"ok": False, "error": "nombre requerido"}), 400
        row = Medication(
            profile_id=p.id,
            nombre=nombre,
            frecuencia=(data.get("frecuencia") or "")[:200],
            notas=data.get("notas") or "",
        )
        db.session.add(row)
        db.session.commit()
        return jsonify({"ok": True, "id": row.id})
    rows = Medication.query.filter_by(profile_id=p.id).order_by(Medication.id.desc()).all()
    return jsonify(
        [
            {
                "id": r.id,
                "nombre": r.nombre,
                "frecuencia": r.frecuencia,
                "notas": r.notas,
            }
            for r in rows
        ]
    )


@app.route("/api/recordatorios", methods=["GET", "POST", "PATCH"])
@require_subscription
def api_recordatorios():
    p = get_or_create_profile()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        try:
            fh = datetime.fromisoformat(data.get("fecha_hora").replace("Z", "+00:00"))
            if fh.tzinfo:
                fh = fh.replace(tzinfo=None)
        except (ValueError, TypeError, AttributeError):
            return jsonify({"ok": False, "error": "fecha_hora ISO requerida"}), 400
        titulo = (data.get("titulo") or "Recordatorio")[:200]
        cat = (data.get("categoria") or "otro")[:50]
        row = Reminder(profile_id=p.id, fecha_hora=fh, titulo=titulo, categoria=cat, hecho=False)
        db.session.add(row)
        db.session.commit()
        return jsonify({"ok": True, "id": row.id})
    if request.method == "PATCH":
        data = request.get_json(silent=True) or {}
        rid = data.get("id")
        if rid is None:
            return jsonify({"ok": False, "error": "id requerido"}), 400
        row = Reminder.query.filter_by(id=rid, profile_id=p.id).first()
        if not row:
            return jsonify({"ok": False, "error": "no encontrado"}), 404
        if "hecho" in data:
            row.hecho = bool(data["hecho"])
        db.session.commit()
        return jsonify({"ok": True})
    rows = (
        Reminder.query.filter_by(profile_id=p.id)
        .order_by(Reminder.fecha_hora.asc())
        .limit(200)
        .all()
    )
    return jsonify(
        [
            {
                "id": r.id,
                "fecha_hora": r.fecha_hora.isoformat(),
                "titulo": r.titulo,
                "categoria": r.categoria,
                "hecho": r.hecho,
            }
            for r in rows
        ]
    )


@app.route("/api/educacion/<seccion>", methods=["GET"])
@require_subscription
def api_educacion(seccion):
    if seccion not in EDUCATION_SECTIONS:
        return jsonify({"error": "sección no encontrada"}), 404
    return jsonify(EDUCATION_SECTIONS[seccion])


@app.route("/api/consejo-aleatorio", methods=["GET"])
@require_subscription
def api_consejo_aleatorio():
    import random

    from pregnancy_data import EMOTIONAL_TIPS as _tips

    return jsonify({"texto": random.choice(_tips)})


@app.route("/api/bienestar", methods=["GET"])
@require_subscription
def api_bienestar():
    import random

    from pregnancy_data import EMOTIONAL_TIPS as _tips

    mensaje = random.choice(
        [
            "Hoy eres suficiente. Cuidarte también es cuidar a tu bebé.",
            "Pequeños descansos cuentan: un vaso de agua, estirar espalda, respirar lento.",
            "Pedir ayuda es valentía, no debilidad.",
            "Tu cuerpo está haciendo un trabajo enorme; trátate con la misma amabilidad que darías a una amiga.",
        ]
    )
    return jsonify({"mensaje_positivo": mensaje, "consejo_estres": random.choice(_tips)})


@app.route("/api/luma/chat", methods=["POST"])
@require_subscription
def api_luma_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    p = get_or_create_profile()
    week = gestational_week(p.fecha_fum)
    text, intent = luma_reply(message, week)
    return jsonify({"reply": text, "intent": intent, "semana_contexto": week})


@app.route("/api/alimentacion", methods=["GET"])
@require_subscription
def api_alimentacion():
    """
    Devuelve recomendaciones de alimentación y, opcionalmente, una respuesta breve para una consulta concreta (?q=...).
    Útil para integrarlo en bienestar/notas diarias sin depender del chat.
    """
    from luma import reply as _reply

    p = get_or_create_profile()
    week = gestational_week(p.fecha_fum)
    q = (request.args.get("q") or "").strip()
    quick = None
    if q:
        quick, _intent = _reply(q, week)
    return jsonify(
        {
            "semana_contexto": week,
            "titulo": EDUCATION_SECTIONS["alimentacion"]["titulo"],
            "puntos": EDUCATION_SECTIONS["alimentacion"]["puntos"],
            "respuesta_rapida": quick,
        }
    )


@app.cli.command("init-db")
def init_db():
    """Crea las tablas (flask --app app init-db)."""
    with app.app_context():
        db.create_all()
        migrate_sqlite_profile_columns()
    print("Base de datos inicializada.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        migrate_sqlite_profile_columns()
    # Puerto 8080 para coincidir con .vscode/launch.json (Chrome contra localhost)
    app.run(debug=True, host="127.0.0.1", port=8080)
