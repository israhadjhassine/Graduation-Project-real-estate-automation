<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-primary-950">Team Analytics & KPIs</h2>
    </div>
    <div v-if="loading" class="grid md:grid-cols-2 gap-6 animate-pulse">
       <div class="h-64 bg-white rounded-[2rem]"></div>
       <div class="h-64 bg-white rounded-[2rem]"></div>
    </div>
    <div v-else class="grid lg:grid-cols-2 gap-8">
       <!-- Doughnut: Property Statuses -->
       <div class="card-premium h-[400px] flex flex-col">
          <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Agency Portfolio Status</h3>
          <div class="flex-1 relative">
             <ChartsDoughnutChart v-if="propertyStatusChartData" :chart-data="propertyStatusChartData" />
          </div>
       </div>
       
       <!-- Bar: Agent Performance -->
       <div class="card-premium h-[400px] flex flex-col">
          <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Sub-Agent Closed Deals</h3>
          <div class="flex-1 relative">
             <ChartsBarChart v-if="agentPerformanceChartData" :chart-data="agentPerformanceChartData" />
          </div>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  loading: boolean
  propertyStatusChartData: any
  agentPerformanceChartData: any
}>()
</script>
