"""
Luma: asistente basado en reglas y contexto de semana.
Responde a muchos temas con orientación empática; no sustituye al médico.
"""
import random
import re
from typing import Optional, Tuple

from pregnancy_data import EMOTIONAL_TIPS, EDUCATION_SECTIONS, NUTRITION_FAQ, info_for_week


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower().strip())


def _words(s: str) -> set:
    return set(re.findall(r"[\wáéíóúñü]+", _norm(s), re.IGNORECASE))


def pregnancy_week_context(week: Optional[int]) -> str:
    if week is None or week < 1:
        return "Aún no registramos tu semana. Indica tu fecha de última menstruación (FUM) en tu perfil."
    if week > 40:
        return "Según tu FUM podrías estar en o después de la semana 40. Consulta con tu matrona o médico."
    return f"Según tu perfil, vas aproximadamente en la semana {week} de gestación."


def _week_snippet(week: Optional[int]) -> str:
    if week is None or week < 1:
        return ""
    info = info_for_week(min(40, max(1, week)))
    parts = [info.get("bebe", "")]
    if info.get("comparacion_fruta"):
        parts.append(f"Como referencia de tamaño, a veces se compara con: {info['comparacion_fruta']}.")
    return " ".join(p for p in parts if p).strip()


def _best_education_match(message: str) -> Optional[str]:
    mw = _words(message)
    if len(mw) < 2:
        return None
    stop = {
        "el", "la", "los", "las", "un", "una", "de", "en", "y", "a", "que", "por", "con", "me", "mi",
        "tu", "te", "se", "es", "son", "estoy", "está", "como", "cómo", "qué", "para", "muy", "más",
    }
    mw = {w for w in mw if len(w) > 2 and w not in stop}
    if not mw:
        return None
    best_punto = None
    best_score = 0
    for section in EDUCATION_SECTIONS.values():
        for punto in section.get("puntos", []):
            pw = _words(punto)
            score = len(mw & pw)
            if score > best_score:
                best_score = score
                best_punto = punto
    if best_score >= 1 and best_punto:
        return best_punto
    return None


def _wants_pregnancy_help(m: str) -> bool:
    """Temas de embarazo / cuerpo: si aparecen, no devolvemos solo un saludo genérico."""
    keys = (
        "acidez",
        "reflujo",
        "ardor",
        "estómago",
        "estomago",
        "digest",
        "indigest",
        "náusea",
        "nausea",
        "vómito",
        "vomito",
        "gases",
        "estreñ",
        "diarrea",
        "dolor",
        "sangr",
        "contracci",
        "contracción",
        "fiebre",
        "mareo",
        "hinchaz",
        "presión",
        "presion",
        "tensión",
        "tension",
        "peso",
        "kilos",
        "insomnio",
        "dormir",
        "duermo",
        "sueño",
        "sueno",
        "cansanc",
        "fatiga",
        "patada",
        "patadas",
        "movimiento",
        "medicamento",
        "pastilla",
        "vitamina",
        "ácido fólico",
        "acido folico",
        "aliment",
        "dieta",
        "comida",
        "comer",
        "ejercicio",
        "espalda",
        "cabeza",
        "picazón",
        "picazon",
        "orina",
        "micción",
        "miccion",
        "bebe",
        "bebé",
        "embaraz",
        "gestacion",
        "gestación",
        "semana",
        "parto",
        "lactancia",
        "eco",
        "matrona",
        "gine",
        "médico",
        "medico",
    )
    return any(k in m for k in keys)


def _general_chitchat(m: str) -> Optional[Tuple[str, str]]:
    if any(x in m for x in ("gracias", "te agradezco", "mil gracias")):
        return (
            "¡De nada! Me alegra poder acompañarte un poco en este camino. "
            "Si surge cualquier otra duda, aquí estaré.",
            "thanks",
        )
    if any(x in m for x in ("adiós", "adios", "hasta luego", "nos vemos", "chao", "bye")):
        return (
            "Cuídate mucho. Recuerda que descansar y pedir ayuda también es fortaleza. ¡Hasta pronto!",
            "bye",
        )
    if any(x in m for x in ("quién eres", "quien eres", "qué eres", "que eres", "para qué sirves")):
        return (
            "Soy Luma, una asistente de esta app pensada para orientarte sobre embarazo, salud y bienestar. "
            "No soy médica: para diagnósticos y tratamientos tu equipo de salud es la referencia.",
            "about",
        )
    if "hora" in m and any(x in m for x in ("qué", "que ", "dime")):
        return (
            "No tengo reloj en tiempo real, pero puedes mirar la hora en tu dispositivo. "
            "Si lo que te preocupa es organizar descansos o citas, en la app puedes anotar recordatorios.",
            "time",
        )
    if any(x in m for x in ("clima", "tiempo hace", "llover", "frío", "calor afuera")):
        return (
            "El tiempo exterior lo verás mejor en una app del clima de tu zona. "
            "En el embarazo, si hace mucho calor hidrátate y evita el sol fuerte; si hace frío, abrígate bien.",
            "weather",
        )
    return None


