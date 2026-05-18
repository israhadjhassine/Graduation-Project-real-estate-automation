<template>
  <div class="space-y-4">
    <!-- Filters Bar -->
    <div class="flex justify-end">
      <div class="relative w-full md:w-64">
        <LucideFilter class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <select 
          v-model="statusFilter"
          class="w-full pl-11 pr-4 py-2.5 bg-white border border-primary-100 rounded-2xl text-xs focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm appearance-none cursor-pointer"
        >
          <option value="all">All Statuses</option>
          <option value="available">Available</option>
          <option value="pending_sold">Pending Sale</option>
          <option value="pending_rent">Pending Rent</option>
          <option value="sold">Sold</option>
          <option value="rented">Currently Rented</option>
        </select>
      </div>
    </div>

    <!-- Table Container -->
    <div class="card-premium p-0 overflow-hidden">
      <table class="w-full text-left">
        <thead>
          <tr class="bg-primary-50">
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Status</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Head Agent</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Assigned Agent</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Price</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-primary-50">
          <tr v-for="prop in filteredProperties" :key="prop.id" @click="$emit('view-property', prop)" class="hover:bg-primary-50/50 transition-colors cursor-pointer group">
          <td class="px-6 py-4">
            <div class="flex items-center gap-4">
               <div class="w-12 h-12 rounded-xl overflow-hidden bg-primary-100 flex-shrink-0">
                 <img v-if="prop.images?.length" :src="getPublicUrl(prop.images[0].image_url)" class="w-full h-full object-cover" />
                 <LucideImage v-else class="w-12 h-12 p-3 text-primary-200" />
              </div>
              <div>
              <div>
                <p class="font-bold text-primary-950 text-sm max-w-xs truncate group-hover:text-accent-600 transition-colors">{{ prop.title }}</p>
                <p class="text-[10px] text-primary-400">{{ prop.city }}, {{ prop.country }}</p>
              </div>
              </div>
            </div>
          </td>
          <td class="px-6 py-4">
            <span v-if="prop.status === 'sold'" class="px-2 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded-lg uppercase">Sold</span>
            <span v-else-if="prop.status === 'pending_sold'" class="px-2 py-1 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-lg uppercase">Pending Sale</span>
            <span v-else-if="prop.status === 'rented'" class="px-2 py-1 bg-purple-100 text-purple-700 text-[10px] font-bold rounded-lg uppercase block mb-1 w-max">Currently Rented</span>
            <span v-else-if="prop.status === 'pending_rent'" class="px-2 py-1 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-lg uppercase block mb-1 w-max">Pending Rent</span>
            <span v-else class="px-2 py-1 bg-blue-100 text-blue-700 text-[10px] font-bold rounded-lg uppercase">Available</span>
            
            <div v-if="prop.status === 'rented' && prop.rent_end_date" class="text-[9px] text-primary-500 font-medium mt-1">
              Available again from: <br/><span class="font-bold text-primary-700">{{ new Date(prop.rent_end_date).toLocaleDateString() }}</span>
            </div>
          </td>
          <td class="px-6 py-4">
            <div class="flex flex-col">
              <span class="text-sm font-medium text-primary-950 truncate max-w-[120px]" :title="prop.owner?.full_name">
                {{ prop.owner?.full_name || 'System' }}
              </span>
              <span v-if="prop.owner_id === currentUserId" class="text-[8px] text-accent-600 font-bold uppercase tracking-tighter">Your Listing</span>
            </div>
          </td>
          <td class="px-6 py-4">
            <select 
              v-if="isAdmin || prop.owner_id === currentUserId"
              :value="prop.agent_id" 
              @change.stop="$emit('assign-agent', prop.id, ($event.target as HTMLSelectElement).value)" 
              @click.stop
              class="bg-primary-50 text-primary-950 font-medium text-xs rounded-lg px-2 py-1.5 border border-primary-200 outline-none focus:border-accent-400 w-full"
            >
              <option :value="null">Unassigned</option>
              <option v-for="agent in staff" :key="agent.id" :value="agent.id">{{ agent.full_name }}</option>
            </select>
            <span v-else class="text-xs text-primary-400 font-medium italic">
              {{ prop.agent?.full_name || 'Unassigned' }}
            </span>
          </td>
          <td class="px-6 py-4 font-bold text-primary-950 text-sm">
            {{ formatPrice(prop.price) }} <span class="text-[10px]">{{ prop.currency }}</span>
          </td>
          <td class="px-6 py-4">
              <div class="flex gap-1" @click.stop>
                <template v-if="isAdmin || prop.owner_id === currentUserId">
                  <button @click="$emit('edit-property', prop)" class="p-2 hover:bg-primary-100 rounded-lg text-primary-400 transition-colors" title="Edit Property">
                    <LucideEdit class="w-4 h-4" />
                  </button>
                  <button @click="$emit('delete-property', prop.id)" class="p-2 hover:bg-red-50 rounded-lg text-red-400 transition-colors" title="Delete Property">
                    <LucideTrash2 class="w-4 h-4" />
                  </button>
                </template>
                <button v-else @click="$emit('view-property', prop)" class="p-2 hover:bg-primary-100 rounded-lg text-primary-400 transition-colors" title="View Details">
                  <LucideEye class="w-4 h-4" />
                </button>
              </div>
          </td>
        </tr>
        <tr v-if="!filteredProperties.length">
          <td colspan="6" class="px-6 py-12 text-center text-primary-500">
            <LucideHome class="w-12 h-12 mx-auto text-primary-200 mb-3" />
            <p>No matching properties found.</p>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  LucideImage, LucideEdit, LucideTrash2, 
  LucideEye, LucideHome, LucideFilter
} from 'lucide-vue-next'
import { useAssetUrl } from '~/composables/useAssetUrl'

const props = defineProps<{
  properties: any[]
  staff: any[]
  currentUserId: number | undefined
  isAdmin: boolean
}>()

defineEmits([
  'view-property', 
  'edit-property', 
  'delete-property', 
  'assign-agent'
])

const { getPublicUrl } = useAssetUrl()

const statusFilter = ref('all')

const filteredProperties = computed(() => {
  return props.properties.filter(prop => {
    if (statusFilter.value === 'all') return true
    return prop.status === statusFilter.value
  })
})

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}
</script>
