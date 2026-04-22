<template>
  <section class="space-y-6 pt-10 border-t border-primary-50">
    <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest">Property Gallery</label>
    <div class="grid grid-cols-4 gap-4">
      <div v-for="(img, i) in previews" :key="i" class="relative group aspect-square rounded-2xl overflow-hidden border border-primary-100">
        <img :src="img" class="w-full h-full object-cover" />
        <button v-if="!readOnly" @click="$emit('remove', i)" class="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
          <LucideX class="w-3 h-3" />
        </button>
      </div>
      <label v-if="!readOnly" class="aspect-square rounded-2xl border-2 border-dashed border-primary-200 flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-primary-50 hover:border-primary-400 transition-all text-primary-300 hover:text-primary-600">
        <LucidePlus class="w-6 h-6" />
        <span class="text-[10px] font-bold uppercase tracking-widest">Add Photos</span>
        <input type="file" multiple @change="$emit('change', $event)" class="hidden" accept="image/*" />
      </label>
    </div>
  </section>
</template>

<script setup>
import { LucideX, LucidePlus } from 'lucide-vue-next'

const props = defineProps({
  previews: Array,
  readOnly: Boolean
})

defineEmits(['change', 'remove'])
</script>
