import { ref, computed } from 'vue'
import { useAgencyService } from '~/services/agencyService'

export const useAgencyAnalytics = () => {
  const agencyService = useAgencyService()

  // State
  const statistics = ref<any>(null)
  const visits = ref<any[]>([])
  const clients = ref<any[]>([])
  const loading = ref(false)

  // Computed properties
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
    const sorted = [...data].sort((a, b) => b.deals - a.deals)
    
    return {
      labels: sorted.map((d: any) => d.agent),
      datasets: [{
        label: 'Closed Deals',
        data: sorted.map((d: any) => d.deals),
        backgroundColor: '#3b82f6',
        borderRadius: 6
      }]
    }
  })

  // Methods
  const fetchAnalytics = async () => {
    loading.value = true
    try {
      const [clientsRes, statsRes, visitsRes] = await Promise.all([
        agencyService.getClients(),
        agencyService.getStatistics(),
        agencyService.getVisits()
      ])
      clients.value = clientsRes.data || []
      statistics.value = statsRes.data || null
      visits.value = visitsRes.data || []
    } catch (e) {
      console.error("Failed to fetch analytics:", e)
    } finally {
      loading.value = false
    }
  }

  return {
    statistics,
    visits,
    clients,
    loading,
    propertyStatusChartData,
    agentPerformanceChartData,
    fetchAnalytics
  }
}
