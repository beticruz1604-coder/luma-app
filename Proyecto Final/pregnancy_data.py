# Información educativa resumida por semana (1–40). No sustituye consejo médico.

from datetime import date, timedelta
from typing import Optional
import hashlib

# tamaño_cm / peso_aprox_g / comparacion_fruta: referencias orientativas (varían mucho entre personas).
WEEK_INFO = {
    1: {
        "bebe": "La fecundación ocurre; las células comienzan a dividirse.",
        "madre": "Puede que aún no sepas que estás embarazada. Algunas mujeres notan sensibilidad mamaria o cansancio leve.",
        "tamaño_cm": "microscópico",
        "peso_aprox_g": "< 1 g",
        "comparacion_fruta": "punto microscópico (célula en división)",
    },
    4: {
        "bebe": "El embrión se implanta en el útero; comienza a formarse la placenta.",
        "madre": "Posible retraso menstrual, náuseas leves o cambios de humor.",
        "tamaño_cm": "≈ 0,2–0,3 cm",
        "peso_aprox_g": "< 1 g",
        "comparacion_fruta": "como una semilla de amapola",
    },
    8: {
        "bebe": "Órganos principales en formación; el embrión mide unos centímetros.",
        "madre": "Náuseas matutinas frecuentes, cansancio, necesidad de orinar más a menudo.",
        "tamaño_cm": "≈ 1,5–2 cm",
        "peso_aprox_g": "1–2 g",
        "comparacion_fruta": "como una frambuesa",
    },
    12: {
        "bebe": "Ya se le llaman feto; los órganos siguen madurando. Puede moverse, aún no lo notas.",
        "madre": "Muchas mejoran las náuseas; el útero crece y puede notarse ligero bulto.",
        "tamaño_cm": "≈ 5–6 cm",
        "peso_aprox_g": "14–20 g",
        "comparacion_fruta": "como una ciruela",
    },
    16: {
        "bebe": "Músculos y sistema nervioso se desarrollan; a veces ya se escucha el latido en control.",
        "madre": "Más energía en algunas; posible aumento de apetito y cambios en la piel.",
        "tamaño_cm": "≈ 11–12 cm",
        "peso_aprox_g": "100 g",
        "comparacion_fruta": "como un aguacate pequeño",
    },
    20: {
        "bebe": "Mitad del embarazo aproximadamente; en la ecografía morfológica se revisa el desarrollo.",
        "madre": "Puedes empezar a sentir movimientos (rápidos o como burbujas).",
        "tamaño_cm": "≈ 16 cm (cabeza a trasero)",
        "peso_aprox_g": "300 g",
        "comparacion_fruta": "como un plátano",
    },
    24: {
        "bebe": "Los pulmones se preparan; el bebé responde a sonidos externos.",
        "madre": "Linea alba, posibles calambres; control de glucosa según indique tu médico.",
        "tamaño_cm": "≈ 21–30 cm",
        "peso_aprox_g": "600 g",
        "comparacion_fruta": "como una mazorca de maíz / papaya pequeña",
    },
    28: {
        "bebe": "Puede abrir los ojos; acumula grasa bajo la piel.",
        "madre": "Tercer trimestre; más peso del útero puede causar molestias de espalda.",
        "tamaño_cm": "≈ 25–38 cm",
        "peso_aprox_g": "1 kg",
        "comparacion_fruta": "como una berenjena",
    },
    32: {
        "bebe": "Suele girar a posición cefálica; sueño con ciclos más definidos.",
        "madre": "Disnea al hacer esfuerzos, acidez; hidratación y postura ayudan.",
        "tamaño_cm": "≈ 28–42 cm",
        "peso_aprox_g": "1,7 kg",
        "comparacion_fruta": "como una piña pequeña",
    },
    36: {
        "bebe": "Considerado casi a término; pulmones casi listos para nacer.",
        "madre": "Contracciones de Braxton Hicks frecuentes; prepara la bolsa para el hospital.",
        "tamaño_cm": "≈ 32–47 cm",
        "peso_aprox_g": "2,6 kg",
        "comparacion_fruta": "como una lechuga romana / melón pequeño",
    },
    40: {
        "bebe": "Término completo; listo para nacer. Tamaño y peso varían.",
        "madre": "Puede haber más presión pélvica; consulta cualquier sangrado o disminución de movimientos.",
        "tamaño_cm": "≈ 48–52 cm (al nacer, variable)",
        "peso_aprox_g": "3–3,6 kg (muy variable)",
        "comparacion_fruta": "como una sandía pequeña",
    },
}


