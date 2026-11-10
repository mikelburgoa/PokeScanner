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
        <div class="absolute top-3 right-3 badge-success font-mono font-bold shadow-md">
          {{ card.condition || 'NM' }}
        </div>

        <!-- Cantidad de copias -->
        <div class="absolute top-3 left-3 badge-rose font-mono font-bold shadow-md">
          x{{ card.quantity || 1 }}
        </div>
      </div>

      <!-- Información y Precios -->
      <div class="p-5 flex flex-col flex-grow justify-between space-y-4">
        <div>
          <div class="flex items-center justify-between gap-2">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-zinc-400 bg-zinc-950 border border-zinc-800 px-2 py-0.5 rounded-md">
              {{ card.set || 'Sin Expansión' }}
            </span>
            <span class="text-[11px] font-mono text-zinc-500">#{{ card.number }}</span>
          </div>
          <h3 class="font-bold text-base text-zinc-100 font-heading mt-2 line-clamp-1">{{ card.name }}</h3>
          <p class="text-xs text-zinc-400 mt-0.5">{{ card.rarity }}</p>
        </div>

        <!-- Footer con precio estimado y links externos -->
        <div class="pt-3 border-t border-zinc-800/80 flex items-center justify-between">
          <div>
            <p class="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Valor Estimado</p>
            <p class="text-lg font-bold text-emerald-400 font-heading">
              {{ Number(card.value_eur || 0).toFixed(2) }} €
            </p>
          </div>

          <div class="flex items-center space-x-1.5">
            <!-- Cardmarket -->
            <a 
              :href="getCardmarketUrl(card)" 
              target="_blank" 
              rel="noopener"
              class="btn-icon text-xs font-mono font-bold text-indigo-400 hover:text-indigo-300" 
              title="Ver en Cardmarket (EUR)"
            >
              EUR ↗
            </a>

            <!-- TCGplayer -->
            <a 
              :href="getTcgplayerUrl(card)" 
              target="_blank" 
              rel="noopener"
              class="btn-icon text-xs font-mono font-bold text-sky-400 hover:text-sky-300" 
              title="Ver en TCGplayer (USD)"
            >
              USD ↗
            </a>

            <!-- Eliminar -->
            <button
              type="button"
              @click="$emit('delete', card.uid)"
              class="p-2 bg-red-950/40 hover:bg-red-900/60 text-red-400 rounded-lg border border-red-800/40 transition-all cursor-pointer"
              title="Eliminar carta"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { cardmarketUrl as getCardmarketUrl, tcgplayerUrl as getTcgplayerUrl } from '../utils/links'

defineProps({
  collection: { type: Array, required: true }
})
defineEmits(['delete'])
</script>