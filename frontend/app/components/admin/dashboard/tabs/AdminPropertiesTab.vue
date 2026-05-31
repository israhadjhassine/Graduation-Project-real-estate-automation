<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-primary-950">Global Property Feed</h2>
    </div>

    <!-- Filters Bar -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="relative">
        <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <input 
          :value="propSearchQuery"
          @input="$emit('update:propSearchQuery', ($event.target as HTMLInputElement).value)"
          type="text" 
          placeholder="Search by property name..."
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
        />
      </div>

      <div class="relative">
        <LucideMapPin class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <input 
          :value="propLocationQuery"
          @input="$emit('update:propLocationQuery', ($event.target as HTMLInputElement).value)"
          type="text" 
          placeholder="Filter by city/location..."
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
        />
      </div>
    </div>

    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
       <div v-for="prop in filteredProperties" :key="prop.id" class="relative group">
         <PropertyCard :property="prop" />
         <div class="absolute inset-x-0 bottom-0 p-4 translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all flex gap-2">
           <button 
             @click.stop="$emit('view-property', prop)"
             class="flex-1 bg-white/90 backdrop-blur-md py-2 px-3 rounded-xl text-xs font-bold text-primary-950 hover:bg-white flex items-center justify-center gap-2 shadow-xl"
           >
             <LucideEye class="w-3.5 h-3.5" /> View Details
           </button>
         </div>
       </div>
        <div v-if="!filteredProperties.length" class="col-span-full text-center py-12 text-primary-400">
          {{ properties.length > 0 ? 'No properties match your filters.' : 'No properties listed yet.' }}
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  LucideSearch, LucideMapPin, LucideEye 
} from 'lucide-vue-next'

defineProps<{
  filteredProperties: any[]
  properties: any[]
  propSearchQuery: string
  propLocationQuery: string
}>()

defineEmits<{
  (e: 'update:propSearchQuery', val: string): void
  (e: 'update:propLocationQuery', val: string): void
  (e: 'view-property', property: any): void
}>()
</script>
