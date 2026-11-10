<template>
  <div class="max-w-2xl mx-auto space-y-6 pb-12">
    <div
      v-if="notice"
      role="status"
      class="rounded-2xl px-5 py-3 text-sm border"
      :class="notice.type === 'ok'
        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
        : 'bg-red-950/40 border-red-500/40 text-red-300'"
    >
      {{ notice.text }}
    </div>

    <!-- IA -->
    <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5 shadow-xl">
      <div>
        <h2 class="text-xl font-black text-white">🤖 Lectura de fotos (IA)</h2>
        <p class="text-sm text-slate-400 mt-1">
          Elige qué IA identifica tus cartas. Las claves se guardan solo en tu equipo
          (<code class="font-mono text-slate-300">settings.json</code>) y no se vuelven a mostrar.
        </p>
      </div>

      <p v-if="!info" class="text-sm text-slate-400">Cargando…</p>

      <template v-else>
        <p class="text-xs text-slate-500">
          📁 Tus datos (colección, Excel, copias de seguridad y claves) se guardan solo en tu equipo, en:
          <code class="font-mono text-slate-300 break-all">{{ info.dataDir }}</code>
        </p>

        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1" for="ai-provider">Proveedor</label>
          <select id="ai-provider" v-model="form.provider" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-red-500 transition-colors">
            <option value="auto">Automático (el primero con clave: Gemini, Claude, OpenAI)</option>
            <option v-for="(p, id) in info.providers" :key="id" :value="id">{{ p.label }}</option>
          </select>
        </div>

        <div
          v-for="(p, id) in info.providers"
          :key="id"
          class="rounded-xl border p-4 space-y-3 transition-colors"
          :class="form.provider === id ? 'border-red-500' : 'border-slate-800'"
        >
          <div class="flex flex-wrap items-center gap-2">
            <h3 class="font-bold text-white text-sm">{{ p.label }}</h3>
            <span
              class="text-xs font-semibold rounded-full px-2 py-0.5"
              :class="p.needsKey && p.hasKey ? 'bg-emerald-950 text-emerald-300' : 'bg-slate-800 text-slate-400'"
            >
              {{ !p.needsKey ? 'Sin clave' : p.hasKey ? 'Clave guardada' : 'Sin clave' }}
            </span>
          </div>
          <p class="text-xs text-slate-400">
            {{ META[id].hint }}
            <a :href="META[id].link" target="_blank" rel="noopener" class="underline hover:text-white">{{ META[id].linkText }}</a>
          </p>

          <div v-if="p.needsKey">
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1" :for="`key-${id}`">API key</label>
            <div class="flex gap-2">
              <input
                :id="`key-${id}`"
                v-model="form.keys[id]"
                type="password"
                autocomplete="off"
                spellcheck="false"
                :placeholder="p.hasKey ? '•••••••• (deja vacío para conservarla)' : 'Pega aquí tu clave'"
                class="w-full min-w-0 bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-sm font-mono outline-none focus:border-red-500 transition-colors"
              />
              <button v-if="p.hasKey" type="button" @click="removeKey(id)" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold rounded-xl transition-all">
                Borrar
              </button>
            </div>
          </div>
          <div v-else>
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1" for="ollama-url">URL de Ollama</label>
            <input id="ollama-url" v-model="form.ollamaUrl" placeholder="http://localhost:11434" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-sm font-mono outline-none focus:border-red-500 transition-colors" />
          </div>

          <div>
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1" :for="`model-${id}`">Modelo</label>
            <input :id="`model-${id}`" v-model="form.models[id]" autocomplete="off" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-sm font-mono outline-none focus:border-red-500 transition-colors" />
          </div>
        </div>

        <button type="button" :disabled="saving" @click="saveAi" class="px-5 py-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-bold rounded-xl transition-all">
          {{ saving ? 'Guardando…' : 'Guardar ajustes de IA' }}
        </button>
      </template>
    </section>

    <!-- Auditoría de Seguridad -->
    <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-xl font-black text-white">🛡️ Auditoría de Seguridad</h2>
          <p class="text-sm text-slate-400 mt-1">Escaneo interno del sistema y estado de protección de API Keys.</p>
        </div>
        <button type="button" @click="checkSecurity" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-all">
          Reescanear
        </button>
      </div>

      <div v-if="auditData" class="rounded-xl border p-4 space-y-3" :class="auditData.passed ? 'border-emerald-500/40 bg-emerald-950/20' : 'border-red-500/40 bg-red-950/20'">
        <div class="flex items-center gap-2">
          <span class="text-lg">{{ auditData.passed ? '✅' : '⚠️' }}</span>
          <h3 class="font-bold text-sm" :class="auditData.passed ? 'text-emerald-400' : 'text-red-400'">
            {{ auditData.passed ? 'Sistema Seguro: Sin vulnerabilidades ni fugas de claves' : 'Se encontraron advertencias de seguridad' }}
          </h3>
        </div>

        <div v-if="auditData.findings.length > 0" class="space-y-2 pt-2">
          <div v-for="(f, i) in auditData.findings" :key="i" class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs space-y-1">
            <div class="flex justify-between font-bold text-slate-200">
              <span>{{ f.category }}</span>
              <span class="text-red-400 uppercase font-mono">{{ f.severity }}</span>
            </div>
            <p class="text-slate-300">{{ f.issue }}</p>
            <p class="text-slate-400 italic">💡 Solución: {{ f.fix }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Gestión -->
    <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
      <div>
        <h2 class="text-xl font-black text-white">🧰 Gestión de Excel y pruebas</h2>
        <p class="text-sm text-slate-400 mt-1">Opciones para restablecer archivos, borrar el Excel o vaciar la colección durante tus pruebas.</p>
      </div>
      <div class="flex flex-col gap-3">
        <button type="button" @click="deleteExcel" class="px-5 py-3 bg-red-700 hover:bg-red-600 text-white font-semibold rounded-xl transition-all text-left">
          🗑️ Borrar archivo Excel (coleccion_pokemon.xlsx)
        </button>
        <button type="button" @click="emptyCollection" class="px-5 py-3 bg-red-700 hover:bg-red-600 text-white font-semibold rounded-xl transition-all text-left">
          🧹 Vaciar toda la colección
        </button>
        <button type="button" @click="resetAll" class="px-5 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl transition-all text-left">
          🔄 Restablecer todo (colección + Excel)
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getSettings, saveSettings, clearExcel, clearCollection, getSecurityAudit } from '../services/api'

