<template>
  <div class="max-w-7xl mx-auto px-6 pb-20">
    <!-- Hero Section -->
    <section class="py-20 lg:py-32 flex flex-col items-center text-center relative overflow-hidden">
      <!-- Background Bloom -->
      <div class="absolute -top-40 -left-20 w-96 h-96 bg-primary-200/30 blur-[120px] rounded-full"></div>
      <div class="absolute -bottom-40 -right-20 w-80 h-80 bg-accent-100/40 blur-[100px] rounded-full"></div>

      <div class="relative z-10 max-w-3xl">
        <h1 class="text-5xl lg:text-7xl font-bold text-primary-950 tracking-tight leading-tight mb-6">
          Elevate Your <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-accent-600">Standard</span> of Living
        </h1>
        <p class="text-lg lg:text-xl text-primary-600 mb-10 max-w-2xl mx-auto leading-relaxed">
          Discover exclusive, meticulously curated properties tailored to your highest aspirations. Experience the future of real estate.
        </p>
        <NuxtLink to="/properties" class="inline-flex items-center gap-2 px-8 py-4 bg-primary-950 text-white rounded-full font-bold hover:bg-primary-800 transition-all shadow-xl shadow-primary-900/20 group">
          Explore Portfolio <LucideArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </NuxtLink>
      </div>
    </section>

    <!-- Listings Grid -->
    <section class="mt-12">
      <div class="flex justify-between items-end mb-12">
        <div>
          <h2 class="text-4xl font-bold text-primary-950 mb-2">Featured Listings</h2>
          <p class="text-primary-400">Curated luxury properties across the nation</p>
        </div>
        <NuxtLink to="/properties" class="text-accent-600 font-bold hover:text-accent-700 flex items-center gap-1 group">
          View All <LucideArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </NuxtLink>
      </div>

      <div v-if="loading" class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div v-for="i in 6" :key="i" class="h-96 bg-primary-100 animate-pulse rounded-3xl"></div>
      </div>

      <div v-else-if="properties.length > 0" class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        <PropertyCard 
          v-for="prop in properties" 
          :key="prop.id" 
          :property="prop"
          @click="navigateTo(`/properties/${prop.slug}`)"
        />
      </div>

      <div v-else class="text-center py-20 bg-white/50 rounded-3xl border-2 border-dashed border-primary-100">
        <LucideGhost class="w-12 h-12 text-primary-200 mx-auto mb-4" />
        <h3 class="text-xl font-bold text-primary-400">No properties found</h3>
        <p class="text-primary-300">Try adjusting your semantic search for better results.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { 
  LucideSearch, LucideSparkles, LucideLoader2, 
  LucideArrowRight, LucideGhost 
} from 'lucide-vue-next'

const api = useApi()
const searchQuery = ref('')
const loading = ref(false)
const properties = ref([])

const fetchProperties = async () => {
  loading.value = true
  try {
    const res = await api.get('/properties')
    properties.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value) return fetchProperties()
  
  loading.value = true
  try {
    const res = await api.get(`/search/semantic?query=${encodeURIComponent(searchQuery.value)}`)
    properties.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProperties()
})
</script>
