from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PregnancyProfile(db.Model):
    __tablename__ = "pregnancy_profile"
    id = db.Column(db.Integer, primary_key=True)
    nombre_madre = db.Column(db.String(120), default="")
    # Fecha de última menstruación (FUM) — base para semana gestacional
    fecha_fum = db.Column(db.Date, nullable=True)
    # Opcional: nombre elegido para el bebé; sexo para personalizar la app (no sustituye diagnóstico médico)
    nombre_bebe = db.Column(db.String(120), default="")
    sexo_bebe = db.Column(db.String(20), default="desconocido")  # desconocido | nina | nino
    suscripcion_activa = db.Column(db.Boolean, default=False)
    suscripcion_hasta = db.Column(db.Date, nullable=True)
    plan_suscripcion = db.Column(db.String(30), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WeightLog(db.Model):
    __tablename__ = "weight_log"
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("pregnancy_profile.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    peso_kg = db.Column(db.Float, nullable=False)


class BloodPressureLog(db.Model):
    __tablename__ = "blood_pressure_log"
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("pregnancy_profile.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    sistolica = db.Column(db.Integer, nullable=False)
    diastolica = db.Column(db.Integer, nullable=False)


class MedicalAppointment(db.Model):
    __tablename__ = "medical_appointment"
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("pregnancy_profile.id"), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    notas = db.Column(db.Text, default="")
    tipo = db.Column(db.String(50), default="cita")  # cita, vitamina, estudio


class Medication(db.Model):
    __tablename__ = "medication"
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("pregnancy_profile.id"), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    frecuencia = db.Column(db.String(200), default="")
    notas = db.Column(db.Text, default="")


class Reminder(db.Model):
    __tablename__ = "reminder"
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("pregnancy_profile.id"), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), default="otro")  # cita, vitamina, estudio
    hecho = db.Column(db.Boolean, default=False)
