<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-6">
      
      <!-- Sub-Agent Header -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-6">
          <div class="w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-900 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-900/20 text-white">
            <LucideHeadset class="w-10 h-10" />
          </div>
        <div class="flex items-center gap-4">
           <LucideHeadset class="w-10 h-10 text-blue-600" />
           <div>
             <h1 class="text-2xl font-bold text-primary-950">Agent Workspace</h1>
             <p class="text-xs text-primary-500">Manage property visits and track your portfolio.</p>
           </div>
        </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <LucideHome class="w-6 h-6 text-blue-600" />
            </div>
          </div>
           <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">My Listings</p>
           <p class="text-3xl font-bold text-primary-950 mt-1">{{ myProperties.length }}</p>
        </div>

        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-accent-100 rounded-xl flex items-center justify-center">
              <LucideCalendar class="w-6 h-6 text-accent-600" />
            </div>
          </div>
          <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">Upcoming Visits</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">{{ upcomingVisits.length }}</p>
        </div>

        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <LucideCheckCircle2 class="w-6 h-6 text-green-600" />
            </div>
          </div>
           <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">Completed Visits</p>
           <p class="text-3xl font-bold text-primary-950 mt-1">{{ finishedVisits.length }}</p>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex gap-4 border-b border-primary-100 mb-8 overflow-x-auto pb-2">
         <button 
           @click="activeTab = 'visits'" 
           :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'visits' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
         >
           <LucideCalendar class="w-4 h-4 inline-block mr-2" /> Property Visits
         </button>
        <button 
          @click="activeTab = 'properties'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'properties' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucideHome class="w-4 h-4 inline-block mr-2" /> My Portfolio
        </button>
      </div>


      <!-- Tab Content: Properties -->
      <div v-show="activeTab === 'properties'">
         <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Property</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Price</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-100">
              <tr v-for="prop in myProperties" :key="prop.id" @click="viewProperty(prop)" class="hover:bg-primary-50/50 transition-colors cursor-pointer group">
                <td class="px-6 py-4">
                   <p class="font-bold text-sm text-primary-950 group-hover:text-accent-600 transition-colors">{{ prop.title }}</p>
                   <p class="text-[10px] text-primary-400">{{ prop.city }}</p>
                </td>
                <td class="px-6 py-4 text-sm font-bold text-primary-950">
                   {{ prop.price }} {{ prop.currency }}
                </td>
                <td class="px-6 py-4">
                   <span :class="[
                     'px-2 py-1 text-[10px] font-bold rounded-lg uppercase',
                     prop.status === 'sold' ? 'bg-purple-100 text-purple-700' : prop.status === 'pending_sold' ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                   ]">
                      {{ prop.status }}
                   </span>
                </td>
                <td class="px-6 py-4 text-right" @click.stop>
                    <template v-if="prop.status === 'available'">
                      <button 
                        v-if="prop.listing_type === 'sale'"
                        @click="openSaleModal(prop.id)"
                        class="px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-xl text-[10px] font-bold uppercase transition-all shadow-lg shadow-accent-900/10 mb-1 inline-block"
                      >
                        Request Sale
                      </button>
                      <button 
                        v-if="prop.listing_type === 'rent'"
                        @click="openRentModal(prop.id)"
                        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-[10px] font-bold uppercase transition-all shadow-lg shadow-blue-900/10 mb-1 inline-block"
                      >
                        Request Rent
                      </button>
                    </template>
                    <span v-else-if="prop.status === 'pending_sold' || prop.status === 'pending_rent'" class="px-3 py-1 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-lg uppercase animate-pulse">
                      Approval Pending
                    </span>
                    <span v-else class="text-[10px] font-bold text-primary-300 uppercase italic">Goal Reached</span>
                </td>
              </tr>
              <tr v-if="!myProperties.length">
                 <td colspan="4" class="py-12 text-center text-primary-500">
                    <LucideHome class="w-12 h-12 text-primary-200 mx-auto mb-3" />
                    <p>No listings assigned to you yet.</p>
                 </td>
              </tr>
            </tbody>
          </table>
         </div>
      </div>
      <div v-show="activeTab === 'visits'">
         <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Date & Time</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Client</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Listing</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-100">
              <tr v-for="visit in visits" :key="visit.id" class="hover:bg-primary-50/50">
                <td class="px-6 py-4 text-sm font-bold text-primary-950">
                   <div class="flex items-center gap-3">
                      <LucideCalendar class="w-4 h-4 text-primary-400" />
                      {{ new Date(visit.visit_date).toLocaleString() }}
                   </div>
                </td>
                <td class="px-6 py-4 text-sm text-primary-600">
                   <p class="font-bold text-primary-950">{{ visit.client?.full_name || 'Visitor' }}</p>
                   <p class="text-[10px] text-primary-400">{{ visit.client?.email || visit.telegram_chat_id || 'No contact' }}</p>
                </td>
                <td class="px-6 py-4 text-sm text-primary-600">
                   <p class="font-bold text-primary-950">{{ visit.property?.title || 'Unknown Property' }}</p>
                   <p class="text-[10px] text-primary-400">{{ visit.property?.city || '' }}</p>
                </td>
                <td class="px-6 py-4">
                   <span :class="[
                     'px-3 py-1 text-[10px] font-bold rounded-lg uppercase',
                     visit.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                     visit.status === 'finished' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                   ]">
                      {{ visit.status }}
                   </span>
                </td>
                <td class="px-6 py-4">
                   <div v-if="visit.status === 'scheduled'" class="flex items-center gap-2">
                      <button @click="updateVisitStatus(visit.id, 'finished')" class="text-xs font-bold text-green-600 hover:text-green-700 bg-green-50 hover:bg-green-100 px-3 py-1.5 rounded-lg transition-colors">
                        Complete
                      </button>
                      <button @click="updateVisitStatus(visit.id, 'cancelled')" class="text-xs font-bold text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-lg transition-colors">
                        Cancel
                      </button>
                   </div>
                   <span v-else class="text-xs text-primary-400 font-medium">No actions</span>
                </td>
              </tr>
              <tr v-if="!visits.length">
                 <td colspan="5" class="py-12 text-center text-primary-500">
                    <LucideCalendarOff class="w-12 h-12 text-primary-200 mx-auto mb-3" />
                    <p>No property viewings scheduled.</p>
                 </td>
              </tr>
            </tbody>
          </table>
         </div>
      </div>

    </div>

    <!-- Sale Request Modal -->
    <div v-if="showSaleModal" class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-primary-950/40 backdrop-blur-sm transition-all" @click="showSaleModal = false">
      <div class="bg-white rounded-3xl w-full max-w-md p-8 shadow-2xl relative border border-primary-50" @click.stop>
        <button @click="showSaleModal = false" class="absolute top-6 right-6 text-primary-400 hover:text-primary-950 transition-colors">
          <LucideX class="w-6 h-6" />
        </button>
        <h3 class="text-2xl font-bold text-primary-950 mb-3">Request Sale Approval</h3>
        <p class="text-primary-600 mb-6 leading-relaxed">Select the registered client who purchased this property.</p>
        
        <div class="space-y-4 mb-8">
          <div>
            <label class="block text-sm font-bold text-primary-950 mb-2">Registered Client (Buyer)</label>
            <select v-model="selectedClientId" class="w-full bg-primary-50 p-3 rounded-xl border border-primary-200 outline-none focus:border-accent-500">
              <option value="" disabled>Select a client...</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                {{ client.email }}
              </option>
            </select>
          </div>
        </div>
        
        <button @click="submitSaleRequest" class="w-full py-3.5 bg-accent-600 hover:bg-accent-700 text-white font-bold rounded-xl transition-colors shadow-lg shadow-accent-600/30">
          Submit Request
        </button>
      </div>
    </div>

    <!-- Rent Request Modal -->
    <div v-if="showRentModal" class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-primary-950/40 backdrop-blur-sm transition-all" @click="showRentModal = false">
      <div class="bg-white rounded-3xl w-full max-w-md p-8 shadow-2xl relative border border-primary-50" @click.stop>
        <button @click="showRentModal = false" class="absolute top-6 right-6 text-primary-400 hover:text-primary-950 transition-colors">
          <LucideX class="w-6 h-6" />
        </button>
        <h3 class="text-2xl font-bold text-primary-950 mb-3">Request Rent Approval</h3>
        <p class="text-primary-600 mb-6 leading-relaxed">Select the rental duration for this property.</p>
        
        <div class="space-y-4 mb-8">
          <div>
            <label class="block text-sm font-bold text-primary-950 mb-2">Registered Client (Tenant)</label>
            <select v-model="selectedClientId" class="w-full bg-primary-50 p-3 rounded-xl border border-primary-200 outline-none focus:border-accent-500">
              <option value="" disabled>Select a client...</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                {{ client.email }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-bold text-primary-950 mb-2">Start Date</label>
            <input type="date" v-model="rentStartDate" class="w-full bg-primary-50 p-3 rounded-xl border border-primary-200 outline-none focus:border-accent-500" />
          </div>
          <div>
            <label class="block text-sm font-bold text-primary-950 mb-2">End Date</label>
            <input type="date" v-model="rentEndDate" class="w-full bg-primary-50 p-3 rounded-xl border border-primary-200 outline-none focus:border-accent-500" />
          </div>
        </div>
        
        <button @click="submitRentRequest" class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-colors shadow-lg shadow-blue-600/30">
          Submit Request
        </button>
      </div>
    </div>
    
    <PropertyUploadModal 
      :show="showDetailsModal" 
      :edit-data="selectedProperty"
      :read-only="isReadOnly"
      @close="handleClose" 
    />
  </div>
</template>

<script setup>
import { 
  LucideHeadset, LucideCalendar, 
  LucideCheckCircle2, LucideHome,
  LucideCalendarOff, LucideX
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import axios from 'axios'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const activeTab = ref('visits')

const visits = ref([])
const properties = ref([])
const clients = ref([])

const myProperties = computed(() => properties.value.filter(p => p.agent_id === auth.user?.id))

// Computed properties for dashboard stats
const upcomingVisits = computed(() => visits.value.filter(v => v.status === 'scheduled'))
const finishedVisits = computed(() => visits.value.filter(v => v.status === 'finished'))

const showDetailsModal = ref(false)
const selectedProperty = ref(null)
const isReadOnly = ref(false)

const viewProperty = (prop) => {
  isReadOnly.value = true
  selectedProperty.value = prop
  showDetailsModal.value = true
}

const handleClose = () => {
  showDetailsModal.value = false
  selectedProperty.value = null
  isReadOnly.value = false
}

// Config
const config = useRuntimeConfig()
const getApiUrl = () => {
    let url = config.public.apiUrl
    if (process.client && url.includes('backend')) {
        url = 'http://localhost:8000'
    }
    return url
}

const fetchData = async () => {
  try {
    const [visitsRes, propsRes, clientsRes] = await Promise.all([
      axios.get(`${getApiUrl()}/agent/visits`, { headers: { Authorization: `Bearer ${auth.token}` } }),
      axios.get(`${getApiUrl()}/properties`, { headers: { Authorization: `Bearer ${auth.token}` } }),
      axios.get(`${getApiUrl()}/agency/clients`, { headers: { Authorization: `Bearer ${auth.token}` } })
    ])
    visits.value = visitsRes.data
    properties.value = propsRes.data
    clients.value = clientsRes.data
  } catch (e) {
    console.error("Agent dashboard fetch error:", e)
  }
}


const showSaleModal = ref(false)
const selectedSalePropertyId = ref(null)
const selectedClientId = ref('')

const openSaleModal = (id) => {
  selectedSalePropertyId.value = id
  selectedClientId.value = ''
  showSaleModal.value = true
}

const submitSaleRequest = async () => {
  if (!selectedClientId.value) {
    alert("Please select a registered client.")
    return
  }
  try {
    await axios.patch(`${getApiUrl()}/properties/${selectedSalePropertyId.value}/status`, { 
      status: 'pending_sold',
      buyer_id: selectedClientId.value 
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    fetchData()
    showSaleModal.value = false
    alert("Sale request sent! Your head agent will review and approve.")
  } catch (e) {
    console.error("Failed to request sale", e)
    alert(e.response?.data?.detail || "Failed to submit sale request.")
  }
}

const showRentModal = ref(false)
const selectedRentPropertyId = ref(null)
const rentStartDate = ref('')
const rentEndDate = ref('')

const openRentModal = (id) => {
  selectedRentPropertyId.value = id
  rentStartDate.value = ''
  rentEndDate.value = ''
  selectedClientId.value = ''
  showRentModal.value = true
}

const submitRentRequest = async () => {
  if (!selectedClientId.value) {
    alert("Please select a registered client.")
    return
  }
  if (!rentStartDate.value || !rentEndDate.value) {
    alert("Please select both start and end dates.")
    return
  }
  
  try {
    await axios.patch(`${getApiUrl()}/properties/${selectedRentPropertyId.value}/status`, { 
      status: 'pending_rent',
      rent_start_date: new Date(rentStartDate.value).toISOString(),
      rent_end_date: new Date(rentEndDate.value).toISOString(),
      buyer_id: selectedClientId.value
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    
    showRentModal.value = false
    fetchData()
    alert("Rent request sent! Your head agent will review and approve.")
  } catch (e) {
    console.error("Failed to request rent", e)
    alert(e.response?.data?.detail || "Failed to submit rent request.")
  }
}

const updateVisitStatus = async (visitId, newStatus) => {
  try {
    await axios.put(`${getApiUrl()}/agent/visits/${visitId}/status?status=${newStatus}`, null, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    fetchData()
  } catch (e) {
    console.error("Failed to update visit status", e)
  }
}

onMounted(() => {
  // Allow Head Agents and Admins to view this dashboard too for demonstration/testing
  watchEffect(() => {
    if (auth.isInitialized) {
      if (!auth.isAgent && !auth.isHeadAgent && !auth.isAdmin) {
        navigateTo('/')
      } else {
        fetchData()
      }
    }
  })
})

useHead({
  title: 'Agent Workspace | Elite Real Estate'
})
</script>
