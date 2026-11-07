<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-12">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-6">
      <div>
        <h2 class="text-2xl font-black text-white">⚙️ Ajustes de Configuración</h2>
        <p class="text-sm text-slate-400 mt-1">Configura las claves de API de IA y gestiona los datos de tu colección.</p>
      </div>

      <div class="space-y-4 pt-4 border-t border-slate-800">
        <div>
          <label class="block text-sm font-semibold text-slate-300 mb-1">Clave de API de Gemini (Google AI Studio)</label>
          <input type="password" v-model="geminiKey" placeholder="AIza..." class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 outline-none focus:border-red-500 font-mono transition-colors" />
          <p class="text-xs text-slate-500 mt-1">La aplicación incluye una clave integrada por defecto. Puedes proporcionar tu propia clave si lo prefieres.</p>
        </div>

        <button @click="saveSettings" class="px-6 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold rounded-xl shadow-lg shadow-red-600/30 transition-all">
          Guardar Ajustes
        </button>
      </div>

      <div class="space-y-4 pt-6 border-t border-slate-800">
        <h3 class="font-bold text-lg text-white">Zona de Peligro / Gestión de Datos</h3>
        <p class="text-sm text-slate-400">Acciones de mantenimiento y borrado de la colección local.</p>

        <div class="flex flex-wrap gap-4 pt-2">
          <button @click="clearCol" class="px-5 py-2.5 bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 text-red-400 font-semibold rounded-xl transition-all">
            🗑️ Vaciar Colección Completa
          </button>
          <button @click="clearExcelFile" class="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl transition-all border border-slate-700">
            🧹 Limpiar Archivo Excel Temporal
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['refreshCollection'])
const geminiKey = ref(localStorage.getItem('cc_gemini_key') || '')

function saveSettings() {
  localStorage.setItem('cc_gemini_key', geminiKey.value)
  alert('Ajustes guardados correctamente.')
}

async function clearCol() {
  if (!confirm('¿Estás seguro de que deseas vaciar toda la colección? Esta acción no se puede deshacer.')) return
  try {
    const res = await fetch('/api/clear_collection', { method: 'POST' })
    if (res.ok) {
      emit('refreshCollection')
      alert('Colección vaciada con éxito.')
    }
  } catch (e) {
    alert('Error al vaciar colección')
  }
}

async function clearExcelFile() {
  try {
    await fetch('/api/clear_excel', { method: 'POST' })
    alert('Archivo Excel temporal limpiado.')
  } catch (e) {
    alert('Error al limpiar Excel')
  }
}
</script>
