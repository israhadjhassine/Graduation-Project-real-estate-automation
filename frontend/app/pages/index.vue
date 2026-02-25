<template>
  <div class="max-w-7xl mx-auto px-6 pb-20">
    <!-- Hero Section -->
    <section class="py-20 lg:py-32 flex flex-col items-center text-center relative overflow-hidden">
      <!-- Background Bloom -->
      <div class="absolute -top-40 -left-20 w-96 h-96 bg-primary-200/30 blur-[120px] rounded-full"></div>
      <div class="absolute -bottom-40 -right-20 w-80 h-80 bg-accent-100/40 blur-[100px] rounded-full"></div>

      <div class="relative z-10 max-w-4xl">
        <h1 class="text-6xl md:text-8xl font-bold text-primary-950 mb-8 leading-[1.1]">
          The Art of <span class="text-accent-500 font-serif italic font-normal">Living</span> <br/> 
          Defined by AI.
        </h1>
        <p class="text-xl text-primary-500 max-w-2xl mx-auto mb-12">
          Experience the next generation of real estate. Our semantic engine understands your dreams beyond keywords. Find your perfect match in Tunisia with a simple sentence.
        </p>

        <!-- Semantic Search Bar -->
        <div class="max-w-2xl mx-auto w-full group">
          <div class="relative flex items-center p-2 bg-white rounded-full shadow-2xl shadow-primary-900/10 border border-primary-100 focus-within:border-accent-400 focus-within:ring-4 focus-within:ring-accent-50 transition-all duration-300">
            <LucideSearch class="ml-4 text-primary-300 w-6 h-6" />
            <input 
              v-model="searchQuery"
              @keyup.enter="handleSearch"
              type="text" 
              placeholder="e.g. 'Cozy quiet villa with a pool in Tunis near the beach'..."
              class="w-full bg-transparent border-none focus:ring-0 text-primary-950 placeholder:text-primary-200 px-4 py-3"
            />
            <button 
              @click="handleSearch"
              class="btn-accent !py-3 !px-8 hover:scale-105 active:scale-95 transition-transform"
              :disabled="loading"
            >
              <LucideSparkles v-if="!loading" class="w-5 h-5" />
              <LucideLoader2 v-else class="w-5 h-5 animate-spin" />
              <span>Find Home</span>
            </button>
          </div>
          <p class="mt-4 text-[10px] text-primary-300 uppercase tracking-widest font-bold">Powered by Google Gemini 1.5 & pgvector</p>
        </div>
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
