<template>
  <div class="max-w-7xl mx-auto space-y-8 pb-12">
    <!-- Panel de estadísticas y acciones -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl flex flex-col md:flex-row justify-between items-center gap-6">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-6 w-full md:w-auto">
        <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800 text-center">
          <span class="text-xs text-slate-400 block">Cartas Únicas</span>
          <span class="text-2xl font-black text-white font-mono">{{ totalUnique }}</span>
        </div>
        <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800 text-center">
          <span class="text-xs text-slate-400 block">Total Copias</span>
          <span class="text-2xl font-black text-white font-mono">{{ totalCopies }}</span>
        </div>
        <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800 text-center col-span-2">
          <span class="text-xs text-slate-400 block">Valor Estimado Colección</span>
          <span class="text-2xl font-black text-emerald-400 font-mono">{{ totalValue.toFixed(2) }} €</span>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end">
        <button @click="handleRefresh" :disabled="refreshing" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-xl transition-all flex items-center space-x-2 border border-slate-700 disabled:opacity-50">
          <span>🔄</span><span>{{ refreshing ? 'Actualizando...' : 'Actualizar precios' }}</span>
        </button>
        <button @click="handleExportExcel" :disabled="exporting" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-bold rounded-xl shadow-lg shadow-emerald-600/30 transition-all flex items-center space-x-2 disabled:opacity-50">
          <span>📊</span><span>{{ exporting ? 'Exportando...' : 'Exportar Excel' }}</span>
        </button>
      </div>
    </div>

    <!-- Filtros y búsqueda -->
    <div class="flex flex-col sm:flex-row gap-4 items-center justify-between">
      <div class="relative w-full sm:w-96">
        <input type="text" v-model="searchQuery" placeholder="Buscar en la colección por nombre o set..." class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 outline-none focus:border-red-500 transition-colors pl-10" />
        <span class="absolute left-3.5 top-3 text-slate-500">🔍</span>
      </div>

      <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
        <select v-model="selectedSet" class="bg-slate-900 border border-slate-800 text-slate-300 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-red-500 transition-colors">
          <option value="">Todas las expansiones</option>
          <option v-for="s in uniqueSets" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <!-- Cuadrícula de colección o vacío -->
    <CardGrid v-if="filteredCollection.length > 0" :collection="filteredCollection" @delete="removeCard" />

    <div v-else class="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center space-y-4 shadow-xl">
      <div class="w-16 h-16 rounded-full bg-slate-950 border border-slate-800 flex items-center justify-center text-3xl mx-auto shadow">🃏</div>
      <h3 class="text-xl font-bold text-white">Tu colección está vacía</h3>
      <p class="text-sm text-slate-400 max-w-md mx-auto">Escanea tu primera carta de Pokémon con la cámara o súbela para empezar a construir tu colección y calcular su valor en el mercado.</p>
      <router-link to="/" class="inline-block px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl shadow-lg shadow-red-600/30 transition-all">
        📷 Escanear primera carta
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import CardGrid from '../components/CardGrid.vue'
import { deleteCard, refreshPrices, api } from '../services/api'

const props = defineProps({
  collection: { type: Array, required: true }
})
const emit = defineEmits(['refreshCollection'])

const searchQuery = ref('')
const selectedSet = ref('')
const refreshing = ref(false)
const exporting = ref(false)

const COND_MULT = { NM: 1.0, LP: 0.85, MP: 0.70, HP: 0.50 }

const totalUnique = computed(() => props.collection.length)
const totalCopies = computed(() => props.collection.reduce((acc, c) => acc + (c.quantity || 1), 0))
const totalValue = computed(() => {
  return props.collection.reduce((acc, c) => {
    const mult = COND_MULT[(c.condition || 'NM').toUpperCase()] || 1.0
    const price = (c.price_eur || 0) * mult
    const qty = c.quantity || 1
    return acc + (price * qty)
  }, 0)
})

const uniqueSets = computed(() => {
  const sets = props.collection.map(c => c.set || 'Sin Expansión')
  return [...new Set(sets)].sort()
})

const filteredCollection = computed(() => {
  return props.collection.filter(c => {
    const matchQuery = (c.name || '').toLowerCase().includes(searchQuery.value.toLowerCase()) || (c.set || '').toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchSet = !selectedSet.value || (c.set || 'Sin Expansión') === selectedSet.value
    return matchQuery && matchSet
  })
})

async function removeCard(uid) {
  if (!confirm('¿Seguro que deseas eliminar esta carta de la colección?')) return
  try {
    await deleteCard(uid)
    emit('refreshCollection')
  } catch (e) {
    alert(e.message || 'Error al eliminar carta')
  }
}

async function handleRefresh() {
  refreshing.value = true
  try {
    await refreshPrices()
    emit('refreshCollection')
    alert('Precios actualizados correctamente desde TCGdex.')
  } catch (e) {
    alert(e.message || 'Error actualizando precios')
  } finally {
    refreshing.value = false
  }
}

async function handleExportExcel() {
  if (props.collection.length === 0) {
    alert('No hay cartas en la colección para exportar.')
    return
  }
  exporting.value = true
  try {
    const res = await api.get('/api/export_excel')
    alert(res.message || 'Excel generado y actualizado correctamente en server/excel/')
  } catch (e) {
    alert(e.message || 'Error al exportar el archivo Excel')
  } finally {
    exporting.value = false
  }
}
</script>