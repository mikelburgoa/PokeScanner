<template>
  <div class="relative w-full aspect-[2.5/3.5] max-w-[360px] mx-auto rounded-2xl overflow-hidden bg-zinc-950 flex items-center justify-center border border-zinc-800 shadow-2xl group">
    <!-- Video en vivo -->
    <video ref="videoRef" playsinline autoplay muted class="w-full h-full object-cover" :hidden="!isCameraActive"></video>
    
    <!-- Imagen capturada / subida -->
    <img v-if="previewUrl && !isCameraActive" :src="previewUrl" class="w-full h-full object-contain bg-zinc-950" alt="Carta escaneada" />
    
    <!-- Placeholder sin cámara -->
    <div v-if="!isCameraActive && !previewUrl" class="absolute inset-0 flex flex-col items-center justify-center p-6 text-center text-zinc-500">
      <div class="w-16 h-16 mb-4 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400 shadow-inner group-hover:border-rose-500/40 transition-colors">
        <svg class="w-8 h-8 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <p class="font-bold text-base text-zinc-200 font-heading">Coloca la carta aquí o activa la cámara</p>
      <p class="text-xs text-zinc-500 mt-2 leading-relaxed">También puedes arrastrar una imagen o usar el botón para subir</p>
    </div>

    <!-- Guía de encuadre en vivo con esquinas rojas mate -->
    <div v-if="isCameraActive" class="absolute inset-5 border border-rose-500/40 rounded-xl pointer-events-none flex items-center justify-center">
      <div class="absolute top-0 left-0 w-5 h-5 border-t-2 border-l-2 border-rose-500 rounded-tl"></div>
      <div class="absolute top-0 right-0 w-5 h-5 border-t-2 border-r-2 border-rose-500 rounded-tr"></div>
      <div class="absolute bottom-0 left-0 w-5 h-5 border-b-2 border-l-2 border-rose-500 rounded-bl"></div>
      <div class="absolute bottom-0 right-0 w-5 h-5 border-b-2 border-r-2 border-rose-500 rounded-br"></div>
      
      <span class="bg-zinc-950/80 text-rose-400 text-[10px] px-3 py-1 rounded-full font-mono uppercase tracking-wider backdrop-blur-md border border-rose-500/30">
        Alinea la carta
      </span>
    </div>

    <input ref="fileInputRef" type="file" accept="image/*" @change="onFileSelected" class="hidden" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
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

function onFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (evt) => {
    const dataUrl = evt.target.result
    previewUrl.value = dataUrl
    stopCamera()
    props.onImageCaptured(dataUrl)
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