defineProps({ collection: { type: Array, default: () => [] } })
const emit = defineEmits(['refreshCollection'])

const META = {
  gemini: {
    hint: 'Gratis (con límites) y sin tarjeta.',
    link: 'https://aistudio.google.com/apikey',
    linkText: 'Conseguir una key en AI Studio',
  },
  anthropic: {
    hint: 'API de pago. No es lo mismo que la suscripción de Claude.ai.',
    link: 'https://console.anthropic.com/settings/keys',
    linkText: 'Crear una key en Anthropic Console',
  },
  openai: {
    hint: 'API de pago. No es lo mismo que ChatGPT Plus.',
    link: 'https://platform.openai.com/api-keys',
    linkText: 'Crear una key en OpenAI',
  },
  ollama: {
    hint: 'Corre en tu propio PC, sin clave ni coste. Necesita un modelo con visión (p. ej. «ollama pull qwen2.5vl»).',
    link: 'https://ollama.com/download',
    linkText: 'Descargar Ollama',
  },
}
const KEYED = ['gemini', 'anthropic', 'openai']

const info = ref(null)
const auditData = ref(null)
const saving = ref(false)
const notice = ref(null)
let noticeTimer

const form = reactive({
  provider: 'auto',
  ollamaUrl: '',
  keys: { gemini: '', anthropic: '', openai: '' },
  models: { gemini: '', anthropic: '', openai: '', ollama: '' },
})

function say(text, type = 'ok') {
  notice.value = { type, text }
  clearTimeout(noticeTimer)
  noticeTimer = setTimeout(() => (notice.value = null), type === 'ok' ? 3000 : 6000)
}

function applyInfo(s) {
  info.value = s
  form.provider = s.provider
  form.ollamaUrl = s.ollamaUrl
  for (const [id, p] of Object.entries(s.providers)) form.models[id] = p.model
  KEYED.forEach((id) => (form.keys[id] = ''))
}

async function checkSecurity() {
  try {
    auditData.value = await getSecurityAudit()
  } catch (e) {
    console.error('Error obteniendo la auditoría:', e)
  }
}

onMounted(() => {
  getSettings()
    .then(applyInfo)
    .catch((e) => say(e.message, 'error'))
  checkSecurity()
})

async function saveAi() {
  saving.value = true
  try {
    const keys = {}
    KEYED.forEach((id) => {
      if (form.keys[id].trim()) keys[id] = form.keys[id].trim()
    })
    applyInfo(await saveSettings({ provider: form.provider, keys, models: { ...form.models }, ollamaUrl: form.ollamaUrl }))
    say('Ajustes de IA guardados.')
  } catch (e) {
    say(e.message, 'error')
  } finally {
    saving.value = false
  }
}

async function removeKey(id) {
  if (!confirm('¿Borrar la API key guardada de ' + info.value.providers[id].label + '?')) return
  try {
    applyInfo(await saveSettings({ keys: { [id]: null } }))
    say('Clave borrada.')
  } catch (e) {
    say(e.message, 'error')
  }
}

async function run(fn, okMsg, refresh = false) {
  try {
    await fn()
    if (refresh) emit('refreshCollection')
    say(okMsg)
  } catch (e) {
    say(e.message || 'Ha ocurrido un error.', 'error')
  }
}

function deleteExcel() {
  if (!confirm('¿Deseas eliminar el archivo coleccion_pokemon.xlsx del servidor?')) return
  run(() => clearExcel(), 'Archivo Excel eliminado correctamente.')
}

function emptyCollection() {
  if (!confirm('¿Seguro que quieres vaciar la colección entera? Se borrarán todas las cartas.')) return
  run(() => clearCollection(), 'Colección vaciada.', true)
}

function resetAll() {
  if (!confirm('¿Restablecer todo? Se borrarán la colección y el archivo Excel.')) return
  run(async () => {
    await clearCollection()
    await clearExcel()
  }, 'Todo restablecido a cero.', true)
}
</script>