import { ref, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useAdminService } from '~/services/adminService'
import { usePropertyService } from '~/services/propertyService'
import { useAlert } from '~/composables/useAlert'

export const useAdminDashboard = () => {
  const auth = useAuthStore()
  const adminService = useAdminService()
  const propertyService = usePropertyService()
  const alert = useAlert()

  // State
  const users = ref<any[]>([])
  const properties = ref<any[]>([])
  const reports = ref<any[]>([])
  const visits = ref<any[]>([])
  const statistics = ref<any>(null)
  
  const loading = ref(false)
  const statsLoading = ref(false)

  // Filters State
  const userSearchQuery = ref('')
  const userRoleFilter = ref('all')
  const userStatusFilter = ref('all')
  const propSearchQuery = ref('')
  const propLocationQuery = ref('')

  // Computed properties
  const filteredUsers = computed(() => {
    return users.value.filter(u => {
      const matchesSearch = !userSearchQuery.value || 
        u.full_name.toLowerCase().includes(userSearchQuery.value.toLowerCase())
      
      const matchesRole = userRoleFilter.value === 'all' || u.role === userRoleFilter.value
      
      const matchesStatus = userStatusFilter.value === 'all' || 
        (userStatusFilter.value === 'active' ? u.is_active : !u.is_active)
        
      const isStaff = u.role !== 'client'
        
      return matchesSearch && matchesRole && matchesStatus && isStaff
    })
  })

  const filteredProperties = computed(() => {
    return properties.value.filter(p => {
      const matchesSearch = !propSearchQuery.value || 
        p.title.toLowerCase().includes(propSearchQuery.value.toLowerCase())
      
      const matchesLocation = !propLocationQuery.value || 
        p.city?.toLowerCase().includes(propLocationQuery.value.toLowerCase())
        
      return matchesSearch && matchesLocation
    })
  })

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

  const headAgents = computed(() => users.value.filter(u => u.role === 'head_agent'))

  const closedDealsCount = computed(() => properties.value.filter(p => ['sold', 'rented'].includes(p.status)).length)

  // Methods
  const fetchData = async () => {
    loading.value = true
    statsLoading.value = true
    try {
      const [usersRes, propsRes, reportsRes, statsRes, visitsRes] = await Promise.all([
        adminService.getUsers(),
        propertyService.getProperties(),
        adminService.getReports(),
        adminService.getStatistics(),
        adminService.getVisits()
      ])
      
      users.value = usersRes.data || []
      properties.value = propsRes.data || []
      reports.value = reportsRes.data || []
      statistics.value = statsRes.data || null
      visits.value = visitsRes.data || []
    } catch (e) {
      console.error("Failed to load admin data", e)
    } finally {
      loading.value = false
      statsLoading.value = false
    }
  }

  const createUser = async (payload: any) => {
    try {
      await adminService.createUser(payload)
      fetchData() // Refresh data
    } catch (e: any) {
      console.error("Failed to create user", e)
      throw new Error(e.response?.data?.detail || "Failed to create user")
    }
  }

  const toggleUserStatus = async (userId: number | string) => {
    try {
      await adminService.toggleUserStatus(userId)
      fetchData()
    } catch (e: any) {
      console.error("Failed to toggle user status", e)
      alert.error("Status Update Failed", e.response?.data?.detail || "Failed to update account status")
    }
  }

  const downloadReport = async (report: any) => {
    try {
      if (!report.id) {
        console.error("Report ID is missing", report)
        throw new Error("Invalid report ID")
      }
      const res = await adminService.downloadReport(report.id)
      const url = window.URL.createObjectURL(res.data)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Report_${report.property_title || 'Transaction'}.pdf`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (e) {
      console.error("Failed to download report", e)
      alert.error("Download Failed", "Could not download report.")
    }
  }

  return {
    // State
    users,
    properties,
    reports,
    visits,
    statistics,
    loading,
    statsLoading,
    
    // Filters
    userSearchQuery,
    userRoleFilter,
    userStatusFilter,
    propSearchQuery,
    propLocationQuery,
    
    // Computed
    filteredUsers,
    filteredProperties,
    userRolesChartData,
    topAgentsChartData,
    propertyStatusChartData,
    headAgents,
    closedDealsCount,
    
    // Methods
    fetchData,
    createUser,
    toggleUserStatus,
    downloadReport
  }
}
