import { ref, computed } from 'vue'
import { useAgentService } from '~/services/agentService'
import { usePropertyService } from '~/services/propertyService'
import { useAgencyService } from '~/services/agencyService'

export const useAgentDashboard = () => {
  const agentService = useAgentService()
  const propertyService = usePropertyService()
  const agencyService = useAgencyService()

  // State
  const visits = ref<any[]>([])
  const myProperties = ref<any[]>([])
  const clients = ref<any[]>([])
  const inquiries = ref<any[]>([])
  const statistics = ref<any>(null)
  
  // Filters State
  const searchQuery = ref('')
  const locationQuery = ref('')
  const statusFilter = ref('all')
  const dateFilter = ref('all')
  
  const loading = ref(false)
  const statsLoading = ref(false)

  // Computed
  const upcomingVisits = computed(() => visits.value.filter(v => v.status === 'scheduled'))
  const finishedVisits = computed(() => visits.value.filter(v => v.status === 'finished'))

  const filteredVisits = computed(() => {
    return visits.value.filter(v => {
      // Status Filter
      const matchesStatus = statusFilter.value === 'all' || v.status === statusFilter.value
      
      // Property Name Filter
      const matchesProperty = !searchQuery.value || 
        v.property?.title?.toLowerCase().includes(searchQuery.value.toLowerCase())
        
      // Location Filter
      const matchesLocation = !locationQuery.value || 
        v.property?.city?.toLowerCase().includes(locationQuery.value.toLowerCase())
        
      // Date Filter
      let matchesDate = true
      if (dateFilter.value !== 'all') {
        const vDate = new Date(v.visit_date)
        const now = new Date()
        
        if (dateFilter.value === 'today') {
          matchesDate = vDate.toDateString() === now.toDateString()
        } else if (dateFilter.value === 'week') {
          // Start of current week (Monday)
          const currentNow = new Date()
          const day = currentNow.getDay()
          const diff = currentNow.getDate() - day + (day === 0 ? -6 : 1)
          const monday = new Date(currentNow.setDate(diff))
          monday.setHours(0,0,0,0)
          matchesDate = vDate >= monday
        } else if (dateFilter.value === 'month') {
          matchesDate = vDate.getMonth() === now.getMonth() && vDate.getFullYear() === now.getFullYear()
        }
      }
      
      return matchesStatus && matchesProperty && matchesLocation && matchesDate
    })
  })

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
  const fetchData = async () => {
    loading.value = true
    try {
      const [visitsRes, propsRes, clientsRes, inquiriesRes] = await Promise.all([
        agentService.getVisits(),
        agentService.getProperties(),
        agencyService.getClients(),
        agentService.getInquiries()
      ])
      visits.value = visitsRes.data
      myProperties.value = propsRes.data
      clients.value = clientsRes.data
      inquiries.value = inquiriesRes.data || []
      
      // Fetch stats
      statsLoading.value = true
      try {
        const statsRes = await agentService.getStatistics()
        statistics.value = statsRes.data
      } catch (err) {
        console.error("Failed to load statistics", err)
      } finally {
        statsLoading.value = false
      }
    } catch (e) {
      console.error("Agent dashboard fetch error:", e)
    } finally {
      loading.value = false
    }
  }

  const submitSaleRequest = async (propertyId: number | string, clientId: number | string) => {
    const prop = myProperties.value.find(p => p.id === propertyId)
    await propertyService.requestTransaction(propertyId, { 
      type: 'Sale',
      price: prop.price,
      client_id: clientId 
    })
  }

  const submitRentRequest = async (propertyId: number | string, clientId: number | string, startDate: string, endDate: string) => {
    const prop = myProperties.value.find(p => p.id === propertyId)
    await propertyService.requestTransaction(propertyId, { 
      type: 'Rent',
      price: prop.price,
      client_id: clientId,
      rent_start_date: new Date(startDate).toISOString(),
      rent_end_date: new Date(endDate).toISOString()
    })
  }

  const updateVisitStatus = async (visitId: number | string, newStatus: string) => {
    try {
      await agentService.updateVisitStatus(visitId, newStatus)
      fetchData()
    } catch (e) {
      console.error("Failed to update visit status", e)
      throw e
    }
  }

  return {
    visits,
    myProperties,
    clients,
    inquiries,
    statistics,
    searchQuery,
    locationQuery,
    statusFilter,
    dateFilter,
    loading,
    statsLoading,
    upcomingVisits,
    finishedVisits,
    filteredVisits,
    visitChartData,
    propertyStatusChartData,
    monthlyVisitsChartData,
    fetchData,
    submitSaleRequest,
    submitRentRequest,
    updateVisitStatus
  }
}
