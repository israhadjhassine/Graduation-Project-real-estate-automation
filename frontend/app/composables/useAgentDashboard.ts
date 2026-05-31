import { ref } from 'vue'
import { useAgentVisits } from './agent/useAgentVisits'
import { useAgentProperties } from './agent/useAgentProperties'
import { useAgentInquiries } from './agent/useAgentInquiries'
import { useAgentAnalytics } from './agent/useAgentAnalytics'

export const useAgentDashboard = () => {
  const visitsDomain = useAgentVisits()
  const propertiesDomain = useAgentProperties()
  const inquiriesDomain = useAgentInquiries()
  const analyticsDomain = useAgentAnalytics()

  const loading = ref(false)

  const fetchData = async () => {
    loading.value = true
    try {
      await Promise.all([
        visitsDomain.fetchVisits(),
        propertiesDomain.fetchPropertiesAndClients(),
        inquiriesDomain.fetchInquiries(),
        analyticsDomain.fetchAnalytics()
      ])
    } catch (e) {
      console.error("Agent dashboard fetch error:", e)
    } finally {
      loading.value = false
    }
  }

  return {
    // Visits
    visits: visitsDomain.visits,
    searchQuery: visitsDomain.searchQuery,
    locationQuery: visitsDomain.locationQuery,
    statusFilter: visitsDomain.statusFilter,
    dateFilter: visitsDomain.dateFilter,
    upcomingVisits: visitsDomain.upcomingVisits,
    finishedVisits: visitsDomain.finishedVisits,
    filteredVisits: visitsDomain.filteredVisits,
    updateVisitStatus: visitsDomain.updateVisitStatus,

    // Properties
    myProperties: propertiesDomain.myProperties,
    clients: propertiesDomain.clients,
    submitSaleRequest: propertiesDomain.submitSaleRequest,
    submitRentRequest: propertiesDomain.submitRentRequest,

    // Inquiries
    inquiries: inquiriesDomain.inquiries,

    // Analytics
    statistics: analyticsDomain.statistics,
    statsLoading: analyticsDomain.loading,
    visitChartData: analyticsDomain.visitChartData,
    propertyStatusChartData: analyticsDomain.propertyStatusChartData,
    monthlyVisitsChartData: analyticsDomain.monthlyVisitsChartData,

    // Global
    loading,
    fetchData
  }
}
