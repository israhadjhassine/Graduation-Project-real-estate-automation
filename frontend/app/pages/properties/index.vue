<template>
  <div class="flex h-[calc(100vh-96px)] overflow-hidden bg-primary-50/20">
    <!-- Left Sidebar / Filters -->
    <div class="w-80 bg-white border-r border-primary-100 flex flex-col h-full z-20 shadow-[4px_0_24px_-12px_rgba(0,0,0,0.05)]">
      <!-- Sidebar Header -->
      <div class="px-6 py-6 border-b border-primary-50 flex items-center justify-between bg-white/80 backdrop-blur-md sticky top-0 shrink-0">
        <h2 class="font-bold text-primary-950 text-xl tracking-tight">Refine Search</h2>
        <button @click="resetFilters" class="text-xs font-bold text-accent-600 hover:text-accent-500 transition-colors uppercase tracking-widest">Reset</button>
      </div>

      <!-- Scrollable Filters -->
      <div class="flex-1 overflow-y-auto px-6 py-6 space-y-8 custom-scrollbar">
        <!-- Semantic Search -->
        <div class="space-y-3">
          <label class="text-[10px] font-bold text-primary-400 uppercase tracking-widest">Semantic Search</label>
          <div class="relative group">
            <LucideSparkles class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-accent-500" />
            <input 
              v-model="searchQuery" 
              @keyup.enter="handleSearch"
              placeholder="e.g. Cozy villa near beach" 
              class="w-full bg-primary-50/50 border border-primary-100 rounded-xl pl-10 pr-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" 
            />
          </div>
          <button @click="handleSearch" class="w-full py-3 bg-primary-950 hover:bg-primary-900 text-white rounded-xl font-bold transition-all shadow-lg shadow-primary-900/20 text-sm flex items-center justify-center gap-2">
            <LucideSearch class="w-4 h-4" /> Search
          </button>
        </div>

        <div class="h-px bg-primary-50 w-full"></div>

        <!-- Location -->
        <div class="space-y-3">
          <label class="text-[10px] font-bold text-primary-400 uppercase tracking-widest">Location</label>
          <div class="relative">
             <LucideMapPin class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400 z-10 pointer-events-none" />
             <select v-model="location" @change="handleSearch" class="w-full bg-white border border-primary-100 rounded-xl pl-10 pr-4 py-3 text-sm font-medium appearance-none focus:border-primary-300 focus:ring-4 focus:ring-primary-50 transition-all outline-none cursor-pointer relative z-0">
               <option value="">Any Place</option>
               <option v-for="gov in governorates" :key="gov" :value="gov">{{ gov }}</option>
             </select>
             <LucideChevronDown class="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400 pointer-events-none z-10" />
          </div>
        </div>

        <!-- Property Type -->
        <div class="space-y-3">
          <label class="text-[10px] font-bold text-primary-400 uppercase tracking-widest">Type</label>
          <div class="grid grid-cols-2 gap-2">
            <button @click="setPropertyType('All')" :class="['py-2 px-3 border rounded-lg text-xs font-bold transition-all', propertyType === 'All' ? 'border-primary-950 bg-primary-950 text-white' : 'border-primary-100 bg-white text-primary-600 hover:bg-primary-50 hover:border-primary-200']">All</button>
            <button @click="setPropertyType('Villa')" :class="['py-2 px-3 border rounded-lg text-xs font-bold transition-all', propertyType === 'Villa' ? 'border-primary-950 bg-primary-950 text-white' : 'border-primary-100 bg-white text-primary-600 hover:bg-primary-50 hover:border-primary-200']">Villa</button>
            <button @click="setPropertyType('Apartment')" :class="['py-2 px-3 border rounded-lg text-xs font-bold transition-all', propertyType === 'Apartment' ? 'border-primary-950 bg-primary-950 text-white' : 'border-primary-100 bg-white text-primary-600 hover:bg-primary-50 hover:border-primary-200']">Apartment</button>
            <button @click="setPropertyType('Studio')" :class="['py-2 px-3 border rounded-lg text-xs font-bold transition-all', propertyType === 'Studio' ? 'border-primary-950 bg-primary-950 text-white' : 'border-primary-100 bg-white text-primary-600 hover:bg-primary-50 hover:border-primary-200']">Studio</button>
          </div>
        </div>

        <!-- Price Range -->
        <div class="space-y-4">
          <label class="text-[10px] font-bold text-primary-400 uppercase tracking-widest flex justify-between">
            <span>Price Range</span>
            <span class="text-primary-950">DT</span>
          </label>
          <div class="flex items-center gap-2">
            <input v-model="minPrice" type="number" placeholder="Min" @keyup.enter="handleSearch" class="w-full bg-white border border-primary-100 rounded-xl px-3 py-2 text-sm font-medium focus:border-primary-300 focus:ring-4 focus:ring-primary-50 outline-none transition-all" />
            <span class="text-primary-300">-</span>
            <input v-model="maxPrice" type="number" placeholder="Max" @keyup.enter="handleSearch" class="w-full bg-white border border-primary-100 rounded-xl px-3 py-2 text-sm font-medium focus:border-primary-300 focus:ring-4 focus:ring-primary-50 outline-none transition-all" />
          </div>
        </div>

        <!-- Sorting -->
        <div class="space-y-3">
          <label class="text-[10px] font-bold text-primary-400 uppercase tracking-widest">Sort By</label>
          <div class="relative">
             <LucideArrowUpDown class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400 z-10 pointer-events-none" />
             <select v-model="sortPrice" @change="handleSearch" class="w-full bg-white border border-primary-100 rounded-xl pl-10 pr-4 py-3 text-sm font-medium appearance-none focus:border-primary-300 focus:ring-4 focus:ring-primary-50 transition-all outline-none cursor-pointer relative z-0">
               <option value="">Recommended</option>
               <option value="asc">Price: Low to High</option>
               <option value="desc">Price: High to Low</option>
             </select>
             <LucideChevronDown class="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400 pointer-events-none z-10" />
          </div>
        </div>

      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col overflow-hidden relative">
      <!-- Header Controls -->
      <div class="h-[76px] border-b border-primary-100 bg-white/95 backdrop-blur-md px-8 flex items-center justify-between shrink-0 sticky top-0 z-10">
        <div>
          <p class="text-sm font-bold text-primary-950"><span class="text-accent-600 text-lg">{{ properties.length }}</span> Properties Found</p>
        </div>
        <div class="flex bg-primary-50 p-1 rounded-xl border border-primary-100/50">
          <button 
            @click="viewMode = 'list'"
            :class="['p-2 rounded-lg transition-all', viewMode === 'list' ? 'bg-white shadow-sm text-primary-950' : 'text-primary-400 hover:text-primary-600']"
          >
            <LucideLayoutGrid class="w-4 h-4" />
          </button>
          <button 
            @click="viewMode = 'map'"
            :class="['p-2 rounded-lg transition-all', viewMode === 'map' ? 'bg-white shadow-sm text-primary-950' : 'text-primary-400 hover:text-primary-600']"
          >
            <LucideMap class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Content Views -->
      <div class="flex-1 flex overflow-hidden">
        <!-- Listings List -->
        <div :class="['overflow-y-auto px-8 py-8 transition-all duration-500', viewMode === 'map' ? 'w-1/2' : 'w-full']">
          <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8" :class="{'xl:grid-cols-3': viewMode === 'list'}">
             <div v-for="i in 6" :key="i" class="h-[400px] bg-white border border-primary-50 shadow-sm animate-pulse rounded-3xl"></div>
          </div>
          <div v-else-if="properties.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8" :class="{'xl:grid-cols-3': viewMode === 'list'}">
            <PropertyCard 
              v-for="prop in properties" 
              :key="prop.id" 
              :property="prop"
              @click="navigateTo(`/properties/${prop.slug}`)"
            />
          </div>
          <div v-else class="h-full flex flex-col items-center justify-center opacity-40">
             <LucideGhost class="w-20 h-20 mb-6 text-primary-300" />
             <p class="font-bold text-xl text-primary-950">No properties found</p>
             <p class="text-primary-500 mt-2 text-sm">Adjust your filters to discover more.</p>
          </div>
        </div>

        <!-- Map View -->
        <div :class="['transition-all duration-500 h-full p-8 pl-0 relative', viewMode === 'map' ? 'w-1/2' : 'w-0 invisible opacity-0']">
           <div class="w-full h-full rounded-[2.5rem] overflow-hidden shadow-2xl border border-primary-100 relative">
             <PropertyMap :properties="properties" class="border-none shadow-none rounded-none" />
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  LucideSearch, LucideLayoutGrid, LucideMap, 
  LucideGhost, LucideSparkles, LucideMapPin, LucideChevronDown, LucideArrowUpDown
} from 'lucide-vue-next'

