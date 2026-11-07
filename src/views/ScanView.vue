<template>
  <div class="max-w-6xl mx-auto space-y-8 pb-12">
    <CameraScanner :onImageCaptured="handleImageCaptured" />

    <div v-if="loading" class="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center space-y-3 shadow-xl">
      <div class="w-10 h-10 border-4 border-red-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="font-bold text-lg text-white">Analizando la carta con Inteligencia Artificial...</p>
    </div>

    <div v-if="errorMsg" class="bg-red-950/40 border border-red-500/40 rounded-2xl p-5 text-red-300 text-sm flex items-center justify-between">
      <span>{{ errorMsg }}</span>
      <button @click="errorMsg = ''" class="text-xs underline font-semibold">Cerrar</button>
    </div>

    <div v-if="selectedCard && !loading" class="space-y-6">
      <h2 class="text-xl font-black text-white flex items-center space-x-2">
        <span>✨</span><span>Resultado Identificado</span>
      </h2>
      <CardPocket :card="selectedCard" @save="saveCollectedCard" @cancel="selectedCard = null" />
    </div>

    <div v-if="candidates.length > 0 && !loading" class="space-y-4 pt-4 border-t border-slate-800">
      <h3 class="font-bold text-lg text-slate-200">Elige otra coincidencia:</h3>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div v-for="cand in candidates" :key="cand.id" @click="selectCandidate(cand)" class="bg-slate-900 border border-slate-800 hover:border-red-500 rounded-xl p-3 cursor-pointer transition-all flex flex-col items-center text-center group">
          <div class="w-24 h-32 bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center p-2 mb-2">
            <img :src="cand.image" :alt="cand.name" class="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform" />
          </div>
          <span class="font-bold text-xs text-white line-clamp-1 w-full">{{ cand.name }}</span>
          <span class="text-[11px] text-slate-400 font-mono mt-0.5">#{{ cand.number }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CameraScanner from '../components/CameraScanner.vue'
import CardPocket from '../components/CardPocket.vue'
import { identifyCard, saveCard } from '../services/api'

const router = useRouter()
const emit = defineEmits(['cardAdded'])

const loading = ref(false)
const errorMsg = ref('')
const selectedCard = ref(null)
const candidates = ref([])

async function handleImageCaptured(base64Data) {
  loading.value = true
  errorMsg.value = ''
  selectedCard.value = null
  candidates.value = []

  try {
    const res = await identifyCard(base64Data)
    if (!res.success) {
      errorMsg.value = res.message || 'No se pudo identificar la carta.'
      return
    }
    candidates.value = res.candidates || []
    if (candidates.value.length > 0) {
      selectedCard.value = candidates.value[0]
    } else {
      errorMsg.value = 'Se identificó la carta pero no se encontró en TCGdex.'
    }
  } catch (e) {
    errorMsg.value = e.message || 'Error al conectar con el servidor.'
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