def info_for_week(week: int) -> dict:
    if week < 1:
        week = 1
    if week > 40:
        week = 40
    keys = sorted(WEEK_INFO.keys())
    chosen = keys[0]
    for k in keys:
        if k <= week:
            chosen = k
    base = WEEK_INFO[chosen].copy()
    base["semana_referencia"] = chosen
    return base


EDUCATION_SECTIONS = {
    "alimentacion": {
        "titulo": "Alimentación en el embarazo",
        "puntos": [
            "Base del plato: verduras y frutas bien lavadas, legumbres, cereales integrales y proteínas magras.",
            "Incluye calcio y vitamina D (lácteos pasteurizados, yogur, queso pasteurizado) y grasas saludables (AOVE, frutos secos).",
            "Evita alcohol. Limita cafeína (café, té, cola, energéticas): si tienes dudas, consulta el límite recomendado por tu médico.",
            "Seguridad alimentaria: lava bien frutas/verduras; cocina bien carne, pescado y huevos; evita huevo crudo y mayonesa casera.",
            "Evita lácteos no pasteurizados y quesos blandos si no son pasteurizados (riesgo de listeria).",
            "Evita pescado crudo (sushi/ceviche) y mariscos crudos; el pescado bien cocido suele ser buena opción (omega‑3).",
            "Precaución con pescados grandes por mercurio (pez espada/emperador, tiburón/cazón, lucio). Si comes atún, modera la cantidad.",
            "Si comes embutidos/jamón curado, mejor solo si está bien cocinado o si tu equipo sanitario lo considera seguro en tu zona.",
            "Hierro: legumbres, carnes bien cocidas y hojas verdes; combina con vitamina C (cítricos) para mejorar absorción.",
            "Suplementos (ácido fólico, hierro, yodo, etc.) solo según pauta: no te automediques.",
        ],
    },
    "ejercicio": {
        "titulo": "Ejercicio seguro",
        "puntos": [
            "Caminar, natación o yoga prenatal suelen ser adecuados si tu médico lo autoriza.",
            "Evita deportes de contacto, caídas o sobrecalentamiento extremo.",
            "Hidrátate y detente si hay dolor, mareos o sangrado.",
        ],
    },
    "alertas": {
        "titulo": "Señales de alerta — acude a urgencias o llama a tu centro",
        "puntos": [
            "Sangrado vaginal abundante o con coágulos.",
            "Dolor abdominal intenso o contracciones regulares antes de tiempo.",
            "Disminución notable de movimientos fetales respecto a lo habitual para ti.",
            "Cefalea intensa, visión borrosa, hinchazón súbita de cara o manos (posible preeclampsia).",
            "Fiebre alta o pérdida de líquido en gran cantidad.",
        ],
    },
    "sueno": {
        "titulo": "Descanso y sueño",
        "puntos": [
            "El cansancio es frecuente; intenta acostarte y levantarte a horas similares.",
            "Evita cafeína por la tarde si te cuesta dormir; hidrátate por la mañana.",
            "Una almohada entre las rodillas o bajo el vientre puede aliviar la espalda al dormir de lado.",
            "Si los ronquidos son nuevos y fuertes o hay pausas al respirar, coméntalo en consulta.",
            "Pantallas apagadas una hora antes de dormir ayudan a regular el ritmo.",
        ],
    },
    "hidratacion": {
        "titulo": "Agua e hidratación",
        "puntos": [
            "Beber agua regularmente favorece circulación, digestión y el líquido amniótico.",
            "Lleva una botella reutilizable y reparte la ingesta a lo largo del día.",
            "En calor o tras caminar, aumenta un poco el líquido salvo indicación médica contraria.",
            "Limita bebidas muy azucaradas y energéticas.",
            "Orina de color muy oscuro puede indicar deshidratación: sube el agua y consulta si hay ardor o dolor.",
        ],
    },
    "dental": {
        "titulo": "Salud bucal",
        "puntos": [
            "Las encías pueden sangrar más por hormonas; mantén higiene suave y visita al dentista si persiste.",
            "Usa pasta con flúor y cepillo de cerdas medias; no olvides la seda dental.",
            "Ante tratamientos dentales, informa siempre que estás embarazada.",
            "Vómitos frecuentes: enjuaga con agua y espera unos minutos antes de cepillar para no dañar el esmalte.",
        ],
    },
    "piel_sol": {
        "titulo": "Piel y sol",
        "puntos": [
            "La piel puede ser más sensible; usa protector solar y sombrero en exterior.",
            "Manchas del embarazo (melasma) pueden oscurecerse con el sol: protección es clave.",
            "Hidrata la piel del vientre y pecho con cremas suaves si te apetece (no previenen estrías al 100%).",
            "Evita sol fuerte en las horas centrales del día.",
        ],
    },
    "viajes": {
        "titulo": "Viajes y movilidad",
        "puntos": [
            "En coche o avión, levántate a caminar cada hora o dos si tu médico lo permite.",
            "Lleva documentación médica y contacto de tu centro por si acaso.",
            "Cinturón de seguridad: banda bajo el abdomen, diagonal entre los pechos.",
            "Consulta restricciones aéreas según semana y embarazo de riesgo.",
        ],
    },
    "lactancia_previa": {
        "titulo": "Preparación para la lactancia",
        "puntos": [
            "Informarte antes del parto reduce la ansiedad: grupos preparto o matrona pueden orientarte.",
            "El agarre correcto evita grietas; pide ayuda en las primeras tomas.",
            "Lactancia a demanda suele ser lo habitual al inicio; cada bebé marca su ritmo.",
            "Si no puedes o no deseas lactar, la alimentación con fórmula también es válida con apoyo pediátrico.",
        ],
    },
    "postparto": {
        "titulo": "Primeros días tras el nacimiento",
        "puntos": [
            "Descansa cuando el bebé duerme; los quehaceres pueden esperar un poco.",
            "Sangrado vaginal (lochia) es normal al inicio; si huele mal o hay fiebre, avisa.",
            "Dolor al orinar, pechos muy calientes con fiebre o ideas de daño requieren valoración urgente.",
            "Pide ayuda en casa; delegar es parte del cuidado de ti y del bebé.",
        ],
    },
    "vacunas": {
        "titulo": "Vacunas e inmunización (orientación general)",
        "puntos": [
            "Las recomendaciones dependen del país y de tu historial; sigue el calendario de tu centro de salud.",
            "La vacuna de la tosferina en embarazo se recomienda en muchos países para proteger al recién nacido.",
            "La vacuna antigripal suele indicarse en temporada; pregunta en tu consulta.",
            "No te automediques ni evites vacunas por miedo sin hablar con un profesional.",
        ],
    },
    "pareja_familia": {
        "titulo": "Pareja, familia y límites",
        "puntos": [
            "Comunicar expectativas sobre visitas tras el parto evita tensiones.",
            "El acompañante puede participar en cursos preparto y en el cuidado práctico.",
            "No estás obligada a aceptar consejos no solicitados; un 'gracias, lo consulto con mi médico' basta.",
            "Reserva tiempo para la pareja o para ti sola, aunque sean minutos.",
        ],
    },
}

