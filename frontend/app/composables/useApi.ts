import axios from 'axios'
import { useAuthStore } from '~/stores/auth'

export const useApi = () => {
    const config = useRuntimeConfig()
    const authStore = useAuthStore()

    let baseURL = config.public.apiUrl as string

    // If on client, and apiUrl is the internal docker name, fallback to localhost
    if (process.client && baseURL.includes('backend')) {
        baseURL = 'http://localhost:8000'
    }

    const api = axios.create({
        baseURL
    })

    api.interceptors.request.use((config) => {
        if (authStore.token) {
            config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
    })

    api.interceptors.response.use(
        (response) => response,
        (error) => {
            if (error.response?.status === 401) {
                authStore.logout()
            }
            return Promise.reject(error)
        }
    )

    return api
}
