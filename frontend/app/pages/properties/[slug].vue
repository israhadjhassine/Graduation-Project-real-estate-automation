<template>
  <div v-if="property" class="max-w-7xl mx-auto px-6 py-12">
    <!-- Breadcrumbs & Actions -->
    <div class="flex items-center justify-between mb-8">
      <NuxtLink to="/" class="flex items-center gap-2 text-primary-400 hover:text-primary-950 transition-colors font-medium">
        <LucideChevronLeft class="w-4 h-4" /> Back to Search
      </NuxtLink>
      <div class="flex gap-4">
        <button class="w-10 h-10 rounded-full border border-primary-200 flex items-center justify-center hover:bg-white transition-all">
          <LucideShare2 class="w-4 h-4 text-primary-600" />
        </button>
        <button class="w-10 h-10 rounded-full border border-primary-200 flex items-center justify-center hover:bg-white transition-all">
          <LucideHeart class="w-4 h-4 text-primary-600" />
        </button>
      </div>
    </div>

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
        <!-- AI Assistant -->
        <AiChatBox :propertyId="property.id" />

        <!-- Agency Info -->
        <div class="card-premium">
           <h4 class="font-bold text-primary-950 mb-6 uppercase tracking-widest text-xs">Interested?</h4>
           <div class="flex items-center gap-4 mb-8">
              <div class="w-14 h-14 bg-primary-900 rounded-2xl flex items-center justify-center text-white text-xl font-bold">
                E
              </div>
              <div>
                <p class="font-bold text-primary-950">Elite Agency</p>
                <p class="text-xs text-primary-400">Exclusive Luxury Partner</p>
              </div>
           </div>
           <button class="btn-primary w-full shadow-primary-700/40">Schedule a Visit</button>
           <p class="text-center mt-6 text-[10px] text-primary-300 font-bold uppercase tracking-widest">or inquire via Telegram</p>
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
  LucideImage
} from 'lucide-vue-next'

const route = useRoute()
const api = useApi()
const property = ref(null)
const loading = ref(true)

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

onMounted(() => {
  fetchProperty()
})
</script>
