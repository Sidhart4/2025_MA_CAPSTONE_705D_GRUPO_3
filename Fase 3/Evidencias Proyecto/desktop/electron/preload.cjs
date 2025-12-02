// electron/preload.cjs
const { contextBridge } = require("electron");

const API_BASE = process.env.ELECTRON_API_URL || "http://127.0.0.1:8000";
let accessToken = null;

/** Fetch básico */
async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const isFormData = options.body instanceof FormData;

  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  if (!isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const text = await res.text().catch(() => "");
  if (!res.ok) throw new Error(`API ${res.status}: ${text || res.statusText}`);

  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? JSON.parse(text) : text;
}

/** Intenta varias rutas en orden; usa la primera que responda OK */
async function apiFetchTry(paths, options = {}) {
  let lastErr;
  for (const p of paths) {
    try {
      return await apiFetch(p, options);
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error("API: todas las rutas fallaron");
}

function cleanParams(params = {}) {
  return Object.fromEntries(
    Object.entries(params).filter(
      ([, v]) => v !== undefined && v !== null && String(v).trim() !== ""
    )
  );
}

// Si el payload trae imagenFile, lo convertimos a FormData (campo real "imagen")
function toFormData(obj = {}) {
  const fd = new FormData();
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null || v === "") continue;
    if (k === "imagenFile") fd.append("imagen", v);
    else fd.append(k, v);
  }
  return fd;
}

