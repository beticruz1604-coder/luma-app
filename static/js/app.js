(function () {
  "use strict";

  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));

  async function api(path, opts = {}) {
    const r = await fetch(path, {
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      ...opts,
    });
    const text = await r.text();
    let data;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = null;
    }
    if (!r.ok) {
      const err = (data && data.error) || r.statusText || "Error";
      if (err === "subscription_required") {
        throw new Error("Tu suscripción no está activa. Renueva en la pestaña Suscripción.");
      }
      throw new Error(err);
    }
    return data;
  }

  async function fetchSuscripcionEstado() {
    const r = await fetch("/api/suscripcion", { headers: { Accept: "application/json" } });
    return r.json();
  }

  function showMainAppChrome() {
    document.body.classList.remove("app-locked");
  }

  function syncThemeColorMeta() {
    const m = document.querySelector('meta[name="theme-color"]');
    if (!m) return;
    const th = document.body.getAttribute("data-baby-theme") || "neutral";
    const map = { neutral: "#d4528a", nina: "#e84890", nino: "#2e9edb" };
    m.setAttribute("content", map[th] || map.neutral);
  }

  function applyPlaceholdersSinSub() {
    $("#semanaNum").textContent = "—";
    $("#semanaSub").textContent = "Activa tu suscripción para ver tu semana y el seguimiento.";
    $("#textoBebe").textContent = "Con plan activo verás aquí el desarrollo semana a semana.";
    $("#textoMadre").textContent = "—";
    $("#countdownBig").textContent = "—";
    $("#countdownSub").textContent = "Necesitas FUM en el perfil y suscripción activa para la cuenta atrás.";
    $("#mensajeDiario").textContent = "Los mensajes diarios se mostrarán cuando actives tu suscripción.";
    $("#mensajeEtapa").textContent = "Flujo: guarda tu perfil → elige plan → disfruta la app.";
    const cx = $("#consejoExtra");
    if (cx) {
      cx.hidden = true;
      cx.textContent = "";
    }
    const ht = $("#heroBannerText");
    if (ht) ht.textContent = "Primero completa tu perfil; activa tu plan en la pestaña Suscripción.";
    const leg = $("#heroLegend");
    if (leg) leg.textContent = "Con suscripción activa verás el crecimiento ilustrado según tu semana.";
    const wrap = $("#heroBabyWrap");
    if (wrap) wrap.style.setProperty("--baby-scale", "0.18");
    const ff = $("#heroFruitFloat");
    if (ff) ff.textContent = "🌸";
    const face = $("#heroBabyFace");
    if (face) face.textContent = "👶";
    const stats = $("#growthStats");
    if (stats) stats.hidden = true;
    const lead = $("#babyGrowthLead");
    if (lead) lead.textContent = "Con plan activo: tamaño, peso y comparación divertida con frutas.";
    const emojiEl = $("#babyGrowthEmoji");
    if (emojiEl) emojiEl.textContent = "🤰";
  }

  function todayISODate() {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }

  function setPanel(id) {
    $$(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.panel === id));
    $$(".panel").forEach((p) => {
      const on = p.id === "panel-" + id;
      p.classList.toggle("active", on);
      p.hidden = !on;
    });
    const nav = $("#mainNav");
    const toggle = $("#navToggle");
    if (nav && toggle) {
      nav.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    }
    if (id === "suscripcion") loadSubPanel();
  }

  function initNav() {
    $$(".nav-btn").forEach((btn) => {
      btn.addEventListener("click", () => setPanel(btn.dataset.panel));
    });
    const toggle = $("#navToggle");
    const nav = $("#mainNav");
    if (toggle && nav) {
      toggle.addEventListener("click", () => {
        const open = !nav.classList.contains("open");
        nav.classList.toggle("open", open);
        toggle.setAttribute("aria-expanded", String(open));
      });
    }
  }

  function applyBabyTheme(sexo) {
    const map = { desconocido: "neutral", nina: "nina", nino: "nino" };
    document.body.setAttribute("data-baby-theme", map[sexo] || "neutral");
    syncThemeColorMeta();
  }

  function formatDateES(iso) {
    if (!iso) return "";
    const d = new Date(iso + "T12:00:00");
    return d.toLocaleDateString("es", { day: "numeric", month: "long", year: "numeric" });
  }

  async function loadPerfil() {
    const p = await api("/api/profile");
    $("#nombreMadre").value = p.nombre_madre || "";
    $("#fechaFum").value = p.fecha_fum || "";
    $("#nombreBebe").value = p.nombre_bebe || "";
    $("#sexoBebe").value = p.sexo_bebe || "desconocido";
    applyBabyTheme($("#sexoBebe").value);
    return p;
  }

  async function loadSubPanel() {
    try {
      const s = await fetchSuscripcionEstado();
      const t = $("#subEstadoTexto");
      const x = $("#subEstadoExtra");
      const alta = $("#subCardAlta");
      const ren = $("#subCardRenovar");
      if (!t) return;
      if (s.activa) {
        if (alta) alta.hidden = true;
        if (ren) ren.hidden = false;
        const planLabels = {
          mensual: "Mensual",
          trimestral: "Trimestral",
          semestral: "Semestral",
          embarazo_completo: "Embarazo completo (9 meses)",
          anual: "Anual",
        };
        const planTxt = planLabels[s.plan] || (s.plan ? s.plan : "Activo");
        t.textContent = "Tienes un plan " + planTxt + " en curso.";
        x.textContent = s.hasta
          ? "Vigencia hasta el " + formatDateES(s.hasta) + "."
          : "";
      } else {
        if (alta) alta.hidden = false;
        if (ren) ren.hidden = true;
        t.textContent = "No hay suscripción activa.";
        x.textContent =
          "Completa el formulario de abajo para activar tu plan y usar todas las funciones.";
      }
    } catch (e) {
      console.error(e);
    }
  }

  const FRUIT_EMOJI = {
    1: "🌱",
    4: "✨",
    8: "🫐",
    12: "🍇",
    16: "🥑",
    20: "🍌",
    24: "🌽",
    28: "🍆",
    32: "🍍",
    36: "🍈",
    40: "🍉",
  };

  async function loadSeguimiento() {
    const s = await api("/api/seguimiento");
    const sem = s.semana;
    const ref = s.bloque_referencia_semana;

    if (s.sexo_bebe) applyBabyTheme(s.sexo_bebe);

    $("#semanaNum").textContent = sem != null ? String(sem) : "—";
    $("#semanaSub").textContent =
      sem != null
        ? "Resumen basado en bloques por semana (referencia: semana " + (ref || sem) + ")"
        : "Configura tu FUM en el perfil.";
    $("#textoBebe").textContent = s.desarrollo_bebe || "—";
    $("#textoMadre").textContent = s.cambios_madre || "—";

    $("#mensajeDiario").textContent = s.mensaje_diario || "—";
    $("#mensajeEtapa").textContent = s.mensaje_etapa || "—";
    const consejoX = $("#consejoExtra");
    if (consejoX) {
      consejoX.hidden = true;
      consejoX.textContent = "";
    }

    const cb = $("#countdownBig");
    const cs = $("#countdownSub");
    if (!s.fecha_probable_parto) {
      cb.textContent = "—";
      cs.textContent =
        "Indica tu FUM para estimar la fecha probable de parto (40 semanas desde la FUM, orientativo).";
    } else {
      const d = s.dias_hasta_parto_aprox;
      const fs = formatDateES(s.fecha_probable_parto);
      if (d > 1) {
        cb.textContent = "Quedan " + d + " días";
        cs.textContent = "Fecha probable de parto (orientativa): " + fs + ". Tu médico puede ajustarla.";
      } else if (d === 1) {
        cb.textContent = "¡Queda 1 día!";
        cs.textContent = "FPP orientativa: " + fs + ". Ante síntomas de parto, contacta a tu centro.";
      } else if (d === 0) {
        cb.textContent = "¡Hoy es la fecha estimada!";
        cs.textContent = "FPP orientativa: " + fs + ". Tu equipo de salud te indicará los siguientes pasos.";
      } else {
        cb.textContent = Math.abs(d) + " días después de la FPP";
        cs.textContent =
          "La fecha probable orientativa fue el " +
          fs +
          ". Consulta con tu matrona o médico para el seguimiento.";
      }
    }

    const wrap = $("#heroBabyWrap");
    const w = sem == null ? 0 : sem;
    const scale = Math.min(1, Math.max(0.12, (w / 40) * 0.9 + 0.1));
    if (wrap) wrap.style.setProperty("--baby-scale", String(scale));

    const sexo = s.sexo_bebe || "desconocido";
    let face = "👶";
    if (sexo === "nina") face = "👧";
    else if (sexo === "nino") face = "👦";
    const faceEl = $("#heroBabyFace");
    if (faceEl) faceEl.textContent = face;

    const fruitEl = $("#heroFruitFloat");
    if (fruitEl) {
      const key = ref != null && FRUIT_EMOJI[ref] != null ? ref : sem;
      fruitEl.textContent =
        key != null && FRUIT_EMOJI[key] != null
          ? FRUIT_EMOJI[key]
          : sem != null
            ? "👶"
            : "🌸";
    }

    const nb = (s.nombre_bebe || "").trim();
    const heroTxt = $("#heroBannerText");
    if (heroTxt) {
      if (nb && sem != null) {
        heroTxt.textContent =
          "¡" + nb + " va creciendo! Semana " + sem + " — un poquito más cada día.";
      } else if (sem != null) {
        heroTxt.textContent = "Semana " + sem + ": tu bebé sigue creciendo dentro de ti.";
      } else {
        heroTxt.textContent = "Cada semana es un paso lleno de vida.";
      }
    }

    const leg = $("#heroLegend");
    if (leg) {
      leg.textContent =
        sem != null && s.comparacion_fruta
          ? "Referencia divertida de tamaño: " + s.comparacion_fruta + "."
          : "Vista ilustrativa: al registrar la FUM, el dibujo crecerá semana a semana.";
    }

    const stats = $("#growthStats");
    const lead = $("#babyGrowthLead");
    const emojiEl = $("#babyGrowthEmoji");
    if (sem != null && s.tamaño_aprox) {
      stats.hidden = false;
      lead.textContent =
        "Referencia orientativa: cada bebé crece a su ritmo; tu ecografía y tu médico son la guía más fiable.";
      $("#growthTamano").textContent = s.tamaño_aprox || "—";
      $("#growthPeso").textContent = s.peso_aprox_g || "—";
      $("#growthFruta").textContent = s.comparacion_fruta || "—";
      const gkey = ref != null && FRUIT_EMOJI[ref] != null ? ref : sem;
      emojiEl.textContent = FRUIT_EMOJI[gkey] || FRUIT_EMOJI[12] || "👶";
    } else {
      stats.hidden = true;
      lead.textContent =
        "Indica tu FUM para ver tamaño aproximado, peso orientativo y una comparación divertida con frutas.";
      emojiEl.textContent = "🤰";
    }
  }

  async function guardarPerfil() {
    const msg = $("#perfilMsg");
    msg.textContent = "";
    const nombre = $("#nombreMadre").value.trim();
    if (!nombre) {
      msg.textContent = "Por favor escribe tu nombre.";
      $("#nombreMadre").focus();
      return;
    }
    try {
      await api("/api/profile", {
        method: "POST",
        body: JSON.stringify({
          nombre_madre: nombre,
          fecha_fum: $("#fechaFum").value || null,
        }),
      });
      msg.textContent = "Perfil guardado.";
      const sub = await fetchSuscripcionEstado();
      if (!sub.activa) {
        msg.textContent = "Perfil guardado. Activa tu plan en la pestaña Suscripción.";
        applyPlaceholdersSinSub();
        await loadSubPanel();
        setPanel("suscripcion");
        return;
      }
      await loadSeguimiento();
    } catch (e) {
      msg.textContent = e.message || "No se pudo guardar.";
    }
  }

  async function guardarBebe() {
    const msg = $("#bebeMsg");
    if (!msg) return;
    msg.textContent = "";
    try {
      await api("/api/profile", {
        method: "POST",
        body: JSON.stringify({
          nombre_bebe: $("#nombreBebe").value.trim(),
          sexo_bebe: $("#sexoBebe").value,
        }),
      });
      msg.textContent = "Datos del bebé guardados.";
      applyBabyTheme($("#sexoBebe").value);
      const sub = await fetchSuscripcionEstado();
      if (sub.activa) await loadSeguimiento();
    } catch (e) {
      msg.textContent = e.message || "No se pudo guardar.";
    }
  }

  function appendChat(role, text) {
    const log = $("#chatLog");
    const div = document.createElement("div");
    div.className = "chat-bubble " + (role === "user" ? "user" : "luma");
    div.textContent = text;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  async function sendChat(e) {
    e.preventDefault();
    const input = $("#chatInput");
    const t = input.value.trim();
    if (!t) return;
    appendChat("user", t);
    input.value = "";
    try {
      const res = await api("/api/luma/chat", {
        method: "POST",
        body: JSON.stringify({ message: t }),
      });
      appendChat("luma", res.reply || "…");
    } catch (err) {
      appendChat("luma", "No pude responder ahora. Intenta de nuevo.");
    }
  }

  async function loadPesos() {
    const list = $("#listaPesos");
    list.innerHTML = "";
    const rows = await api("/api/pesos");
    rows.forEach((r) => {
      const li = document.createElement("li");
      li.textContent = `${r.fecha}: ${r.peso_kg} kg`;
      list.appendChild(li);
    });
  }

  async function loadPresion() {
    const list = $("#listaPresion");
    list.innerHTML = "";
    const rows = await api("/api/presion");
    rows.forEach((r) => {
      const li = document.createElement("li");
      li.textContent = `${r.fecha}: ${r.sistolica}/${r.diastolica} mmHg`;
      list.appendChild(li);
    });
  }

  async function loadCitas() {
    const list = $("#listaCitas");
    list.innerHTML = "";
    const rows = await api("/api/citas");
    rows.forEach((r) => {
      const li = document.createElement("li");
      li.textContent = `${r.fecha_hora.slice(0, 16).replace("T", " ")} — ${r.titulo}`;
      list.appendChild(li);
    });
  }

  async function loadMeds() {
    const list = $("#listaMeds");
    list.innerHTML = "";
    const rows = await api("/api/medicamentos");
    rows.forEach((r) => {
      const li = document.createElement("li");
      li.textContent = `${r.nombre}${r.frecuencia ? " · " + r.frecuencia : ""}`;
      list.appendChild(li);
    });
  }

  async function loadRecs() {
    const list = $("#listaRec");
    list.innerHTML = "";
    const rows = await api("/api/recordatorios");
    rows.forEach((r) => {
      const li = document.createElement("li");
      const left = document.createElement("span");
      left.innerHTML = `<strong>${r.titulo}</strong><br/><small>${r.fecha_hora.slice(0, 16).replace("T", " ")} · ${r.categoria}${r.hecho ? " ✓" : ""}</small>`;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "small";
      btn.textContent = r.hecho ? "Desmarcar" : "Hecho";
      btn.addEventListener("click", async () => {
        await api("/api/recordatorios", {
          method: "PATCH",
          body: JSON.stringify({ id: r.id, hecho: !r.hecho }),
        });
        loadRecs();
      });
      li.appendChild(left);
      li.appendChild(btn);
      list.appendChild(li);
    });
  }

  async function loadEdu(seccion) {
    const data = await api("/api/educacion/" + seccion);
    $("#eduTitulo").textContent = data.titulo;
    const ul = $("#eduLista");
    ul.innerHTML = "";
    (data.puntos || []).forEach((p) => {
      const li = document.createElement("li");
      li.textContent = p;
      ul.appendChild(li);
    });
  }

  async function loadBienestar() {
    const b = await api("/api/bienestar");
    $("#mensajePositivo").textContent = b.mensaje_positivo;
    $("#consejoEstres").textContent = b.consejo_estres;
  }

  function initEduTabs() {
    $$(".tab-mini").forEach((tab) => {
      tab.addEventListener("click", () => {
        $$(".tab-mini").forEach((t) => {
          t.classList.toggle("active", t === tab);
          t.setAttribute("aria-selected", t === tab ? "true" : "false");
        });
        loadEdu(tab.dataset.edu);
      });
    });
  }

  function initForms() {
    $("#pesoFecha").value = todayISODate();
    $("#paFecha").value = todayISODate();

    $("#btnGuardarPerfil").addEventListener("click", guardarPerfil);
    const btnBebe = $("#btnGuardarBebe");
    if (btnBebe) btnBebe.addEventListener("click", guardarBebe);
    $("#sexoBebe").addEventListener("change", () => applyBabyTheme($("#sexoBebe").value));

    const btnIrPerfil = $("#btnSubIrPerfil");
    if (btnIrPerfil) {
      btnIrPerfil.addEventListener("click", () => {
        setPanel("inicio");
        const n = $("#nombreMadre");
        if (n) n.focus();
      });
    }

    $("#formSuscripcion").addEventListener("submit", async (e) => {
      e.preventDefault();
      const msg = $("#subAltaMsg");
      if (msg) msg.textContent = "";
      try {
        const res = await fetch("/api/suscripcion/pagar", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({
            plan: $("#subPlan").value,
            titular_tarjeta: $("#subTitular").value.trim(),
            ultimos_4_digitos: $("#subDigitos").value.trim(),
          }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          if (msg) msg.textContent = data.error || "No se pudo completar.";
          return;
        }
        if (msg) msg.textContent = data.mensaje || "¡Listo!";
        showMainAppChrome();
        await loadAppAfterUnlock();
        setPanel("inicio");
      } catch (err) {
        if (msg) msg.textContent = err.message || "Error de red.";
      }
    });

    const formRen = $("#formRenovarSub");
    if (formRen) {
      formRen.addEventListener("submit", async (e) => {
        e.preventDefault();
        const msg = $("#subRenovarMsg");
        msg.textContent = "";
        try {
          const res = await fetch("/api/suscripcion/pagar", {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({
              plan: $("#subPlanRenovar").value,
              titular_tarjeta: $("#subTitularRenovar").value.trim(),
              ultimos_4_digitos: $("#subDigitosRenovar").value.trim(),
            }),
          });
          const data = await res.json().catch(() => ({}));
          if (!res.ok) {
            msg.textContent = data.error || "Error";
            return;
          }
          msg.textContent = "Plan actualizado hasta el " + formatDateES(data.hasta) + ".";
          await loadSubPanel();
        } catch (err) {
          msg.textContent = err.message || "Error";
        }
      });
    }

    $("#btnOtroConsejo").addEventListener("click", async () => {
      try {
        const r = await api("/api/consejo-aleatorio");
        const el = $("#consejoExtra");
        if (el && r.texto) {
          el.textContent = "Consejo extra: " + r.texto;
          el.hidden = false;
        }
      } catch (e) {
        console.error(e);
      }
    });

    $("#formPeso").addEventListener("submit", async (e) => {
      e.preventDefault();
      await api("/api/pesos", {
        method: "POST",
        body: JSON.stringify({
          fecha: $("#pesoFecha").value,
          peso_kg: parseFloat($("#pesoKg").value),
        }),
      });
      $("#pesoKg").value = "";
      loadPesos();
    });

    $("#formPresion").addEventListener("submit", async (e) => {
      e.preventDefault();
      await api("/api/presion", {
        method: "POST",
        body: JSON.stringify({
          fecha: $("#paFecha").value,
          sistolica: parseInt($("#paSis").value, 10),
          diastolica: parseInt($("#paDia").value, 10),
        }),
      });
      $("#paSis").value = "";
      $("#paDia").value = "";
      loadPresion();
    });

    $("#formCita").addEventListener("submit", async (e) => {
      e.preventDefault();
      const raw = $("#citaFechaHora").value;
      if (!raw) return;
      const iso = raw.length === 16 ? raw + ":00" : raw;
      await api("/api/citas", {
        method: "POST",
        body: JSON.stringify({
          fecha_hora: iso,
          titulo: $("#citaTitulo").value,
          notas: $("#citaNotas").value,
          tipo: "cita",
        }),
      });
      $("#citaTitulo").value = "";
      $("#citaNotas").value = "";
      loadCitas();
    });

    $("#formMed").addEventListener("submit", async (e) => {
      e.preventDefault();
      await api("/api/medicamentos", {
        method: "POST",
        body: JSON.stringify({
          nombre: $("#medNombre").value,
          frecuencia: $("#medFreq").value,
          notas: $("#medNotas").value,
        }),
      });
      $("#medNombre").value = "";
      $("#medFreq").value = "";
      $("#medNotas").value = "";
      loadMeds();
    });

    $("#formRec").addEventListener("submit", async (e) => {
      e.preventDefault();
      const raw = $("#recFechaHora").value;
      const iso = raw.length === 16 ? raw + ":00" : raw;
      await api("/api/recordatorios", {
        method: "POST",
        body: JSON.stringify({
          fecha_hora: iso,
          titulo: $("#recTitulo").value,
          categoria: $("#recCat").value,
        }),
      });
      $("#recTitulo").value = "";
      loadRecs();
    });

    $("#chatForm").addEventListener("submit", sendChat);
    $("#btnNuevoMensaje").addEventListener("click", loadBienestar);
  }

  async function loadAppAfterUnlock() {
    await loadPerfil();
    await loadSeguimiento();
    await loadPesos();
    await loadPresion();
    await loadCitas();
    await loadMeds();
    await loadRecs();
    await loadEdu("alimentacion");
    await loadBienestar();
    await loadSubPanel();
    const log = $("#chatLog");
    if (log && !sessionStorage.getItem("nl_luma_greet")) {
      sessionStorage.setItem("nl_luma_greet", "1");
      appendChat(
        "luma",
        "¡Hola! Soy Luma. Escribe lo que necesites; leeré tu mensaje y te contestaré sobre eso. Si algo es urgente, tu médico o urgencias son el sitio adecuado."
      );
    }
  }

  function hideSplash() {
    const sp = document.getElementById("splashScreen");
    if (!sp) return;
    sp.classList.add("splash-screen--hide");
    const remove = () => {
      sp.remove();
      document.body.classList.remove("splash-open");
    };
    sp.addEventListener("transitionend", remove, { once: true });
    setTimeout(remove, 600);
  }

  async function boot() {
    const splashStarted = performance.now();
    document.body.classList.add("splash-open");
    initNav();
    initForms();
    initEduTabs();
    syncThemeColorMeta();
    try {
      const sub = await fetchSuscripcionEstado();
      if (sub.activa) {
        showMainAppChrome();
        await loadAppAfterUnlock();
      } else {
        showMainAppChrome();
        await loadPerfil();
        await loadSubPanel();
        applyPlaceholdersSinSub();
      }
    } catch (e) {
      console.error(e);
      showMainAppChrome();
      try {
        await loadPerfil();
        await loadSubPanel();
      } catch (e2) {
        console.error(e2);
      }
      applyPlaceholdersSinSub();
    }
    const elapsed = performance.now() - splashStarted;
    await new Promise((r) => setTimeout(r, Math.max(0, 2000 - elapsed)));
    hideSplash();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
