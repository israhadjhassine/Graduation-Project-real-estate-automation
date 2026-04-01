export const useAssetUrl = () => {
    const config = useRuntimeConfig()

    const getPublicUrl = (path: string) => {
        if (!path) return ''
        if (path.startsWith('http')) return path

        let baseURL = config.public.apiUrl as string

        // Fix for browser access when using Docker internal network name
        if (process.client && baseURL.includes('backend')) {
            baseURL = 'http://localhost:8000'
        }

        // Remove trailing slash from baseURL and leading slash from path if needed
        const base = baseURL.replace(/\/$/, '')
        const p = path.replace(/^\//, '')

        return `${base}/${p}`
    }

    return {
        getPublicUrl
    }
}
