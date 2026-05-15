export const usePropertyService = () => {
    const api = useApi()

    return {
        async getProperties() {
            return api.get('/properties')
        },

        async getAgencyProperties() {
            return api.get('/agency/properties')
        },

        async getPropertyById(id: number | string) {
            return api.get(`/properties/${id}`)
        },

        async createProperty(data: any) {
            return api.post('/properties', data)
        },

        async updateProperty(id: number | string, data: any) {
            return api.put(`/properties/${id}`, data)
        },

        async deleteProperty(id: number | string) {
            return api.delete(`/properties/${id}`)
        },

        async assignProperty(id: number | string, data: { agent_id: number | string }) {
            return api.put(`/properties/${id}/assign`, data)
        },

        async requestTransaction(id: number | string, data: any) {
            return api.post(`/properties/${id}/request-transaction`, data)
        },

        async uploadImages(propertyId: number | string, files: File[]) {
            const formData = new FormData()
            files.forEach(file => {
                formData.append('files', file)
            })
            return api.post(`/properties/${propertyId}/images`, formData)
        },

        async getStaff() {
            return api.get('/agency/staff')
        },

        async getHeads() {
            return api.get('/admin/head_agents')
        },

        async getFeatures() {
            return api.get('/features')
        },

        async deleteImage(imageId: number | string) {
            return api.delete(`/properties/images/${imageId}`)
        }
    }
}
