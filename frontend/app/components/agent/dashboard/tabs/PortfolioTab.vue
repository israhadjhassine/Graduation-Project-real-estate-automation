<template>
  <div class="space-y-4">
    <!-- Filters Bar -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="relative">
        <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Search by property name..."
          class="w-full pl-11 pr-4 py-2.5 bg-white border border-primary-100 rounded-2xl text-xs focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
        />
      </div>

      <div class="relative">
        <LucideFilter class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <select 
          v-model="statusFilter"
          class="w-full pl-11 pr-4 py-2.5 bg-white border border-primary-100 rounded-2xl text-xs focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm appearance-none cursor-pointer"
        >
          <option value="all">All Statuses</option>
          <option value="available">Available</option>
          <option value="pending_sold">Pending Sale Approval</option>
          <option value="pending_rent">Pending Rent Approval</option>
          <option value="approved_sold">Approved Sale</option>
          <option value="approved_rent">Approved Rent</option>
          <option value="sold">Sold</option>
          <option value="rented">Rented</option>
        </select>
      </div>
    </div>

    <!-- Table Container -->
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
          <tr v-for="prop in filteredProperties" :key="prop.id" @click="$emit('view-property', prop)" class="hover:bg-primary-50/50 transition-colors cursor-pointer group">
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
               prop.status === 'sold' ? 'bg-purple-100 text-purple-700' :
               prop.status === 'rented' ? 'bg-indigo-100 text-indigo-700' :
               prop.status === 'pending_sold' || prop.status === 'pending_rent' ? 'bg-amber-100 text-amber-700' :
               prop.status === 'approved_sold' || prop.status === 'approved_rent' ? 'bg-emerald-100 text-emerald-700 animate-pulse' :
               'bg-green-100 text-green-700'
             ]">
                {{ prop.status === 'approved_sold' || prop.status === 'approved_rent' ? 'Approved' : prop.status }}
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
              <template v-else-if="prop.status === 'approved_sold' || prop.status === 'approved_rent'">
                <div class="flex items-center justify-end gap-2">
                  <button 
                    @click="$emit('finalize-transaction', prop.id, 'complete')"
                    class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-[10px] font-bold uppercase transition-all shadow-sm"
                  >
                    Complete
                  </button>
                  <button 
                    @click="$emit('finalize-transaction', prop.id, 'cancel')"
                    class="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg text-[10px] font-bold uppercase transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </template>
              <span v-else class="text-[10px] font-bold text-primary-300 uppercase italic">Goal Reached</span>
          </td>
        </tr>
        <tr v-if="!filteredProperties.length">
           <td colspan="4" class="py-12 text-center text-primary-500">
              <LucideHome class="w-12 h-12 text-primary-200 mx-auto mb-3" />
              <p>No matching listings found.</p>
           </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { LucideHome, LucideSearch, LucideFilter } from 'lucide-vue-next'

const props = defineProps<{
  myProperties: any[]
}>()

defineEmits(['view-property', 'open-sale-modal', 'open-rent-modal', 'finalize-transaction'])

const searchQuery = ref('')
const statusFilter = ref('all')

const filteredProperties = computed(() => {
  return props.myProperties.filter(prop => {
    const titleMatch = prop.title.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    let statusMatch = true
    if (statusFilter.value !== 'all') {
      statusMatch = prop.status === statusFilter.value
    }
    
    return titleMatch && statusMatch
  })
})
</script>
