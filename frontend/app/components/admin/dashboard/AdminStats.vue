<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-10">
    <div class="card-premium border-l-4 border-l-primary-900 !rounded-lg">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
          <LucideUsers class="w-6 h-6 text-primary-900" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Total Users</p>
          <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ usersLength }}</p>
        </div>
      </div>
    </div>

    <div class="card-premium border-l-4 border-l-purple-600 !rounded-lg">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
          <LucideUsers class="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Head Agents</p>
          <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ headAgentsLength }}</p>
        </div>
      </div>
    </div>

    <div class="card-premium border-l-4 border-l-green-600 !rounded-lg">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
          <LucideHome class="w-6 h-6 text-green-600" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Total Listings</p>
          <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ propertiesLength }}</p>
        </div>
      </div>
    </div>

    <div class="card-premium border-l-4 border-l-blue-600 !rounded-lg">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
          <LucideCalendar class="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Scheduled Visits</p>
          <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ visitsLength }}</p>
        </div>
      </div>
    </div>

    <div class="card-premium border-l-4 border-l-orange-600 !rounded-lg">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
          <LucideTrendingUp class="w-6 h-6 text-orange-600" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Closed Deals</p>
          <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ closedDealsCount }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  LucideUsers, LucideHome, LucideCalendar, LucideTrendingUp 
} from 'lucide-vue-next'

defineProps<{
  usersLength: number
  headAgentsLength: number
  propertiesLength: number
  visitsLength: number
  closedDealsCount: number
}>()
</script>
