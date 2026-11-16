// Panel del administrador: RF-07 a RF-11.

const $ = (id) => document.getElementById(id);
const CLAVE_SESION = "reservas.adminKey";

function leerClave() {
  try { return sessionStorage.getItem(CLAVE_SESION) || ""; } catch { return ""; }
}
function guardarClave(valor) {
  try { valor ? sessionStorage.setItem(CLAVE_SESION, valor) : sessionStorage.removeItem(CLAVE_SESION); } catch { /* sin almacenamiento */ }
}

let clave = leerClave();
let fecha = hoyEnSede();

function adminApi(metodo, ruta, cuerpo) {
  return api(metodo, ruta, { cuerpo, cabeceras: { "X-Admin-Key": clave } }).catch((e) => {
    if (e.status === 401) salir("La sesión expiró o la clave cambió. Vuelve a entrar.");
    throw e;
  });
}

// --- Acceso (RF-07) ---
function mostrarPanel(visible) {
  $("seccion-login").classList.toggle("oculto", visible);
  $("panel").classList.toggle("oculto", !visible);
  $("btn-salir").classList.toggle("oculto", !visible);
}

function salir(mensaje) {
  clave = "";
  guardarClave("");
  mostrarPanel(false);
  const form = $("form-login");
  limpiarErrores(form);
  if (mensaje) mostrarErroresCampos(form, { clave: mensaje });
}

$("form-login").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.currentTarget;
  limpiarErrores(form);
  const valor = form.clave.value;
  if (!valor) { mostrarErroresCampos(form, { clave: "Escribe la clave" }); return; }
  try {
    await api("POST", "/api/admin/login", { cabeceras: { "X-Admin-Key": valor } });
  } catch (e) {
    mostrarErroresCampos(form, { clave: e.status === 401 ? "Clave incorrecta" : e.message });
    return;
  }
  clave = valor;
  guardarClave(valor);
  form.reset();
  entrar();
});

$("btn-salir").addEventListener("click", () => salir());

function entrar() {
  mostrarPanel(true);
  cargarAgenda();
  cargarCanchas();
}

// --- Pestañas ---
function seleccionarPestana(nombre) {
  for (const n of ["agenda", "canchas"]) {
    $(`tab-${n}`).setAttribute("aria-selected", String(n === nombre));
    $(`vista-${n}`).classList.toggle("oculto", n !== nombre);
  }
  if (nombre === "agenda") cargarAgenda();
}
$("tab-agenda").addEventListener("click", () => seleccionarPestana("agenda"));
$("tab-canchas").addEventListener("click", () => seleccionarPestana("canchas"));

// --- Agenda (RF-08), bloqueos (RF-10) y cancelación (RF-11) ---
const inputFecha = $("a-fecha");
inputFecha.value = fecha;
inputFecha.addEventListener("change", () => { fecha = inputFecha.value; cargarAgenda(); });
$("btn-hoy").addEventListener("click", () => { fecha = hoyEnSede(); inputFecha.value = fecha; cargarAgenda(); });

async function cargarAgenda() {
  $("a-fecha-texto").textContent = fecha ? fechaLarga(fecha) : "";
  $("aviso-agenda").replaceChildren();
  if (!fecha) return;
  let datos;
  try {
    datos = await adminApi("GET", `/api/admin/agenda?fecha=${encodeURIComponent(fecha)}`);
  } catch (e) {
    if (e.status !== 401) aviso($("aviso-agenda"), "error", e.message);
    return;
  }
  if (!datos.canchas.length) {
    $("agenda").replaceChildren();
    aviso($("aviso-agenda"), "info", "No hay canchas. Créalas en la pestaña Canchas.");
    return;
  }
  $("agenda").replaceChildren(...datos.canchas.map(pintarCanchaAgenda));
}

function resumenOcupacion(franjas) {
  const n = (estadoBuscado) => franjas.filter((f) => f.estado === estadoBuscado).length;
  return `${n("reservada")} reservadas · ${n("bloqueada")} bloqueadas · ${n("libre")} libres`;
}

function pintarCanchaAgenda(c) {
  const filas = c.franjas.map((f) => {
    let detalle = "", accion = null;
    if (f.estado === "reservada") {
      detalle = `${f.reserva.nombre} · ${f.reserva.telefono} · ${f.reserva.codigo}`;
      accion = el("button", { class: "btn peligro chico", type: "button",
        onclick: () => cancelarReserva(f.reserva, c, f) }, "Cancelar reserva");
    } else if (f.estado === "bloqueada") {
      detalle = f.bloqueo.motivo || "Sin motivo";
      accion = el("button", { class: "btn secundario chico", type: "button",
        onclick: () => desbloquear(f.bloqueo.id) }, "Desbloquear");
    } else if (c.activa) {
      accion = el("button", { class: "btn secundario chico", type: "button",
        onclick: () => bloquear(c, f) }, "Bloquear");
    }
    return el("tr", {},
      el("td", { class: "c-hora" }, el("strong", {}, f.hora_inicio)),
      el("td", { class: "c-estado" }, el("span", { class: `etiqueta ${f.estado}` }, f.estado)),
      el("td", { class: "c-detalle detalle" }, detalle),
      el("td", { class: "c-accion acciones" }, accion));
  });
  return el("section", { class: "tarjeta cancha-agenda" },
    el("h3", {}, c.nombre, el("span", { class: "detalle", style: "font-weight: 400; color: var(--muted); font-size: .85rem" }, `${c.deporte} · ${resumenOcupacion(c.franjas)}`),
      c.activa ? null : el("span", { class: "etiqueta inactiva" }, "desactivada")),
    el("div", { class: "desplazable" },
      el("table", { class: "tabla" },
        el("thead", {}, el("tr", {}, el("th", { style: "width: 80px" }, "Hora"), el("th", { style: "width: 120px" }, "Estado"), el("th", {}, "Detalle"), el("th", {}))),
        el("tbody", {}, filas))));
}

