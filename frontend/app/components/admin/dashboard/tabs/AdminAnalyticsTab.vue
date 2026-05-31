<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-primary-950">Platform Analytics & KPIs</h2>
    </div>
    
    <div v-if="statsLoading" class="grid md:grid-cols-2 gap-6 animate-pulse">
       <div class="h-64 bg-white rounded-[2rem]"></div>
       <div class="h-64 bg-white rounded-[2rem]"></div>
    </div>
    
    <!-- Key Metrics Cards -->
    <div v-else-if="statistics" class="grid md:grid-cols-4 gap-6 mb-8">
        <div class="bg-gradient-to-br from-green-500 to-green-700 rounded-3xl p-6 text-white shadow-lg shadow-green-900/20">
           <p class="text-xs font-bold uppercase tracking-widest opacity-80 mb-1">Total Sales Revenue</p>
           <p class="text-3xl font-bold">{{ formatPrice(statistics.revenue.sales) }} <span class="text-xs font-normal">TND</span></p>
        </div>
        <div class="bg-gradient-to-br from-purple-500 to-purple-700 rounded-3xl p-6 text-white shadow-lg shadow-purple-900/20">
           <p class="text-xs font-bold uppercase tracking-widest opacity-80 mb-1">Total Rental Revenue</p>
           <p class="text-3xl font-bold">{{ formatPrice(statistics.revenue.rentals) }} <span class="text-xs font-normal">TND</span></p>
        </div>
        <div class="bg-white rounded-3xl p-6 border border-primary-100 shadow-sm flex flex-col justify-center">
           <p class="text-xs font-bold text-primary-400 uppercase tracking-widest mb-1">Total Sold</p>
           <p class="text-3xl font-bold text-primary-950">{{ statistics.property_statuses.sold || 0 }}</p>
        </div>
        <div class="bg-white rounded-3xl p-6 border border-primary-100 shadow-sm flex flex-col justify-center">
           <p class="text-xs font-bold text-primary-400 uppercase tracking-widest mb-1">Available</p>
           <p class="text-3xl font-bold text-primary-950">{{ statistics.property_statuses.available || 0 }}</p>
        </div>
    </div>

    <div v-if="!statsLoading && statistics" class="grid lg:grid-cols-2 gap-8">
       <!-- Doughnut: User Roles -->
       <div class="card-premium h-[400px] flex flex-col">
          <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Platform Users by Role</h3>
          <div class="flex-1 relative pb-4">
             <ChartsDoughnutChart v-if="userRolesChartData" :chart-data="userRolesChartData" />
          </div>
       </div>
       
       <!-- Bar: Top Agents -->
       <div class="card-premium h-[400px] flex flex-col">
          <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Top 5 Performing Agents</h3>
          <div class="flex-1 relative pb-4">
             <ChartsBarChart v-if="topAgentsChartData" :chart-data="topAgentsChartData" />
          </div>
       </div>
       
       <!-- Doughnut: Platform Property Statuses -->
       <div class="card-premium h-[400px] flex flex-col lg:col-span-2">
          <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-[60px]">Total Properties Breakdown</h3>
          <div class="flex-1 relative">
             <ChartsDoughnutChart v-if="propertyStatusChartData" :chart-data="propertyStatusChartData" :chart-options="{ cutout: '65%' }" />
          </div>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  statsLoading: boolean
  statistics: any
  userRolesChartData: any
  topAgentsChartData: any
  propertyStatusChartData: any
}>()

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('fr-TN').format(price || 0)
}
</script>
