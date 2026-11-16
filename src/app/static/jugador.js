// Vista del jugador: RF-01 a RF-06.

const estado = { canchas: [], cancha: null, fecha: hoyEnSede(), hora: null };

const $ = (id) => document.getElementById(id);
const contCanchas = $("canchas");
const contFranjas = $("franjas");
const inputFecha = $("fecha");
const formReserva = $("form-reserva");
const btnReservar = $("btn-reservar");

inputFecha.min = hoyEnSede();
inputFecha.max = hoyEnSede(MAX_DIAS);
inputFecha.value = estado.fecha;

function canchaActual() {
  return estado.canchas.find((c) => c.id === estado.cancha);
}

function actualizarResumen() {
  const c = canchaActual();
  btnReservar.disabled = !(c && estado.hora);
  $("resumen-seleccion").textContent = c && estado.hora
    ? `${c.nombre} · ${fechaLarga(estado.fecha)} · ${estado.hora} · ${dinero(c.precio_hora)}`
    : "Elige una cancha y un horario libre para continuar.";
}

async function cargarCanchas() {
  try {
    estado.canchas = await api("GET", "/api/canchas");
  } catch (e) {
    aviso($("aviso-canchas"), "error", e.message);
    return;
  }
  if (!estado.canchas.length) {
    contCanchas.replaceChildren();
    aviso($("aviso-canchas"), "info", "Todavía no hay canchas disponibles.");
    return;
  }
  if (!canchaActual()) estado.cancha = estado.canchas[0].id;
  pintarCanchas();
  cargarFranjas();
}

function pintarCanchas() {
  contCanchas.replaceChildren(...estado.canchas.map((c) =>
    el("button", {
      type: "button", class: "cancha", "aria-pressed": String(c.id === estado.cancha),
      "aria-label": `${c.nombre}, ${c.deporte}, ${dinero(c.precio_hora)} por hora`,
      onclick: () => { estado.cancha = c.id; estado.hora = null; pintarCanchas(); cargarFranjas(); },
    },
    el("span", { class: "nombre" }, c.nombre),
    el("span", { class: "detalle" }, `${c.deporte} · ${dinero(c.precio_hora)} / hora`))));
}

async function cargarFranjas() {
  $("fecha-texto").textContent = estado.fecha ? fechaLarga(estado.fecha) : "";
  $("aviso-franjas").replaceChildren();
  actualizarResumen();
  if (!estado.cancha || !estado.fecha) { contFranjas.replaceChildren(); return; }
  let datos;
  try {
    datos = await api("GET", `/api/canchas/${estado.cancha}/disponibilidad?fecha=${encodeURIComponent(estado.fecha)}`);
  } catch (e) {
    contFranjas.replaceChildren();
    aviso($("aviso-franjas"), "error", e.message);
    return;
  }
  const libres = datos.franjas.filter((f) => f.estado === "libre" && !f.pasada);
  if (estado.hora && !libres.some((f) => f.hora_inicio === estado.hora)) estado.hora = null;
  contFranjas.replaceChildren(...datos.franjas.map((f) => {
    const disponible = f.estado === "libre" && !f.pasada;
    const texto = f.pasada ? "Pasada" : f.estado === "libre" ? "Libre" : "Ocupada";
    return el("button", {
      type: "button", class: "franja", disabled: !disponible,
      "aria-pressed": String(f.hora_inicio === estado.hora),
      "aria-label": `${f.hora_inicio}, ${texto.toLowerCase()}`,
      onclick: () => { estado.hora = f.hora_inicio; cargarFranjasSinRed(datos); },
    }, f.hora_inicio, el("small", {}, texto));
  }));
  if (!libres.length) aviso($("aviso-franjas"), "info", "No quedan horarios libres este día. Prueba con otra fecha.");
  actualizarResumen();
}

function cargarFranjasSinRed() {
  contFranjas.querySelectorAll(".franja").forEach((b) => {
    b.setAttribute("aria-pressed", String(b.firstChild.textContent === estado.hora));
  });
  actualizarResumen();
  if (window.matchMedia("(max-width: 700px)").matches) $("seccion-datos").scrollIntoView({ behavior: "smooth", block: "start" });
}

inputFecha.addEventListener("change", () => {
  estado.fecha = inputFecha.value;
  estado.hora = null;
  cargarFranjas();
});

