<template>
  <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-2xl flex flex-col md:flex-row gap-6 items-center">
    <div class="relative w-44 sm:w-52 aspect-[3/4] bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-center p-3 overflow-hidden shadow-inner flex-shrink-0">
      <img :src="card.image" :alt="card.name" class="max-h-full max-w-full object-contain drop-shadow-xl" />
    </div>

    <div class="flex-grow space-y-4 w-full">
      <div>
        <div class="flex items-center justify-between">
          <span class="text-xs font-mono uppercase tracking-wider text-red-400 bg-red-950/60 border border-red-500/30 px-2.5 py-0.5 rounded-full">{{ card.set || 'Sin Expansión' }}</span>
          <span class="text-xs font-mono text-slate-400">#{{ card.number }}</span>
        </div>
        <h2 class="text-2xl font-black text-white mt-2">{{ card.name }}</h2>
        <p class="text-xs text-slate-400 mt-0.5">{{ card.rarity }}</p>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
        <div>
          <span class="text-xs text-slate-400 block">Precio Cardmarket</span>
          <span class="text-lg font-bold text-emerald-400 font-mono">{{ (card.price_eur || 0).toFixed(2) }} €</span>
        </div>
        <div>
          <span class="text-xs text-slate-400 block">Precio TCGplayer</span>
          <span class="text-lg font-bold text-sky-400 font-mono">${{ (card.price_usd || 0).toFixed(2) }}</span>
        </div>
        <div class="col-span-2 sm:col-span-1">
          <span class="text-xs text-slate-400 block">Enlaces</span>
          <div class="flex space-x-2 mt-1">
            <a v-if="card.cardmarket_url" :href="card.cardmarket_url" target="_blank" class="text-xs text-indigo-400 hover:underline">Cardmarket ↗</a>
            <a v-if="card.tcgplayer_url" :href="card.tcgplayer_url" target="_blank" class="text-xs text-indigo-400 hover:underline">TCGplayer ↗</a>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Estado de conservación</label>
          <select v-model="condition" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-red-500 transition-colors">
            <option value="NM">NM (Near Mint) - 100%</option>
            <option value="LP">LP (Lightly Played) - 85%</option>
            <option value="MP">MP (Moderately Played) - 70%</option>
            <option value="HP">HP (Heavily Played) - 50%</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Cantidad</label>
          <input type="number" min="1" v-model.number="quantity" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-red-500 font-mono transition-colors" />
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3 pt-2">
        <button @click="save" class="flex-grow px-6 py-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold rounded-xl shadow-lg shadow-red-600/30 transition-all flex items-center justify-center space-x-2">
          <span>🃏</span><span>Añadir a la Colección</span>
        </button>
        <button @click="$emit('cancel')" class="px-5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl transition-all">
          Cancelar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

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
