// Vista del jugador como asistente paso a paso (RF-01 a RF-06, issue #62).
// Todo dato viene de la API; las reglas (franjas, límites, conflictos) las decide el servidor.

const $ = (id) => document.getElementById(id);
const DIAS_RAPIDOS = 7;
const LIMITE_CANCELACION_H = 6; // RN-13 (cambio del ciclo 3, D-11): debe coincidir con CANCEL_LIMIT_HOURS
const OFFSET_SEDE = "-05:00"; // America/Panama no tiene horario de verano

// ---------- Iconos (SVG en línea, sin dependencias) ----------
const TRAZOS = {
  cancha: '<rect x="3" y="5" width="18" height="14" rx="1"/><line x1="12" y1="5" x2="12" y2="19"/><circle cx="12" cy="12" r="3"/>',
  reloj: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  calendario: '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
  alerta: '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
  info: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
  equis: '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
  check: '<polyline points="20 6 9 17 4 12"/>',
  copiar: '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  lupa: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
};
function icono(nombre, tam = 18, grosor = 2) {
  const plantilla = document.createElement("template");
  plantilla.innerHTML = `<svg class="ico" width="${tam}" height="${tam}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${grosor}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${TRAZOS[nombre]}</svg>`;
  return plantilla.content.firstChild;
}
$("logo").append(icono("cancha", 16));