const api = useApi()
const viewMode = ref('list')
const loading = ref(false)
const properties = ref([])

// Filters state
const searchQuery = ref('')
const location = ref('')
const propertyType = ref('All')
const minPrice = ref('')
const maxPrice = ref('')
const sortPrice = ref('')

// Governorates
const governorates = [
  "Ariana", "Béja", "Ben Arous", "Bizerte", "Gabès", "Gafsa", "Jendouba", 
  "Kairouan", "Kasserine", "Kébili", "Le Kef", "Mahdia", "La Manouba", 
  "Médenine", "Monastir", "Nabeul", "Sfax", "Sidi Bouzid", "Siliana", 
  "Sousse", "Tataouine", "Tozeur", "Tunis", "Zaghouan"
]

const setPropertyType = (type) => {
  propertyType.value = type
  handleSearch()
}

const resetFilters = () => {
  searchQuery.value = ''
  location.value = ''
  propertyType.value = 'All'
  minPrice.value = ''
  maxPrice.value = ''
  sortPrice.value = ''
  handleSearch()
}

const handleSearch = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (searchQuery.value) params.append('query', searchQuery.value)
    if (location.value) params.append('location', location.value)
    if (propertyType.value && propertyType.value !== 'All') params.append('property_type', propertyType.value)
    if (minPrice.value) params.append('min_price', minPrice.value)
    if (maxPrice.value) params.append('max_price', maxPrice.value)
    if (sortPrice.value) params.append('sort_price', sortPrice.value)
    
    // Convert to query string
    const queryString = params.toString()
    
    // If no semantic query and no filters, just get all properties
    // Otherwise use the semantic search endpoint which now handles filters too
    const endpoint = queryString ? `/search/semantic?${queryString}` : '/properties'
    
    const res = await api.get(endpoint)
    properties.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e2e8f0;
  border-radius: 20px;
}
</style>
