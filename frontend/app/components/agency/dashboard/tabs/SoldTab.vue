<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-primary-950">Sold Portfolio</h2>
    </div>

    <div class="card-premium p-0 overflow-hidden">
      <table class="w-full text-left">
        <thead>
          <tr class="bg-primary-50">
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Sold By</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Client Email</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Price</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-primary-50">
          <tr v-for="prop in properties" @click="$emit('view-property', prop)" :key="prop.id" class="hover:bg-primary-50/50 transition-colors cursor-pointer group">
            <td class="px-6 py-4">
               <p class="font-bold text-primary-950 text-sm group-hover:text-accent-600 transition-colors">{{ prop.title }}</p>
            </td>
            <td class="px-6 py-4">
               <span class="text-xs font-medium text-primary-600">{{ staff.find(s => s.id === prop.agent_id)?.full_name || 'System' }}</span>
            </td>
            <td class="px-6 py-4">
               <span class="text-xs font-medium text-primary-600">{{ clients.find(c => c.id === prop.buyer_id)?.email || 'Unknown' }}</span>
            </td>
            <td class="px-6 py-4 font-bold text-primary-950 text-sm">
              {{ formatPrice(prop.price) }} <span class="text-[10px]">{{ prop.currency }}</span>
            </td>
          </tr>
          <tr v-if="!properties.length">
            <td colspan="4" class="px-6 py-12 text-center text-primary-500">
              <LucideCheckCircle2 class="w-12 h-12 mx-auto text-primary-200 mb-3" />
              <p>No properties have been marked as sold yet.</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LucideCheckCircle2 } from 'lucide-vue-next'

defineProps<{
  properties: any[]
  staff: any[]
  clients: any[]
}>()

defineEmits(['view-property'])

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}
</script>
