import { useApi } from '~/composables/useApi'

export const useAgentService = () => {
    const api = useApi()

    return {
        async getVisits() {
            return api.get('/agent/visits')
        },
        async updateVisitStatus(visitId: number | string, status: string) {
            return api.put(`/agent/visits/${visitId}/status?status=${status}`)
        },
        async getProperties() {
            return api.get('/agent/properties')
        },
        async getInquiries() {
            return api.get('/agent/inquiries')
        },
        async approveInquiry(inquiryId: number | string) {
            return api.post(`/agent/inquiries/${inquiryId}/approve`)
        },
        async rejectInquiry(inquiryId: number | string) {
            return api.post(`/agent/inquiries/${inquiryId}/reject`)
        },
        async updateInquiryStatus(inquiryId: number | string, status: string) {
            return api.put(`/agent/inquiries/${inquiryId}/status?status=${status}`)
        },
        async getStatistics() {
            return api.get('/statistics/agent')
        }
    }
}
