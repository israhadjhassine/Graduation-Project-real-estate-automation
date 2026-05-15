<template>
  <section class="grid grid-cols-3 gap-6 pt-10 border-t border-primary-50">
    <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
      <LucideBedDouble class="w-6 h-6 text-primary-300" />
      <div class="flex-1">
        <p class="text-[10px] uppercase font-bold text-primary-300">Bedrooms</p>
        <input v-model="form.bedrooms" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
      </div>
    </div>
    <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
      <LucideBath class="w-6 h-6 text-primary-300" />
      <div class="flex-1">
        <p class="text-[10px] uppercase font-bold text-primary-300">Bathrooms</p>
        <input v-model="form.bathrooms" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
      </div>
    </div>
    <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
      <LucideChefHat class="w-6 h-6 text-primary-300" />
      <div class="flex-1">
        <p class="text-[10px] uppercase font-bold text-primary-300">Kitchens</p>
        <input v-model="form.kitchens" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
      </div>
    </div>
    <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
      <LucideLayout class="w-6 h-6 text-primary-300" />
      <div class="flex-1">
        <p class="text-[10px] uppercase font-bold text-primary-300">Living Rooms</p>
        <input v-model="form.living_rooms" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
      </div>
    </div>
    
    <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
      <LucideLayers class="w-6 h-6 text-primary-300" />
      <div class="flex-1">
        <p class="text-[10px] uppercase font-bold text-primary-300">Floor info</p>
        <div class="flex items-center">
          <input v-model="form.floor_number" type="number" :disabled="readOnly" placeholder="No." class="bg-transparent border-none p-0 focus:ring-0 text-lg font-bold w-12" />
           <span class="mx-1 text-primary-200">/</span>
           <input v-model="form.floors" type="number" :disabled="readOnly" placeholder="Total" class="bg-transparent border-none p-0 focus:ring-0 text-lg font-bold w-12" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { 
  LucideBedDouble, LucideBath, 
  LucideChefHat, LucideLayout, LucideLayers 
} from 'lucide-vue-next'

const props = defineProps({
  form: Object,
  readOnly: Boolean
})
</script>
