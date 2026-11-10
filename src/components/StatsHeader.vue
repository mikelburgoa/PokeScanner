<template>
  <header class="bg-zinc-950 border-b border-zinc-900 sticky top-0 z-30">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      
      <!-- Logo Pokeball & Marca -->
      <router-link to="/" class="flex items-center space-x-3 group">
        <div class="w-9 h-9 rounded-full bg-zinc-900 border border-zinc-800 p-1 flex items-center justify-center group-hover:border-rose-500/50 transition-colors">
          <div class="w-full h-full rounded-full bg-zinc-950 border border-zinc-800 flex items-center justify-center relative overflow-hidden">
            <div class="absolute top-0 left-0 right-0 h-1/2 bg-rose-600"></div>
            <div class="w-2.5 h-2.5 rounded-full bg-white border border-zinc-950 z-10"></div>
          </div>
        </div>
        <span class="font-bold text-xl tracking-tight text-white font-heading">
          PokeScanner
        </span>
      </router-link>

      <!-- Menú de Navegación -->
      <nav class="flex items-center space-x-3">
        
        <!-- Cápsula Segmentada (Escanear + Colección) -->
        <div class="bg-zinc-900/90 p-1 rounded-2xl border border-zinc-800/80 flex items-center space-x-1 shadow-inner">
          
          <!-- Escanear -->
          <router-link
            to="/"
            class="px-4 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center space-x-2 cursor-pointer"
            :class="[$route.path === '/' 
              ? 'bg-rose-600 text-white shadow-md shadow-rose-950/60' 
              : 'text-zinc-400 hover:text-zinc-200']"
          >
            <span>Escanear</span>
          </router-link>

          <!-- Colección -->
          <router-link
            to="/collection"
            class="px-4 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center space-x-2 cursor-pointer"
            :class="[$route.path === '/collection' 
              ? 'bg-rose-600 text-white shadow-md shadow-rose-950/60' 
              : 'text-zinc-400 hover:text-zinc-200']"
          >
            <span>Colección</span>
            <span
              v-if="collectionCount > 0"
              class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-md bg-zinc-800 text-zinc-300"
            >
              {{ collectionCount }}
            </span>
          </router-link>
        </div>

        <!-- Ajustes (Fuera de la cápsula) -->
        <router-link
          to="/settings"
          class="px-3 py-1.5 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center space-x-1.5 cursor-pointer text-zinc-400 hover:text-zinc-200"
          :class="[$route.path === '/settings' ? 'text-white' : '']"
        >
          <svg class="w-4 h-4 shrink-0 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
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