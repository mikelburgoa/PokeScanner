<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
    <StatsHeader :collectionCount="collection.length" />
    
    <main class="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view :collection="collection" @refreshCollection="loadCollection" @cardAdded="loadCollection" />
    </main>

    <footer class="bg-slate-900 border-t border-slate-800 py-6 text-center text-xs text-slate-500 font-mono">
      PokeScanner — Vue 3 Vite + Tailwind CSS & FastAPI Backend
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
