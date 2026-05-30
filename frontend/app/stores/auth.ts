import { defineStore } from 'pinia'
import axios from 'axios'

interface User {
    id: number
    email: string
    full_name: string
    role: 'admin' | 'head_agent' | 'agent' | 'client'
    agency_id?: number
}

interface AuthState {
    user: User | null
    token: string | null
    isInitialized: boolean
}

export const useAuthStore = defineStore('auth', {
    state: (): AuthState => ({
        user: null,
        token: null,
        isInitialized: false
    }),

    getters: {
        isAuthenticated: (state) => !!state.token,
        isAdmin: (state) => state.user?.role === 'admin',
        isHeadAgent: (state) => state.user?.role === 'head_agent',
        isAgent: (state) => state.user?.role === 'agent',
        isClient: (state) => state.user?.role === 'client',

        authenticatedHomeLink: (state) => {
            if (state.user?.role === 'admin') return '/admin'
            if (state.user?.role === 'head_agent') return '/agency'
            if (state.user?.role === 'agent') return '/agent'
            return '/'
        },

        profileLink: (state) => {
            if (!state.user) return '/login'
            if (state.user.role === 'client') return '/profile'
            return '/dashboard/profile'
        }
    },

    actions: {
        async init() {
            if (process.server) return
            const token = localStorage.getItem('token')
            if (token) {
                this.token = token
                await this.fetchUser()
            }
            this.isInitialized = true
        },

        async login(email: string, password: string) {
            const config = useRuntimeConfig()
            let apiUrl = config.public.apiUrl as string
            if (process.client && apiUrl.includes('backend')) {
                apiUrl = 'http://localhost:8000'
            }

            const formData = new FormData()
            formData.append('username', email)
            formData.append('password', password)

            try {
                const response = await axios.post(`${apiUrl}/auth/login`, formData)
                this.token = response.data.access_token
                if (this.token) {
                    localStorage.setItem('token', this.token)
                    await this.fetchUser()
                }
            } catch (error) {
                throw error
            }
        },

        async fetchUser() {
            const config = useRuntimeConfig()
            let apiUrl = config.public.apiUrl as string
            if (process.client && apiUrl.includes('backend')) {
                apiUrl = 'http://localhost:8000'
            }

            try {
                const response = await axios.get(`${apiUrl}/auth/me`, {
                    headers: { Authorization: `Bearer ${this.token}` }
                })
                this.user = response.data
            } catch (error) {
                this.logout()
            }
        },

        logout() {
            this.user = null
            this.token = null
            if (process.client) {
                localStorage.removeItem('token')
            }
            return navigateTo('/login')
        }
    }
})
