import { useApi } from '~/composables/useApi'

export const useAgencyService = () => {
    const api = useApi()

    return {
        async getProperties() {
            return api.get('/agency/properties')
        },
        async getStaff() {
            return api.get('/agency/staff')
        },
        async getClients() {
            return api.get('/agency/clients')
        },
        async getStatistics() {
            return api.get('/statistics/agency')
        },
        async createStaff(data: any) {
            return api.post('/agency/staff', data)
        },
        async updateStaff(id: number | string, data: any) {
            return api.put(`/agency/staff/${id}`, data)
        },
        async deleteStaff(id: number | string) {
            return api.delete(`/agency/staff/${id}`)
        },
        async getVisits() {
            return api.get('/agent/visits')
        },
        async getReports() {
            return api.get('/admin/reports')
        },
        async toggleAgentStatus(id: number | string) {
            return api.patch(`/agency/staff/${id}/toggle-status`, {})
        },
        async downloadReport(id: number | string) {
            return api.get(`/admin/reports/${id}/download`, { responseType: 'blob' })
        }
    }
}
