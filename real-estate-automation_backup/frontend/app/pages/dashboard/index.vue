<template>
  <div class="max-w-7xl mx-auto px-6 py-12">
    <div class="flex items-center justify-between mb-12">
      <div>
        <h1 class="text-4xl font-bold text-primary-950 mb-2">Agent Dashboard</h1>
        <p class="text-primary-400">Manage your exclusive property portfolio</p>
      </div>
      <button @click="showModal = true" class="btn-primary">
        <LucidePlus class="w-5 h-5" /> List New Property
      </button>
    </div>

    <!-- Quick Stats -->
    <div class="grid md:grid-cols-3 gap-6 mb-12">
       <div class="card-premium flex items-center gap-6">
          <div class="w-14 h-14 bg-primary-100 rounded-2xl flex items-center justify-center">
            <LucideLayoutDashboard class="w-7 h-7 text-primary-600" />
          </div>
          <div>
            <p class="text-xs font-bold text-primary-300 uppercase tracking-widest">Total Listings</p>
            <p class="text-3xl font-bold text-primary-950">{{ properties.length }}</p>
          </div>
       </div>
       <div class="card-premium flex items-center gap-6">
          <div class="w-14 h-14 bg-accent-100 rounded-2xl flex items-center justify-center">
            <LucideEye class="w-7 h-7 text-accent-600" />
          </div>
          <div>
            <p class="text-xs font-bold text-primary-300 uppercase tracking-widest">Global Views</p>
            <p class="text-3xl font-bold text-primary-950">1,284</p>
          </div>
       </div>
       <div class="card-premium flex items-center gap-6">
          <div class="w-14 h-14 bg-green-100 rounded-2xl flex items-center justify-center">
            <LucideTrendingUp class="w-7 h-4 text-green-600" />
          </div>
          <div>
            <p class="text-xs font-bold text-primary-300 uppercase tracking-widest">AI Inquiries</p>
            <p class="text-3xl font-bold text-primary-950">42</p>
          </div>
       </div>
    </div>

    <!-- Listings Table -->
    <div class="card-premium p-0 overflow-hidden">
      <table class="w-full text-left">
        <thead>
          <tr class="bg-primary-50/50 border-b border-primary-100">
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Status</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Price</th>
            <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-primary-50">
          <tr v-for="prop in properties" :key="prop.id" class="hover:bg-primary-50/30 transition-colors">
            <td class="px-6 py-4">
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl overflow-hidden bg-primary-100">
                   <img v-if="prop.images?.length" :src="`http://localhost:8000${prop.images[0].image_url}`" class="w-full h-full object-cover" />
                   <LucideImage v-else class="w-12 h-12 p-3 text-primary-200" />
                </div>
                <div>
                  <p class="font-bold text-primary-950 text-sm">{{ prop.title }}</p>
                  <p class="text-[10px] text-primary-400">{{ prop.city }}</p>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="px-2 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded-lg uppercase">{{ prop.status }}</span>
            </td>
            <td class="px-6 py-4 font-bold text-primary-950 text-sm">
              {{ formatPrice(prop.price) }} <span class="text-[10px]">{{ prop.currency }}</span>
            </td>
            <td class="px-6 py-4">
               <div class="flex gap-2">
                 <button class="p-2 hover:bg-primary-100 rounded-lg text-primary-400 transition-colors">
                   <LucideEdit class="w-4 h-4" />
                 </button>
                 <button class="p-2 hover:bg-red-50 rounded-lg text-red-400 transition-colors">
                   <LucideTrash2 class="w-4 h-4" />
                 </button>
               </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="!properties.length" class="text-center py-20 bg-white rounded-3xl border-2 border-dashed border-primary-100 mt-6">
       <LucideBuilding class="w-12 h-12 text-primary-100 mx-auto mb-4" />
       <p class="text-primary-300 font-medium">No properties listed yet. Start by adding a new one.</p>
    </div>

    <!-- Modals -->
    <PropertyUploadModal 
      :show="showModal" 
      @close="showModal = false" 
      @success="handleSuccess"
    />
  </div>
</template>

<script setup>
import { 
  LucidePlus, LucideLayoutDashboard, LucideEye, 
  LucideTrendingUp, LucideImage, LucideEdit, LucideTrash2,
  LucideBuilding
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const api = useApi()
const properties = ref([])
const loading = ref(false)
const showModal = ref(false)

const handleSuccess = () => {
  showModal.value = false
  fetchMyProperties()
}

const fetchMyProperties = async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/properties') // For Head Agent, we will filter on backend or here
    properties.value = res.data.filter(p => p.owner_id === auth.user?.id)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}

onMounted(() => {
  if (!auth.isHeadAgent && !auth.isAdmin) {
    navigateTo('/login')
  } else {
    fetchMyProperties()
  }
})
</script>
