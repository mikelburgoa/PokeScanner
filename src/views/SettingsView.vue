<template>
  <div class="max-w-7xl mx-auto space-y-6 pb-12 px-4">
    <!-- Notificación -->
    <div
      v-if="notice"
      role="status"
      class="rounded-2xl px-5 py-3 text-sm border transition-all"
      :class="notice.type === 'ok'
        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
        : 'bg-red-950/40 border-red-500/40 text-red-300'"
    >
      {{ notice.text }}
    </div>

    <!-- Layout Dashboard: Grid de 2 columnas -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- Columna Principal / Izquierda: Configuración de IA (7 cols) -->
      <section class="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5 shadow-xl">
        <div>
          <h2 class="text-xl font-black text-white flex items-center gap-2">
            <span>🤖</span> Lectura de fotos (IA)
          </h2>
          <p class="text-sm text-slate-400 mt-1">
            Elige qué IA identifica tus cartas. Las claves se guardan solo en tu equipo
            (<code class="font-mono text-slate-300">settings.json</code>) y no se vuelven a mostrar.
          </p>
        </div>

        <p v-if="!info" class="text-sm text-slate-400">Cargando…</p>

        <template v-else>
          <div class="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <p class="text-xs text-slate-400 leading-relaxed">
              📁 <strong class="text-slate-300">Ruta de almacenamiento local:</strong><br />
              <code class="font-mono text-slate-300 break-all select-all">{{ info.dataDir }}</code>
            </p>
          </div>

          <div>
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1" for="ai-provider">Proveedor Activo</label>
            <select id="ai-provider" v-model="form.provider" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-sm outline-none focus:border-red-500 transition-colors">
              <option value="auto">Automático (el primero con clave: Gemini, Claude, OpenAI)</option>
              <option v-for="(p, id) in info.providers" :key="id" :value="id">{{ p.label }}</option>
            </select>
          </div>

          <!-- Cards de Proveedores en Grid de 2 columnas pequeñas -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="(p, id) in info.providers"
              :key="id"
              class="rounded-xl border p-4 space-y-3 transition-all flex flex-col justify-between"
              :class="form.provider === id ? 'border-red-500 bg-red-950/10' : 'border-slate-800 bg-slate-950/30'"
            >
              <div class="space-y-2">
                <div class="flex items-center justify-between gap-2">
                  <h3 class="font-bold text-white text-sm">{{ p.label }}</h3>
                  <span
                    class="text-[10px] font-semibold rounded-full px-2 py-0.5 whitespace-nowrap"
                    :class="!p.needsKey ? 'bg-indigo-950 text-indigo-300' : p.hasKey ? 'bg-emerald-950 text-emerald-300' : 'bg-slate-800 text-slate-400'"
                  >
                    {{ !p.needsKey ? 'Local' : p.hasKey ? 'Clave guardada' : 'Sin clave' }}
                  </span>
                </div>
                <p class="text-[11px] text-slate-400 leading-normal">
                  {{ META[id]?.hint }}
                  <a :href="META[id]?.link" target="_blank" rel="noopener" class="underline hover:text-white block mt-0.5">{{ META[id]?.linkText }}</a>
                </p>
              </div>

              <div class="space-y-3 pt-2 border-t border-slate-800/60">
                <div v-if="p.needsKey">
                  <label class="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1" :for="`key-${id}`">API Key</label>
                  <div class="flex gap-1.5">
                    <input
                      :id="`key-${id}`"
                      v-model="form.keys[id]"
                      type="password"
                      autocomplete="off"
                      spellcheck="false"
                      :placeholder="p.hasKey ? '••••••••' : 'Pega clave'"
                      class="w-full min-w-0 bg-slate-950 border border-slate-800 text-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-mono outline-none focus:border-red-500 transition-colors"
                    />
                    <button v-if="p.hasKey" type="button" @click="removeKey(id)" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg transition-all shrink-0">
                      Borrar
                    </button>
                  </div>
                </div>
                <div v-else>
                  <label class="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1" for="ollama-url">URL Ollama</label>
                  <input id="ollama-url" v-model="form.ollamaUrl" placeholder="http://localhost:11434" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-mono outline-none focus:border-red-500 transition-colors" />
                </div>

                <div>
                  <label class="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1" :for="`model-${id}`">Modelo</label>
                  <input :id="`model-${id}`" v-model="form.models[id]" autocomplete="off" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-mono outline-none focus:border-red-500 transition-colors" />
                </div>
              </div>
            </div>
          </div>

          <button type="button" :disabled="saving" @click="saveAi" class="w-full py-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-bold rounded-xl transition-all shadow-lg shadow-red-950/30">
            {{ saving ? 'Guardando…' : 'Guardar Ajustes de IA' }}
          </button>
        </template>
      </section>

      <!-- Columna Derecha: Auditoría + Herramientas (5 cols) -->
      <div class="lg:col-span-5 space-y-6">
        
        <!-- Auditoría de Seguridad -->
        <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-black text-white flex items-center gap-2">
                <span>🛡️</span> Auditoría
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">Escaneo integral de seguridad.</p>
            </div>
            <button type="button" @click="checkSecurity" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-all border border-slate-700/50">
              Reescanear
            </button>
          </div>

          <div v-if="auditData" class="rounded-xl border p-4 space-y-3" :class="auditData.passed ? 'border-emerald-500/40 bg-emerald-950/20' : 'border-red-500/40 bg-red-950/20'">
            <div class="flex items-center gap-2">
              <span class="text-lg">{{ auditData.passed ? '✅' : '⚠️' }}</span>
              <h3 class="font-bold text-xs" :class="auditData.passed ? 'text-emerald-400' : 'text-red-400'">
                {{ auditData.passed ? 'Sistema Seguro: Sin vulnerabilidades detectadas' : 'Se encontraron advertencias de seguridad' }}
              </h3>
            </div>

            <div v-if="auditData.findings && auditData.findings.length > 0" class="space-y-2 pt-2">
              <div v-for="(f, i) in auditData.findings" :key="i" class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs space-y-1">
                <div class="flex justify-between font-bold text-slate-200">
                  <span>{{ f.category }}</span>
                  <span class="text-red-400 uppercase font-mono text-[10px]">{{ f.severity }}</span>
                </div>
                <p class="text-slate-300 text-[11px]">{{ f.issue }}</p>
                <p class="text-slate-400 italic text-[10px]">💡 {{ f.fix }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Gestión de Excel y Pruebas -->
        <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <div>
            <h2 class="text-xl font-black text-white flex items-center gap-2">
              <span>🧰</span> Herramientas
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">Restablecer datos y mantenimiento de la colección.</p>
          </div>

          <div class="flex flex-col gap-2.5">
            <button type="button" @click="deleteExcel" class="px-4 py-2.5 bg-red-950/40 hover:bg-red-900/50 border border-red-800/40 text-red-200 text-xs font-semibold rounded-xl transition-all text-left flex items-center gap-2">
              <span>🗑️</span> Borrar Excel (coleccion_pokemon.xlsx)
            </button>
            <button type="button" @click="emptyCollection" class="px-4 py-2.5 bg-red-950/40 hover:bg-red-900/50 border border-red-800/40 text-red-200 text-xs font-semibold rounded-xl transition-all text-left flex items-center gap-2">
              <span>🧹</span> Vaciar toda la colección
            </button>
            <button type="button" @click="resetAll" class="px-4 py-2.5 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/50 text-slate-300 text-xs font-semibold rounded-xl transition-all text-left flex items-center gap-2">
              <span>🔄</span> Restablecer todo a cero
            </button>
          </div>
        </section>

      </div>
    </div>
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
    linkText: 'Consigue key en AI Studio',
  },
  anthropic: {
    hint: 'API de pago (Claude API).',
    link: 'https://console.anthropic.com/settings/keys',
    linkText: 'Consigue key en Anthropic',
  },
  openai: {
    hint: 'API de pago (OpenAI Platform).',
    link: 'https://platform.openai.com/api-keys',
    linkText: 'Consigue key en OpenAI',
  },
  ollama: {
    hint: 'Ejecución 100% local sin costes.',
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
  if (!s) return
  info.value = s
  form.provider = s.provider || 'auto'
  form.ollamaUrl = s.ollamaUrl || ''
  if (s.providers) {
    for (const [id, p] of Object.entries(s.providers)) {
      form.models[id] = p?.model || ''
    }
  }
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
      if (form.keys[id]?.trim()) keys[id] = form.keys[id].trim()
    })
    const res = await saveSettings({ provider: form.provider, keys, models: { ...form.models }, ollamaUrl: form.ollamaUrl })
    applyInfo(res)
    say('Ajustes de IA guardados.')
  } catch (e) {
    say(e.message, 'error')
  } finally {
    saving.value = false
  }
}

async function removeKey(id) {
  if (!info.value?.providers?.[id]) return
  if (!confirm('¿Borrar la API key guardada de ' + info.value.providers[id].label + '?')) return
  try {
    const res = await saveSettings({ keys: { [id]: null } })
    applyInfo(res)
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