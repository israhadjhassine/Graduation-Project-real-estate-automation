import { ref, computed } from 'vue'
import { useAdminService } from '~/services/adminService'

export const useAdminAnalytics = () => {
  const adminService = useAdminService()

  const statistics = ref<any>(null)
  const visits = ref<any[]>([])
  const loading = ref(false)

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
      labels: data.map((d: any) => d.agent),
      datasets: [{
        label: 'Sold Properties',
        data: data.map((d: any) => d.sold),
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

  const fetchAnalytics = async () => {
    loading.value = true
    try {
      const [statsRes, visitsRes] = await Promise.all([
        adminService.getStatistics(),
        adminService.getVisits()
      ])
      statistics.value = statsRes.data || null
      visits.value = visitsRes.data || []
    } catch (e) {
      console.error("Failed to load analytics data", e)
    } finally {
      loading.value = false
    }
  }

  return {
    statistics,
    visits,
    loading,
    userRolesChartData,
    topAgentsChartData,
    propertyStatusChartData,
    fetchAnalytics
  }
}
