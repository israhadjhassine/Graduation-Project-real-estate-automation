<template>
  <div class="grid md:grid-cols-3 gap-6 mb-10">
    <div class="card-premium border-l-4 border-l-primary-900 !rounded-lg">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
          <LucideHome class="w-6 h-6 text-primary-900" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">My Listings</p>
          <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ myProperties.length }}</p>
        </div>
      </div>
    </div>

    <div class="card-premium border-l-4 border-l-accent-600 !rounded-lg">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-accent-50 rounded-lg flex items-center justify-center">
          <LucideCalendar class="w-6 h-6 text-accent-600" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Upcoming Visits</p>
          <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ upcomingVisits.length }}</p>
        </div>
      </div>
    </div>

    <div class="card-premium border-l-4 border-l-green-600 !rounded-lg">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
          <LucideCheckCircle2 class="w-6 h-6 text-green-600" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Completed Visits</p>
          <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ finishedVisits.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LucideHome, LucideCalendar, LucideCheckCircle2 } from 'lucide-vue-next'

defineProps<{
  myProperties: any[]
  upcomingVisits: any[]
  finishedVisits: any[]
}>()
</script>
