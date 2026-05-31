import { ref, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useAgencyService } from '~/services/agencyService'
import { useAgentService } from '~/services/agentService'
import { usePropertyService } from '~/services/propertyService'
import { useAlert } from '~/composables/useAlert'

export const useAgencyDashboard = () => {
  const auth = useAuthStore()
  const agencyService = useAgencyService()
  const agentService = useAgentService()
  const propertyService = usePropertyService()
  const alert = useAlert()

  // State
  const properties = ref<any[]>([])
  const staff = ref<any[]>([])
  const inquiries = ref<any[]>([])
  const reports = ref<any[]>([])
  const clients = ref<any[]>([])
  const visits = ref<any[]>([])
  const loading = ref(false)
  const statistics = ref<any>(null)

  // Computed properties
  const soldProperties = computed(() => properties.value.filter(p => p.status === 'sold'))
  const rentedProperties = computed(() => properties.value.filter(p => p.status === 'rented'))
  const activeProperties = computed(() => properties.value.filter(p => !['sold', 'pending_sold'].includes(p.status)))
  const pendingSales = computed(() => properties.value.filter(p => ['pending_sold', 'pending_rent'].includes(p.status)))
  const closedDealsCount = computed(() => soldProperties.value.length + rentedProperties.value.length)

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
  const fetchData = async () => {
    loading.value = true
    try {
      const [propsRes, staffRes, inqRes, clientsRes, statsRes, visitsRes] = await Promise.all([
        agencyService.getProperties(),
        agencyService.getStaff(),
        agentService.getInquiries(),
        agencyService.getClients(),
        agencyService.getStatistics(),
        agencyService.getVisits()
      ])
      
      properties.value = propsRes.data
      staff.value = staffRes.data
      inquiries.value = inqRes.data
      clients.value = clientsRes.data
      statistics.value = statsRes.data
      visits.value = visitsRes.data
      
      if (auth.isAdmin || auth.isHeadAgent) {
        try {
          const reportsRes = await agencyService.getReports()
          reports.value = reportsRes.data
        } catch (e) {
          console.error("Failed to fetch reports", e)
        }
      }
    } catch (e) {
      console.error("Dashboard fetch error:", e)
    } finally {
      loading.value = false
    }
  }

  const deleteProperty = async (propertyId: number | string) => {
    const result = await alert.confirm('Delete Property?', 'Are you sure you want to permanently delete this property listing?', 'Delete')
    if (result.isConfirmed) {
      try {
        await propertyService.deleteProperty(propertyId)
        alert.success('Deleted', 'Property listing has been removed.')
        fetchData()
      } catch (e) {
        console.error("Failed to delete property", e)
        alert.error('Delete Failed', 'Could not remove the property.')
      }
    }
  }

  const assignAgent = async (propertyId: number | string, newAgentId: number | string | null) => {
    try {
      const payload = newAgentId ? { agent_id: parseInt(newAgentId as string) } : { agent_id: null }
      await propertyService.assignProperty(propertyId, payload)
      
      const agentName = newAgentId ? staff.value.find(s => s.id == newAgentId)?.full_name : 'Unassigned'
      alert.success('Agent Assigned', `Property successfully assigned to ${agentName}.`)
      
      fetchData()
    } catch (e) {
      console.error("Failed to assign agent", e)
      alert.error('Assignment Failed', 'Could not update agent assignment.')
    }
  }

  const updateInquiryStatus = async (inquiryId: number | string, status: string) => {
    try {
      await agentService.updateInquiryStatus(inquiryId, status)
      alert.success('Updated', 'Inquiry status has been updated.')
      fetchData()
    } catch (e) {
      console.error("Failed to update inquiry status", e)
      alert.error('Update Failed', "Could not update status.")
    }
  }

  const toggleAgentStatus = async (agentId: number | string) => {
    try {
      await agencyService.toggleAgentStatus(agentId)
      fetchData()
    } catch (e: any) {
      console.error("Failed to toggle agent status", e)
      alert.error('Status Update Failed', e.response?.data?.detail || 'Failed to update status')
    }
  }

  const downloadReport = async (report: any) => {
    try {
      const res = await agencyService.downloadReport(report.id)
      const url = window.URL.createObjectURL(res.data)
      const link = document.createElement('a')
      link.href = url
      const filename = `Report_${report.type}_${report.property_title.replace(/\s+/g, '_')}.pdf`
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
    } catch (e) {
      console.error("Failed to download report", e)
      alert.error('Download Failed', "Could not download report.")
    }
  }

  return {
    // State
    properties,
    staff,
    inquiries,
    reports,
    clients,
    visits,
    loading,
    statistics,
    // Computed
    soldProperties,
    rentedProperties,
    activeProperties,
    pendingSales,
    propertyStatusChartData,
    agentPerformanceChartData,
    closedDealsCount,
    // Methods
    fetchData,
    deleteProperty,
    assignAgent,
    updateInquiryStatus,
    toggleAgentStatus,
    downloadReport
  }
}
