<template>
  <div class="flex flex-col h-[calc(100vh-96px)] overflow-hidden">
    <!-- Filter Bar -->
    <div class="bg-white border-y border-primary-50 px-8 py-4 flex items-center justify-between z-20">
      <div class="flex items-center gap-4">
        <div class="relative group">
           <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
           <input 
             v-model="searchQuery" 
             @keyup.enter="handleSearch"
             placeholder="Search semantically..." 
             class="bg-primary-50/50 border border-primary-100 rounded-full pl-10 pr-4 py-2 text-xs font-medium w-64 focus:w-80 transition-all outline-none" 
           />
        </div>
        <div class="flex gap-2">
           <button class="px-4 py-2 rounded-full border border-primary-100 text-[10px] font-bold uppercase tracking-widest text-primary-400 hover:bg-primary-50 transition-all">Price: Any</button>
           <button class="px-4 py-2 rounded-full border border-primary-100 text-[10px] font-bold uppercase tracking-widest text-primary-400 hover:bg-primary-50 transition-all">Type: All</button>
        </div>
      </div>

      <div class="flex bg-primary-50 p-1 rounded-xl">
        <button 
          @click="viewMode = 'list'"
          :class="['p-2 rounded-lg transition-all', viewMode === 'list' ? 'bg-white shadow-sm text-primary-950' : 'text-primary-300']"
        >
          <LucideLayoutGrid class="w-4 h-4" />
        </button>
        <button 
          @click="viewMode = 'map'"
          :class="['p-2 rounded-lg transition-all', viewMode === 'map' ? 'bg-white shadow-sm text-primary-950' : 'text-primary-300']"
        >
          <LucideMap class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Listings List -->
      <div :class="['overflow-y-auto px-8 py-8 transition-all duration-500', viewMode === 'map' ? 'w-1/2' : 'w-full']">
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
           <div v-for="i in 6" :key="i" class="h-80 bg-primary-100 animate-pulse rounded-3xl"></div>
        </div>
        <div v-else-if="properties.length" class="grid grid-cols-1 md:grid-cols-2 gap-8" :class="{'lg:grid-cols-3': viewMode === 'list'}">
          <PropertyCard 
            v-for="prop in properties" 
            :key="prop.id" 
            :property="prop"
            @click="navigateTo(`/properties/${prop.slug}`)"
          />
        </div>
        <div v-else class="h-full flex flex-col items-center justify-center opacity-30">
           <LucideGhost class="w-16 h-16 mb-4" />
           <p class="font-bold">No properties found.</p>
        </div>
      </div>

      <!-- Map View -->
      <div :class="['transition-all duration-500 h-full p-8 pl-0', viewMode === 'map' ? 'w-1/2' : 'w-0 invisible opacity-0']">
         <PropertyMap :properties="properties" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  LucideSearch, LucideLayoutGrid, LucideMap, 
  LucideGhost 
} from 'lucide-vue-next'

const api = useApi()
const viewMode = ref('map')
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
