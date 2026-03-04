<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-6">
      
      <!-- Head Agent Header -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-6">
          <div class="w-20 h-20 bg-gradient-to-br from-purple-600 to-purple-900 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-900/20 text-white">
            <LucideBriefcase class="w-10 h-10" />
          </div>
          <div>
            <h1 class="text-3xl font-bold text-primary-950">Management Workspace</h1>
            <p class="text-primary-500 font-medium mt-1">Manage listings and your team of sub-agents.</p>
          </div>
        </div>
        
        <button @click="showModal = true" class="btn-primary">
          <LucidePlus class="w-5 h-5" /> List New Property
        </button>
      </div>

      <!-- Quick Stats -->
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <LucideHome class="w-6 h-6 text-primary-600" />
            </div>
          </div>
          <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">Agency Listings</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">{{ properties.length }}</p>
        </div>

        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-accent-100 rounded-xl flex items-center justify-center">
              <LucideUsers class="w-6 h-6 text-accent-600" />
            </div>
          </div>
          <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">Sub-Agents</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">{{ staff.length }}</p>
        </div>

        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <LucideEye class="w-6 h-6 text-green-600" />
            </div>
          </div>
          <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">Total Client Views</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">2,492</p>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex gap-4 border-b border-primary-100 mb-8 overflow-x-auto pb-2">
        <button 
          @click="activeTab = 'properties'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'properties' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucideHome class="w-4 h-4 inline-block mr-2" /> Properties Portfolio
        </button>
        <button 
          @click="activeTab = 'staff'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'staff' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucideUsers class="w-4 h-4 inline-block mr-2" /> Sub-Agent Team
        </button>
      </div>

      <!-- Tab Content: Properties -->
      <div v-show="activeTab === 'properties'">
        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Status</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Assigned Agent</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Price</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-50">
              <tr v-for="prop in properties" :key="prop.id" class="hover:bg-primary-50/30 transition-colors">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl overflow-hidden bg-primary-100 flex-shrink-0">
                       <img v-if="prop.images?.length" :src="`http://localhost:8000${prop.images[0].image_url}`" class="w-full h-full object-cover" />
                       <LucideImage v-else class="w-12 h-12 p-3 text-primary-200" />
                    </div>
                    <div>
                      <p class="font-bold text-primary-950 text-sm max-w-xs truncate">{{ prop.title }}</p>
                      <p class="text-[10px] text-primary-400">{{ prop.city }}, {{ prop.country }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span class="px-2 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded-lg uppercase">{{ prop.status }}</span>
                </td>
                <td class="px-6 py-4">
                  <select :value="prop.agent_id" @change="assignAgent(prop.id, $event.target.value)" class="bg-primary-50 text-primary-950 font-medium text-xs rounded-lg px-2 py-1.5 border border-primary-200 outline-none focus:border-accent-400">
                    <option :value="null">Unassigned</option>
                    <option v-for="agent in staff" :key="agent.id" :value="agent.id">{{ agent.full_name }}</option>
                  </select>
                </td>
                <td class="px-6 py-4 font-bold text-primary-950 text-sm">
                  {{ formatPrice(prop.price) }} <span class="text-[10px]">{{ prop.currency }}</span>
                </td>
                <td class="px-6 py-4">
                   <div class="flex gap-2">
                     <button class="p-2 hover:bg-primary-100 rounded-lg text-primary-400 transition-colors" title="Edit Property">
                       <LucideEdit class="w-4 h-4" />
                     </button>
                     <button class="p-2 hover:bg-red-50 rounded-lg text-red-400 transition-colors" title="Delete Property">
                       <LucideTrash2 class="w-4 h-4" />
                     </button>
                   </div>
                </td>
              </tr>
              <tr v-if="!properties.length">
                <td colspan="5" class="px-6 py-12 text-center text-primary-500">
                  <LucideHome class="w-12 h-12 mx-auto text-primary-200 mb-3" />
                  <p>No properties found for this manager.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab Content: Staff Team -->
      <div v-show="activeTab === 'staff'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Sub-Agent Management</h2>
        </div>

        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Sub-Agent Name</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Email Address</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Phone Number</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Assigned Properties</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-100">
              <tr v-for="agent in staff" :key="agent.id" class="hover:bg-primary-50/50">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-950 font-bold text-xs">
                      {{ agent.full_name.charAt(0) }}
                    </div>
                    <span class="text-sm font-bold text-primary-950">{{ agent.full_name }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-primary-600">{{ agent.email }}</td>
                <td class="px-6 py-4 text-sm text-primary-600">{{ agent.phone_number || 'N/A' }}</td>
                <td class="px-6 py-4">
                  <span class="px-3 py-1 bg-primary-100 text-primary-700 text-[10px] font-bold rounded-lg uppercase">
                    {{ properties.filter(p => p.agent_id === agent.id).length }} Listings
                  </span>
                </td>
              </tr>
              <tr v-if="!staff.length">
                <td colspan="4" class="px-6 py-12 text-center text-primary-500">
                  <LucideUsers class="w-12 h-12 mx-auto text-primary-200 mb-3" />
                  <p>You have not recruited any Sub-Agents yet.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <PropertyUploadModal 
      :show="showModal" 
      @close="showModal = false" 
      @success="handleSuccess"
    />

  </div>
</template>

<script setup>
import { 
  LucideBriefcase, LucideHome, LucideUsers, LucideEye,
  LucidePlus, LucideImage, LucideEdit, LucideTrash2,
  LucideUserPlus, LucideX
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const api = useApi()
const activeTab = ref('properties')
const properties = ref([])
const staff = ref([])
const loading = ref(false)

const showModal = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const [propsRes, staffRes] = await Promise.all([
      api.get('/agency/properties'),
      api.get('/agency/staff')
    ])
    
    properties.value = propsRes.data
    staff.value = staffRes.data
    
    console.log("Agency Dashboard Sync Success:", {
      me: auth.user?.email,
      myId: auth.user?.id,
      properties: properties.value.length,
      staff: staff.value.length,
      staffRaw: staffRes.data
    })
  } catch (e) {
    console.error("Dashboard fetch error:", e)
  } finally {
    loading.value = false
  }
}

const handleSuccess = () => {
  showModal.value = false
  fetchData()
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}

const assignAgent = async (propertyId, newAgentId) => {
  try {
    const payload = newAgentId ? { agent_id: parseInt(newAgentId) } : { agent_id: null }
    await api.put(`/properties/${propertyId}/assign`, payload)
    fetchData()
  } catch (e) {
    console.error("Failed to assign agent", e)
  }
}

onMounted(() => {
  watchEffect(() => {
    if (auth.isInitialized) {
      if (!auth.isHeadAgent && !auth.isAdmin) {
        navigateTo('/')
      } else {
        fetchData()
      }
    }
  })
})

useHead({
  title: 'Agency Dashboard | Elite Real Estate'
})
</script>
