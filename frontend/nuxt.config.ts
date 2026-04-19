export default defineNuxtConfig({
  future: {
    compatibilityVersion: 4,
  },
  srcDir: 'app/',
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt'],
  build: {
    transpile: ['chart.js', 'vue-chartjs']
  },
  vite: {
    server: {
      watch: {
        usePolling: false,
        ignored: ['**/.git/**', '**/node_modules/**']
      }
    }
  },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      apiUrl: process.env.API_URL || 'http://localhost:8000',
      telegramBotName: process.env.NUXT_PUBLIC_TELEGRAM_BOT_NAME || 'Pfe_rea_bot'
    }
  },
  app: {
    head: {
      title: 'Elite Real Estate | Premium Property Automation',
      meta: [
        { name: 'description', content: 'AI-Powered premium real estate platform for luxury listings.' }
      ],
      link: [
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap' },
        { rel: 'stylesheet', href: 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' }
      ]
    }
  }
})