async function bloquear(cancha, franja) {
  const motivo = prompt(`Bloquear ${cancha.nombre} el ${fechaLarga(fecha)} a las ${franja.hora_inicio}.\nMotivo (opcional):`, "Mantenimiento");
  if (motivo === null) return;
  try {
    await adminApi("POST", "/api/admin/bloqueos", { cancha_id: cancha.cancha_id, fecha, hora_inicio: franja.hora_inicio, motivo: motivo || null });
  } catch (e) {
    if (e.status !== 401) aviso($("aviso-agenda"), "error", e.message);
  }
  cargarAgenda();
}

async function desbloquear(id) {
  try { await adminApi("DELETE", `/api/admin/bloqueos/${id}`); }
  catch (e) { if (e.status !== 401) aviso($("aviso-agenda"), "error", e.message); }
  cargarAgenda();
}

async function cancelarReserva(reserva, cancha, franja) {
  if (!confirm(`¿Cancelar la reserva ${reserva.codigo} de ${reserva.nombre} (${cancha.nombre}, ${franja.hora_inicio})?\nEl horario quedará libre.`)) return;
  try { await adminApi("POST", `/api/admin/reservas/${encodeURIComponent(reserva.codigo)}/cancelar`); }
  catch (e) { if (e.status !== 401) aviso($("aviso-agenda"), "error", e.message); }
  cargarAgenda();
}

// --- Canchas (RF-09) ---
const formCancha = $("form-cancha");

function modoEdicion(cancha) {
  limpiarErrores(formCancha);
  $("aviso-cancha").replaceChildren();
  formCancha.id.value = cancha ? cancha.id : "";
  formCancha.nombre.value = cancha ? cancha.nombre : "";
  formCancha.deporte.value = cancha ? cancha.deporte : "";
  formCancha.precio_hora.value = cancha ? (cancha.precio_hora / 100).toFixed(2) : "";
  $("t-form-cancha").textContent = cancha ? `Editar ${cancha.nombre}` : "Nueva cancha";
  $("btn-guardar-cancha").textContent = cancha ? "Guardar cambios" : "Crear";
  $("btn-cancelar-edicion").classList.toggle("oculto", !cancha);
  if (cancha) formCancha.nombre.focus();
}
$("btn-cancelar-edicion").addEventListener("click", () => modoEdicion(null));

formCancha.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  limpiarErrores(formCancha);
  $("aviso-cancha").replaceChildren();
  const precioTexto = formCancha.precio_hora.value.trim();
  const precio = Number(precioTexto);
  if (precioTexto === "" || !Number.isFinite(precio) || precio < 0) {
    mostrarErroresCampos(formCancha, { precio_hora: "Escribe un precio válido (0 o más)" });
    return;
  }
  const cuerpo = { nombre: formCancha.nombre.value, deporte: formCancha.deporte.value, precio_hora: Math.round(precio * 100) };
  const id = formCancha.id.value;
  try {
    const c = id ? await adminApi("PUT", `/api/admin/canchas/${id}`, cuerpo) : await adminApi("POST", "/api/admin/canchas", cuerpo);
    modoEdicion(null);
    aviso($("aviso-cancha"), "ok", id ? `Cancha "${c.nombre}" actualizada.` : `Cancha "${c.nombre}" creada.`);
    cargarCanchas();
  } catch (e) {
    if (e.status === 401) return;
    if (!mostrarErroresCampos(formCancha, e.campos) || e.codigo !== "validacion") aviso($("aviso-cancha"), "error", e.message);
  }
});

async function cargarCanchas() {
  let lista;
  try { lista = await adminApi("GET", "/api/admin/canchas"); }
  catch (e) { if (e.status !== 401) aviso($("aviso-cancha"), "error", e.message); return; }
  const cuerpo = $("lista-canchas");
  if (!lista.length) {
    cuerpo.replaceChildren(el("tr", {}, el("td", { colspan: "5", class: "detalle" }, "Todavía no hay canchas. Crea la primera arriba.")));
    return;
  }
  cuerpo.replaceChildren(...lista.map((c) => el("tr", {},
    el("td", {}, el("strong", {}, c.nombre)),
    el("td", {}, c.deporte),
    el("td", {}, dinero(c.precio_hora)),
    el("td", {}, el("span", { class: `etiqueta ${c.activa ? "libre" : "inactiva"}` }, c.activa ? "activa" : "desactivada")),
    el("td", { class: "acciones" },
      el("button", { class: "btn secundario chico", type: "button", onclick: () => modoEdicion(c) }, "Editar"), " ",
      c.activa ? el("button", { class: "btn peligro chico", type: "button", onclick: () => desactivar(c) }, "Desactivar") : null))));
}

async function desactivar(c) {
  if (!confirm(`¿Desactivar "${c.nombre}"?\nDejará de aparecer para reservar. Sus reservas confirmadas se mantienen.`)) return;
  try {
    await adminApi("POST", `/api/admin/canchas/${c.id}/desactivar`);
    aviso($("aviso-cancha"), "ok", `Cancha "${c.nombre}" desactivada.`);
  } catch (e) {
    if (e.status !== 401) aviso($("aviso-cancha"), "error", e.message);
  }
  cargarCanchas();
}

// --- Arranque ---
if (clave) {
  api("POST", "/api/admin/login", { cabeceras: { "X-Admin-Key": clave } }).then(entrar).catch(() => salir());
} else {
  mostrarPanel(false);
}
