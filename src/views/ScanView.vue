<template>
  <div class="w-full space-y-6">
    <!-- Grid principal Dashboard: 2 Columnas -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- Columna Izquierda: Visor principal de la cámara (7 cols) -->
      <div class="lg:col-span-7 panel-card flex flex-col items-center justify-center p-6 min-h-[34rem]">
        <CameraScanner ref="scannerRef" :onImageCaptured="handleImageCaptured" :busy="loading" />
      </div>

      <!-- Columna Derecha: Controles de Escaneo + Últimas Detectadas (5 cols) -->
      <div class="lg:col-span-5 space-y-6">
        
        <!-- Panel 1: Controles de Escaneo -->
        <section class="panel-card space-y-4">
          <h2 class="text-lg font-bold text-zinc-100 font-heading">Controles de Escaneo</h2>
          
          <div class="flex flex-col gap-3">
            <button
              v-if="!isCamActive"
              type="button"
              @click="scannerRef?.startCamera()"
              class="btn-primary w-full py-3.5 text-base"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>Activar cámara</span>
            </button>

            <button
              v-else
              type="button"
              @click="scannerRef?.capturePhoto()"
              class="btn-primary bg-emerald-600 hover:bg-emerald-500 border-emerald-500/30 shadow-emerald-950/50 animate-pulse w-full py-3.5 text-base"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              </svg>
              <span>Capturar carta (Espacio)</span>
            </button>

            <button
              v-if="isCamActive"
              type="button"
              @click="scannerRef?.stopCamera()"
              class="btn-secondary w-full"
            >
              Detener cámara
            </button>

            <button
              type="button"
              @click="scannerRef?.triggerFileInput()"
              class="btn-secondary w-full"
            >
              <svg class="w-4 h-4 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <span>Subir archivo</span>
            </button>
          </div>

          <p class="text-xs text-zinc-400 leading-relaxed">
            <kbd class="px-1.5 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200 font-mono">Espacio</kbd>
            captura la foto cuando la cámara está activa. También puedes arrastrar una imagen al recuadro.
          </p>

          <!-- Selector de fuente de cámara si hay más de una -->
          <div v-if="availableCameras.length > 1 && isCamActive" class="pt-2">
            <label class="block text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-1">Fuente / Cámara</label>
            <select
              :value="scannerRef?.selectedCameraId"
              @change="scannerRef?.switchCamera($event.target.value)"
              class="select-field text-xs"
            >
              <option v-for="cam in availableCameras" :key="cam.deviceId" :value="cam.deviceId">
                {{ cam.label || `Cámara ${availableCameras.indexOf(cam) + 1}` }}
              </option>
            </select>
          </div>
        </section>

        <!-- Panel 2: Últimas Cartas Detectadas (Historial recientemete escaneado) -->
        <section class="panel-card space-y-3">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-zinc-100 font-heading">Últimas Cartas Detectadas</h2>
            <span class="text-xs text-zinc-400 font-mono">Feed reciente</span>
          </div>

          <div v-if="recentScans.length > 0" class="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
            <div
              v-for="card in recentScans"
              :key="card.uid || card.id"
              class="bg-zinc-950 border border-zinc-800/80 rounded-xl p-2 shrink-0 w-28 text-center space-y-1 hover:border-rose-500/50 transition-colors cursor-pointer"
              @click="selectedCard = card"
            >
              <div class="aspect-[2.5/3.5] bg-zinc-900 rounded-lg overflow-hidden flex items-center justify-center p-1 border border-zinc-800">
                <img :src="card.image" :alt="card.name" class="max-h-full max-w-full object-contain" />
              </div>
              <p class="text-xs font-bold text-zinc-200 truncate">{{ card.name }}</p>
              <p class="text-xs text-emerald-400 font-mono font-bold">{{ Number(card.price_eur || card.price || 0).toFixed(2) }} €</p>
            </div>
          </div>

          <div v-else class="panel-card-subtle text-center py-6 text-xs text-zinc-400">
            Aún no has escaneado cartas en esta sesión.
          </div>
        </section>

      </div>
    </div>

    <!-- Error de escaneo -->
    <div v-if="errorMsg" role="alert" class="bg-red-950/30 border border-red-500/40 rounded-2xl p-4 text-red-300 text-xs sm:text-sm flex items-start justify-between gap-4">
      <div class="flex items-start gap-2">
        <svg class="w-4 h-4 text-red-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="space-y-1">
          <p>{{ errorMsg }}</p>
          <p v-if="errorKind === 'scan'" class="text-red-300/80">Prueba con más luz, sin reflejos y con la carta entera y recta dentro del recuadro.</p>
          <router-link v-if="/ajustes|api key/i.test(errorMsg)" to="/settings" class="inline-block underline font-semibold hover:text-white">Ir a Ajustes</router-link>
        </div>
      </div>
      <button type="button" @click="errorMsg = ''" class="text-xs font-semibold underline text-red-300 hover:text-white shrink-0">
        Cerrar
      </button>
    </div>

    <!-- Resultado Identificado Principal -->
    <div v-if="selectedCard && !loading" class="space-y-4">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-rose-500"></span>
        <h2 class="text-lg font-bold text-zinc-100 font-heading">Resultado Identificado</h2>
      </div>
      <CardPocket :card="selectedCard" @save="saveCollectedCard" @cancel="selectedCard = null" />
    </div>

    <!-- Candidatos alternativos -->
    <div v-if="candidates.length > 0 && !loading" class="space-y-4 pt-6 border-t border-zinc-800/80">
      <h3 class="font-bold text-sm text-zinc-300 font-heading">¿No es esta la carta? Elige otra coincidencia:</h3>
      
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div
          v-for="cand in candidates"
          :key="cand.id"
          @click="selectCandidate(cand)"
          class="bg-zinc-900 border border-zinc-800 hover:border-rose-500/80 rounded-xl p-3 cursor-pointer transition-all flex flex-col items-center text-center group shadow-md"
        >
          <div class="w-full aspect-[2.5/3.5] bg-zinc-950 rounded-lg overflow-hidden flex items-center justify-center p-1.5 mb-2 border border-zinc-800/60">
            <img :src="cand.image" :alt="cand.name" class="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform" />
          </div>
          <span class="font-bold text-xs text-zinc-200 line-clamp-1 w-full">{{ cand.name }}</span>
          <span class="text-xs text-zinc-400 font-mono mt-0.5">#{{ cand.number }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import CameraScanner from '../components/CameraScanner.vue'