EMOTIONAL_TIPS = [
    "Respira hondo: cada etapa pasa; pide ayuda cuando la necesites.",
    "Duerme cuando puedas; el descanso es parte del cuidado de tu bebé y tuyo.",
    "Habla con personas de confianza; compartir miedos normales alivia la carga.",
    "Escribe en un diario tres cosas por las que te sientas agradecida hoy.",
    "Los cambios hormonales afectan el ánimo; no eres 'exagerada' por sentirte distinta.",
]

# Mini-guía para responder preguntas tipo "¿puedo comer X?".
# Nota: orientación general; puede variar por país, análisis (toxoplasma), semanas y recomendaciones médicas.
NUTRITION_FAQ = [
    {
        "keys": ("sushi", "ceviche", "tartar", "carpaccio", "pescado crudo", "pescado sin cocinar", "pescado poco hecho"),
        "titulo": "Pescado crudo (sushi/ceviche/tartar)",
        "respuesta": (
            "En el embarazo se recomienda evitar pescado crudo o poco hecho por el riesgo de bacterias y parásitos. "
            "Si te apetece, una alternativa es elegir sushi de verduras o de pescado bien cocido."
        ),
    },
    {
        "keys": ("huevo crudo", "huevos crudos", "mayonesa casera", "mousse", "tiramisú", "tiramisu"),
        "titulo": "Huevo crudo / mayonesa casera",
        "respuesta": (
            "Mejor evitar huevo crudo o preparaciones con huevo crudo (incluida mayonesa casera) por riesgo de salmonela. "
            "El huevo bien cuajado y la mayonesa industrial pasteurizada suelen ser opciones más seguras."
        ),
    },
    {
        "keys": ("queso fresco", "queso blando", "brie", "camembert", "roquefort", "gorgonzola", "queso sin pasteurizar", "leche cruda"),
        "titulo": "Quesos blandos / no pasteurizados",
        "respuesta": (
            "Evita lácteos no pasteurizados y quesos blandos si no son pasteurizados, por riesgo de listeria. "
            "Busca que indique 'pasteurizado' en la etiqueta."
        ),
    },
    {
        "keys": ("jamón", "jamon", "embutido", "chorizo", "salchichón", "salchichon", "fuet", "mortadela", "pavo fiambre", "fiambre"),
        "titulo": "Jamón/embutidos",
        "respuesta": (
            "Con embutidos y jamón curado hay que tener precaución por riesgo de toxoplasma y listeria (según producto y país). "
            "Si no tienes la inmunidad confirmada o no estás segura, una opción más prudente es tomarlos bien cocinados (por ejemplo, a la plancha) "
            "o elegir alternativas cocidas/envasadas que indique tu profesional."
        ),
    },
    {
        "keys": ("café", "cafe", "te", "té", "mate", "cola", "energética", "energetica"),
        "titulo": "Cafeína (café/té/energéticas)",
        "respuesta": (
            "La cafeína se suele limitar en el embarazo. Si preguntas por una cantidad concreta (tazas al día) "
            "dime qué tomas y cuánto, y te doy una orientación general; para un límite exacto, sigue la recomendación de tu médico."
        ),
    },
    {
        "keys": ("atún", "atun", "pez espada", "emperador", "tiburón", "tiburon", "cazón", "cazon", "lucio", "mercurio"),
        "titulo": "Pescados con mercurio (atún/pez espada, etc.)",
        "respuesta": (
            "En el embarazo se recomienda evitar o limitar pescados grandes por mercurio (pez espada/emperador, tiburón/cazón, lucio). "
            "El atún suele recomendarse con moderación; si me dices si es atún en lata o fresco y la frecuencia, lo ajusto mejor."
        ),
    },
    {
        "keys": ("hígado", "higado", "paté", "pate", "vitamina a", "retinol"),
        "titulo": "Hígado/paté y vitamina A",
        "respuesta": (
            "Mejor evitar hígado y patés (y suplementos con vitamina A/retinol) en exceso durante el embarazo. "
            "Si es un suplemento, consúltalo siempre con tu médico."
        ),
    },
    {
        "keys": ("alcohol", "vino", "cerveza", "licor"),
        "titulo": "Alcohol",
        "respuesta": (
            "La recomendación general es evitar alcohol durante el embarazo."
        ),
    },
]

