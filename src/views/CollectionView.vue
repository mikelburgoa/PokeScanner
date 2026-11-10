<template>
  <div class="max-w-7xl mx-auto space-y-6 pb-12">
    <!-- Panel Dashboard de métricas y acciones globales -->
    <div class="panel-card flex flex-col md:flex-row justify-between items-center gap-6">
      
      <!-- Bloques de estadísticas -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 w-full md:w-auto flex-grow">
        <div class="panel-card-subtle text-center">
          <span class="text-xs text-zinc-400 font-semibold block uppercase tracking-wider">Cartas Únicas</span>
          <span class="text-2xl font-bold text-zinc-100 font-heading mt-1 block">{{ totalUnique }}</span>
        </div>
        
        <div class="panel-card-subtle text-center">
          <span class="text-xs text-zinc-400 font-semibold block uppercase tracking-wider">Total Copias</span>
          <span class="text-2xl font-bold text-zinc-100 font-heading mt-1 block">{{ totalCopies }}</span>
        </div>
        
        <div class="panel-card-subtle text-center col-span-2 sm:col-span-1">
          <span class="text-xs text-zinc-400 font-semibold block uppercase tracking-wider">Valor Estimado</span>
          <span class="text-2xl font-bold text-emerald-400 font-heading mt-1 block">{{ totalValue.toFixed(2) }} €</span>
        </div>
      </div>

      <!-- Botones de Acción -->
      <div class="flex flex-wrap items-center gap-3 w-full md:w-auto justify-end shrink-0">
        <button type="button" @click="handleRefresh" :disabled="refreshing" class="btn-secondary text-xs sm:text-sm">
          <svg class="w-4 h-4 shrink-0" :class="{ 'animate-spin': refreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>{{ refreshing ? 'Actualizando...' : 'Actualizar precios' }}</span>
        </button>

        <button type="button" @click="handleExportExcel" :disabled="exporting" class="btn-primary text-xs sm:text-sm bg-emerald-600 hover:bg-emerald-500 border-emerald-500/30 shadow-emerald-950/40">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{{ exporting ? 'Exportando...' : 'Exportar Excel' }}</span>
        </button>
      </div>
    </div>

    <!-- Controles de Filtros y Búsqueda -->
    <div class="flex flex-col sm:flex-row gap-4 items-center justify-between">
      <!-- Input de búsqueda -->
      <div class="relative w-full sm:w-80">
        <input type="text" v-model="searchQuery" placeholder="Buscar por nombre o set..." class="input-field pl-9 font-sans" />
        <svg class="w-4 h-4 text-zinc-500 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      <!-- Filtro por set -->
      <div class="w-full sm:w-auto">
        <select v-model="selectedSet" class="select-field w-full sm:w-64 font-sans text-xs">
          <option value="">Todas las expansiones</option>
          <option v-for="s in uniqueSets" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
    </div>

    <!-- Cuadrícula de Cartas o Estado Vacío -->
    <CardGrid v-if="filteredCollection.length > 0" :collection="filteredCollection" @delete="removeCard" />

    <div v-else class="panel-card p-12 text-center space-y-4 shadow-2xl">
      <div class="w-16 h-16 rounded-2xl bg-zinc-950 border border-zinc-800 flex items-center justify-center text-zinc-500 mx-auto">
        <svg class="w-8 h-8 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <div>
        <h3 class="text-lg font-bold text-zinc-100 font-heading">Tu colección está vacía</h3>
        <p class="text-xs text-zinc-400 max-w-md mx-auto mt-1 leading-relaxed">
          Escanea tu primera carta de Pokémon con la cámara o sube un archivo para calcular el valor del mercado en tiempo real.
        </p>
      </div>
      <router-link to="/" class="btn-primary inline-flex mt-2">
        <span>Escanear primera carta</span>
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

const totalUnique = computed(() => props.collection.length)
const totalCopies = computed(() => props.collection.reduce((acc, c) => acc + (c.quantity || 1), 0))
const totalValue = computed(() => props.collection.reduce((acc, c) => acc + (c.value_eur || 0), 0))

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