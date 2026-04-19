import re

file_path = r'c:\real-estate-automation\frontend\app\pages\agency\index.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Tab Button
tab_pattern = r'(<button \n\s*@click="activeTab = \'reports\'".*?</button>)'
tab_replacement = r'''\1
        <button 
          @click="activeTab = 'analytics'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap flex items-center gap-2', activeTab === 'analytics' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucidePieChart class="w-4 h-4 inline-block" /> Team Performance
        </button>'''
content = re.sub(tab_pattern, tab_replacement, content, flags=re.DOTALL)


# Add Tab Content
content_pattern = r'(<!-- Tab Content: Reports -->)'
content_replacement = r'''<!-- Tab Content: Analytics -->
      <div v-show="activeTab === 'analytics'">
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

      \1'''
content = re.sub(content_pattern, content_replacement, content)


# Add Imports
import_pattern = r'(LucideFileText, LucideDownload)'
import_replacement = r'\1, LucidePieChart'
content = re.sub(import_pattern, import_replacement, content)


# Add State and Computed
script_pattern = r'(const pendingSales = computed.*?)\n'
script_replacement = r'''\1

// Statistics State
const statistics = ref(null)

const propertyStatusChartData = computed(() => {
  if (!statistics.value || !statistics.value.property_statuses) return null
  const data = statistics.value.property_statuses
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

const agentPerformanceChartData = computed(() => {
  if (!statistics.value || !statistics.value.team_performance) return null
  const data = statistics.value.team_performance
  
  // Sort by deals desc
  const sorted = [...data].sort((a,b) => b.deals - a.deals)
  
  return {
    labels: sorted.map(d => d.agent),
    datasets: [{
      label: 'Closed Deals',
      data: sorted.map(d => d.deals),
      backgroundColor: '#3b82f6',
      borderRadius: 6
    }]
  }
})
'''
content = re.sub(script_pattern, script_replacement, content, count=1)


# Add fetch call
fetch_pattern = r'(const \[propsRes, staffRes, inqRes, clientsRes\] = await Promise.all\(\[.*?\n\s*\]\))'
fetch_replacement = r'''const [propsRes, staffRes, inqRes, clientsRes, statsRes] = await Promise.all([
      api.get('/agency/properties'),
      api.get('/agency/staff'),
      api.get('/agent/inquiries'),
      api.get('/agency/clients'),
      api.get('/statistics/agency')
    ])'''
content = re.sub(fetch_pattern, fetch_replacement, content, flags=re.DOTALL)

assign_pattern = r'(clients\.value = clientsRes\.data)'
assign_replacement = r'\1\n    statistics.value = statsRes.data'
content = re.sub(assign_pattern, assign_replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated agency/index.vue")
