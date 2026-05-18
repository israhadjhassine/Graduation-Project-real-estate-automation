<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-primary-950">Sub-Agent Management</h2>
    </div>

    <!-- Filters Bar -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="relative">
        <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Search sub-agents by name or phone..."
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
          <option value="active">Active Accounts</option>
          <option value="disabled">Disabled Accounts</option>
        </select>
      </div>
    </div>

    <!-- Table Container -->
    <div class="card-premium p-0 overflow-hidden">
      <table class="w-full text-left">
        <thead>
          <tr class="bg-primary-50">
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Sub-Agent Name</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Email Address</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Phone Number</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Google Calendar ID</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Assigned Properties</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-primary-100">
          <tr v-for="agent in filteredStaff" :key="agent.id" class="hover:bg-primary-50/50">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-950 font-bold text-xs">
                  {{ agent.full_name.charAt(0) }}
                </div>
                <span class="text-sm font-bold text-primary-950">{{ agent.full_name }}</span>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-primary-600">{{ agent.email }}</td>
            <td class="px-6 py-4 text-sm text-primary-600">{{ agent.phone_number || 'N/A' }}</td>
            <td class="px-6 py-4 text-sm text-primary-600">
              <button 
                v-if="agent.google_calendar_id" 
                @click="copyToClipboard(agent.google_calendar_id, agent.id)" 
                class="flex items-center gap-2 px-3 py-1.5 bg-primary-50 hover:bg-accent-50 border border-primary-100 hover:border-accent-200 rounded-xl text-xs font-semibold text-primary-700 hover:text-accent-700 transition-all shadow-sm active:scale-95 duration-150"
                title="Click to copy Google Calendar ID"
              >
                <span class="font-medium text-[11px]">{{ copiedId === agent.id ? 'Copied!' : 'Click to copy' }}</span>
                <component :is="copiedId === agent.id ? LucideCheck : LucideCopy" class="w-3.5 h-3.5" />
              </button>
              <span v-else class="px-2 py-1 bg-amber-50 text-amber-700 text-[10px] font-bold rounded-lg border border-amber-200">
                ⚠️ Missing Calendar
              </span>
            </td>
            <td class="px-6 py-4">
              <span class="px-3 py-1 bg-primary-100 text-primary-700 text-[10px] font-bold rounded-lg uppercase">
                {{ properties.filter(p => p.agent_id === agent.id).length }} Listings
              </span>
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'px-2 py-1 text-[10px] font-bold rounded-lg uppercase',
                agent.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              ]">
                {{ agent.is_active ? 'Active' : 'Disabled' }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <button 
                @click="$emit('toggle-status', agent.id)"
                :class="[
                  'text-[10px] font-bold uppercase transition-colors',
                  agent.is_active ? 'text-red-500 hover:text-red-700' : 'text-green-500 hover:text-green-700'
                ]"
              >
                {{ agent.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
          <tr v-if="!filteredStaff.length">
            <td colspan="7" class="px-6 py-12 text-center text-primary-500">
              <LucideUsers class="w-12 h-12 mx-auto text-primary-200 mb-3" />
              <p>No matching Sub-Agents found.</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { LucideUsers, LucideCopy, LucideCheck, LucideSearch, LucideFilter } from 'lucide-vue-next'

const props = defineProps<{
  staff: any[]
  properties: any[]
}>()

defineEmits(['toggle-status'])

const searchQuery = ref('')
const statusFilter = ref('all')

const copiedId = ref<number | null>(null)

const filteredStaff = computed(() => {
  return props.staff.filter(agent => {
    // Search query match (name or phone)
    const nameMatch = agent.full_name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const phoneMatch = agent.phone_number ? agent.phone_number.includes(searchQuery.value) : false
    const matchesSearch = nameMatch || phoneMatch

    // Status match (active / disabled)
    let matchesStatus = true
    if (statusFilter.value === 'active') {
      matchesStatus = agent.is_active === true
    } else if (statusFilter.value === 'disabled') {
      matchesStatus = agent.is_active === false
    }

    return matchesSearch && matchesStatus
  })
})

const copyToClipboard = (text: string, id: number) => {
  navigator.clipboard.writeText(text).then(() => {
    copiedId.value = id
    setTimeout(() => {
      if (copiedId.value === id) {
        copiedId.value = null
      }
    }, 2000)
  }).catch(err => {
    console.error('Failed to copy text: ', err)
  })
}
</script>
