<template>
  <div class="panel-card flex flex-col md:flex-row gap-6 items-center">
    <!-- Vista previa de la carta capturada -->
    <div class="relative w-40 sm:w-48 aspect-[2.5/3.5] bg-zinc-950 rounded-xl border border-zinc-800 flex items-center justify-center p-3 overflow-hidden shadow-inner shrink-0">
      <img :src="card.image" :alt="card.name" class="max-h-full max-w-full object-contain drop-shadow-2xl" />
    </div>

    <!-- Contenido y Opciones -->
    <div class="flex-grow space-y-4 w-full">
      <div>
        <div class="flex items-center justify-between">
          <span class="badge-rose font-mono uppercase tracking-wider">{{ card.set || 'Sin Expansión' }}</span>
          <span class="text-xs font-mono text-zinc-500">#{{ card.number }}</span>
        </div>
        <h2 class="text-xl font-extrabold text-zinc-100 font-heading mt-2">{{ card.name }}</h2>
        <p class="text-xs text-zinc-400 mt-0.5">{{ card.rarity }}</p>
      </div>

      <!-- Cuadro de Precios de Referencia -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 panel-card-subtle">
        <div>
          <span class="text-[10px] text-zinc-400 font-semibold block uppercase">Cardmarket (EUR)</span>
          <span class="text-base font-bold text-emerald-400 font-heading">{{ (card.price_eur || card.price || 0).toFixed(2) }} €</span>
        </div>
        <div>
          <span class="text-[10px] text-zinc-400 font-semibold block uppercase">TCGplayer (USD)</span>
          <span class="text-base font-bold text-sky-400 font-heading">${{ (card.price_usd || card.usd || 0).toFixed(2) }}</span>
        </div>
        <div class="col-span-2 sm:col-span-1">
          <span class="text-[10px] text-zinc-400 font-semibold block uppercase">Enlaces directos</span>
          <div class="flex space-x-3 mt-1 text-xs font-mono font-semibold">
            <a :href="getCardmarketUrl(card)" target="_blank" rel="noopener" class="text-indigo-400 hover:underline">Cardmarket ↗</a>
            <a :href="getTcgplayerUrl(card)" target="_blank" rel="noopener" class="text-sky-400 hover:underline">TCGplayer ↗</a>
          </div>
        </div>
      </div>

      <!-- Selección de Estado y Cantidad -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-semibold text-zinc-400 mb-1">Estado de conservación</label>
          <select v-model="condition" class="select-field">
            <option value="NM">NM (Near Mint) - 100%</option>
            <option value="LP">LP (Lightly Played) - 85%</option>
            <option value="MP">MP (Moderately Played) - 70%</option>
            <option value="HP">HP (Heavily Played) - 50%</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-zinc-400 mb-1">Cantidad</label>
          <input type="number" min="1" v-model.number="quantity" class="input-field" />
        </div>
      </div>

      <!-- Acciones finalizadoras -->
      <div class="flex flex-wrap items-center gap-3 pt-2">
        <button type="button" @click="save" class="btn-primary flex-grow justify-center py-3">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Añadir a la Colección</span>
        </button>
        <button type="button" @click="$emit('cancel')" class="btn-secondary py-3">
          Cancelar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { cardmarketUrl as getCardmarketUrl, tcgplayerUrl as getTcgplayerUrl } from '../utils/links'

const props = defineProps({
  card: { type: Object, required: true }
})
const emit = defineEmits(['save', 'cancel'])

const condition = ref('NM')
const quantity = ref(1)

function save() {
  emit('save', {
    ...props.card,
    condition: condition.value,
    quantity: quantity.value
  })
}
</script>