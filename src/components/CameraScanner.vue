<template>
  <div class="relative bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col items-center justify-center p-4 w-full max-w-md mx-auto">
    <!-- Marco del visor de cámara / previsualización -->
    <div class="relative w-full aspect-[3/4] max-w-[340px] rounded-xl overflow-hidden bg-slate-950 flex items-center justify-center border border-slate-800 shadow-inner">
      <video ref="videoRef" playsinline autoplay muted class="w-full h-full object-cover" :hidden="!isCameraActive"></video>
      <img v-if="previewUrl && !isCameraActive" :src="previewUrl" class="w-full h-full object-contain bg-slate-950" alt="Carta escaneada" />
      
      <div v-if="!isCameraActive && !previewUrl" class="absolute inset-0 flex flex-col items-center justify-center p-6 text-center text-slate-500">
        <div class="w-16 h-16 mb-3 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-2xl shadow">📷</div>
        <p class="font-medium text-slate-300">Coloca la carta aquí o activa la cámara</p>
        <p class="text-xs text-slate-500 mt-1">También puedes arrastrar una imagen o usar el botón de subir</p>
      </div>

      <!-- Guía de encuadre en vivo -->
      <div v-if="isCameraActive" class="absolute inset-6 border-2 border-dashed border-red-500/50 rounded-xl pointer-events-none flex items-center justify-center">
        <span class="bg-slate-900/80 text-red-400 text-xs px-3 py-1 rounded-full font-mono uppercase tracking-wider backdrop-blur-sm border border-red-500/30">Encuadra la carta</span>
      </div>
    </div>

    <!-- Controles -->
    <div class="mt-4 flex flex-wrap items-center justify-center gap-3 w-full">
      <button v-if="!isCameraActive" @click="startCamera" class="px-5 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-semibold rounded-xl shadow-lg shadow-red-600/30 transition-all flex items-center space-x-2">
        <span>📷</span><span>Activar cámara</span>
      </button>

      <button v-if="isCameraActive" @click="capturePhoto" class="px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/30 transition-all flex items-center space-x-2 animate-pulse">
        <span>📸</span><span>Capturar carta (Espacio)</span>
      </button>

      <button v-if="isCameraActive" @click="stopCamera" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl transition-all">
        Detener cámara
      </button>

      <button @click="triggerFileInput" class="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl transition-all flex items-center space-x-2 border border-slate-700">
        <span>📁</span><span>Subir archivo</span>
      </button>
      <input ref="fileInputRef" type="file" accept="image/*" @change="onFileSelected" class="hidden" />
    </div>

    <select v-if="cameras.length > 1 && isCameraActive" v-model="selectedCameraId" @change="switchCamera" class="mt-3 bg-slate-950 border border-slate-800 text-slate-300 text-xs rounded-xl px-3 py-2 outline-none w-full max-w-xs">
      <option v-for="cam in cameras" :key="cam.deviceId" :value="cam.deviceId">{{ cam.label || `Cámara ${cameras.indexOf(cam) + 1}` }}</option>
    </select>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineProps({
  onImageCaptured: { type: Function, required: true }
})

const videoRef = ref(null)
const fileInputRef = ref(null)
const isCameraActive = ref(false)
const previewUrl = ref(null)
const cameras = ref([])
const selectedCameraId = ref(null)
let mediaStream = null

async function getCameras() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    cameras.value = devices.filter(d => d.kind === 'videoinput')
  } catch (e) {
    console.error('Error enumerando cámaras:', e)
  }
}

async function startCamera() {
  try {
    const constraints = {
      video: selectedCameraId.value ? { deviceId: { exact: selectedCameraId.value } } : { facingMode: 'environment' }
    }
    mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      videoRef.value.play()
    }
    isCameraActive.value = true
    previewUrl.value = null
    await getCameras()
  } catch (e) {
    alert('No se pudo acceder a la cámara. Comprueba los permisos o usa subir archivo.')
    console.error(e)
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(t => t.stop())
    mediaStream = null
  }
  isCameraActive.value = false
}

async function switchCamera() {
  stopCamera()
  await startCamera()
}

function capturePhoto() {
  if (!videoRef.value) return
  const video = videoRef.value
  const vw = video.videoWidth || 640
  const vh = video.videoHeight || 480

  // Forzar relación de aspecto vertical 3:4 en el recorte
  const canvas = document.createElement('canvas')
  const targetRatio = 3 / 4

  let sourceWidth = vw
  let sourceHeight = vh
  let sourceX = 0
  let sourceY = 0

  if (vw / vh > targetRatio) {
    sourceWidth = vh * targetRatio
    sourceX = (vw - sourceWidth) / 2
  } else {
    sourceHeight = vw / targetRatio
    sourceY = (vh - sourceHeight) / 2
  }

  canvas.width = 600
  canvas.height = 800
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, canvas.width, canvas.height)

  const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
  previewUrl.value = dataUrl
  stopCamera()
  emit.onImageCaptured(dataUrl)
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (evt) => {
    const dataUrl = evt.target.result
    previewUrl.value = dataUrl
    stopCamera()
    emit.onImageCaptured(dataUrl)
  }
  reader.readAsDataURL(file)
}

function handleKeydown(e) {
  if (e.code === 'Space' && isCameraActive.value) {
    e.preventDefault()
    capturePhoto()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  getCameras()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  stopCamera()
})
</script>