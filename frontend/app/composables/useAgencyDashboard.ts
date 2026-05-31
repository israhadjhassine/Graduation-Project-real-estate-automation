import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useAgencyProperties } from './agency/useAgencyProperties'
import { useAgencyStaff } from './agency/useAgencyStaff'
import { useAgencyInquiries } from './agency/useAgencyInquiries'
import { useAgencyReports } from './agency/useAgencyReports'
import { useAgencyAnalytics } from './agency/useAgencyAnalytics'

export const useAgencyDashboard = () => {
  const auth = useAuthStore()

  const loading = ref(false)

  // Sub-composables
  const propertiesDomain = useAgencyProperties(() => fetchData())
  const staffDomain = useAgencyStaff(() => fetchData())
  const inquiriesDomain = useAgencyInquiries(() => fetchData())
  const reportsDomain = useAgencyReports()
  const analyticsDomain = useAgencyAnalytics()

  const fetchData = async () => {
    loading.value = true
    try {
      const fetchPromises: Promise<any>[] = [
        propertiesDomain.fetchProperties(),
        staffDomain.fetchStaff(),
        inquiriesDomain.fetchInquiries(),
        analyticsDomain.fetchAnalytics()
      ]

      if (auth.isAdmin || auth.isHeadAgent) {
        fetchPromises.push(reportsDomain.fetchReports())
      }

      await Promise.all(fetchPromises)
    } catch (e) {
      console.error("Dashboard fetch error:", e)
    } finally {
      loading.value = false
    }
  }

  // Wrapper for assignAgent that matches original signature
  const assignAgent = async (propertyId: number | string, newAgentId: number | string | null) => {
    await propertiesDomain.assignAgent(propertyId, newAgentId, staffDomain.staff.value)
  }

  return {
    // State
    properties: propertiesDomain.properties,
    staff: staffDomain.staff,
    inquiries: inquiriesDomain.inquiries,
    reports: reportsDomain.reports,
    clients: analyticsDomain.clients,
    visits: analyticsDomain.visits,
    loading,
    statistics: analyticsDomain.statistics,

    // Computed
    soldProperties: propertiesDomain.soldProperties,
    rentedProperties: propertiesDomain.rentedProperties,
    activeProperties: propertiesDomain.activeProperties,
    pendingSales: propertiesDomain.pendingSales,
    propertyStatusChartData: analyticsDomain.propertyStatusChartData,
    agentPerformanceChartData: analyticsDomain.agentPerformanceChartData,
    closedDealsCount: propertiesDomain.closedDealsCount,

    // Methods
    fetchData,
    deleteProperty: propertiesDomain.deleteProperty,
    assignAgent,
    updateInquiryStatus: inquiriesDomain.updateInquiryStatus,
    toggleAgentStatus: staffDomain.toggleAgentStatus,
    downloadReport: reportsDomain.downloadReport
  }
}
