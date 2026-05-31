import { ref, computed } from 'vue'
import { useAgentService } from '~/services/agentService'

export const useAgentVisits = () => {
  const agentService = useAgentService()

  // State
  const visits = ref<any[]>([])
  const loading = ref(false)

  // Filters State
  const searchQuery = ref('')
  const locationQuery = ref('')
  const statusFilter = ref('all')
  const dateFilter = ref('all')

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

  // Methods
  const fetchVisits = async () => {
    loading.value = true
    try {
      const res = await agentService.getVisits()
      visits.value = res.data || []
    } catch (e) {
      console.error("Failed to fetch visits:", e)
    } finally {
      loading.value = false
    }
  }

  const updateVisitStatus = async (visitId: number | string, newStatus: string) => {
    try {
      await agentService.updateVisitStatus(visitId, newStatus)
      await fetchVisits()
    } catch (e) {
      console.error("Failed to update visit status:", e)
      throw e
    }
  }

  return {
    visits,
    loading,
    searchQuery,
    locationQuery,
    statusFilter,
    dateFilter,
    upcomingVisits,
    finishedVisits,
    filteredVisits,
    fetchVisits,
    updateVisitStatus
  }
}
