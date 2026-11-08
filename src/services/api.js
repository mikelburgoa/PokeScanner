// Cliente del backend FastAPI. En desarrollo, Vite hace proxy de /api -> http://localhost:8000
// Las rutas incluyen el prefijo /api (p. ej. api.get('/api/export_excel')).

async function request(path, opts = {}) {
  let res
  try {
    res = await fetch(path, opts)
  } catch {
    throw new Error('No se pudo conectar con el servidor. ¿Está arrancado el backend en el puerto 8000?')
  }
  if (!res.ok) {
    const j = await res.json().catch(() => ({}))
    throw new Error(j.detail || j.error || j.message || `Error ${res.status}`)
  }
  // Si el servidor devuelve un archivo (p. ej. un .xlsx) en vez de JSON, se descarga.
  const type = res.headers.get('content-type') || ''
  if (type.includes('json')) return res.json()
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = Object.assign(document.createElement('a'), { href: url, download: 'coleccion_pokemon.xlsx' })
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
  return { success: true, message: 'Archivo descargado.' }
}

const withBody = (method, body) => ({
  method,
  headers: { 'Content-Type': 'application/json' },
  body: body === undefined ? undefined : JSON.stringify(body),
})

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, withBody('POST', body)),
  put: (path, body) => request(path, withBody('PUT', body)),
  delete: (path) => request(path, { method: 'DELETE' }),
}

// --- Escaneo y colección
/** Envía la imagen (base64 / data URL) a la IA y devuelve { success, candidates, message }. */
export const identifyCard = (base64Data) => api.post('/api/identify', { image: base64Data })
export const getCollection = () => api.get('/api/collection')
export const saveCard = (card) => api.post('/api/collection', card)
export const deleteCard = (uid) => api.delete(`/api/collection/${encodeURIComponent(uid)}`)
export const refreshPrices = () => api.post('/api/refresh')

// --- Ajustes
/** Proveedor de IA activo y estado de cada uno (nunca incluye las claves). */
export const getSettings = () => api.get('/api/settings')
/** Guarda cambios parciales: { provider, keys: { gemini: 'xxx' | null }, models, ollamaUrl }. */
export const saveSettings = (patch) => api.put('/api/settings', patch)
export const clearExcel = () => api.post('/api/clear_excel')
export const clearCollection = () => api.post('/api/clear_collection')