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
             <p class="text-xs text-primary-500">Manage inquiries, visits, and close deals.</p>
           </div>
        </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="grid md:grid-cols-3 gap-6 mb-8">
        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <LucideMessageSquare class="w-6 h-6 text-primary-600" />
            </div>
          </div>
          <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">New Leads</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">{{ pendingInquiries.length }}</p>
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
          <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">Resolved Inquiries</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">{{ resolvedInquiries.length }}</p>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex gap-4 border-b border-primary-100 mb-8 overflow-x-auto pb-2">
        <button 
          @click="activeTab = 'inquiries'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'inquiries' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucideMessageSquare class="w-4 h-4 inline-block mr-2" /> Web & Telegram Leads
        </button>
        <button 
          @click="activeTab = 'visits'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'visits' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucideCalendar class="w-4 h-4 inline-block mr-2" /> Property Viewings
        </button>
        <button 
          @click="activeTab = 'properties'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'properties' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucideHome class="w-4 h-4 inline-block mr-2" /> My Portfolio
        </button>
      </div>

      <!-- Tab Content: Inquiries -->
      <div v-show="activeTab === 'inquiries'">
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="inq in inquiries" :key="inq.id" class="card-premium flex flex-col h-full group relative overflow-hidden">
            <!-- Source Badge -->
            <div class="absolute top-0 right-0 p-4">
               <LucideSend v-if="inq.source === 'telegram'" class="w-5 h-5 text-blue-500" />
               <LucideGlobe v-else class="w-5 h-5 text-primary-400" />
            </div>

            <div class="flex items-center gap-4 mb-4">
              <div class="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center font-bold text-primary-950">
                {{ inq.name.charAt(0) }}
              </div>
              <div>
                <p class="font-bold text-primary-950">{{ inq.name }}</p>
                <a :href="`mailto:${inq.email}`" class="text-xs text-primary-500 hover:text-accent-500 transition-colors">{{ inq.email }}</a>
                <p v-if="inq.phone" class="text-xs text-primary-500">{{ inq.phone }}</p>
              </div>
            </div>

            <div class="flex-grow">
              <h3 class="font-bold text-sm text-primary-950 mb-2">{{ inq.subject }}</h3>
              <p class="text-sm text-primary-600 mb-4 bg-primary-50 p-4 rounded-xl border border-primary-100">{{ inq.message }}</p>
            </div>

            <div class="pt-4 border-t border-primary-100 mt-4 flex items-center justify-between">
               <span :class="[
                  'px-3 py-1 text-[10px] font-bold uppercase rounded-lg',
                  inq.status === 'new' ? 'bg-red-100 text-red-600' : 
                  inq.status === 'replied' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'
               ]">
                 {{ inq.status }}
               </span>

               <button 
                 v-if="inq.status === 'new'" 
                 @click="updateInquiryStatus(inq.id, 'replied')"
                 class="px-4 py-2 bg-primary-950 hover:bg-primary-900 text-white rounded-lg text-xs font-bold transition-all shadow-md shadow-primary-900/20"
               >
                 Mark as Replied
               </button>
               <button 
                 v-else 
                 @click="updateInquiryStatus(inq.id, 'closed')"
                 class="text-xs font-bold text-primary-400 hover:text-red-500 transition-colors"
               >
                 Archive
               </button>
            </div>
          </div>
          
          <div v-if="!inquiries.length" class="col-span-full py-20 text-center bg-white rounded-3xl border-2 border-dashed border-primary-100">
             <LucideInbox class="w-12 h-12 text-primary-200 mx-auto mb-4" />
             <p class="text-primary-400 font-medium">No inquiries received yet.</p>
          </div>
        </div>
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
              <tr v-for="prop in myProperties" :key="prop.id" class="hover:bg-primary-50/50 transition-colors">
                <td class="px-6 py-4">
                   <p class="font-bold text-sm text-primary-950">{{ prop.title }}</p>
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
                <td class="px-6 py-4 text-right">
                    <button 
                      v-if="prop.status === 'available'"
                      @click="markAsSold(prop.id)"
                      class="px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-xl text-[10px] font-bold uppercase transition-all shadow-lg shadow-accent-900/10"
                    >
                      Request Sale
                    </button>
                    <span v-else-if="prop.status === 'pending_sold'" class="px-3 py-1 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-lg uppercase animate-pulse">
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
                <td class="px-6 py-4 text-sm text-primary-600">Registered Client</td>
                <td class="px-6 py-4 text-sm text-primary-600">Assigned Listing</td>
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
  </div>
</template>

<script setup>
import { 
  LucideHeadset, LucideMessageSquare, LucideCalendar, 
  LucideCheckCircle2, LucideSend, LucideGlobe, LucideInbox,
  LucideCalendarOff
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import axios from 'axios'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const activeTab = ref('inquiries')

const inquiries = ref([])
const visits = ref([])
const properties = ref([])

const myProperties = computed(() => properties.value.filter(p => p.agent_id === auth.user?.id))

// Computed properties for dashboard stats
const pendingInquiries = computed(() => inquiries.value.filter(i => i.status === 'new'))
const resolvedInquiries = computed(() => inquiries.value.filter(i => i.status === 'replied' || i.status === 'closed'))
const upcomingVisits = computed(() => visits.value.filter(v => v.status === 'scheduled'))

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
    const [inqRes, visitsRes, propsRes] = await Promise.all([
      axios.get(`${getApiUrl()}/agent/inquiries`, { headers: { Authorization: `Bearer ${auth.token}` } }),
      axios.get(`${getApiUrl()}/agent/visits`, { headers: { Authorization: `Bearer ${auth.token}` } }),
      axios.get(`${getApiUrl()}/properties`, { headers: { Authorization: `Bearer ${auth.token}` } })
    ])
    inquiries.value = inqRes.data
    visits.value = visitsRes.data
    properties.value = propsRes.data
  } catch (e) {
    console.error("Agent dashboard fetch error:", e)
  }
}

const updateInquiryStatus = async (id, status) => {
  try {
    await axios.put(`${getApiUrl()}/agent/inquiries/${id}/status?status=${status}`, null, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    fetchData()
  } catch (e) {
    console.error("Failed to update inquiry", e)
  }
}

const markAsSold = async (id) => {
  if (!confirm("Request sale approval? Your head agent will be notified and must approve before the property is marked as sold.")) return
  try {
    await axios.patch(`${getApiUrl()}/properties/${id}/status`, { status: 'pending_sold' }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    fetchData()
    alert("Sale request sent! Your head agent will review and approve.")
  } catch (e) {
    console.error("Failed to request sale", e)
    alert(e.response?.data?.detail || "Failed to submit sale request.")
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
