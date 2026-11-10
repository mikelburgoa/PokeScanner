<template>
  <div class="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-rose-600/30 selection:text-rose-200">
    <!-- Header de navegación y estadísticas globales -->
    <StatsHeader :collectionCount="collection.length" />
    
    <!-- Vista principal de contenido -->
    <main class="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view :collection="collection" @refreshCollection="loadCollection" @cardAdded="loadCollection" />
    </main>

    <!-- Footer sutil en tono Carbón -->
    <footer class="bg-zinc-900/60 border-t border-zinc-800/80 py-5 text-center text-xs text-zinc-500 font-mono flex items-center justify-center gap-2">
      <span class="inline-block w-2 h-2 rounded-full bg-rose-600 animate-pulse"></span>
      PokeScanner — Engine Local v2.0 - Created By Mikel Burgoa
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import StatsHeader from './components/StatsHeader.vue'
import { getCollection } from './services/api'

const collection = ref([])

async function loadCollection() {
  try {
    const data = await getCollection()
    collection.value = data
  } catch (e) {
    console.error('Error cargando colección:', e)
  }
}

onMounted(() => {
  loadCollection()
})
</script>