# Fecha probable de parto (orientativa): FUM + 280 días (regla de Naegele simplificada).
def fecha_probable_parto(fum: date) -> date:
    return fum + timedelta(days=280)


MENSAJES_DIARIOS = [
    "Hoy respira hondo: tu cuerpo está haciendo un trabajo silencioso y enorme.",
    "Un vaso de agua y cinco minutos de calma cuentan más de lo que crees.",
    "No tienes que tenerlo todo bajo control; solo hoy, un paso a la vez.",
    "Eres la casa perfecta para quien está creciendo dentro: eso ya es muchísimo.",
    "Permítete descansar sin culpa: el descanso también nutre a tu bebé.",
    "Lo que sientes importa; hablar con alguien de confianza es un acto de cuidado.",
    "Cada día que pasa es una nueva página de esta historia única.",
    "Tu intuición y tu equipo médico son un buen equipo: pregunta todo lo que necesites.",
    "Pequeños rituales (un té, una canción, una caricia al vientre) anclan el bienestar.",
    "Hoy celebra una cosa pequeña que tu cuerpo sí pudo hacer.",
    "La comparación con otras embarazadas no define tu camino; el tuyo es válido.",
    "Hidrátate, suaviza los hombros y suelta la mandíbula: ya estás haciendo bastante.",
    "Escribir una línea en un diario puede ordenar emociones que pesan.",
    "Pedir ayuda no te hace menos fuerte; te hace humana y sabia.",
    "Tu bebé no necesita perfección; necesita amor y cuidado, y eso ya lo tienes.",
]

