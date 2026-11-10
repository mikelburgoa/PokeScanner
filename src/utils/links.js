// Enlaces a las tiendas. Los datos de la colección no son de fiar al 100 %, así que solo se usa la URL
// guardada si es https del dominio esperado; si no, se construye un enlace de búsqueda propio.
// (Antes bastaba con que la URL «contuviera» cierto texto, lo que dejaba pasar cosas como javascript:...)
const CARDMARKET = 'https://www.cardmarket.com/'
const TCGPLAYER = 'https://www.tcgplayer.com/'

const query = (c) => encodeURIComponent(`${c.name || ''} ${c.number || ''}`.trim())

export function cardmarketUrl(c) {
  const u = c.cardmarket_url
  if (typeof u === 'string' && u.startsWith(CARDMARKET) && u.includes('idProduct=')) return u
  return `${CARDMARKET}es/Pokemon/Products/Singles?searchString=${query(c)}`
}

export function tcgplayerUrl(c) {
  const u = c.tcgplayer_url
  if (typeof u === 'string' && u.startsWith(TCGPLAYER) && u.includes('/product/')) return u
  return `${TCGPLAYER}search/pokemon/product?q=${query(c)}`
}