formReserva.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  limpiarErrores(formReserva);
  const salida = $("aviso-reserva");
  salida.replaceChildren();
  const c = canchaActual();
  if (!c || !estado.hora) return;
  btnReservar.disabled = true;
  try {
    const r = await api("POST", "/api/reservas", { cuerpo: {
      cancha_id: c.id, fecha: estado.fecha, hora_inicio: estado.hora,
      nombre: formReserva.nombre.value, telefono: formReserva.telefono.value.trim(),
    }});
    aviso(salida, "ok",
      el("strong", {}, "¡Reserva confirmada!"),
      el("div", {}, "Tu código de reserva es:"),
      el("div", { class: "codigo" }, r.codigo),
      el("div", {}, "Guárdalo: lo necesitas junto a tu teléfono para consultar o cancelar."),
      el("dl", { class: "resumen" },
        el("dt", {}, "Cancha"), el("dd", {}, c.nombre),
        el("dt", {}, "Día"), el("dd", {}, fechaLarga(r.fecha)),
        el("dt", {}, "Hora"), el("dd", {}, r.hora_inicio),
        el("dt", {}, "A nombre de"), el("dd", {}, r.nombre),
        el("dt", {}, "Precio"), el("dd", {}, dinero(r.precio_hora))));
    $("c-codigo").value = r.codigo;
    $("c-telefono").value = r.telefono;
    estado.hora = null;
    await cargarFranjas();
  } catch (e) {
    if (!mostrarErroresCampos(formReserva, e.campos) || e.codigo !== "validacion") aviso(salida, "error", e.message);
    if (e.codigo === "conflicto") { estado.hora = null; await cargarFranjas(); }
  } finally {
    actualizarResumen();
  }
});

const formConsulta = $("form-consulta");

function pintarReserva(r) {
  const contenedor = $("aviso-consulta");
  const cancha = estado.canchas.find((c) => c.id === r.cancha_id);
  const hijos = [
    el("dl", { class: "resumen" },
      el("dt", {}, "Código"), el("dd", {}, r.codigo),
      el("dt", {}, "Estado"), el("dd", {}, el("span", { class: `etiqueta ${r.estado}` }, r.estado)),
      el("dt", {}, "Cancha"), el("dd", {}, cancha ? cancha.nombre : `Cancha ${r.cancha_id}`),
      el("dt", {}, "Día"), el("dd", {}, fechaLarga(r.fecha)),
      el("dt", {}, "Hora"), el("dd", {}, r.hora_inicio),
      el("dt", {}, "A nombre de"), el("dd", {}, r.nombre)),
  ];
  if (r.estado === "confirmada") {
    hijos.push(el("div", { style: "margin-top: 14px" },
      el("button", { class: "btn peligro", type: "button", onclick: () => cancelar(r) }, "Cancelar reserva")));
  }
  contenedor.replaceChildren(el("div", { class: "aviso ok", role: "status" }, ...hijos));
}

async function cancelar(r) {
  if (!confirm(`¿Cancelar la reserva ${r.codigo} del ${fechaLarga(r.fecha)} a las ${r.hora_inicio}?`)) return;
  try {
    const actualizada = await api("POST", `/api/reservas/${encodeURIComponent(r.codigo)}/cancelar`, { cuerpo: { telefono: r.telefono } });
    pintarReserva(actualizada);
    $("aviso-consulta").prepend(el("div", { class: "aviso info" }, "Reserva cancelada. El horario quedó libre."));
    cargarFranjas();
  } catch (e) {
    aviso($("aviso-consulta"), "error", e.message);
  }
}

formConsulta.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  limpiarErrores(formConsulta);
  const codigo = formConsulta.codigo.value.trim().toUpperCase();
  const telefono = formConsulta.telefono.value.trim();
  if (!codigo) { mostrarErroresCampos(formConsulta, { codigo: "Escribe tu código" }); return; }
  try {
    pintarReserva(await api("GET", `/api/reservas/${encodeURIComponent(codigo)}?telefono=${encodeURIComponent(telefono)}`));
  } catch (e) {
    if (!mostrarErroresCampos(formConsulta, e.campos)) aviso($("aviso-consulta"), "error", e.message);
  }
});

cargarCanchas();
