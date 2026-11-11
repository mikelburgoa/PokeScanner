<template>
  <div
    class="relative w-full aspect-[2.5/3.5] max-w-[360px] mx-auto rounded-2xl overflow-hidden bg-zinc-950 flex items-center justify-center border shadow-2xl group transition-colors"
    :class="dragging ? 'border-rose-500 bg-rose-950/20' : 'border-zinc-800'"
    @dragover.prevent="dragging = true"
    @dragleave.prevent="dragging = false"
    @drop.prevent="onDrop"
  >
    <!-- Video en vivo -->
    <video ref="videoRef" playsinline autoplay muted class="w-full h-full object-cover" :hidden="!isCameraActive"></video>
    
    <!-- Imagen capturada / subida -->
    <img v-if="previewUrl && !isCameraActive" :src="previewUrl" class="w-full h-full object-contain bg-zinc-950" alt="Carta escaneada" />
    
    <!-- Placeholder sin cámara: zona para soltar una imagen -->
    <div v-if="!isCameraActive && !previewUrl" class="absolute inset-3 flex flex-col items-center justify-center p-6 text-center text-zinc-400 rounded-xl border-2 border-dashed transition-colors" :class="dragging ? 'border-rose-500' : 'border-zinc-700 group-hover:border-rose-500/50'">
      <div class="w-16 h-16 mb-4 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400 shadow-inner">
        <svg class="w-8 h-8 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <template v-if="dragging">
        <p class="font-bold text-base text-rose-300 font-heading">Suelta la imagen aquí</p>
      </template>
      <template v-else>
        <p class="font-bold text-base text-zinc-200 font-heading">Coloca la carta aquí o activa la cámara</p>
        <p class="text-xs text-zinc-400 mt-2 leading-relaxed">Arrastra una imagen a este recuadro o usa «Subir archivo».</p>
        <p class="text-xs text-zinc-400 mt-3">Con la cámara activa, pulsa <kbd class="px-1.5 py-0.5 rounded bg-zinc-800 border border-zinc-700 text-zinc-200 font-mono">Espacio</kbd> para capturar.</p>
      </template>
    </div>

    <!-- Guía de encuadre en vivo con esquinas rojas mate -->
    <div v-if="isCameraActive" class="absolute inset-5 border border-rose-500/40 rounded-xl pointer-events-none flex items-center justify-center">
      <div class="absolute top-0 left-0 w-5 h-5 border-t-2 border-l-2 border-rose-500 rounded-tl"></div>
      <div class="absolute top-0 right-0 w-5 h-5 border-t-2 border-r-2 border-rose-500 rounded-tr"></div>
      <div class="absolute bottom-0 left-0 w-5 h-5 border-b-2 border-l-2 border-rose-500 rounded-bl"></div>
      <div class="absolute bottom-0 right-0 w-5 h-5 border-b-2 border-r-2 border-rose-500 rounded-br"></div>
      
      <span class="bg-zinc-950/80 text-rose-400 text-xs px-3 py-1 rounded-full font-mono uppercase tracking-wider backdrop-blur-md border border-rose-500/30">
        Alinea la carta · Espacio para capturar
      </span>
    </div>

    <!-- Identificando con IA -->
    <div v-if="busy" class="absolute inset-0 bg-zinc-950/75 backdrop-blur-sm flex flex-col items-center justify-center gap-3 text-center p-6" role="status">
      <div class="w-10 h-10 border-4 border-rose-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="font-bold text-zinc-100 font-heading">Identificando carta con IA…</p>
      <p class="text-xs text-zinc-300">Consultando precios y datos en tiempo real.</p>
    </div>

    <!-- Problema con la cámara -->
    <div v-if="cameraError" class="absolute bottom-3 inset-x-3 bg-amber-950/95 border border-amber-500/40 text-amber-200 text-xs p-3 rounded-xl flex items-start gap-2" role="alert">
      <span class="flex-1 leading-snug">{{ cameraError }}</span>
      <button type="button" @click="cameraError = ''" class="font-semibold underline hover:text-white shrink-0">Cerrar</button>
    </div>

    <input ref="fileInputRef" type="file" accept="image/*" @change="onFileSelected" class="hidden" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  onImageCaptured: { type: Function, required: true },
  busy: { type: Boolean, default: false }
})

const videoRef = ref(null)
const fileInputRef = ref(null)
const isCameraActive = ref(false)
const previewUrl = ref(null)
const dragging = ref(false)
const cameraError = ref('')
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
    cameraError.value = ''
    mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      videoRef.value.play()
    }
    isCameraActive.value = true
    previewUrl.value = null
    await getCameras()
  } catch (e) {
    const reasons = {
      NotAllowedError: 'Permiso de cámara denegado. Actívalo con el candado de la barra de direcciones, o usa «Subir archivo».',
      NotFoundError: 'No se ha encontrado ninguna cámara en este equipo. Usa «Subir archivo».',
      NotReadableError: 'La cámara está en uso por otra aplicación. Ciérrala e inténtalo de nuevo.',
      OverconstrainedError: 'Esa cámara ya no está disponible. Elige otra en la lista.',
    }
    cameraError.value = reasons[e?.name] || 'No se pudo acceder a la cámara. Comprueba los permisos o usa «Subir archivo».'
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

async function switchCamera(deviceId) {
  selectedCameraId.value = deviceId
  stopCamera()
  await startCamera()
}

function capturePhoto() {
  if (!videoRef.value) return
  const video = videoRef.value
  const vw = video.videoWidth || 640
  const vh = video.videoHeight || 480

  const canvas = document.createElement('canvas')
  const targetRatio = 2.5 / 3.5

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
  canvas.height = 840
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, canvas.width, canvas.height)

  const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
  previewUrl.value = dataUrl
  stopCamera()
  props.onImageCaptured(dataUrl)
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function readImage(file) {
  if (!file) return
  if (!file.type.startsWith('image/')) {
    cameraError.value = 'Ese archivo no es una imagen. Usa una foto (JPG, PNG, WEBP...).'
    return
  }
  cameraError.value = ''
  const reader = new FileReader()
  reader.onload = (evt) => {
    const dataUrl = evt.target.result
    previewUrl.value = dataUrl
    stopCamera()
    props.onImageCaptured(dataUrl)
  }
  reader.readAsDataURL(file)
}

function onFileSelected(e) {
  readImage(e.target.files[0])
  e.target.value = ''  // permite volver a elegir la misma imagen
}

function onDrop(e) {
  dragging.value = false
  readImage(e.dataTransfer?.files?.[0])
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

defineExpose({
  isCameraActive,
  cameras,
  selectedCameraId,
  startCamera,
  stopCamera,
  switchCamera,
  capturePhoto,
  triggerFileInput
})
</script>