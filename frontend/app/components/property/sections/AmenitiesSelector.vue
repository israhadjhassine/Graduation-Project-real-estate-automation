<template>
  <section class="space-y-6 pt-10 border-t border-primary-50">
    <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest">Amenities & Features</label>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <label 
        v-for="feature in availableFeatures" 
        :key="feature.id"
        class="flex items-center gap-3 p-4 rounded-2xl border cursor-pointer transition-all"
        :class="[
          form.feature_ids.includes(feature.id) 
            ? 'bg-primary-50 border-primary-200 text-primary-950' 
            : 'bg-white border-primary-50 text-primary-400 hover:border-primary-100'
        ]"
      >
        <input 
          type="checkbox" 
          :value="feature.id" 
          v-model="form.feature_ids"
          :disabled="readOnly"
          class="hidden"
        />
        <LucideCheckCircle2 
          class="w-4 h-4" 
          :class="form.feature_ids.includes(feature.id) ? 'text-primary-600' : 'text-primary-100'"
        />
        <span class="text-sm font-medium">{{ feature.name }}</span>
      </label>
    </div>
    <div v-if="!availableFeatures.length" class="text-xs text-primary-300 italic">
      Loading amenities...
    </div>
  </section>
</template>

<script setup>
import { LucideCheckCircle2 } from 'lucide-vue-next'

const props = defineProps({
  form: Object,
  availableFeatures: Array,
  readOnly: Boolean
})
</script>
