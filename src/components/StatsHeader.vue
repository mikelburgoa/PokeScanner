<template>
  <header class="bg-slate-900 border-b border-slate-800 sticky top-0 z-30 shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-red-600 via-red-500 to-amber-400 p-0.5 shadow-lg flex items-center justify-center animate-pulse">
          <div class="w-full h-full rounded-full bg-slate-950 flex items-center justify-center">
            <div class="w-3.5 h-3.5 rounded-full bg-red-500 border-2 border-white"></div>
          </div>
        </div>
        <span class="font-extrabold text-xl tracking-wider text-white font-mono bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">PokeScanner</span>
      </div>

      <nav class="flex space-x-1 sm:space-x-2">
        <router-link to="/" class="px-3 sm:px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center space-x-2" :class="[$route.path === '/' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30' : 'text-slate-400 hover:text-white hover:bg-slate-800']">
          <span>📷</span>
          <span class="hidden sm:inline">Escanear</span>
        </router-link>
        <router-link to="/collection" class="px-3 sm:px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center space-x-2" :class="[$route.path === '/collection' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30' : 'text-slate-400 hover:text-white hover:bg-slate-800']">
          <span>🃏</span>
          <span class="hidden sm:inline">Colección</span>
          <span class="bg-slate-800 text-white text-xs px-2 py-0.5 rounded-full font-mono" v-if="collectionCount > 0">{{ collectionCount }}</span>
        </router-link>
        <router-link to="/settings" class="px-3 sm:px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center space-x-2" :class="[$route.path === '/settings' ? 'bg-red-600 text-white shadow-lg shadow-red-600/30' : 'text-slate-400 hover:text-white hover:bg-slate-800']">
          <span>⚙️</span>
          <span class="hidden sm:inline">Ajustes</span>
        </router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
defineProps({
  collectionCount: { type: Number, default: 0 }
})
</script>
