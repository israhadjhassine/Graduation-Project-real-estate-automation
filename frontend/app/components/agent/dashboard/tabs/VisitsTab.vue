<template>
  <div>
    <!-- Filters Bar -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <!-- Property Name Search -->
      <div class="relative">
        <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <input 
          :value="searchQuery"
          @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
          type="text" 
          placeholder="Search property name..."
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
        />
      </div>

      <!-- Location Filter -->
      <div class="relative">
        <LucideMapPin class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <input 
          :value="locationQuery"
          @input="$emit('update:locationQuery', ($event.target as HTMLInputElement).value)"
          type="text" 
          placeholder="Filter by city/location..."
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
        />
      </div>

      <!-- Status Select -->
      <div class="relative">
        <LucideFilter class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <select 
          :value="statusFilter"
          @change="$emit('update:statusFilter', ($event.target as HTMLSelectElement).value)"
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm appearance-none cursor-pointer"
        >
          <option value="all">All Statuses</option>
          <option value="scheduled">Scheduled</option>
          <option value="finished">Finished</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      <!-- Date Filter -->
      <div class="relative">
        <LucideCalendar class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <select 
          :value="dateFilter"
          @change="$emit('update:dateFilter', ($event.target as HTMLSelectElement).value)"
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm appearance-none cursor-pointer"
        >
          <option value="all">All Time</option>
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
        </select>
      </div>
    </div>

    <div class="card-premium p-0 overflow-hidden">
      <table class="w-full text-left">
        <thead>
          <tr class="bg-primary-50">
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Date & Time</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Client</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Listing</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-primary-100">
          <tr v-for="visit in filteredVisits" :key="visit.id" class="hover:bg-primary-50/50 transition-colors">
            <td class="px-6 py-4 text-sm font-bold text-primary-950">
              <div class="flex items-center gap-3">
                  <LucideCalendar class="w-4 h-4 text-primary-400" />
                  {{ new Date(visit.visit_date).toLocaleString() }}
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-primary-600">
              <p class="font-bold text-primary-950">{{ visit.client?.full_name || 'Visitor' }}</p>
              <p class="text-[10px] text-primary-400">{{ visit.client?.email || visit.telegram_chat_id || 'No contact' }}</p>
            </td>
            <td class="px-6 py-4 text-sm text-primary-600">
              <p class="font-bold text-primary-950">{{ visit.property?.title || 'Unknown Property' }}</p>
              <p class="text-[10px] text-primary-400">{{ visit.property?.city || '' }}</p>
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'px-3 py-1 text-[10px] font-bold rounded-lg uppercase',
                visit.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                visit.status === 'finished' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              ]">
                  {{ visit.status }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="$emit('view-details', visit)" class="text-xs font-bold text-primary-600 hover:text-primary-950 bg-primary-50 hover:bg-primary-100 p-2 rounded-lg transition-colors">
                    <LucideEye :size="16" />
                  </button>
                  <div v-if="visit.status === 'scheduled'" class="flex items-center gap-2">
                      <button @click="$emit('update-status', visit.id, 'finished')" class="text-xs font-bold text-green-600 hover:text-green-700 bg-green-50 hover:bg-green-100 px-3 py-1.5 rounded-lg transition-colors">
                        Complete
                      </button>
                      <button @click="$emit('update-status', visit.id, 'cancelled')" class="text-xs font-bold text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-lg transition-colors">
                        Cancel
                      </button>
                  </div>
                  <span v-else class="text-xs text-primary-400 font-medium">No further actions</span>
                </div>
            </td>
          </tr>
          <tr v-if="!filteredVisits.length">
              <td colspan="5" class="py-12 text-center text-primary-500">
                <LucideCalendarOff class="w-12 h-12 text-primary-200 mx-auto mb-3" />
                <p>{{ visits.length > 0 ? 'No visits match your filters.' : 'No property viewings scheduled.' }}</p>
              </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LucideSearch, LucideMapPin, LucideFilter, LucideCalendar, LucideEye, LucideCalendarOff } from 'lucide-vue-next'

defineProps<{
  searchQuery: string
  locationQuery: string
  statusFilter: string
  dateFilter: string
  filteredVisits: any[]
  visits: any[]
}>()

defineEmits([
  'update:searchQuery',
  'update:locationQuery',
  'update:statusFilter',
  'update:dateFilter',
  'view-details',
  'update-status'
])
</script>
