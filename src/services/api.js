const API_BASE = '/api'

export async function identifyCard(imageBase64) {
  const res = await fetch(`${API_BASE}/identify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageBase64 })
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Error identificando carta')
  return data
}

export async function searchCards(query, number = '', setName = '') {
  const params = new URLSearchParams({ q: query, number, set_name: setName })
  const res = await fetch(`${API_BASE}/search?${params}`)
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Error buscando cartas')
  return data.candidates || []
}

export async function getCollection() {
  const res = await fetch(`${API_BASE}/collection`)
  if (!res.ok) throw new Error('Error cargando colección')
  return res.json()
}

export async function saveCard(cardData) {
  const res = await fetch(`${API_BASE}/collection`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cardData)
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Error guardando carta')
  return data
}

export async function deleteCard(uid) {
  const res = await fetch(`${API_BASE}/collection/${uid}`, {
    method: 'DELETE'
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Error borrando carta')
  return data
}

export async function refreshPrices() {
  const res = await fetch(`${API_BASE}/refresh`, { method: 'POST' })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Error actualizando precios')
  return data
}

export async function clearCollection() {
  const res = await fetch(`${API_BASE}/clear_collection`, { method: 'POST' })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Error vaciando colección')
  return data
}

export function getExcelDownloadUrl() {
  return `${API_BASE}/export_excel`
}
