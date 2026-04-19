import re

file_path = r'c:\real-estate-automation\frontend\app\pages\admin\index.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Tab Button
tab_pattern = r'(<button \n\s*@click="activeTab = \'reports\'".*?</button>)'
tab_replacement = r'''\1
        <button 
          @click="activeTab = 'analytics'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap flex items-center gap-2', activeTab === 'analytics' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucidePieChart class="w-4 h-4 inline-block" /> Platform Analytics
        </button>'''
content = re.sub(tab_pattern, tab_replacement, content, flags=re.DOTALL)


# Add Tab Content
content_pattern = r'(<!-- Tab Content: Reports -->)'
content_replacement = r'''<!-- Tab Content: Analytics -->
      <div v-show="activeTab === 'analytics'">
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

      \1'''
content = re.sub(content_pattern, content_replacement, content)


# Add Imports
import_pattern = r'(LucideFileText, LucideDownload)'
import_replacement = r'\1, LucidePieChart'
content = re.sub(import_pattern, import_replacement, content)


# Add State and Computed
script_pattern = r'(const reports = ref\(\[\]\))\n'
script_replacement = r'''\1
const statistics = ref(null)
const statsLoading = ref(false)

const userRolesChartData = computed(() => {
  if (!statistics.value || !statistics.value.user_roles) return null
  const data = statistics.value.user_roles
  return {
    labels: Object.keys(data).map(k => k.replace('_', ' ').toUpperCase()),
    datasets: [{
      data: Object.values(data),
      backgroundColor: ['#6366f1', '#a855f7', '#ec4899', '#14b8a6', '#f59e0b'],
      borderWidth: 0,
      hoverOffset: 10
    }]
  }
})

const topAgentsChartData = computed(() => {
  if (!statistics.value || !statistics.value.top_agents) return null
  const data = statistics.value.top_agents
  return {
    labels: data.map(d => d.agent),
    datasets: [{
      label: 'Sold Properties',
      data: data.map(d => d.sold),
      backgroundColor: '#f43f5e',
      borderRadius: 6
    }]
  }
})

const propertyStatusChartData = computed(() => {
  if (!statistics.value || !statistics.value.property_statuses) return null
  const data = statistics.value.property_statuses
  return {
    labels: Object.keys(data).map(k => k.replace('_', ' ').toUpperCase()),
    datasets: [{
      data: Object.values(data),
      backgroundColor: ['#3b82f6', '#22c55e', '#ef4444', '#f59e0b', '#8b5cf6'],
      borderWidth: 0,
      hoverOffset: 10
    }]
  }
})

'''
content = re.sub(script_pattern, script_replacement, content)


# Add fetch call
fetch_pattern = r'(const \[usersRes, headAgentsRes, propertiesRes, reportsRes\] = await Promise.all\(\[.*?\n\s*\]\))'
fetch_replacement = r'''const [usersRes, headAgentsRes, propertiesRes, reportsRes, statsRes] = await Promise.all([
      api.get('/admin/users'),
      api.get('/admin/head_agents'),
      api.get('/properties'),
      api.get('/admin/reports'),
      api.get('/statistics/admin')
    ])'''
content = re.sub(fetch_pattern, fetch_replacement, content, flags=re.DOTALL)

assign_pattern = r'(reports\.value = reportsRes\.data)'
assign_replacement = r'\1\n    statistics.value = statsRes.data'
content = re.sub(assign_pattern, assign_replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated admin/index.vue")
