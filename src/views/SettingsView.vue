<template>
  <div class="w-full space-y-6">
    <!-- Notificación: fija en pantalla para que se vea aunque estés abajo del todo -->
    <div
      v-if="notice"
      role="status"
      aria-live="polite"
      class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[60] w-[calc(100%-2rem)] max-w-md rounded-2xl px-5 py-3 text-sm border shadow-2xl"
      :class="notice.type === 'ok'
        ? 'bg-emerald-950 border-emerald-500/50 text-emerald-200'
        : 'bg-red-950 border-red-500/50 text-red-200'"
    >
      {{ notice.text }}
    </div>

    <!-- Confirmación de acciones destructivas -->
    <div v-if="dialog" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75" @click.self="closeDialog" @keydown.esc="closeDialog">
      <div role="dialog" aria-modal="true" aria-labelledby="dlg-title" class="w-full max-w-md bg-slate-900 rounded-2xl p-6 space-y-4 shadow-2xl border" :class="dialog.danger ? 'border-red-900/70' : 'border-slate-700'">
        <h3 id="dlg-title" class="text-lg font-black text-white">{{ dialog.title }}</h3>
        <p v-for="(l, i) in dialog.lines" :key="i" class="text-sm text-slate-300 leading-relaxed">{{ l }}</p>
        <div v-if="dialog.requireText">
          <label for="dlg-typed" class="block text-xs font-semibold text-slate-400 mb-1">Escribe <strong class="text-red-300">{{ dialog.requireText }}</strong> para confirmar</label>
          <input id="dlg-typed" v-model="typed" autocomplete="off" spellcheck="false" @keydown.enter="confirmDialog" class="w-full bg-slate-950 border border-slate-700 text-slate-100 rounded-lg px-3 py-2 text-sm font-mono outline-none focus:border-emerald-500" />
        </div>
        <div class="flex justify-end gap-2 pt-1">
          <button ref="cancelBtn" type="button" @click="closeDialog" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-lg">Cancelar</button>
          <button
            type="button"
            :disabled="!canConfirm"
            @click="confirmDialog"
            class="px-4 py-2 text-white text-sm font-bold rounded-lg disabled:opacity-40 disabled:cursor-not-allowed"
            :class="dialog.danger ? 'bg-red-600 hover:bg-red-500' : 'bg-emerald-600 hover:bg-emerald-500'"
          >{{ dialog.confirmLabel }}</button>
        </div>
      </div>
    </div>

    <!-- Layout Dashboard: Grid de 2 columnas -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
      
      <!-- Columna Principal / Izquierda: Configuración de IA (7 cols) -->
      <section class="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-xl">
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
          <div class="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
            <p class="text-xs text-slate-400 leading-relaxed min-w-0">
              📁 <strong class="text-slate-300">Ruta de almacenamiento local:</strong><br />
              <code class="font-mono text-slate-300 break-all select-all">{{ info.dataDir }}</code>
            </p>
            <div class="flex gap-2 shrink-0">
              <button type="button" @click="copyDataDir" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-all">Copiar ruta</button>
              <button type="button" @click="openFolder" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg transition-all">Abrir carpeta</button>
            </div>
          </div>

          <!-- Selector de proveedor: las propias tarjetas son el selector -->
          <div role="radiogroup" aria-label="Proveedor activo" class="space-y-3">
            <button
              type="button"
              role="radio"
              :aria-checked="form.provider === 'auto'"
              @click="form.provider = 'auto'"
              class="w-full text-left rounded-xl border p-3 flex items-start gap-3 transition-all outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
              :class="form.provider === 'auto' ? 'border-emerald-500 bg-emerald-950/10' : 'border-slate-800 bg-slate-950/30 hover:border-slate-700'"
            >
              <span class="mt-0.5 w-4 h-4 rounded-full border-2 shrink-0 flex items-center justify-center" :class="form.provider === 'auto' ? 'border-emerald-400' : 'border-slate-600'">
                <span v-if="form.provider === 'auto'" class="w-2 h-2 rounded-full bg-emerald-400"></span>
              </span>
              <span>
                <span class="block text-sm font-bold text-white">Automático</span>
                <span class="block text-xs text-slate-400 mt-0.5">Usa el primero que tenga clave (Gemini → Claude → OpenAI) y, si uno falla, prueba el siguiente.</span>
              </span>
            </button>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                v-for="(p, id) in info.providers"
                :key="id"
                class="rounded-xl border p-3.5 space-y-2.5 transition-all flex flex-col justify-between"
                :class="form.provider === id ? 'border-emerald-500 bg-emerald-950/10' : 'border-slate-800 bg-slate-950/30'"
              >
                <div class="space-y-2">
                  <div class="flex items-center justify-between gap-2">
                    <button
                      type="button"
                      role="radio"
                      :aria-checked="form.provider === id"
                      @click="form.provider = id"
                      class="flex items-center gap-2 text-left rounded outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    >
                      <span class="w-4 h-4 rounded-full border-2 shrink-0 flex items-center justify-center" :class="form.provider === id ? 'border-emerald-400' : 'border-slate-600'">
                        <span v-if="form.provider === id" class="w-2 h-2 rounded-full bg-emerald-400"></span>
                      </span>
                      <span class="font-bold text-white text-sm">{{ p.label }}</span>
                    </button>
                    <span
                      class="text-xs font-semibold rounded-full px-2 py-0.5 whitespace-nowrap"
                      :class="!p.needsKey ? 'bg-indigo-950 text-indigo-300' : p.hasKey ? 'bg-emerald-950 text-emerald-300' : 'bg-slate-800 text-slate-300'"
                    >
                      {{ !p.needsKey ? 'Local' : p.hasKey ? 'Clave guardada' : 'Sin clave' }}
                    </span>
                  </div>
                  <p class="text-xs text-slate-400 leading-normal">
                    {{ META[id]?.hint }}
                    <a :href="META[id]?.link" target="_blank" rel="noopener" class="underline hover:text-white block mt-0.5">{{ META[id]?.linkText }}</a>
                  </p>
                </div>

                <div class="space-y-3 pt-2 border-t border-slate-800/60">
                  <div v-if="p.needsKey">
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1" :for="`key-${id}`">API Key</label>
                    <div class="flex gap-1.5">
                      <div class="relative flex-1 min-w-0">
                        <input
                          :id="`key-${id}`"
                          v-model="form.keys[id]"
                          :type="showKey[id] ? 'text' : 'password'"
                          autocomplete="off"
                          spellcheck="false"
                          :placeholder="p.hasKey ? '•••••••• (guardada)' : 'Pega tu clave'"
                          @input="clearTest(id)"
                          class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-lg pl-2.5 pr-16 py-1.5 text-xs font-mono outline-none focus:border-emerald-500 transition-colors placeholder:text-slate-500"
                        />
                        <button type="button" @click="showKey[id] = !showKey[id]" class="absolute right-1 top-1/2 -translate-y-1/2 px-2 py-0.5 text-xs text-slate-400 hover:text-white rounded">
                          {{ showKey[id] ? 'Ocultar' : 'Mostrar' }}
                        </button>
                      </div>
                      <button v-if="p.hasKey" type="button" @click="askRemoveKey(id)" title="Borra la clave guardada (se aplica al instante)" class="px-2.5 py-1.5 bg-slate-800 hover:bg-red-950/60 text-slate-300 hover:text-red-200 text-xs font-semibold rounded-lg transition-all shrink-0">
                        Borrar
                      </button>
                    </div>
                  </div>
                  <div v-else>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1" for="ollama-url">URL Ollama</label>
                    <input id="ollama-url" v-model="form.ollamaUrl" @input="clearTest(id)" placeholder="http://localhost:11434" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-mono outline-none focus:border-emerald-500 transition-colors placeholder:text-slate-500" />
                  </div>

                  <div>
                    <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1" :for="`model-${id}`">Modelo</label>
                    <input :id="`model-${id}`" v-model="form.models[id]" :list="`models-${id}`" @input="clearTest(id)" autocomplete="off" class="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-mono outline-none focus:border-emerald-500 transition-colors" />
                    <datalist :id="`models-${id}`"><option v-for="m in MODEL_HINTS[id]" :key="m" :value="m" /></datalist>
                    <p v-if="p.retiredModel" class="text-xs text-amber-300 mt-1 leading-snug">
                      El modelo guardado («{{ p.retiredModel }}») ya no existe. Se usa «{{ p.model }}»; pulsa Guardar para dejarlo fijado.
                    </p>
                  </div>

                  <div class="space-y-1.5">
                    <button type="button" :disabled="tests[id]?.loading" @click="runTest(id)" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs font-semibold rounded-lg transition-all">
                      {{ tests[id]?.loading ? 'Probando…' : 'Probar conexión' }}
                    </button>
                    <p v-if="tests[id] && !tests[id].loading" role="status" class="text-xs leading-snug" :class="tests[id].ok ? 'text-emerald-300' : 'text-red-300'">
                      {{ tests[id].ok ? '✓' : '✕' }} {{ tests[id].msg }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-2">
            <button type="button" :disabled="saving || !dirty" @click="saveAi" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all shadow-lg shadow-emerald-950/30">
              {{ saving ? 'Guardando…' : dirty ? 'Guardar cambios' : 'Todo guardado' }}
            </button>
            <p v-if="dirty" class="text-xs text-amber-300 text-center">Tienes cambios sin guardar.</p>
          </div>
        </template>
      </section>

      <!-- Columna Derecha: Auditoría + Herramientas (5 cols) -->
      <div class="lg:col-span-5 space-y-5">
        
        <!-- Auditoría de Seguridad -->
        <section class="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-xl">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-xl font-black text-white flex items-center gap-2">
                <span>🛡️</span> Auditoría
              </h2>
              <p class="text-xs text-slate-400 mt-0.5">Revisa el código y la configuración de esta instalación.</p>
            </div>
            <button type="button" :disabled="auditLoading" @click="checkSecurity" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs font-semibold rounded-lg transition-all border border-slate-700/50 shrink-0">
              {{ auditLoading ? 'Revisando…' : 'Volver a revisar' }}
            </button>
          </div>

          <p v-if="auditError" class="rounded-xl border border-red-500/40 bg-red-950/20 p-3 text-xs text-red-300">
            No se pudo ejecutar la auditoría: {{ auditError }}
          </p>

          <div v-else-if="auditData" class="rounded-xl border p-4 space-y-3" :class="auditData.passed ? 'border-emerald-500/40 bg-emerald-950/20' : 'border-amber-500/40 bg-amber-950/20'">
            <div class="flex items-start gap-2">
              <span class="text-lg leading-none">{{ auditData.passed ? '✅' : '⚠️' }}</span>
              <div>
                <h3 class="font-bold text-xs" :class="auditData.passed ? 'text-emerald-400' : 'text-amber-300'">
                  {{ auditData.passed
                    ? `Sin hallazgos en las ${auditData.checks?.length || 0} comprobaciones`
                    : `${auditData.total_findings} hallazgo(s) que revisar` }}
                </h3>
                <p class="text-xs text-slate-400 mt-0.5">Es un análisis automático de lo que comprueba la lista de abajo; no garantiza que no existan otros riesgos.</p>
              </div>
            </div>

            <div v-if="auditData.findings && auditData.findings.length > 0" class="space-y-2 pt-1">
              <div v-for="(f, i) in auditData.findings" :key="i" class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs space-y-1">
                <div class="flex justify-between font-bold text-slate-200">
                  <span>{{ f.category }}</span>
                  <span class="text-amber-300 uppercase font-mono text-xs">{{ f.severity }}</span>
                </div>
                <p class="text-slate-300 text-xs">{{ f.issue }}</p>
                <p class="text-slate-400 italic text-xs">💡 {{ f.fix }}</p>
              </div>
            </div>

            <details v-if="auditData.checks?.length" class="text-xs">
              <summary class="cursor-pointer text-slate-400 hover:text-slate-200 select-none">Qué se ha comprobado</summary>
              <ul class="mt-2 space-y-1">
                <li v-for="c in auditData.checks" :key="c.name" class="flex items-start gap-2 text-slate-300">
                  <span :class="c.ok ? 'text-emerald-400' : 'text-amber-300'">{{ c.ok ? '✓' : '!' }}</span>
                  <span>{{ c.name }}</span>
                </li>
              </ul>
            </details>
          </div>

          <p v-else class="text-xs text-slate-400">Revisando…</p>
        </section>

        <!-- Recuperar -->
        <section class="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-xl">
          <div>
            <h2 class="text-xl font-black text-white flex items-center gap-2"><span>🕘</span> Copias de seguridad</h2>
            <p class="text-xs text-slate-400 mt-0.5">Antes de vaciar la colección se guarda una copia automática (se conservan las últimas 10).</p>
          </div>
          <p class="text-xs text-slate-300">
            <template v-if="backups.latest">Última copia: <strong>{{ backups.latest.cards }} carta(s)</strong>, {{ formatDateTime(backups.latest.date) }}.</template>
            <template v-else>Todavía no hay copias.</template>
          </p>
          <button type="button" :disabled="!backups.latest" @click="askRestore" class="w-full px-4 py-2.5 bg-emerald-950/40 hover:bg-emerald-900/40 disabled:opacity-40 disabled:cursor-not-allowed border border-emerald-700/40 text-emerald-200 text-sm font-semibold rounded-xl transition-all text-left">
            ↩️ Restaurar la última copia
          </button>
        </section>

        <!-- Zona de peligro -->
        <section class="bg-red-950/10 border border-red-900/50 rounded-2xl p-5 space-y-4 shadow-xl">
          <div>
            <h2 class="text-xl font-black text-red-300 flex items-center gap-2"><span>⚠️</span> Zona de peligro</h2>
            <p class="text-xs text-slate-400 mt-0.5">Estas acciones borran datos. Te pediremos confirmar antes de hacerlas.</p>
          </div>

          <div class="flex flex-col gap-2.5">
            <button type="button" @click="askDeleteExcel" class="px-4 py-2.5 border border-red-800/60 hover:bg-red-950/50 text-red-200 text-sm font-semibold rounded-xl transition-all text-left flex items-center gap-2">
              <span>🗑️</span> Borrar el archivo Excel
            </button>
            <button type="button" @click="askEmptyCollection" class="px-4 py-2.5 border border-red-800/60 hover:bg-red-950/50 text-red-200 text-sm font-semibold rounded-xl transition-all text-left flex items-center gap-2">
              <span>🧹</span> Vaciar toda la colección
            </button>
            <button type="button" @click="askResetAll" class="px-4 py-2.5 bg-red-700 hover:bg-red-600 text-white text-sm font-bold rounded-xl transition-all text-left flex items-center gap-2">
              <span>💥</span> Restablecer todo (colección + Excel)
            </button>
          </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { getSettings, saveSettings, clearExcel, clearCollection, getSecurityAudit, getBackups, restoreBackup, testProvider, openDataDir } from '../services/api'
import { formatDateTime } from '../utils/format'

const props = defineProps({ collection: { type: Array, default: () => [] } })
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
// Sugerencias al escribir el modelo (se puede poner cualquier otro)
const MODEL_HINTS = {
  gemini: ['gemini-flash-lite-latest', 'gemini-flash-latest'],
  anthropic: ['claude-sonnet-5-5', 'claude-haiku-5-5', 'claude-opus-5-5'],
  openai: ['gpt-4o-mini', 'gpt-4o'],
  ollama: ['qwen2.5vl', 'llava', 'llama3.2-vision'],
}

const info = ref(null)
const auditData = ref(null)
const auditLoading = ref(false)
const auditError = ref('')
const backups = ref({ count: 0, latest: null })
const dialog = ref(null)
const typed = ref('')
const cancelBtn = ref(null)
const saving = ref(false)
const tests = reactive({})
const showKey = reactive({})
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

async function copyDataDir() {
  try {
    await navigator.clipboard.writeText(info.value.dataDir)
    say('Ruta copiada.')
  } catch {
    say('No se pudo copiar. Selecciona la ruta y cópiala con Ctrl+C.', 'error')
  }
}

async function openFolder() {
  try {
    await openDataDir()
    say('Carpeta abierta en el explorador.')
  } catch (e) {
    say(e.message, 'error')
  }
}

async function checkSecurity() {
  auditLoading.value = true
  auditError.value = ''
  try {
    auditData.value = await getSecurityAudit()
  } catch (e) {
    auditError.value = e.message || 'error desconocido'
  } finally {
    auditLoading.value = false
  }
}

async function loadBackups() {
  try {
    backups.value = await getBackups()
  } catch {
    backups.value = { count: 0, latest: null }
  }
}

onMounted(() => {
  getSettings()
    .then(applyInfo)
    .catch((e) => say(e.message, 'error'))
  checkSecurity()
  loadBackups()
})

// ¿Hay algo escrito en pantalla que no esté guardado?
const dirty = computed(() => {
  const s = info.value
  if (!s) return false
  if (form.provider !== s.provider || form.ollamaUrl !== s.ollamaUrl) return true
  if (Object.entries(s.providers).some(([id, p]) => form.models[id] !== p.model)) return true
  return KEYED.some((id) => form.keys[id]?.trim())
})

onBeforeRouteLeave(() => {
  if (dirty.value && !window.confirm('Tienes cambios sin guardar en Ajustes. ¿Salir sin guardar?')) return false
})

function clearTest(id) {
  delete tests[id]
}

async function runTest(id) {
  tests[id] = { loading: true }
  try {
    const r = await testProvider({
      provider: id,
      key: form.keys[id]?.trim() || '',
      model: form.models[id]?.trim() || '',
      ollamaUrl: id === 'ollama' ? form.ollamaUrl.trim() : '',
    })
    tests[id] = { ok: r.ok, msg: r.message }
  } catch (e) {
    tests[id] = { ok: false, msg: e.message || 'No se pudo hacer la prueba.' }
  }
}

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

function askRemoveKey(id) {
  const label = info.value?.providers?.[id]?.label
  if (!label) return
  ask({
    title: `¿Borrar la clave de ${label}?`,
    lines: ['La clave se elimina de tu equipo ahora mismo (no hace falta pulsar «Guardar»). Tendrás que volver a pegarla para usar este proveedor.'],
    confirmLabel: 'Borrar clave',
    danger: true,
    action: () => removeKey(id),
  })
}

async function removeKey(id) {
  try {
    info.value = await saveSettings({ keys: { [id]: null } })  // solo se actualiza el estado; lo escrito en pantalla se conserva
    form.keys[id] = ''
    clearTest(id)
    say('Clave borrada.')
  } catch (e) {
    say(e.message, 'error')
  }
}

async function run(fn, okMsg, refresh = false, after = null) {
  try {
    await fn()
    if (refresh) emit('refreshCollection')
    if (after) await after()
    say(okMsg)
  } catch (e) {
    say(e.message || 'Ha ocurrido un error.', 'error')
  }
}

// --- Confirmaciones (modal propio en vez de confirm() del navegador)
const canConfirm = computed(() => !dialog.value?.requireText || typed.value.trim().toUpperCase() === dialog.value.requireText)

function ask(cfg) {
  typed.value = ''
  dialog.value = cfg
}
function closeDialog() {
  dialog.value = null
}
async function confirmDialog() {
  if (!canConfirm.value) return
  const d = dialog.value
  dialog.value = null
  await d.action()
}
watch(dialog, async (d) => {
  if (d) {
    await nextTick()
    cancelBtn.value?.focus() // por defecto el foco queda en «Cancelar»
  }
})

const BACKUP_NOTE = 'Antes de borrar se guarda una copia automática que podrás recuperar con «Restaurar la última copia».'

function askDeleteExcel() {
  ask({
    title: '¿Borrar el archivo Excel?',
    lines: ['Se eliminará coleccion_pokemon.xlsx. Tu colección no se toca y puedes volver a generarlo con «Exportar Excel».'],
    confirmLabel: 'Borrar Excel',
    danger: true,
    action: () => run(() => clearExcel(), 'Archivo Excel eliminado.'),
  })
}

function askEmptyCollection() {
  const n = props.collection.length
  ask({
    title: '¿Vaciar toda la colección?',
    lines: [n ? `Se eliminarán las ${n} carta(s) de tu colección.` : 'Tu colección ya está vacía.', BACKUP_NOTE],
    confirmLabel: 'Vaciar colección',
    danger: true,
    action: () => run(() => clearCollection(), 'Colección vaciada. Puedes recuperarla desde «Copias de seguridad».', true, loadBackups),
  })
}

function askResetAll() {
  const n = props.collection.length
  ask({
    title: '¿Restablecer todo?',
    lines: [`Se eliminarán las ${n} carta(s) de tu colección y el archivo Excel.`, BACKUP_NOTE],
    requireText: 'BORRAR',
    confirmLabel: 'Restablecer todo',
    danger: true,
    action: () =>
      run(async () => {
        await clearCollection()
        await clearExcel()
      }, 'Todo restablecido a cero.', true, loadBackups),
  })
}

function askRestore() {
  const b = backups.value.latest
  if (!b) return
  ask({
    title: '¿Restaurar la última copia?',
    lines: [
      `Tu colección pasará a ser la de la copia: ${b.cards} carta(s), ${formatDateTime(b.date)}.`,
      'Lo que tengas ahora se guarda antes en otra copia, así que también se puede deshacer.',
    ],
    confirmLabel: 'Restaurar',
    danger: false,
    action: () => run(() => restoreBackup(), 'Colección restaurada.', true, loadBackups),
  })
}
</script>