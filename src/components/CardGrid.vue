<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div
      v-for="card in collection"
      :key="card.uid || card.id"
      class="panel-card !p-0 overflow-hidden hover:border-zinc-700/80 transition-all flex flex-col group shadow-2xl"
    >
      <!-- Imagen de la carta con fondo Carbón -->
      <div class="relative bg-zinc-950 aspect-[2.5/3.5] flex items-center justify-center overflow-hidden p-4 border-b border-zinc-800/80">
        <img :src="card.image" :alt="card.name" class="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300 drop-shadow-2xl" />
        
        <!-- Estado de conservación -->
        <div
          class="absolute top-3 right-3 text-xs font-semibold rounded-full px-2.5 py-0.5 whitespace-nowrap border font-mono font-bold shadow-md cursor-help"
          :class="condInfo(card.condition).cls"
          :title="`Estado: ${condInfo(card.condition).name}`"
        >
          {{ card.condition || 'NM' }}
        </div>

        <!-- Cantidad de copias -->
        <div class="absolute top-3 left-3 badge-rose font-mono font-bold shadow-md cursor-help" :title="`Tienes ${card.quantity || 1} ${(card.quantity || 1) === 1 ? 'copia' : 'copias'}`">
          x{{ card.quantity || 1 }}
        </div>
      </div>

      <!-- Información y Precios -->
      <div class="p-5 flex flex-col flex-grow justify-between space-y-4">
        <div>
          <div class="flex items-center justify-between gap-2">
            <span class="text-xs font-mono font-bold uppercase tracking-wider text-zinc-400 bg-zinc-950 border border-zinc-800 px-2 py-0.5 rounded-md">
              {{ card.set || 'Sin Expansión' }}
            </span>
            <span class="text-xs font-mono text-zinc-400">#{{ card.number }}</span>
          </div>
          <h3 class="font-bold text-base text-zinc-100 font-heading mt-2 line-clamp-1">{{ card.name }}</h3>
          <p class="text-xs text-zinc-400 mt-0.5">{{ card.rarity }}</p>
        </div>

        <!-- Precio, fecha del precio y eliminar -->
        <div class="pt-3 border-t border-zinc-800/80 space-y-3">
          <div class="flex items-end justify-between gap-3">
            <div class="min-w-0">
              <p class="text-xs text-zinc-400 uppercase tracking-wider font-semibold">
                {{ (card.quantity || 1) > 1 ? `Valor de ${card.quantity} copias` : 'Valor estimado' }}
              </p>
              <p class="text-lg font-bold text-emerald-400 font-heading">
                {{ Number(card.value_eur || 0).toFixed(2) }} €
              </p>
              <p class="text-xs mt-0.5" :class="card.prices_updated ? 'text-zinc-400' : 'text-amber-400/90'" :title="card.prices_updated ? formatDateTime(card.prices_updated) : ''">
                {{ card.prices_updated ? `Precio de ${timeAgo(card.prices_updated)}` : 'Sin fecha de precio: pulsa «Actualizar precios»' }}
              </p>
            </div>

            <!-- Eliminar: aislado de los enlaces y con zona de clic cómoda -->
            <button
              type="button"
              @click="$emit('delete', card.uid)"
              class="w-10 h-10 shrink-0 flex items-center justify-center bg-red-950/40 hover:bg-red-900/60 text-red-400 rounded-lg border border-red-800/40 transition-all cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
              :aria-label="`Eliminar ${card.name} de la colección`"
              title="Eliminar carta"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>

          <!-- Enlaces a las tiendas, con su nombre -->
          <div class="grid grid-cols-2 gap-2">
            <a :href="getCardmarketUrl(card)" target="_blank" rel="noopener" class="btn-icon flex items-center justify-center text-xs font-semibold text-indigo-300 hover:text-indigo-200" title="Abrir en Cardmarket (precios en €)">
              Cardmarket ↗
            </a>
            <a :href="getTcgplayerUrl(card)" target="_blank" rel="noopener" class="btn-icon flex items-center justify-center text-xs font-semibold text-sky-300 hover:text-sky-200" title="Abrir en TCGplayer (precios en $)">
              TCGplayer ↗
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { cardmarketUrl as getCardmarketUrl, tcgplayerUrl as getTcgplayerUrl } from '../utils/links'
import { timeAgo, formatDateTime } from '../utils/format'

defineProps({
  collection: { type: Array, required: true }
})

// Estado de conservación: nombre completo y color (verde = mejor, naranja = peor)
const CONDITIONS = {
  NM: { name: 'Near Mint (como nueva)', cls: 'bg-emerald-950/80 border-emerald-500/30 text-emerald-400' },
  LP: { name: 'Lightly Played (poco uso)', cls: 'bg-lime-950/80 border-lime-500/30 text-lime-300' },
  MP: { name: 'Moderately Played (uso moderado)', cls: 'bg-amber-950/80 border-amber-500/30 text-amber-400' },
  HP: { name: 'Heavily Played (muy usada)', cls: 'bg-orange-950/80 border-orange-500/30 text-orange-400' },
}
const condInfo = (c) => CONDITIONS[c || 'NM'] || CONDITIONS.NM
defineEmits(['delete'])
</script>