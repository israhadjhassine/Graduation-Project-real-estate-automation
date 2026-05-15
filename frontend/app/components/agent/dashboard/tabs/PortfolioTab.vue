<template>
  <div class="card-premium p-0 overflow-hidden">
    <table class="w-full text-left">
      <thead>
        <tr class="bg-primary-50">
          <th class="px-6 py-4 text-xs font-bold text-primary-600">Property</th>
          <th class="px-6 py-4 text-xs font-bold text-primary-600">Price</th>
          <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
          <th class="px-6 py-4 text-xs font-bold text-primary-600 text-right">Actions</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-primary-100">
        <tr v-for="prop in myProperties" :key="prop.id" @click="$emit('view-property', prop)" class="hover:bg-primary-50/50 transition-colors cursor-pointer group">
          <td class="px-6 py-4">
             <p class="font-bold text-sm text-primary-950 group-hover:text-accent-600 transition-colors">{{ prop.title }}</p>
             <p class="text-[10px] text-primary-400">{{ prop.city }}</p>
          </td>
          <td class="px-6 py-4 text-sm font-bold text-primary-950">
             {{ prop.price }} {{ prop.currency }}
          </td>
          <td class="px-6 py-4">
             <span :class="[
               'px-2 py-1 text-[10px] font-bold rounded-lg uppercase',
               prop.status === 'sold' ? 'bg-purple-100 text-purple-700' : prop.status === 'pending_sold' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
             ]">
                {{ prop.status }}
             </span>
          </td>
          <td class="px-6 py-4 text-right" @click.stop>
              <template v-if="prop.status === 'available'">
                <button 
                  v-if="prop.listing_type === 'sale'"
                  @click="$emit('open-sale-modal', prop.id)"
                  class="px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-xl text-[10px] font-bold uppercase transition-all shadow-lg shadow-accent-900/10 mb-1 inline-block"
                >
                  Request Sale
                </button>
                <button 
                  v-if="prop.listing_type === 'rent'"
                  @click="$emit('open-rent-modal', prop.id)"
                  class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-[10px] font-bold uppercase transition-all shadow-lg shadow-blue-900/10 mb-1 inline-block"
                >
                  Request Rent
                </button>
              </template>
              <span v-else-if="prop.status === 'pending_sold' || prop.status === 'pending_rent'" class="px-3 py-1 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-lg uppercase animate-pulse">
                Approval Pending
              </span>
              <span v-else class="text-[10px] font-bold text-primary-300 uppercase italic">Goal Reached</span>
          </td>
        </tr>
        <tr v-if="!myProperties.length">
           <td colspan="4" class="py-12 text-center text-primary-500">
              <LucideHome class="w-12 h-12 text-primary-200 mx-auto mb-3" />
              <p>No listings assigned to you yet.</p>
           </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { LucideHome } from 'lucide-vue-next'

defineProps<{
  myProperties: any[]
}>()

defineEmits(['view-property', 'open-sale-modal', 'open-rent-modal'])
</script>
