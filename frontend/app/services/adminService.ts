import { useApi } from '~/composables/useApi'

export const useAdminService = () => {
    const api = useApi()

    return {
        async getUsers() {
            return api.get('/admin/users')
        },
        async createUser(data: any) {
            return api.post('/admin/users', data)
        },
        async toggleUserStatus(id: number | string) {
            return api.patch(`/admin/users/${id}/toggle-status`, {})
        },
        async getReports() {
            return api.get('/admin/reports')
        },
        async getVisits() {
            return api.get('/agent/visits')
        },
        async getStatistics() {
            return api.get('/statistics/admin')
        },
        async downloadReport(id: number | string) {
            return api.get(`/admin/reports/${id}/download`, { responseType: 'blob' })
        }
    }
}