MENSAJES_ETAPA_SIN_FUM = [
    "Cuando registres tu FUM, podremos acompañarte semana a semana con información personalizada.",
    "Mientras tanto, confía en tu intuición y en los consejos de tu profesional de salud.",
]

MENSAJES_ETAPA_PRIMERO = [
    "Primer trimestre: muchas novedades en poco tiempo. Sé amable contigo en los días de cansancio.",
    "Es normal sentirse entre la ilusión y el agotamiento; ambas cosas pueden convivir.",
    "Prioriza lo esencial: descanso, alimentación sencilla y seguimiento médico.",
    "Si las náuseas aprietan, prueba comidas pequeñas y frecuentes.",
]

MENSAJES_ETAPA_SEGUNDO = [
    "Segundo trimestre: a menudo llega más energía. Aprovéchala sin exigirte al máximo.",
    "Es un buen momento para hablar con tu bebé, poner música suave o soñar en voz alta.",
    "Mantén la hidratación y el movimiento suave si tu médico lo aprueba.",
    "Las molestias pueden cambiar; lo que ayer era incómodo puede mejorar pronto.",
]

MENSAJES_ETAPA_TERCERO = [
    "Tercer trimestre: el cuerpo se prepara para el encuentro. Descansa en posturas que alivien.",
    "Prepara la mochila o bolsa con calma; cada cosa lista es un abrazo a tu yo del futuro.",
    "Las contracciones de práctica son frecuentes; ante dudas, consulta sin esperar.",
    "Cada semana acerca el abrazo: respira, pide apoyo y confía en tu equipo.",
]

MENSAJES_ETAPA_POSTERIOR = [
    "Has llegado a la fecha estimada o más allá: tu médico o matrona te guiarán en los siguientes pasos.",
    "La espera final puede ser intensa; distrácte con cosas que te calmen y mantén contacto con tu centro.",
]


def _seed_del_dia() -> int:
    h = hashlib.sha256(date.today().isoformat().encode("utf-8")).hexdigest()
    return int(h[:14], 16)


def mensaje_del_dia_payload(
    semana: Optional[int],
    nombre_bebe: str = "",
    sexo_bebe: str = "desconocido",
) -> dict:
    """Mensajes estables durante el mismo día (cambian a medianoche)."""
    seed = _seed_del_dia()
    diario = MENSAJES_DIARIOS[seed % len(MENSAJES_DIARIOS)]

    if semana is None or semana < 1:
        etapa_list = MENSAJES_ETAPA_SIN_FUM
    elif semana < 14:
        etapa_list = MENSAJES_ETAPA_PRIMERO
    elif semana < 28:
        etapa_list = MENSAJES_ETAPA_SEGUNDO
    elif semana <= 42:
        etapa_list = MENSAJES_ETAPA_TERCERO
    else:
        etapa_list = MENSAJES_ETAPA_POSTERIOR

    etapa = etapa_list[(seed // 1000) % len(etapa_list)]

    nb = (nombre_bebe or "").strip()
    extra = f" Hoy puedes dedicarle un pensamiento cariñoso a {nb}." if nb else ""

    return {
        "fecha": date.today().isoformat(),
        "mensaje_diario": diario + extra,
        "mensaje_etapa": etapa,
    }
