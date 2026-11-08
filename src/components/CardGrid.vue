<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div v-for="card in collection" :key="card.uid || card.id" class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl hover:border-slate-700 transition-all flex flex-col group">
      <div class="relative bg-slate-950 aspect-[3/4] flex items-center justify-center overflow-hidden p-4">
        <img :src="card.image" :alt="card.name" class="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300 drop-shadow-lg" />
        <div class="absolute top-3 right-3 bg-slate-900/90 backdrop-blur-md border border-slate-700 text-xs px-2.5 py-1 rounded-full font-mono text-emerald-400 font-bold shadow">
          {{ card.condition || 'NM' }}
        </div>
        <div class="absolute top-3 left-3 bg-red-600 text-white text-xs px-2.5 py-1 rounded-full font-mono font-bold shadow">
          x{{ card.quantity || 1 }}
        </div>
      </div>

      <div class="p-4 flex flex-col flex-grow justify-between space-y-3">
        <div>
          <div class="flex items-center justify-between gap-2">
            <span class="text-xs font-mono uppercase tracking-wider text-slate-400 bg-slate-800 px-2 py-0.5 rounded">{{ card.set || 'Sin Expansión' }}</span>
            <span class="text-xs font-mono text-slate-500">#{{ card.number }}</span>
          </div>
          <h3 class="font-bold text-lg text-white mt-1.5 line-clamp-1">{{ card.name }}</h3>
          <p class="text-xs text-slate-400 mt-0.5">{{ card.rarity }}</p>
        </div>

        <div class="pt-3 border-t border-slate-800 flex items-center justify-between">
          <div>
            <p class="text-xs text-slate-400">Valor Estimado</p>
            <p class="text-lg font-extrabold text-emerald-400 font-mono">
              {{ ((card.price_eur || card.price || 0) * (card.condition === 'LP' ? 0.85 : card.condition === 'MP' ? 0.70 : card.condition === 'HP' ? 0.50 : 1.0) * (card.quantity || 1)).toFixed(2) }} €
            </p>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Cardmarket (Europa) -->
            <a 
              :href="getCardmarketUrl(card)" 
              target="_blank" 
              rel="noopener"
              class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-colors flex items-center justify-center" 
              title="Ver en Cardmarket (EUR)"
            >
              🛒
            </a>

            <!-- TCGplayer (EE.UU.) -->
            <a 
              :href="getTcgplayerUrl(card)" 
              target="_blank" 
              rel="noopener"
              class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-sky-400 text-xs transition-colors flex items-center justify-center font-bold" 
              title="Ver en TCGplayer (USD)"
            >
              🇺🇸
            </a>

            <!-- Eliminar -->
            <button @click="$emit('delete', card.uid)" class="p-2 rounded-xl bg-red-600/20 hover:bg-red-600/30 text-red-400 text-xs transition-colors" title="Eliminar carta">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  collection: { type: Array, required: true }
})
defineEmits(['delete'])

function getCardmarketUrl(card) {
  if (card.cardmarket_url && card.cardmarket_url.includes('idProduct=')) {
    return card.cardmarket_url
  }
  const query = `${card.name || ''} ${card.number || ''}`.trim()
  return `https://www.cardmarket.com/es/Pokemon/Products/Singles?searchString=${encodeURIComponent(query)}`
}

function getTcgplayerUrl(card) {
  if (card.tcgplayer_url && card.tcgplayer_url.includes('/product/')) {
    return card.tcgplayer_url
  }
  const query = `${card.name || ''} ${card.number || ''}`.trim()
  return `https://www.tcgplayer.com/search/pokemon/product?q=${encodeURIComponent(query)}`
}
</script>