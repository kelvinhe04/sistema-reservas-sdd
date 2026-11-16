// Utilidades compartidas por la vista del jugador y el panel de administración.

const ZONA = "America/Panama";
const MAX_DIAS = 30;

function el(etiqueta, atributos = {}, ...hijos) {
  const nodo = document.createElement(etiqueta);
  for (const [clave, valor] of Object.entries(atributos)) {
    if (valor === null || valor === undefined || valor === false) continue;
    if (clave.startsWith("on")) nodo.addEventListener(clave.slice(2), valor);
    else if (clave === "class") nodo.className = valor;
    else nodo.setAttribute(clave, valor === true ? "" : valor);
  }
  for (const hijo of hijos.flat()) {
    if (hijo === null || hijo === undefined || hijo === false) continue;
    nodo.append(hijo instanceof Node ? hijo : document.createTextNode(String(hijo)));
  }
  return nodo;
}

function hoyEnSede(desplazamientoDias = 0) {
  const ahora = new Date(Date.now() + desplazamientoDias * 86400000);
  return new Intl.DateTimeFormat("en-CA", { timeZone: ZONA, year: "numeric", month: "2-digit", day: "2-digit" }).format(ahora);
}

function dinero(centavos) {
  return new Intl.NumberFormat("es-PA", { style: "currency", currency: "USD", currencyDisplay: "narrowSymbol" }).format(centavos / 100);
}

function fechaLarga(iso) {
  const [a, m, d] = iso.split("-").map(Number);
  return new Intl.DateTimeFormat("es", { weekday: "long", day: "numeric", month: "long", timeZone: "UTC" })
    .format(new Date(Date.UTC(a, m - 1, d)));
}

class ErrorApi extends Error {
  constructor(status, cuerpo) {
    super((cuerpo && cuerpo.mensaje) || "No se pudo completar la operación");
    this.status = status;
    this.codigo = cuerpo && cuerpo.error;
    this.campos = (cuerpo && cuerpo.campos) || {};
  }
}

async function api(metodo, ruta, { cuerpo, cabeceras } = {}) {
  let respuesta;
  try {
    respuesta = await fetch(ruta, {
      method: metodo,
      headers: { ...(cuerpo !== undefined ? { "Content-Type": "application/json" } : {}), ...(cabeceras || {}) },
      body: cuerpo !== undefined ? JSON.stringify(cuerpo) : undefined,
    });
  } catch {
    throw new ErrorApi(0, { mensaje: "No hay conexión con el servidor. Intenta de nuevo." });
  }
  if (respuesta.status === 204) return null;
  let datos = null;
  try { datos = await respuesta.json(); } catch { /* sin cuerpo */ }
  if (!respuesta.ok) throw new ErrorApi(respuesta.status, datos);
  return datos;
}

function aviso(contenedor, tipo, ...contenido) {
  contenedor.replaceChildren(el("div", { class: `aviso ${tipo}`, role: tipo === "error" ? "alert" : "status" }, ...contenido));
}

function limpiarErrores(formulario) {
  formulario.querySelectorAll("[aria-invalid]").forEach((i) => i.removeAttribute("aria-invalid"));
  formulario.querySelectorAll(".error").forEach((e) => (e.textContent = ""));
}

function mostrarErroresCampos(formulario, campos) {
  let alguno = false;
  for (const [campo, mensaje] of Object.entries(campos || {})) {
    const entrada = formulario.querySelector(`[name="${campo}"]`);
    const destino = formulario.querySelector(`[data-error-de="${campo}"]`);
    if (entrada) entrada.setAttribute("aria-invalid", "true");
    if (destino) { destino.textContent = mensaje; alguno = true; }
  }
  return alguno;
}
