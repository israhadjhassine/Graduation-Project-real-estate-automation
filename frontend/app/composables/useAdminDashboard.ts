import { ref, computed } from 'vue'
import { useAdminUsers } from './admin/useAdminUsers'
import { useAdminProperties } from './admin/useAdminProperties'
import { useAdminReports } from './admin/useAdminReports'
import { useAdminAnalytics } from './admin/useAdminAnalytics'

export const useAdminDashboard = () => {
  const usersDomain = useAdminUsers()
  const propertiesDomain = useAdminProperties()
  const reportsDomain = useAdminReports()
  const analyticsDomain = useAdminAnalytics()

  const loading = ref(false)

  const closedDealsCount = computed(() => {
    if (!analyticsDomain.statistics.value || !analyticsDomain.statistics.value.property_statuses) return 0
    const sold = analyticsDomain.statistics.value.property_statuses.sold || 0
    const rented = analyticsDomain.statistics.value.property_statuses.rented || 0
    return sold + rented
  })

  const fetchData = async () => {
    loading.value = true
    try {
      await Promise.all([
        usersDomain.fetchUsers(),
        propertiesDomain.fetchProperties(),
        reportsDomain.fetchReports(),
        analyticsDomain.fetchAnalytics()
      ])
    } catch (e) {
      console.error("Failed to fetch all dashboard data", e)
    } finally {
      loading.value = false
    }
  }

  return {
    // Users
    users: usersDomain.users,
    userSearchQuery: usersDomain.userSearchQuery,
    userRoleFilter: usersDomain.userRoleFilter,
    userStatusFilter: usersDomain.userStatusFilter,
    filteredUsers: usersDomain.filteredUsers,
    headAgents: usersDomain.headAgents,
    createUser: usersDomain.createUser,
    toggleUserStatus: usersDomain.toggleUserStatus,

    // Properties
    properties: propertiesDomain.properties,
    propSearchQuery: propertiesDomain.propSearchQuery,
    propLocationQuery: propertiesDomain.propLocationQuery,
    filteredProperties: propertiesDomain.filteredProperties,
    closedDealsCount,

    // Reports
    reports: reportsDomain.reports,
    downloadReport: reportsDomain.downloadReport,

    // Analytics
    statistics: analyticsDomain.statistics,
    visits: analyticsDomain.visits,
    statsLoading: analyticsDomain.loading,
    transactionRequestsPipelineChartData: analyticsDomain.transactionRequestsPipelineChartData,
    topAgentsChartData: analyticsDomain.topAgentsChartData,
    propertyStatusChartData: analyticsDomain.propertyStatusChartData,

    // Global
    loading,
    fetchData
  }
}

