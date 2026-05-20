<template>
  <div v-if="property" class="max-w-7xl mx-auto px-6 py-12">
    

    <div class="grid lg:grid-cols-3 gap-12">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-12">
        <!-- Gallery -->
        <div class="grid grid-cols-4 grid-rows-2 gap-4 h-[600px]">
          <div class="col-span-3 row-span-2 rounded-3xl overflow-hidden shadow-2xl">
            <img :src="mainImage" class="w-full h-full object-cover" />
          </div>
          <div v-for="(img, i) in sideImages" :key="i" class="rounded-2xl overflow-hidden shadow-xl">
             <img :src="getPublicUrl(img.image_url)" class="w-full h-full object-cover" />
          </div>
          <div v-if="sideImages.length < 2" class="bg-primary-100 rounded-2xl flex items-center justify-center">
            <LucideImage class="w-8 h-8 text-primary-200" />
          </div>
        </div>

        <!-- Details -->
        <div class="space-y-6">
          <div class="flex items-start justify-between">
            <div>
              <h1 class="text-5xl font-bold text-primary-950 mb-4">{{ property.title }}</h1>
               <p class="text-primary-500 flex items-center gap-2 text-lg">
                <LucideMapPin class="w-5 h-5 text-accent-500" /> {{ property.city }}, {{ property.country }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-xs font-bold text-primary-400 uppercase tracking-[0.2em] mb-1">Asking Price</p>
              <p class="text-4xl font-bold text-primary-950">{{ formatPrice(property.price) }} <span class="text-lg font-serif italic font-normal text-accent-500">{{ property.currency }}</span></p>
            </div>
          </div>

          <div class="flex gap-8 py-8 border-y border-primary-100">
             <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 rounded-2xl bg-primary-100 flex items-center justify-center">
                  <LucideBedDouble class="w-6 h-6 text-primary-600" />
                </div>
                <span class="text-sm font-bold">{{ property.bedrooms }} Bedrooms</span>
             </div>
             <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 rounded-2xl bg-primary-100 flex items-center justify-center">
                  <LucideBath class="w-6 h-6 text-primary-600" />
                </div>
                <span class="text-sm font-bold">{{ property.bathrooms }} Bathrooms</span>
             </div>
             <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 rounded-2xl bg-primary-100 flex items-center justify-center">
                  <LucideMaximize class="w-6 h-6 text-primary-600" />
                </div>
                <span class="text-sm font-bold">{{ property.area }} m² Living</span>
             </div>
          </div>

          <div class="prose prose-primary max-w-none">
            <h3 class="text-2xl font-bold text-primary-950 mb-4">About this property</h3>
            <p class="text-primary-800 leading-relaxed text-lg">{{ property.description }}</p>
          </div>

          <div v-if="property.features.length" class="space-y-6">
             <h3 class="text-2xl font-bold text-primary-950">Amenities</h3>
             <div class="flex flex-wrap gap-3">
                <span v-for="feat in property.features" :key="feat.id" 
                  class="px-4 py-2 bg-white border border-primary-100 rounded-full text-xs font-bold text-primary-600 shadow-sm"
                >
                  {{ feat.name }}
                </span>
             </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-8">
        <!-- Map Integration -->
        <div class="h-80 w-full rounded-3xl overflow-hidden shadow-2xl border border-primary-50">
           <PropertyMap :properties="[property]" />
        </div>

        <!-- Agency Info -->
        <div class="bg-gradient-to-br from-primary-900 to-primary-950 rounded-3xl p-8 text-white shadow-2xl relative overflow-hidden">
           <div class="absolute -top-20 -right-20 w-40 h-40 bg-accent-500/20 blur-3xl rounded-full"></div>
           <h4 class="font-bold text-primary-300 mb-6 uppercase tracking-[0.2em] text-[10px]">Interested?</h4>
           <div class="flex items-center gap-4 mb-8 relative z-10">
              <div class="w-16 h-16 bg-white/10 backdrop-blur-md rounded-2xl flex items-center justify-center text-white text-2xl font-serif italic border border-white/20">
                E
              </div>
              <div>
                <p class="font-bold text-xl tracking-wide">Elite Agency</p>
                <p class="text-xs text-primary-300 uppercase tracking-wider mt-1">Exclusive Luxury Partner</p>
              </div>
           </div>
           
           <div class="space-y-3 relative z-10">
             <button @click="handleTelegramInquiry" class="w-full py-4 bg-[#229ED9] hover:bg-[#1E8CC0] text-white rounded-xl font-bold transition-all shadow-lg shadow-[#229ED9]/30 flex items-center justify-center gap-2 group">
               <LucideSend class="w-4 h-4 group-hover:-translate-y-1 group-hover:translate-x-1 transition-transform" /> Inquire via Telegram
             </button>
           </div>
        </div>
      </div>
    </div>
    
    <!-- Auth Required Modal -->
    <div v-if="showAuthModal" class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-primary-950/40 backdrop-blur-sm transition-all" @click="showAuthModal = false">
      <div class="bg-white rounded-3xl w-full max-w-md p-8 shadow-2xl relative border border-primary-50" @click.stop>
        <button @click="showAuthModal = false" class="absolute top-6 right-6 text-primary-400 hover:text-primary-950 transition-colors">
          <LucideX class="w-6 h-6" />
        </button>
        
        <div class="w-16 h-16 bg-accent-50 rounded-2xl flex items-center justify-center mb-6">
          <LucideLock class="w-8 h-8 text-accent-600" />
        </div>
        
        <h3 class="text-2xl font-bold text-primary-950 mb-3">Authentication Required</h3>
        <p class="text-primary-600 mb-8 leading-relaxed">
          For your security and a personalized experience, please sign in or create a client account to inquire about this exclusive property via Telegram.
        </p>
        
        <div class="space-y-3">
          <button @click="navigateTo('/login')" class="btn-primary w-full py-3.5 !rounded-xl">
            Sign In to your Account
          </button>
          <button @click="navigateTo('/register')" class="w-full py-3.5 bg-primary-50 hover:bg-primary-100 text-primary-950 font-bold rounded-xl transition-colors border border-primary-200 text-sm">
            Create an Elite Account
          </button>
        </div>
      </div>
    </div>
    
  </div>
  
  <div v-else-if="loading" class="max-w-7xl mx-auto px-6 py-12 animate-pulse space-y-12">
    <div class="h-[600px] bg-primary-100 rounded-3xl"></div>
    <div class="grid grid-cols-3 gap-12">
       <div class="col-span-2 h-96 bg-primary-50 rounded-3xl"></div>
       <div class="h-96 bg-primary-50 rounded-3xl"></div>
    </div>
  </div>
</template>

<script setup>
import { 
  LucideChevronLeft, LucideShare2, LucideHeart, 
  LucideMapPin, LucideBedDouble, LucideBath, LucideMaximize,
  LucideImage, LucideSend, LucideLock, LucideX
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

const route = useRoute()
const api = useApi()
const auth = useAuthStore()
const property = ref(null)
const loading = ref(true)
const showAuthModal = ref(false)

const fetchProperty = async () => {
  loading.value = true
  try {
    const res = await api.get('/properties')
    // Simulating slug filter as our current API returns all
    property.value = res.data.find(p => p.slug === route.params.slug)
    if (!property.value) showError({ statusCode: 404, message: 'Property not found' })
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const { getPublicUrl } = useAssetUrl()

const mainImage = computed(() => {
  const primary = property.value?.images?.find(img => img.is_primary)
  return primary ? getPublicUrl(primary.image_url) : 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80'
})

const sideImages = computed(() => {
  return property.value?.images?.filter(img => !img.is_primary).slice(0, 2) || []
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}

const config = useRuntimeConfig()

const handleTelegramInquiry = () => {
  if (!property.value) return
  
  if (!auth.isAuthenticated || !auth.user) {
    showAuthModal.value = true
    return
  }

  // Check if client has linked their Telegram account
  if (!auth.user.telegram_chat_id) {
    navigateTo('/profile?tab=telegram')
    return
  }

  // Construct the Telegram link with the property slug as context
  const botUsername = config.public.telegramBotName || 'Pfe_rea_bot'
  const slugContext = property.value.slug
  const telegramUrl = `https://t.me/${botUsername}?start=${slugContext}`
  
  window.open(telegramUrl, '_blank')
}

onMounted(() => {
  fetchProperty()
})
</script>