import CardPocket from '../components/CardPocket.vue'
import { identifyCard, saveCard } from '../services/api'

const router = useRouter()
const emit = defineEmits(['cardAdded'])

const scannerRef = ref(null)
const loading = ref(false)
const errorMsg = ref('')
const errorKind = ref('')  // 'scan' = no se reconoció la carta; 'system' = fallo del servidor, la clave, etc.
const selectedCard = ref(null)
const candidates = ref([])
const recentScans = ref([])

const isCamActive = computed(() => scannerRef.value?.isCameraActive || false)
const availableCameras = computed(() => scannerRef.value?.cameras || [])

async function handleImageCaptured(base64Data) {
  loading.value = true
  errorMsg.value = ''
  errorKind.value = ''
  selectedCard.value = null
  candidates.value = []

  try {
    const res = await identifyCard(base64Data)
    if (!res.success) {
      errorMsg.value = res.message || 'No se pudo identificar la carta.'
      errorKind.value = 'scan'
      return
    }
    candidates.value = res.candidates || []
    if (candidates.value.length > 0) {
      selectedCard.value = candidates.value[0]
      recentScans.value.unshift(candidates.value[0])
      if (recentScans.value.length > 5) recentScans.value.pop()
    } else {
      errorMsg.value = 'Se identificó la carta pero no se encontró en TCGdex.'
      errorKind.value = 'scan'
    }
  } catch (e) {
    errorMsg.value = e.message || 'Error al conectar con el servidor.'
    errorKind.value = 'system'
  } finally {
    loading.value = false
  }
}

function selectCandidate(cand) {
  selectedCard.value = cand
}

async function saveCollectedCard(cardData) {
  try {
    await saveCard(cardData)
    emit('cardAdded')
    router.push('/collection')
  } catch (e) {
    errorMsg.value = e.message || 'Error al guardar la carta.'
  }
}
</script>