<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-primary-950">Analytics & KPIs</h2>
    </div>
    <div v-if="statsLoading" class="grid md:grid-cols-2 gap-6 animate-pulse">
        <div class="h-64 bg-white rounded-[2rem]"></div>
        <div class="h-64 bg-white rounded-[2rem]"></div>
    </div>
    <div v-else class="grid lg:grid-cols-2 gap-8">
        <!-- Doughnut: Visit Statuses -->
        <div class="card-premium h-[400px] flex flex-col">
          <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Visit Success Rate</h3>
          <div class="flex-1 relative">
              <ChartsDoughnutChart v-if="visitChartData" :chart-data="visitChartData" />
          </div>
        </div>
        
        <!-- Line: Monthly Visits -->
        <div class="card-premium h-[400px] flex flex-col">
          <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Monthly Visits Setup</h3>
          <div class="flex-1 relative">
              <ChartsLineChart v-if="monthlyVisitsChartData" :chart-data="monthlyVisitsChartData" />
          </div>
        </div>
        
        <!-- Doughnut: Portfolio Status -->
        <div class="card-premium h-[400px] flex flex-col lg:col-span-2">
          <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">My Listings Breakdown</h3>
          <div class="flex-1 relative flex items-center justify-center pt-8">
              <ChartsDoughnutChart v-if="propertyStatusChartData" :chart-data="propertyStatusChartData" :chart-options="{ cutout: '60%' }" />
          </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ChartsDoughnutChart from '~/components/Charts/DoughnutChart.vue'
import ChartsLineChart from '~/components/Charts/LineChart.vue'

defineProps<{
  statsLoading: boolean
  visitChartData: any
  monthlyVisitsChartData: any
  propertyStatusChartData: any
}>()
</script>
