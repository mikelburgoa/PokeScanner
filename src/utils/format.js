// Fechas legibles para la interfaz.
const MIN = 60, HOUR = 3600, DAY = 86400

/** «hace 5 min», «hace 3 h», «hace 2 días»... a partir de una fecha ISO. Devuelve '' si no hay fecha válida. */
export function timeAgo(iso) {
  const t = Date.parse(iso)
  if (!iso || Number.isNaN(t)) return ''
  const s = Math.max(0, Math.round((Date.now() - t) / 1000))
  if (s < MIN) return 'hace un momento'
  if (s < HOUR) return `hace ${Math.floor(s / MIN)} min`
  if (s < DAY) return `hace ${Math.floor(s / HOUR)} h`
  const d = Math.floor(s / DAY)
  return d === 1 ? 'hace 1 día' : `hace ${d} días`
}

/** «10/11/2026 23:50» */
export function formatDateTime(iso) {
  const t = Date.parse(iso)
  if (!iso || Number.isNaN(t)) return ''
  return new Date(t).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' })
}