contextBridge.exposeInMainWorld("api", {
  // ---------- Auth ----------
  login: async (username, password) => {
    const data = await apiFetch("/api/auth/jwt/create/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    accessToken = data?.access || null;
    return { ok: !!accessToken, access: accessToken };
  },
  loadToken: (token) => {
    accessToken = token || null;
    return !!accessToken;
  },
  logout: () => { accessToken = null; },
  isAuthenticated: () => !!accessToken,

  // ---------- Productos ----------
  getProductos: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/productos/${q ? "?" + q : ""}`);
  },
  createProducto: (payload = {}) => {
    const hasFile = !!payload.imagenFile;
    const body = hasFile ? toFormData(payload) : JSON.stringify(payload);
    return apiFetch("/api/productos/", { method: "POST", body });
  },
  updateProducto: (id, payload = {}) => {
    const hasFile = !!payload.imagenFile;
    const body = hasFile ? toFormData(payload) : JSON.stringify(payload);
    return apiFetch(`/api/productos/${id}/`, { method: "PATCH", body });
  },
  deleteProducto: (id) => apiFetch(`/api/productos/${id}/`, { method: "DELETE" }),

  // ---------- Agenda / Citas ----------
  // Prefiere /api/citas/; si tu router registró "agenda", hace fallback a /api/agenda/
  getCitas: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    const qs = q ? "?" + q : "";
    return apiFetchTry([`/api/citas/${qs}`, `/api/agenda/${qs}`]);
  },
  createCita: (payload) =>
    apiFetchTry(
      ["/api/citas/", "/api/agenda/"],
      { method: "POST", body: JSON.stringify(payload) }
    ),
  updateCita: (id, payload) =>
    apiFetchTry(
      [`/api/citas/${id}/`, `/api/agenda/${id}/`],
      { method: "PATCH", body: JSON.stringify(payload) }
    ),
  // Próximas citas para el resumen
  getCitasProximas: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    const qs = q ? "?" + q : "";
    return apiFetchTry([`/api/citas/proximas/${qs}`, `/api/agenda/proximas/${qs}`]);
  },

  // ---------- Profesionales ----------
  getProfesionales: (params = {}) => {
    const q = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v != null))
    ).toString();
    const qs = q ? "?" + q : "";
    return apiFetchTry([`/api/profesionales/${qs}`, `/api/agenda/profesionales/${qs}`]);
  },

  // ---------- Atención ----------
  getAtencionPorCita: (citaId) => apiFetch(`/api/atenciones/${citaId}/`),
  createAtencion: (payload) =>
    apiFetch("/api/atenciones/", { method: "POST", body: JSON.stringify(payload) }),
  updateAtencion: (id, payload) =>
    apiFetch(`/api/atenciones/${id}/`, { method: "PATCH", body: JSON.stringify(payload) }),

  // ---------- Ventas (CRUD + Resumen/Top) ----------
  getVentas: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/ventas/${q ? "?" + q : ""}`);
  },
  createVenta: (payload) =>
    apiFetch("/api/ventas/", { method: "POST", body: JSON.stringify(payload) }),
  getVentasResumen: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/ventas/resumen/${q ? "?" + q : ""}`);
  },
  getTopProductosVendidos: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/ventas/top/${q ? "?" + q : ""}`);
  },

  // ---------- Caja ----------
  getCajaActual: () => apiFetch(`/api/caja/actual/`),
  abrirCaja: ({ saldo_inicial = 0, observacion = "", caja_nombre = "" } = {}) =>
    apiFetch(`/api/caja/abrir/`, {
      method: "POST",
      body: JSON.stringify({ saldo_inicial, observacion, caja_nombre }),
    }),
  cerrarCaja: () => apiFetch(`/api/caja/cerrar/`, { method: "POST" }),
  crearMovimientoCaja: ({ tipo, monto, descripcion = "" }) =>
    apiFetch(`/api/caja/movimiento/`, {
      method: "POST",
      body: JSON.stringify({ tipo, monto, descripcion }),
    }),
  getCajaMovimientos: () => apiFetch(`/api/caja/movimientos/`),
  registrarVentaEnCaja: (venta_id) =>
    apiFetch(`/api/caja/registrar-venta/`, {
      method: "POST",
      body: JSON.stringify({ venta_id }),
    }),

  // ---------- Dashboard / KPIs y Series ----------
  getVentasKPIs: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/ventas/kpis/${q ? "?" + q : ""}`);
  },
  getVentasSerieDiaria: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/ventas/serie-diaria/${q ? "?" + q : ""}`);
  },
  getVentasPorMetodo: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/ventas/por-metodo/${q ? "?" + q : ""}`);
  },
  getVentasPorCategoria: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/ventas/por-categoria/${q ? "?" + q : ""}`);
  },

  // ---------- Fichas / Clientes (alias de "Propietarios") ----------
  // Endpoints REALES (tu backend expone /api/clientes/)
  getClientes: (params = {}) => {
    const q = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v != null))
    ).toString();
    return apiFetch(`/api/clientes/${q ? "?" + q : ""}`);
  },
  createCliente: (payload = {}) =>
    apiFetch("/api/clientes/", { method: "POST", body: JSON.stringify(payload) }),
  updateCliente: (id, payload = {}) =>
    apiFetch(`/api/clientes/${id}/`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteCliente: (id) =>
    apiFetch(`/api/clientes/${id}/`, { method: "DELETE" }),

  // Aliases "Propietarios" que FALLBACK a /api/clientes/
  getPropietarios: (params = {}) => {
    const q = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v != null))
    ).toString();
    const qs = q ? "?" + q : "";
    return apiFetchTry([`/api/propietarios/${qs}`, `/api/clientes/${qs}`]);
  },
  createPropietario: (payload = {}) =>
    apiFetchTry(
      ["/api/propietarios/", "/api/clientes/"],
      { method: "POST", body: JSON.stringify(payload) }
    ),
  updatePropietario: (id, payload = {}) =>
    apiFetchTry(
      [`/api/propietarios/${id}/`, `/api/clientes/${id}/`],
      { method: "PATCH", body: JSON.stringify(payload) }
    ),
  deletePropietario: (id) =>
    apiFetchTry(
      [`/api/propietarios/${id}/`, `/api/clientes/${id}/`],
      { method: "DELETE" }
    ),

  // ---------- Mascotas ----------
  getMascotas: (params = {}) => {
    const q = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v != null))
    ).toString();
    return apiFetch(`/api/mascotas/${q ? "?" + q : ""}`);
  },
  createMascota: (payload = {}) =>
    apiFetch("/api/mascotas/", { method: "POST", body: JSON.stringify(payload) }),
  updateMascota: (id, payload = {}) =>
    apiFetch(`/api/mascotas/${id}/`, { method: "PATCH", body: JSON.stringify(payload) }),

  // ---------- Usuarios clientes ----------
  getUsuariosClientes: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/usuarios-clientes/${q ? "?" + q : ""}`);
  },
  createUsuarioCliente: (payload = {}) =>
    apiFetch(`/api/usuarios-clientes/`, { method: "POST", body: JSON.stringify(payload) }),
  updateUsuarioCliente: (id, payload = {}) =>
    apiFetch(`/api/usuarios-clientes/${id}/`, { method: "PATCH", body: JSON.stringify(payload) }),

  // ---------- Mascotas de usuario (perfil) ----------
  getMascotasPerfil: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/mascotas-perfil/${q ? "?" + q : ""}`);
  },
  createMascotaPerfil: (payload = {}) =>
    apiFetch(`/api/mascotas-perfil/`, { method: "POST", body: JSON.stringify(payload) }),
  updateMascotaPerfil: (id, payload = {}) =>
    apiFetch(`/api/mascotas-perfil/${id}/`, { method: "PATCH", body: JSON.stringify(payload) }),

  // ---------- Fichas clínicas ----------
  getFichasClinicas: (params = {}) => {
    const q = new URLSearchParams(cleanParams(params)).toString();
    return apiFetch(`/api/fichas-clinicas/${q ? "?" + q : ""}`);
  },
  createFichaClinica: (payload = {}) =>
    apiFetch(`/api/fichas-clinicas/`, { method: "POST", body: JSON.stringify(payload) }),
  updateFichaClinica: (id, payload = {}) =>
    apiFetch(`/api/fichas-clinicas/${id}/`, { method: "PATCH", body: JSON.stringify(payload) }),

});
