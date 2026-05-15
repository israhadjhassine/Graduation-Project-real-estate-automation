<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-primary-950">Sub-Agent Management</h2>
    </div>

    <div class="card-premium p-0 overflow-hidden">
      <table class="w-full text-left">
        <thead>
          <tr class="bg-primary-50">
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Sub-Agent Name</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Email Address</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Phone Number</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Assigned Properties</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-primary-100">
          <tr v-for="agent in staff" :key="agent.id" class="hover:bg-primary-50/50">
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
          <tr v-if="!staff.length">
            <td colspan="4" class="px-6 py-12 text-center text-primary-500">
              <LucideUsers class="w-12 h-12 mx-auto text-primary-200 mb-3" />
              <p>You have not recruited any Sub-Agents yet.</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LucideUsers } from 'lucide-vue-next'

defineProps<{
  staff: any[]
  properties: any[]
}>()

defineEmits(['toggle-status'])
</script>