def _digest_intent(m: str) -> str:
    """
    Distingue náuseas / vómitos frente a acidez-reflujo para no mezclar respuestas.
    Devuelve: 'nausea', 'reflux', 'both', 'stomach_vague' o ''.
    """
    has_n = any(
        k in m
        for k in (
            "náusea",
            "náuseas",
            "nausea",
            "nauseas",
            "asco",
            "devolver",
            "arcadas",
            "vomito",
            "vómito",
            "vomitar",
            "vómitos",
            "vomitos",
        )
    )
    has_r = any(
        k in m
        for k in (
            "acidez",
            "reflujo",
            "pirosis",
            "regurgit",
            "gastritis",
            "indigest",
            "ardor estómago",
            "ardor de estómago",
            "ardor al subir",
            "ardor en el pecho",
            "duele el pecho",
            "sube la comida",
        )
    )
    if "ardor" in m and any(x in m for x in ("estómago", "estomago", "pecho", "esófago", "esofago", "trag")):
        has_r = True
    if has_n and has_r:
        return "both"
    if has_n:
        return "nausea"
    if has_r:
        return "reflux"
    if "estómago" in m or "estomago" in m:
        return "stomach_vague"
    return ""


def _nutrition_answer(message_norm: str, week: Optional[int]) -> str:
    """
    Respuestas cortas y concretas para dudas de alimentación.
    message_norm: mensaje ya normalizado con _norm().
    """
    wctx = pregnancy_week_context(week)

    # Picante: suele ser seguro, pero puede empeorar acidez/reflujo o náuseas.
    if "picante" in message_norm or "chile" in message_norm or "ají" in message_norm or "aji" in message_norm:
        return (
            f"{wctx} El picante no está 'prohibido' por regla general en el embarazo, "
            "pero a muchas personas les empeora la acidez/reflujo o las náuseas. "
            "Si notas ardor, reflujo o diarrea, reduce el picante y prueba comidas más suaves. "
            "Si tienes molestias fuertes o persistentes, coméntalo con tu médico."
        )

    # Crudos / poco hechos: respuesta directa aunque no pregunten con 'puedo comer'.
    if any(x in message_norm for x in ("crudo", "cruda", "crudos", "crudas", "poco hecho", "sin cocinar")):
        return (
            f"{wctx} En el embarazo se recomienda evitar alimentos crudos o poco hechos de origen animal "
            "(carne, pescado/marisco, huevo) y elegirlos bien cocinados. "
            "También evita lácteos no pasteurizados. Es una medida de seguridad alimentaria."
        )

    # Preguntas directas de "¿puedo comer X?"
    if any(x in message_norm for x in ("puedo comer", "se puede comer", "puedo tomar", "se puede tomar", "es seguro comer", "es seguro tomar")):
        for item in NUTRITION_FAQ:
            if any(k in message_norm for k in item["keys"]):
                return f"{wctx} {item['respuesta']}"

    # Coincidencia por palabra clave, aunque no escriban "puedo comer"
    for item in NUTRITION_FAQ:
        if any(k in message_norm for k in item["keys"]):
            return f"{wctx} {item['respuesta']}"

    pts = EDUCATION_SECTIONS["alimentacion"]["puntos"]
    return (
        f"{wctx} Sobre alimentación en el embarazo, una guía rápida: "
        f"{pts[0]} {pts[3]} "
        "Si me dices qué alimento concreto te preocupa (por ejemplo sushi, queso, café, jamón, atún), te respondo más exacto."
    )


