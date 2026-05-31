import { ref, computed } from 'vue'
import { useAgentService } from '~/services/agentService'

export const useAgentAnalytics = () => {
  const agentService = useAgentService()

  // State
  const statistics = ref<any>(null)
  const loading = ref(false)

  // Chart Computeds
  const visitChartData = computed(() => {
    if (!statistics.value || !statistics.value.visit_statuses) return null
    const data = statistics.value.visit_statuses
    return {
      labels: Object.keys(data).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
      datasets: [{
        data: Object.values(data),
        backgroundColor: ['#3b82f6', '#22c55e', '#ef4444', '#f59e0b'],
        borderWidth: 0,
        hoverOffset: 10
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
        backgroundColor: ['#6366f1', '#a855f7', '#ec4899', '#14b8a6', '#f59e0b'],
        borderWidth: 0,
        hoverOffset: 10
      }]
    }
  })

  const monthlyVisitsChartData = computed(() => {
    if (!statistics.value || !statistics.value.monthly_visits) return null
    const data = statistics.value.monthly_visits
    return {
      labels: Object.keys(data),
      datasets: [{
        label: 'Visits Conducted',
        data: Object.values(data),
        borderColor: '#3b82f6',
        backgroundColor: '#ebf5ff',
        borderWidth: 3,
        fill: true
      }]
    }
  })

  // Methods
  const fetchAnalytics = async () => {
    loading.value = true
    try {
      const res = await agentService.getStatistics()
      statistics.value = res.data || null
    } catch (e) {
      console.error("Failed to fetch analytics statistics:", e)
    } finally {
      loading.value = false
    }
  }

  return {
    statistics,
    loading,
    visitChartData,
    propertyStatusChartData,
    monthlyVisitsChartData,
    fetchAnalytics
  }
}
