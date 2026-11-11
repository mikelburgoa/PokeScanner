<template>
  <!-- Teleport: se dibuja fuera de la vista, así no le afecta ningún reescalado ni recorte de la página -->
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75" @click.self="$emit('cancel')" @keydown.esc="$emit('cancel')">
      <div role="dialog" aria-modal="true" aria-labelledby="confirm-title" class="w-full max-w-md bg-zinc-900 rounded-2xl p-6 space-y-4 shadow-2xl border" :class="danger ? 'border-red-900/70' : 'border-zinc-700'">
        <div class="flex items-start gap-4">
          <img v-if="image" :src="image" alt="" class="w-16 aspect-[2.5/3.5] object-contain rounded-lg bg-zinc-950 border border-zinc-800 shrink-0" />
          <div class="space-y-2 min-w-0">
            <h3 id="confirm-title" class="text-lg font-black text-white font-heading">{{ title }}</h3>
            <p v-for="(l, i) in lines" :key="i" class="text-sm text-zinc-300 leading-relaxed">{{ l }}</p>
          </div>
        </div>
        <div class="flex justify-end gap-2 pt-1">
          <button ref="cancelBtn" type="button" @click="$emit('cancel')" class="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-sm font-semibold rounded-lg">Cancelar</button>
          <button type="button" @click="$emit('confirm')" class="px-4 py-2 text-white text-sm font-bold rounded-lg" :class="danger ? 'bg-red-600 hover:bg-red-500' : 'bg-emerald-600 hover:bg-emerald-500'">{{ confirmLabel }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
  lines: { type: Array, default: () => [] },
  image: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Aceptar' },
  danger: { type: Boolean, default: false },
})
defineEmits(['confirm', 'cancel'])

const cancelBtn = ref(null)
watch(() => props.open, async (v) => {
  if (v) {
    await nextTick()
    cancelBtn.value?.focus() // el foco empieza en «Cancelar»: Intro no borra nada por accidente
  }
})
</script>