// ---------- Fechas en la hora de la sede ----------
function fmt(fecha, opciones) {
  const [a, m, d] = fecha.split("-").map(Number);
  return new Intl.DateTimeFormat("es", { timeZone: "UTC", ...opciones }).format(new Date(Date.UTC(a, m - 1, d)));
}
const fechaCorta = (f) => fmt(f, { weekday: "short", day: "numeric" }).replace(".", "");
const fechaMedia = (f) => fmt(f, { weekday: "short", day: "numeric", month: "short" }).replaceAll(".", "");
const hh = (hora) => Number(hora.slice(0, 2));
const finFranja = (hora) => `${String(hh(hora) + 1).padStart(2, "0")}:00`;
const rango = (hora) => `${hora} – ${finFranja(hora)}`;
const inicioReal = (fecha, hora) => new Date(`${fecha}T${hora}:00${OFFSET_SEDE}`);
function limiteCancelacion(fecha, hora) {
  const limite = new Date(inicioReal(fecha, hora).getTime() - LIMITE_CANCELACION_H * 3600000);
  const dia = new Intl.DateTimeFormat("es", { timeZone: ZONA, weekday: "long", day: "numeric", month: "long" }).format(limite);
  const hora2 = new Intl.DateTimeFormat("es", { timeZone: ZONA, hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(limite);
  return { fecha: limite, texto: `${dia} a las ${hora2}` };
}
function cuantoFalta(fecha) {
  const dias = Math.round((Date.parse(fecha) - Date.parse(hoyEnSede())) / 86400000);
  return dias <= 0 ? "es hoy" : dias === 1 ? "falta 1 día" : `faltan ${dias} días`;
}

// ---------- Estado ----------
const E = {
  vista: "reservar", paso: 1, canchas: [], cargandoCanchas: true, errorCanchas: "",
  cancha: null, fecha: hoyEnSede(), hora: null,
  nombre: "", telefono: "", tocado: false, erroresServidor: {},
  enviando: false, aviso: null, reserva: null,
  disp: {},
};
const enCurso = new Set();

function disponibilidad(cid, fecha) {
  const clave = `${cid}|${fecha}`;
  if (clave in E.disp) return E.disp[clave];
  if (!enCurso.has(clave)) {
    enCurso.add(clave);
    api("GET", `/api/canchas/${cid}/disponibilidad?fecha=${encodeURIComponent(fecha)}`)
      .then((d) => { E.disp[clave] = d; })
      .catch(() => { E.disp[clave] = null; })
      .finally(() => { enCurso.delete(clave); programar(); });
  }
  return undefined; // cargando
}
function olvidarDisponibilidad() { E.disp = {}; }

function conteo(datos) {
  if (!datos) return null;
  const vigentes = datos.franjas.filter((f) => !f.pasada);
  const libres = vigentes.filter((f) => f.estado === "libre").length;
  return { libres, vigentes: vigentes.length, ocupacion: vigentes.length ? Math.round((vigentes.length - libres) / vigentes.length * 100) : 100 };
}
const libresTxt = (n) => `${n} ${n === 1 ? "libre" : "libres"}`;
function tono(n) {
  if (n === 0) return { txt: "Sin cupo", c: "bad" };
  if (n <= 3) return { txt: `Quedan ${n}`, c: "warn" };
  return { txt: libresTxt(n), c: "ok" };
}
const canchaSel = () => E.canchas.find((c) => c.id === E.cancha) || null;
const diasRapidos = () => Array.from({ length: DIAS_RAPIDOS }, (_, i) => hoyEnSede(i));

let pendiente = false;
function programar() {
  if (pendiente) return;
  pendiente = true;
  requestAnimationFrame(() => { pendiente = false; render(); });
}

// ---------- Componentes ----------
function aviso(tipo, nombreIcono, titulo, texto, extra) {
  return el("div", { class: `aviso ${tipo}${extra ? " entre" : ""}`, role: tipo === "bad" ? "alert" : "status" },
    el("div", { style: "display: flex; gap: 10px; align-items: flex-start" }, icono(nombreIcono),
      el("div", {}, titulo ? el("strong", {}, titulo, " ") : null, texto)),
    extra || null);
}
const ficha = (texto, c) => el("span", { class: `ficha tono-${c}` }, el("span", { class: "punto", "aria-hidden": "true" }), texto);

// ---------- Render general ----------
function render() {
  const reservar = E.vista === "reservar";
  $("vista-reservar").classList.toggle("oculto", !reservar);
  $("vista-mia").classList.toggle("oculto", reservar);
  $("nav-reservar").removeAttribute("aria-current");
  $("nav-mia").removeAttribute("aria-current");
  $(reservar ? "nav-reservar" : "nav-mia").setAttribute("aria-current", "page");
  const titulo = reservar ? "Nueva reserva" : "Mi reserva";
  $("titulo").textContent = titulo;
  $("miga-actual").textContent = titulo;
  document.title = `${titulo} · Reserva tu cancha`;
  if (!reservar) return;
  renderKpis();
  renderPasos();
  renderResumen();
  // El paso 3 no se repinta con cada carga de datos para no perder lo que se está escribiendo.
  if (E.paso !== 3 || !$("principal").dataset.paso3) renderPrincipal();
}

function renderKpis() {
  const c = canchaSel();
  const datos = E.canchas.map((x) => conteo(disponibilidad(x.id, E.fecha)));
  const listos = datos.every((d) => d !== null && d !== undefined);
  const conCupo = datos.filter((d) => d && d.libres > 0).length;
  const libres = c ? conteo(disponibilidad(c.id, E.fecha)) : null;
  const totalLibres = c ? (libres ? libres.libres : null) : (listos ? datos.reduce((s, d) => s + d.libres, 0) : null);
  const t1 = !listos ? null : conCupo === E.canchas.length ? "ok" : conCupo === 0 ? "bad" : "warn";
  const t2 = totalLibres === null ? null : tono(totalLibres).c;
  const kpi = (ic, t, titulo, valor, sub) => el("div", { class: "kpi" },
    el("div", { class: `icono tono-${t || "info"}` }, icono(ic, 20)),
    el("div", { style: "min-width: 0" }, el("div", { class: "t" }, titulo), el("div", { class: "v" }, valor), el("div", { class: `s txt-${t || "info"}` }, sub)));
  $("kpis").replaceChildren(
    kpi("cancha", t1, `Canchas con cupo · ${fechaCorta(E.fecha)}`, listos ? `${conCupo} de ${E.canchas.length}` : "…",
      !listos ? "Cargando" : conCupo === E.canchas.length ? "Todas con horarios libres" : conCupo === 0 ? "Ninguna con cupo" : `${E.canchas.length - conCupo} sin cupo`),
    kpi("reloj", t2, `Horarios libres · ${c ? c.nombre : "todas las canchas"}`, totalLibres === null ? "…" : String(totalLibres),
      totalLibres === null ? "Cargando" : totalLibres === 0 ? "Sin cupo para esta fecha" : totalLibres <= 3 ? "Disponibilidad baja" : "Disponibilidad normal"),
    kpi("calendario", "info", "Política de cancelación", `${LIMITE_CANCELACION_H} h antes`, `Reservas hasta ${MAX_DIAS} días`));
}

const PASOS = ["Cancha", "Fecha y horario", "Datos del responsable", "Confirmación"];
function renderPasos() {
  $("barra-progreso").style.width = `${Math.round((E.paso - 1) / 3 * 100)}%`;
  $("texto-progreso").textContent = `Paso ${E.paso} de 4`;
  $("lista-pasos").replaceChildren(...PASOS.map((nombre, i) => {
    const n = i + 1, hecho = n < E.paso, actual = n === E.paso, navegable = hecho && E.paso < 4;
    return el("li", {}, el("button", {
      type: "button", class: `paso${actual ? " actual" : ""}${hecho ? " hecho" : ""}`,
      "aria-current": actual ? "step" : null, disabled: !navegable && !actual ? true : null,
      onclick: () => { if (navegable) irA(n); },
    },
    el("span", { class: "circulo" }, hecho ? icono("check", 14, 3) : String(n)),
    el("span", {}, el("span", { class: "l" }, nombre), el("span", { class: "s" }, actual ? "En curso" : hecho ? "Completado" : "Pendiente"))));
  }));
}

function renderResumen() {
  const c = canchaSel();
  const confirmada = E.paso === 4 && E.reserva;
  const estado = confirmada ? ["Confirmada", "ok"] : E.hora ? ["Horario elegido", "warn"] : ["Borrador", "info"];
  const badge = $("estado-resumen");
  badge.className = `ficha tono-${estado[1]}`;
  badge.textContent = estado[0];
  const filas = [
    ["Cancha", c ? c.nombre : "—"],
    ["Fecha", c && E.paso > 1 ? fechaMedia(E.fecha) : "—"],
    ["Horario", E.hora ? rango(E.hora) : "—"],
    ["Duración", "1 hora"],
  ];
  $("resumen").replaceChildren(...filas.flatMap(([k, v]) => [el("dt", {}, k), el("dd", {}, v)]));
  $("total").textContent = c ? dinero(c.precio_hora) : dinero(0);
  $("condiciones").replaceChildren(
    el("li", {}, icono("reloj", 16), "Franjas de 1 hora, de 08:00 a 22:00."),
    el("li", {}, icono("calendario", 16), `Reservas con hasta ${MAX_DIAS} días de anticipación.`),
    el("li", {}, icono("equis", 16), `Cancelación sin costo hasta ${LIMITE_CANCELACION_H} horas antes.`));
}

function irA(paso, avisoNuevo = null) {
  E.paso = paso;
  E.aviso = avisoNuevo;
  delete $("principal").dataset.paso3;
  render();
  if (window.matchMedia("(max-width: 900px)").matches) $("principal").scrollIntoView({ behavior: "smooth", block: "start" });
}

function pie({ atras = true, pista = "", etiqueta = "Continuar", habilitado = true, accion }) {
  return el("div", { class: "pie" },
    el("div", { class: "izq-pie" },
      atras ? el("button", { type: "button", class: "btn", onclick: () => irA(E.paso - 1) }, "Atrás") : null,
      pista ? el("span", { class: "pista" }, pista) : null),
    el("button", { type: "button", class: "btn primario", id: "btn-siguiente", disabled: !habilitado, onclick: accion }, etiqueta));
}

function cabecera(titulo, texto) {
  return el("div", { class: "seccion-cab" }, el("h2", {}, titulo), el("p", {}, texto));
}

function renderPrincipal() {
  const cont = $("principal");
  const vistas = { 1: paso1, 2: paso2, 3: paso3, 4: paso4 };
  cont.replaceChildren(...vistas[E.paso]());
  // En móvil la lista de días se desliza en horizontal: mantener visible el día elegido.
  const dia = cont.querySelector('.dia[aria-pressed="true"]');
  const lista = dia && dia.parentElement;
  if (lista && lista.scrollWidth > lista.clientWidth) lista.scrollLeft = dia.offsetLeft - lista.offsetLeft - 8;
}

// ---------- Paso 1: cancha ----------
function paso1() {
  const partes = [cabecera("1. Selecciona la cancha", `Disponibilidad para el ${fechaLarga(E.fecha)}. La fecha se puede cambiar en el siguiente paso.`)];
  const cuerpo = el("div", { class: "seccion-cuerpo" });
  if (E.cargandoCanchas) cuerpo.append(el("p", { class: "pista" }, "Cargando canchas…"));
  else if (E.errorCanchas) cuerpo.append(aviso("bad", "equis", "No se pudieron cargar las canchas.", E.errorCanchas));
  else if (!E.canchas.length) cuerpo.append(aviso("info", "info", "Todavía no hay canchas disponibles.", "Vuelve a intentarlo más tarde."));
  else {
    const filas = E.canchas.map((c) => {
      const d = conteo(disponibilidad(c.id, E.fecha));
      const t = d ? tono(d.libres) : null;
      const color = t ? `var(--${t.c === "ok" ? "accent" : t.c})` : "var(--faint)";
      return el("button", {
        type: "button", class: "fila-cancha", "aria-pressed": String(c.id === E.cancha),
        "aria-label": `${c.nombre}, ${c.deporte}, ${dinero(c.precio_hora)} por hora${t ? ", " + t.txt : ""}`,
        onclick: () => { if (E.cancha !== c.id) { E.cancha = c.id; E.hora = null; } render(); },
      },
      el("span", { class: "r" }, el("span", { class: "radio" })),
      el("span", { class: "nombre" }, c.nombre),
      el("span", { class: "dep" }, c.deporte),
      el("span", { class: "h" }, dinero(c.precio_hora), el("span", { style: "color: var(--muted)" }, " / h")),
      el("span", { class: "f" }, t ? ficha(t.txt, t.c) : el("span", { class: "pista" }, "…")),
      el("span", { class: "m medidor", style: `--m: ${color}` },
        el("span", { class: "barra" }, el("span", { style: `width: ${d ? d.ocupacion : 0}%` })),
        el("span", { class: "pct" }, d ? `${d.ocupacion}%` : "")));
    });
    cuerpo.append(el("div", { class: "tabla-canchas", role: "group", "aria-label": "Canchas" },
      el("div", { class: "enc", "aria-hidden": "true" }, el("span"), el("span", {}, "Cancha"), el("span", {}, "Deporte"), el("span", {}, "Tarifa"), el("span", {}, "Disponibilidad"), el("span", {}, "Ocupación del día")),
      ...filas));
    const c = canchaSel();
    const d = c ? conteo(disponibilidad(c.id, E.fecha)) : null;
    if (d && d.libres === 0) cuerpo.append(aviso("bad", "equis", "Cancha sin cupo ese día.", "Puedes seleccionarla y elegir otra fecha en el paso 2."));
  }
  partes.push(cuerpo, pie({ atras: false, pista: E.cancha ? "" : "Selecciona una cancha para continuar.", habilitado: !!E.cancha, accion: () => irA(2) }));
  return partes;
}

// ---------- Paso 2: fecha y horario ----------
function paso2() {
  const c = canchaSel();
  const partes = [cabecera("2. Selecciona fecha y horario", `${c.nombre} · franjas de 1 hora · hasta ${MAX_DIAS} días por adelantado.`)];
  const dias = diasRapidos();
  const lista = dias.map((f, i) => {
    const d = conteo(disponibilidad(c.id, f));
    const t = d ? tono(d.libres) : null;
    return el("button", {
      type: "button", class: "dia", "aria-pressed": String(f === E.fecha),
      onclick: () => { E.fecha = f; E.hora = null; E.aviso = null; render(); },
    }, el("span", {}, i === 0 ? `Hoy, ${fechaMedia(f)}` : fechaMedia(f)),
    t ? el("span", { class: `ficha tono-${t.c}` }, d.libres === 0 ? "Sin cupo" : libresTxt(d.libres)) : el("span", { class: "pista" }, "…"));
  });
  const otra = el("input", {
    type: "date", min: hoyEnSede(), max: hoyEnSede(MAX_DIAS), value: E.fecha, "aria-label": "Otra fecha",
    onchange: (ev) => { if (ev.target.value) { E.fecha = ev.target.value; E.hora = null; E.aviso = null; render(); } },
  });
  const columnaDias = el("div", { class: "dias", role: "group", "aria-label": "Fecha" },
    el("div", { class: "enc" }, "Fecha"),
    el("div", { class: "lista" }, ...lista),
    el("label", { class: "otra-fecha" }, "Otra fecha (hasta 30 días)", otra));

  const datos = disponibilidad(c.id, E.fecha);
  const derecha = el("div", { class: "horarios" });
  if (E.aviso) derecha.append(E.aviso);
  if (datos === undefined) derecha.append(el("p", { class: "pista" }, "Cargando horarios…"));
  else if (datos === null) derecha.append(aviso("bad", "equis", "No se pudieron cargar los horarios.", "Revisa tu conexión e inténtalo de nuevo."));
  else {
    const n = conteo(datos);
    if (n.libres === 0) {
      const sugerido = dias.find((f) => f !== E.fecha && (conteo(disponibilidad(c.id, f)) || { libres: 0 }).libres > 3);
      const boton = sugerido ? el("button", { type: "button", class: "btn peligro chico", onclick: () => { E.fecha = sugerido; E.hora = null; render(); } },
        `Ver ${fechaCorta(sugerido)} (${libresTxt(conteo(disponibilidad(c.id, sugerido)).libres)})`) : null;
      derecha.append(aviso("bad", "equis", "Sin horarios disponibles.", "Esta cancha no tiene cupo para la fecha seleccionada.", boton));
    } else if (n.libres <= 3) {
      derecha.append(aviso("warn", "alerta", "Disponibilidad baja:", n.libres === 1 ? "queda 1 horario para esta fecha." : `quedan ${n.libres} horarios para esta fecha.`));
    }
    if (E.fecha === hoyEnSede() && datos.franjas.some((f) => f.pasada) && n.libres > 0) {
      derecha.append(aviso("info", "info", "", "Los horarios de hoy que ya empezaron no están disponibles."));
    }
    derecha.append(
      el("div", { class: "horarios-cab" },
        el("h3", {}, `Horarios · ${fechaLarga(E.fecha)}`),
        el("div", { class: "leyenda", "aria-hidden": "true" },
          el("span", {}, el("i", { style: "border: 1.5px solid var(--ok-border)" }), "Libre"),
          el("span", {}, el("i", { style: "background: var(--accent)" }), "Seleccionado"),
          el("span", {}, el("i", { style: "background: var(--slot-occ); border: 1.5px solid var(--border-soft)" }), "Ocupado"),
          el("span", {}, el("i", { style: "border: 1.5px dashed var(--border)" }), "No disponible"))),
      el("div", { class: "rejilla", role: "group", "aria-label": "Horario" }, ...datos.franjas.map((f) => {
        const ocupada = f.estado !== "libre", pasada = f.pasada && !ocupada, sel = f.hora_inicio === E.hora;
        const sub = sel ? "Seleccionado" : pasada ? "No disponible" : ocupada ? "Ocupado" : "Libre";
        return el("button", {
          type: "button", class: `franja${ocupada ? " ocupada" : ""}${pasada ? " pasada" : ""}`,
          disabled: ocupada || f.pasada, "aria-pressed": String(sel), "aria-label": `${f.hora_inicio}, ${sub.toLowerCase()}`,
          onclick: () => { E.hora = f.hora_inicio; E.aviso = null; render(); },
        }, el("span", { class: "t" }, f.hora_inicio), el("span", { class: "s" }, sub));
      })));
  }
  partes.push(
    el("div", { class: "seccion-cuerpo" }, el("div", { class: "fecha-y-hora" }, columnaDias, derecha)),
    pie({ pista: E.hora ? "" : "Selecciona un horario disponible.", habilitado: !!E.hora, accion: () => irA(3) }));
  return partes;
}

// ---------- Paso 3: datos ----------
function validarNombre(v) {
  const limpio = v.trim().replace(/\s+/g, " ");
  if (!limpio) return "Ingresa tu nombre.";
  if (limpio.length < 2) return "El nombre debe tener al menos 2 caracteres.";
  if (limpio.length > 60) return "El nombre admite como máximo 60 caracteres.";
  return "";
}
function validarTelefono(v) {
  const digitos = v.replace(/\s/g, "");
  if (!digitos) return "Ingresa un teléfono.";
  if (/\D/.test(digitos)) return "El teléfono solo puede tener dígitos.";
  if (digitos.length < 7 || digitos.length > 15) return `El teléfono debe tener entre 7 y 15 dígitos (tiene ${digitos.length}).`;
  return "";
}

function campo(id, etiqueta, valor, atributos, validar, alCambiar) {
  const error = el("span", { class: "error", id: `${id}-error`, role: "alert" });
  const check = icono("check", 16, 3);
  check.classList.add("check");
  const entrada = el("input", { id, value: valor, "aria-describedby": `${id}-error`, ...atributos });
  const caja = el("div", { class: "entrada" }, entrada, check);
  const actualizar = () => {
    const msg = E.erroresServidor[id] || validar(entrada.value);
    const mostrar = E.tocado && msg;
    caja.classList.toggle("invalida", !!mostrar);
    caja.classList.toggle("valida", !msg);
    check.style.visibility = msg ? "hidden" : "visible";
    entrada.setAttribute("aria-invalid", mostrar ? "true" : "false");
    error.textContent = mostrar ? msg : "";
  };
  entrada.addEventListener("input", () => { delete E.erroresServidor[id]; alCambiar(entrada.value); actualizar(); });
  entrada.addEventListener("blur", () => { E.tocado = true; actualizar(); });
  actualizar();
  return { nodo: el("div", { class: "campo" }, el("label", { for: id }, etiqueta, " ", el("span", { class: "req", "aria-hidden": "true" }, "*")), caja, error), actualizar };
}

function paso3() {
  const c = canchaSel();
  $("principal").dataset.paso3 = "1";
  const nombre = campo("nombre", "Nombre", E.nombre, { autocomplete: "name", maxlength: "60", placeholder: "Ej. Ana Pérez" }, validarNombre, (v) => { E.nombre = v; });
  const telefono = campo("telefono", "Teléfono", E.telefono, { type: "tel", inputmode: "numeric", autocomplete: "tel", maxlength: "18", placeholder: "Solo dígitos" }, validarTelefono, (v) => { E.telefono = v; });
  const zonaAviso = el("div");
  if (E.aviso) zonaAviso.append(E.aviso);

  const enviar = async () => {
    E.tocado = true;
    nombre.actualizar(); telefono.actualizar();
    if (validarNombre(E.nombre) || validarTelefono(E.telefono)) { (validarNombre(E.nombre) ? $("nombre") : $("telefono")).focus(); return; }
    const boton = $("btn-siguiente");
    boton.disabled = true; boton.textContent = "Reservando…";
    zonaAviso.replaceChildren();
    try {
      E.reserva = await api("POST", "/api/reservas", { cuerpo: {
        cancha_id: c.id, fecha: E.fecha, hora_inicio: E.hora,
        nombre: E.nombre.trim().replace(/\s+/g, " "), telefono: E.telefono.replace(/\s/g, ""),
      }});
      olvidarDisponibilidad();
      irA(4);
    } catch (e) {
      if (e.codigo === "conflicto") {
        olvidarDisponibilidad();
        E.hora = null;
        irA(2, aviso("bad", "reloj", "Ese horario se acaba de ocupar.", "Elige otro horario para continuar."));
        return;
      }
      if (e.codigo === "validacion" && Object.keys(e.campos).length) {
        E.erroresServidor = { ...e.campos };
        nombre.actualizar(); telefono.actualizar();
      } else {
        zonaAviso.replaceChildren(aviso("bad", "equis", "No se pudo reservar.", e.message));
      }
      boton.disabled = false; boton.textContent = `Reservar · ${dinero(c.precio_hora)}`;
    }
  };

  return [
    cabecera("3. Datos del responsable", "Solo se requiere nombre y teléfono. No es necesario crear una cuenta."),
    el("div", { class: "seccion-cuerpo" },
      zonaAviso,
      el("div", {}, el("h3", { class: "subtitulo" }, "Selección"),
        el("div", { class: "cajas" },
          el("div", { class: "caja" }, el("div", { class: "t" }, "Cancha"), el("div", { class: "v" }, c.nombre)),
          el("div", { class: "caja" }, el("div", { class: "t" }, "Fecha"), el("div", { class: "v" }, fechaLarga(E.fecha))),
          el("div", { class: "caja" }, el("div", { class: "t" }, "Horario"), el("div", { class: "v" }, rango(E.hora))))),
      el("form", { novalidate: true, onsubmit: (ev) => { ev.preventDefault(); enviar(); } },
        el("h3", { class: "subtitulo" }, "Responsable"),
        el("div", { class: "campos" }, nombre.nodo, telefono.nodo),
        el("button", { type: "submit", class: "sr", tabindex: "-1" }, "Reservar")),
      aviso("info", "info", "", "El teléfono y el código de reserva se usarán para consultar o cancelar la reserva.")),
    pie({ etiqueta: `Reservar · ${dinero(c.precio_hora)}`, accion: enviar }),
  ];
}

// ---------- Paso 4: confirmación ----------
function paso4() {
  const r = E.reserva;
  const c = E.canchas.find((x) => x.id === r.cancha_id);
  const nombreCancha = c ? c.nombre : `Cancha ${r.cancha_id}`;
  const limite = limiteCancelacion(r.fecha, r.hora_inicio);
  const copiar = async () => {
    try { await navigator.clipboard.writeText(r.codigo); mostrarToast("Código copiado al portapapeles"); }
    catch { mostrarToast("No se pudo copiar; anótalo a mano"); }
  };
  return [
    cabecera("4. Confirmación", "Comprobante de la reserva."),
    el("div", { class: "seccion-cuerpo" },
      el("div", { class: "aviso ok", role: "status" },
        el("span", { style: "width: 32px; height: 32px; border-radius: 99px; background: var(--accent); color: var(--on-accent); display: grid; place-items: center; flex: 0 0 auto" }, icono("check", 16, 3)),
        el("div", {}, el("strong", { style: "display: block; font-size: 15px" }, "¡Reserva confirmada!"),
          `${nombreCancha} · ${fechaLarga(r.fecha)} · ${rango(r.hora_inicio)}`)),
      el("div", { class: "comprobante" },
        el("div", { class: "detalle" }, el("div", { class: "enc" }, "Detalle"),
          el("dl", { class: "tabla" },
            el("dt", {}, "Cancha"), el("dd", {}, nombreCancha),
            el("dt", {}, "Fecha"), el("dd", {}, fechaLarga(r.fecha)),
            el("dt", {}, "Horario"), el("dd", {}, rango(r.hora_inicio)),
            el("dt", {}, "A nombre de"), el("dd", {}, r.nombre),
            el("dt", {}, "Teléfono"), el("dd", {}, r.telefono),
            el("dt", {}, "Precio"), el("dd", {}, dinero(r.precio_hora)))),
        el("div", { class: "caja-codigo" },
          el("div", { class: "subtitulo", style: "margin: 0" }, "Código de reserva"),
          el("div", { class: "codigo mono", id: "codigo-reserva" }, r.codigo),
          el("button", { type: "button", class: "btn borde-acento", onclick: copiar }, icono("copiar", 16), "Copiar código"),
          el("div", { class: "nota-warn" }, icono("alerta", 16), el("span", {}, "Guárdalo: lo necesitas junto a tu teléfono para consultar o cancelar.")))),
      aviso("info", "reloj", "", el("span", {}, "Cancelación sin costo hasta el ", el("strong", {}, limite.texto), "."))),
    el("div", { class: "pie", style: "justify-content: flex-end" },
      el("button", { type: "button", class: "btn", onclick: nuevaReserva }, "Nueva reserva"),
      el("button", { type: "button", class: "btn primario", onclick: () => verMiReserva(r.codigo, r.telefono) }, "Ver mi reserva")),
  ];
}

function nuevaReserva() {
  Object.assign(E, { paso: 1, hora: null, nombre: "", telefono: "", tocado: false, erroresServidor: {}, reserva: null, aviso: null });
  irA(1);
}

let temporizadorToast;
function mostrarToast(texto) {
  const t = $("toast");
  t.replaceChildren(icono("check", 16, 3), texto);
  t.classList.remove("oculto");
  clearTimeout(temporizadorToast);
  temporizadorToast = setTimeout(() => t.classList.add("oculto"), 2200);
}

// ---------- Mi reserva (RF-05, RF-06) ----------
const formBuscar = $("form-buscar");
let consultada = null;
let pidiendoConfirmacion = false;

function verMiReserva(codigo, telefono) {
  $("q-codigo").value = codigo;
  $("q-telefono").value = telefono;
  location.hash = "#mi-reserva";
  consultar();
}

$("q-codigo").addEventListener("input", (ev) => { ev.target.value = ev.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 8); });

async function consultar() {
  const codigo = $("q-codigo").value.trim().toUpperCase();
  const telefono = $("q-telefono").value.replace(/\s/g, "");
  $("aviso-buscar").replaceChildren();
  [$("q-codigo"), $("q-telefono")].forEach((i) => i.classList.remove("invalida"));
  if (!codigo || !telefono) {
    $("aviso-buscar").append(aviso("bad", "equis", "", "Escribe el código y el teléfono."));
    return;
  }
  try {
    consultada = await api("GET", `/api/reservas/${encodeURIComponent(codigo)}?telefono=${encodeURIComponent(telefono)}`);
    pidiendoConfirmacion = false;
    renderDetalle();
  } catch (e) {
    consultada = null;
    renderDetalle();
    [$("q-codigo"), $("q-telefono")].forEach((i) => i.classList.add("invalida"));
    $("aviso-buscar").append(e.status === 404
      ? aviso("bad", "equis", "Reserva no encontrada.", "Verifica el código y el teléfono.")
      : aviso("bad", "equis", "", e.campos.telefono || e.message));
  }
}
formBuscar.addEventListener("submit", (ev) => { ev.preventDefault(); consultar(); });

function renderDetalle() {
  const cont = $("detalle-reserva");
  const badge = $("estado-reserva");
  if (!consultada) {
    $("sub-detalle").textContent = "Sin reserva seleccionada";
    badge.classList.add("oculto");
    cont.replaceChildren(el("div", { class: "vacio" }, icono("lupa", 32, 1.5), el("p", { style: "margin: 8px 0 0" }, "Busca una reserva para ver su detalle.")));
    return;
  }
  const r = consultada;
  const c = E.canchas.find((x) => x.id === r.cancha_id);
  const limite = limiteCancelacion(r.fecha, r.hora_inicio);
  const yaEmpezo = inicioReal(r.fecha, r.hora_inicio) <= new Date();
  const fueraDePlazo = limite.fecha <= new Date();
  const cancelada = r.estado === "cancelada";
  const estado = cancelada ? ["Cancelada", "bad"] : pidiendoConfirmacion ? ["Pendiente de cancelación", "warn"] : yaEmpezo ? ["Jugada", "info"] : ["Activa", "ok"];
  $("sub-detalle").textContent = `Reserva ${r.codigo}`;
  badge.className = `ficha tono-${estado[1]}`;
  badge.replaceChildren(el("span", { class: "punto", "aria-hidden": "true" }), estado[0]);

  const tabla = el("div", { style: `border: 1px solid var(--${cancelada || pidiendoConfirmacion ? "bad-border" : "ok-border"}); border-radius: 6px; overflow: hidden` },
    el("dl", { class: "tabla" },
      el("dt", {}, "Código"), el("dd", { class: "mono", style: "letter-spacing: .1em" }, r.codigo),
      el("dt", {}, "Cancha"), el("dd", {}, c ? c.nombre : `Cancha ${r.cancha_id}`),
      el("dt", {}, "Fecha"), el("dd", {}, fechaLarga(r.fecha)),
      el("dt", {}, "Horario"), el("dd", {}, rango(r.hora_inicio)),
      el("dt", {}, "A nombre de"), el("dd", {}, r.nombre),
      el("dt", {}, "Precio"), el("dd", {}, dinero(r.precio_hora))));

  let accion = null;
  if (cancelada) {
    accion = aviso("warn", "check", "Reserva cancelada.", "El horario quedó libre.");
  } else if (yaEmpezo) {
    accion = aviso("info", "info", "", "Esta reserva ya empezó o ya se jugó.");
  } else if (fueraDePlazo) {
    accion = aviso("warn", "alerta", "Ya pasó el límite de cancelación en línea.", `Era hasta el ${limite.texto}.`);
  } else if (pidiendoConfirmacion) {
    const zonaError = el("div");
    accion = el("div", { role: "alertdialog", "aria-labelledby": "cc-titulo", class: "aviso bad", style: "flex-direction: column; align-items: stretch; gap: 12px" },
      el("div", { style: "display: flex; gap: 10px" }, icono("alerta", 20),
        el("div", {}, el("strong", { id: "cc-titulo", style: "display: block" }, "¿Confirmas la cancelación?"),
          `El horario de las ${r.hora_inicio} quedará libre para otros jugadores. Esta acción no se puede deshacer.`)),
      zonaError,
      el("div", { style: "display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end" },
        el("button", { type: "button", class: "btn", onclick: () => { pidiendoConfirmacion = false; renderDetalle(); } }, "No, mantener"),
        el("button", { type: "button", class: "btn peligro-lleno", id: "btn-si-cancelar", onclick: async (ev) => {
          ev.currentTarget.disabled = true;
          try {
            consultada = await api("POST", `/api/reservas/${encodeURIComponent(r.codigo)}/cancelar`, { cuerpo: { telefono: r.telefono } });
            pidiendoConfirmacion = false;
            olvidarDisponibilidad();
            renderDetalle();
          } catch (e) {
            ev.currentTarget.disabled = false;
            zonaError.replaceChildren(el("div", { role: "alert" }, e.message));
          }
        } }, "Sí, cancelar")));
  } else {
    accion = el("div", { class: "aviso info entre" },
      el("div", { style: "display: flex; gap: 10px; align-items: center" }, icono("reloj"),
        el("span", {}, "Puedes cancelar sin costo hasta el ", el("strong", {}, limite.texto), ` (${cuantoFalta(r.fecha)}).`)),
      el("button", { type: "button", class: "btn peligro chico", onclick: () => { pidiendoConfirmacion = true; renderDetalle(); } }, "Cancelar reserva"));
  }
  cont.replaceChildren(el("div", { class: "seccion-cuerpo" }, tabla, accion));
}

// ---------- Navegación entre vistas ----------
function aplicarRuta() {
  E.vista = location.hash === "#mi-reserva" ? "mia" : "reservar";
  render();
  if (E.vista === "mia" && !consultada) renderDetalle();
}
window.addEventListener("hashchange", aplicarRuta);

async function iniciar() {
  aplicarRuta();
  try {
    E.canchas = await api("GET", "/api/canchas");
  } catch (e) {
    E.errorCanchas = e.message;
  }
  E.cargandoCanchas = false;
  render();
}
iniciar();