def reply(message: str, week: Optional[int]) -> Tuple[str, str]:
    """
    Returns (reply_text, intent_tag).
    """
    m = _norm(message)
    wctx = pregnancy_week_context(week)
    snippet = _week_snippet(week)

    if not m:
        return (
            "Aquí estoy. Escribe tu mensaje cuando quieras y te leo con atención.",
            "empty",
        )

    cc = _general_chitchat(m)
    if cc:
        return cc

    # Alertas graves primero (incluye vómitos con sangre, sangrado, etc.)
    # Nota: "mareo" suelto lo tratamos aparte; aquí no forzamos urgencia por mareos leves.
    if any(
        x in m
        for x in (
            "sangr",
            "sangre",
            "dolor fuerte",
            "contraccion",
            "contracción",
            "fiebre",
            "líquido",
            "liquido",
            "emergencia",
            "urgencia",
            "desmayo",
            "desmayar",
            "pérdida de consciencia",
            "perdida de consciencia",
        )
    ):
        return (
            "Si tienes sangrado intenso, dolor muy fuerte, fiebre alta, pérdida de líquido abundante "
            "o notas mucha menos actividad del bebé de lo habitual, acude a urgencias o llama a tu centro de salud ahora. "
            "No esperes a confirmar por chat.",
            "urgent_info",
        )

    # Digestivo: respuesta distinta si preguntas por náuseas, por acidez o por ambas
    dig = _digest_intent(m)
    if dig == "nausea":
        return (
            f"{wctx} Entiendo que hablas de náuseas o ganas de vomitar: es muy típico, sobre todo en el primer trimestre, "
            "por el aumento de hormonas (como la hCG). Suele ayudar repartir la comida en tomas pequeñas, evitar olores "
            "que te disgusten, hidratarte a sorbos y descansar. Algunas personas toleran mejor cosas secas o frías; "
            "otras mejor con algo ligero al levantarse — prueba qué te sienta a ti. "
            "Si no puedes retener líquidos, vomitas muy a menudo o bajas de peso, debes valorarlo con urgencia o con tu médico. "
            "Cualquier medicamento o suplemento debe indicártelo tu ginecólogo o médico.",
            "symptoms_nausea",
        )
    if dig == "reflux":
        return (
            f"{wctx} Sobre acidez y reflujo: en el embarazo es frecuente porque la progesterona relaja el músculo que cierra "
            "el estómago y, más adelante, el útero puede empujar hacia arriba y empeorar la sensación. "
            "Suele ayudar comer poco y varias veces, evitar picante y grasa muy pesada, moderar café/chocolate y no tumbarse "
            "justo después de comer (puedes elevar un poco la cabecera al dormir). "
            "Si el ardor es muy intenso, no toleras líquidos o hay vómitos con sangre, acude a urgencias o a tu médico. "
            "Cualquier medicamento debe indicártelo tu ginecólogo o médico según tu caso.",
            "symptoms_reflux",
        )
    if dig == "both":
        return (
            f"{wctx} Veo que comentas náuseas y también sensación de acidez o reflujo; son molestias distintas pero pueden ir juntas. "
            "Para las náuseas ayudan comidas muy ligeras y frecuentes y evitar olores fuertes; para la acidez, no acostarte enseguida "
            "de comer y repartir las ingestas. Si no retienes líquidos, el malestar es muy intenso o hay sangre en vómitos, "
            "acude a urgencias o a tu médico. Los medicamentos solo con prescripción adaptada a tu embarazo.",
            "symptoms_nausea_reflux",
        )
    if dig == "stomach_vague":
        return (
            f"{wctx} Noto que te duele o molesta el estómago pero no especificas si es más náuseas, ardor o dolor punzante. "
            "Si es ardor o subida de acidez, suele ser reflujo frecuente en el embarazo; si es más mareo interno o ganas de vomitar, "
            "se parece más a náuseas. Cuéntame un poco más (qué sensación es, desde cuándo y si asocia comidas) y afinamos; "
            "si el dolor es muy fuerte, fiebre o sangrado, acude a urgencias.",
            "symptoms_stomach_vague",
        )

    # Saludos (solo si no hay una consulta de embarazo en el mismo mensaje)
    if not _wants_pregnancy_help(m) and any(
        x in m for x in ("hola", "buenos", "buenas", "hey", "hi", "buen día", "buen dia")
    ):
        extra = f" {snippet}" if snippet else ""
        return (
            f"¡Hola! Soy Luma.{extra} "
            "Escribe lo que te pase o te preocupe y te respondo sobre eso. Ante una emergencia médica, contacta a tu equipo de salud.",
            "greeting",
        )

    # Estrés / ánimo
    if any(
        x in m
        for x in (
            "estrés",
            "estres",
            "ansiedad",
            "miedo",
            "triste",
            "llorar",
            "agobi",
            "nervios",
            "depres",
            "mal humor",
        )
    ):
        tip = random.choice(EMOTIONAL_TIPS)
        return (
            f"Es muy humano sentirse así en el embarazo. {tip} "
            "Si la tristeza o la ansiedad no te dejan funcionar en el día a día, habla con tu médico o apoyo psicológico.",
            "emotional",
        )

    # Alimentación
    if any(
        x in m
        for x in (
            "comer",
            "comida",
            "dieta",
            "aliment",
            "vitamina",
            "ácido fólico",
            "acido folico",
            "hambre",
            "desayun",
            "merienda",
            "cena",
            "sushi",
            "queso",
            "jamon",
            "jamón",
            "embut",
            "atún",
            "atun",
            "café",
            "cafe",
            "alcohol",
            "picante",
            "crudo",
            "cruda",
            "crudos",
            "crudas",
            "poco hecho",
            "sin cocinar",
        )
    ):
        return (
            _nutrition_answer(m, week)
            + " Si tienes náuseas o acidez, también puedo sugerirte ideas de comidas suaves.",
            "nutrition",
        )

    # Ejercicio
    if any(x in m for x in ("ejercicio", "caminar", "yoga", "deporte", "gimnasio", "correr", "bailar")):
        pts = EDUCATION_SECTIONS["ejercicio"]["puntos"]
        return wctx + " " + " ".join(pts), "exercise"

    # Peso / presión
    if "peso" in m or "kilos" in m or "subí" in m or "subi " in m:
        return (
            f"{wctx} El aumento de peso recomendado depende de tu IMC previo y de tu equipo médico. "
            "Puedes registrar tu peso en la sección Salud para llevar un historial a tus consultas.",
            "weight",
        )
    if "presión" in m or "presion" in m or "tensión" in m or "tension" in m:
        return (
            f"{wctx} Anota la presión en reposo, si es posible siempre a la misma hora. "
            "Valores muy altos o síntomas como dolor de cabeza intenso o visión borrosa requieren valoración urgente.",
            "bp",
        )

    # Citas / recordatorios
    if any(x in m for x in ("cita", "médico", "medico", "eco", "ultrason", "control", "matrona", "gine")):
        return (
            f"{wctx} Llevar un calendario de controles y estudios ayuda mucho. "
            "Puedes registrar citas y recordatorios en la app. Los esquemas varían según tu país y tu riesgo obstétrico.",
            "appointments",
        )

    # Otras molestias digestivas (si no entraron arriba)
    if any(x in m for x in ("estreñ", "diarrea", "gases", "boca amarga", "sabor amargo")):
        return (
            f"{wctx} Los cambios digestivos son habituales en el embarazo. "
            "Hidrátate, fibra gradual si tu médico lo ve bien, y movimiento suave. "
            "Diarrea con fiebre o dolor fuerte, o estreñimiento con vómitos, merece valoración pronto.",
            "symptoms_digest2",
        )

    # Mareos (no urgencia genérica; sí aviso si van con otros síntomas)
    if "mareo" in m or "mareos" in m or "vertigo" in m or "vértigo" in m:
        return (
            f"{wctx} Los mareos o sensación de vértigo pueden aparecer por cansancio, bajar glucosa, "
            "cambios de presión o simplemente levantarte deprisa. Siéntate o túmbate de lado, hidrátate y come algo ligero. "
            "Si vienen con dolor de cabeza muy fuerte, visión borrosa, hinchazón brusca de cara o manos, o desmayos, "
            "llama a tu centro de salud o acude a urgencias.",
            "dizziness",
        )

    # Espalda / piernas / hinchazón
    if any(x in m for x in ("espalda", "lumbar", "piernas", "calambre", "hinchaz", "tobillos")):
        return (
            f"{wctx} El peso del útero y la postura pueden cargar espalda y piernas. "
            "Descansos, calzado cómodo, hidratación y ejercicio suave (si tu médico lo autoriza) ayudan. "
            "Hinchazón brusca de cara o manos con dolor de cabeza debe valorarse pronto.",
            "body_aches",
        )

    # Sueño
    if "duermo" in m or "insomnio" in m or "dormir" in m or "sueño" in m or "sueno" in m:
        return (
            f"{wctx} Prueba rutina relajante, lado izquierdo con almohada entre piernas si te resulta cómodo, "
            "y evita pantallas justo antes de dormir. Si el insomnio es severo, coméntalo en tu próxima visita.",
            "sleep",
        )

    # Movimientos fetales
    if any(x in m for x in ("patada", "patadas", "mueve", "movimiento", "no se mueve", "menos movimiento")):
        return (
            f"{wctx} Los patrones de movimiento son personales. "
            "Si notas un cambio claro o disminución respecto a lo habitual para ti, llama a tu centro de salud o acude; no lo dejes para mañana.",
            "movement",
        )

    # Parto / lactancia
    if any(x in m for x in ("parto", "epidural", "cesárea", "cesarea", "contracciones de parto", "bolsa")):
        return (
            f"{wctx} Cada centro explica señales de parto y opciones de alivio del dolor. "
            "Anota tus dudas para la próxima visita; en sangrado o contracciones regulares antes de tiempo, valoración urgente.",
            "birth",
        )
    if any(x in m for x in ("lactancia", "pecho", "teta", "biberón", "biberon", "amamant")):
        return (
            "La lactancia se aprende con apoyo: grupos de lactancia, matrona o pediatra pueden orientarte sobre agarre, frecuencia y dolor. "
            "Lo importante es que tú y el bebé estéis bien; pide ayuda sin culpa.",
            "breastfeeding",
        )

    # Relaciones / sexo / pareja
    if any(x in m for x in ("sexo", "sexual", "relaciones", "pareja", "marido", "novio")):
        return (
            f"{wctx} En muchos embarazos las relaciones sexuales son seguras si tu médico no ha indicado lo contrario. "
            "Si hay sangrado, dolor intenso u órdenes de reposo, sigue las indicaciones de tu equipo.",
            "relationships",
        )

    # Trabajo / viajes
    if any(x in m for x in ("trabajo", "oficina", "baja", "permiso")):
        return (
            f"{wctx} Los derechos laborales y bajas dependen de tu país y contrato. "
            "Tu médico puede orientarte sobre esfuerzo físico y riesgos; en la empresa suele existir un departamento de RR. HH.",
            "work",
        )
    if any(x in m for x in ("viaje", "viajar", "avión", "avion", "coche largo", "vacaciones")):
        return (
            f"{wctx} En viajes largos levántate a caminar, hidrátate y usa cinturón bajo el bulto abdominal como indique tu médico. "
            "Consulta si hay restricciones según tu semana o riesgo obstétrico.",
            "travel",
        )

    # Piel / estrías / cabello
    if any(x in m for x in ("piel", "estria", "estrías", "manchas", "cabello", "pelo", "uñas")):
        return (
            f"{wctx} Cambios en piel y pelo son frecuentes por hormonas. "
            "Hidrata la piel, protección solar si hay manchas, y cualquier lesión muy nueva o molesta conviene enseñarla en consulta.",
            "skin",
        )

    # Medicamentos
    if any(x in m for x in ("medicamento", "pastilla", "paracetamol", "ibuprofeno", "antibiótico", "antibiotico")):
        return (
            "No puedo decirte qué medicamento tomar: eso solo lo determina tu médico o farmacéutico según tu historial. "
            "Lleva siempre la lista de lo que tomas a cada consulta.",
            "meds",
        )

    # Desarrollo del bebé (genérico)
    if any(x in m for x in ("bebé", "bebe", "feto", "desarrollo", "crece", "tamaño", "fruta", "semanas")):
        line = snippet if snippet else "En Inicio verás un resumen por semana con tamaño aproximado y comparación orientativa."
        return (
            f"{wctx} {line} "
            "Cada embarazo es único; la ecografía y tu médico tienen la información más precisa para ti.",
            "development",
        )

    # Ayuda genérica / qué puedo preguntar
    if any(x in m for x in ("ayuda", "puedo preguntar", "qué sabes", "que sabes", "no sé qué", "no se que")):
        return (
            f"{wctx} Escribe con detalle lo que necesites y te respondo sobre eso. "
            "Para diagnósticos o tratamientos, tu médico o matrona son la referencia.",
            "help",
        )

    # Coincidencia con textos educativos (cualquier frase)
    edu_hit = _best_education_match(message)
    if edu_hit:
        return (
            f"{wctx} Relacionado con lo que comentas: {edu_hit} "
            "Si querías otra cosa, escríbelo con más detalle y lo vemos.",
            "education_match",
        )

    # Fallback sustantivo: siempre una respuesta completa
    tip = random.choice(EMOTIONAL_TIPS)
    if snippet:
        return (
            f"He leído tu mensaje. {wctx} {snippet} "
            f"Además, un recordatorio de bienestar: {tip} "
            "Si me cuentas un poco más o reformulas la pregunta, podré afinar mejor la respuesta.",
            "open_reply",
        )
    return (
        f"He leído tu mensaje. {wctx} {tip} "
        "Puedes preguntarme por síntomas, alimentación, ejercicio, citas o cómo te sientes; "
        "también puedes contarme cualquier cosa y te respondo con lo que sé. "
        "Para diagnósticos o tratamientos, tu médico o matrona son quienes deciden.",
        "open_reply",
    )
