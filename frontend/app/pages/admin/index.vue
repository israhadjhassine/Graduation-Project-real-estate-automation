<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Admin Header -->
      <div class="flex items-center justify-between mb-10 pb-8 border-b border-primary-100">
        <div>
          <h1 class="text-3xl font-extrabold text-primary-950 !font-sans tracking-tight">System Administration</h1>
          <p class="text-primary-500 font-medium mt-1">Superuser Control Panel • Platform Intelligence</p>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-10">
        <div class="card-premium border-l-4 border-l-primary-900 !rounded-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
              <LucideUsers class="w-6 h-6 text-primary-900" />
            </div>
            <div>
              <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Total Users</p>
              <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ users.length }}</p>
            </div>
          </div>
        </div>

        <div class="card-premium border-l-4 border-l-purple-600 !rounded-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
              <LucideUsers class="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Head Agents</p>
              <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ headAgents.length }}</p>
            </div>
          </div>
        </div>

        <div class="card-premium border-l-4 border-l-green-600 !rounded-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
              <LucideHome class="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Total Listings</p>
              <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ properties.length }}</p>
            </div>
          </div>
        </div>

        <div class="card-premium border-l-4 border-l-blue-600 !rounded-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
              <LucideCalendar class="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Scheduled Visits</p>
              <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ visits.length }}</p>
            </div>
          </div>
        </div>

        <div class="card-premium border-l-4 border-l-orange-600 !rounded-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center">
              <LucideTrendingUp class="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Closed Deals</p>
              <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ closedDealsCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex gap-2 border-b border-primary-100 mb-8 overflow-x-auto pb-0">
        <button 
          @click="activeTab = 'users'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'users' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideUsers class="w-4 h-4 inline-block mr-2" /> Manage Users
        </button>
        <button 
          @click="activeTab = 'properties'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'properties' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideHome class="w-4 h-4 inline-block mr-2" /> All Properties
        </button>
        <button 
          @click="activeTab = 'reports'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'reports' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideFileText class="w-4 h-4 inline-block" /> Transaction Reports
        </button>
        <button 
          @click="activeTab = 'analytics'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'analytics' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucidePieChart class="w-4 h-4 inline-block" /> Platform Analytics
        </button>
      </div>



      <!-- Tab Content: Users -->
      <div v-show="activeTab === 'users'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Platform Users</h2>
          <button @click="showUserModal = true" class="btn-primary text-sm">
            <LucidePlus class="w-4 h-4 mr-2" /> Create Staff / Admin
          </button>
        </div>

        <!-- Filters Bar -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div class="relative">
            <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
            <input 
              v-model="userSearchQuery"
              type="text" 
              placeholder="Search by full name..."
              class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
            />
          </div>

          <div class="relative">
            <LucideFilter class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
            <select 
              v-model="userRoleFilter"
              class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm appearance-none cursor-pointer"
            >
              <option value="all">All Roles</option>
              <option value="admin">Administrators</option>
              <option value="head_agent">Head Agents</option>
              <option value="agent">Sub-Agents</option>
            </select>
          </div>

          <div class="relative">
            <LucideUserCheck class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
            <select 
              v-model="userStatusFilter"
              class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm appearance-none cursor-pointer"
            >
              <option value="all">Account Status: All</option>
              <option value="active">Active Accounts</option>
              <option value="disabled">Disabled Accounts</option>
            </select>
          </div>
        </div>

        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Name</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Email</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Role</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600 text-right">Account Control</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-100">
              <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-primary-50/50 transition-colors">
                <td class="px-6 py-4 text-sm font-bold text-primary-950">{{ user.full_name }}</td>
                <td class="px-6 py-4 text-sm text-primary-600">{{ user.email }}</td>
                <td class="px-6 py-4">
                  <span :class="[
                    'px-3 py-1 text-xs font-bold rounded-full uppercase',
                    user.role === 'admin' ? 'bg-red-100 text-red-700' :
                    user.role === 'head_agent' ? 'bg-purple-100 text-purple-700' :
                    user.role === 'agent' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-700'
                  ]">
                    {{ user.role === 'head_agent' ? 'Head Agent' : user.role === 'agent' ? 'Sub-Agent' : user.role === 'admin' ? 'Admin' : user.role }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span :class="[
                    'px-3 py-1 text-[10px] font-bold rounded-lg uppercase',
                    user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  ]">
                    {{ user.is_active ? 'Active' : 'Disabled' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button 
                    v-if="user.id !== auth.user?.id"
                    @click="toggleUserStatus(user.id)" 
                    :class="[
                      'px-4 py-2 rounded-xl text-[10px] font-bold uppercase transition-all shadow-md',
                      user.is_active ? 'bg-red-50 text-red-600 hover:bg-red-100 shadow-red-900/5' : 'bg-green-50 text-green-600 hover:bg-green-100 shadow-green-900/5'
                    ]"
                  >
                    {{ user.is_active ? 'Disable' : 'Enable' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab Content: Properties -->
      <div v-show="activeTab === 'properties'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Global Property Feed</h2>
        </div>

        <!-- Filters Bar -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div class="relative">
            <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
            <input 
              v-model="propSearchQuery"
              type="text" 
              placeholder="Search by property name..."
              class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
            />
          </div>

          <div class="relative">
            <LucideMapPin class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
            <input 
              v-model="propLocationQuery"
              type="text" 
              placeholder="Filter by city/location..."
              class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
            />
          </div>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
           <div v-for="prop in filteredProperties" :key="prop.id" class="relative group">
             <PropertyCard :property="prop" />
             <div class="absolute inset-x-0 bottom-0 p-4 translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all flex gap-2">
               <button 
                 @click.stop="viewProperty(prop)"
                 class="flex-1 bg-white/90 backdrop-blur-md py-2 px-3 rounded-xl text-xs font-bold text-primary-950 hover:bg-white flex items-center justify-center gap-2 shadow-xl"
               >
                 <LucideEye class="w-3.5 h-3.5" /> View Details
               </button>
             </div>
           </div>
            <div v-if="!filteredProperties.length" class="col-span-full text-center py-12 text-primary-400">
              {{ properties.length > 0 ? 'No properties match your filters.' : 'No properties listed yet.' }}
            </div>
        </div>
      </div>

      <!-- Tab Content: Analytics -->
      <div v-show="activeTab === 'analytics'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Platform Analytics & KPIs</h2>
        </div>
        
        <div v-if="statsLoading" class="grid md:grid-cols-2 gap-6 animate-pulse">
           <div class="h-64 bg-white rounded-[2rem]"></div>
           <div class="h-64 bg-white rounded-[2rem]"></div>
        </div>
        
        <!-- Key Metrics Cards -->
        <div v-else-if="statistics" class="grid md:grid-cols-4 gap-6 mb-8">
            <div class="bg-gradient-to-br from-green-500 to-green-700 rounded-3xl p-6 text-white shadow-lg shadow-green-900/20">
               <p class="text-xs font-bold uppercase tracking-widest opacity-80 mb-1">Total Sales Revenue</p>
               <p class="text-3xl font-bold">{{ formatPrice(statistics.revenue.sales) }} <span class="text-xs font-normal">TND</span></p>
            </div>
            <div class="bg-gradient-to-br from-purple-500 to-purple-700 rounded-3xl p-6 text-white shadow-lg shadow-purple-900/20">
               <p class="text-xs font-bold uppercase tracking-widest opacity-80 mb-1">Total Rental Revenue</p>
               <p class="text-3xl font-bold">{{ formatPrice(statistics.revenue.rentals) }} <span class="text-xs font-normal">TND</span></p>
            </div>
            <div class="bg-white rounded-3xl p-6 border border-primary-100 shadow-sm flex flex-col justify-center">
               <p class="text-xs font-bold text-primary-400 uppercase tracking-widest mb-1">Total Sold</p>
               <p class="text-3xl font-bold text-primary-950">{{ statistics.property_statuses.sold || 0 }}</p>
            </div>
            <div class="bg-white rounded-3xl p-6 border border-primary-100 shadow-sm flex flex-col justify-center">
               <p class="text-xs font-bold text-primary-400 uppercase tracking-widest mb-1">Available</p>
               <p class="text-3xl font-bold text-primary-950">{{ statistics.property_statuses.available || 0 }}</p>
            </div>
        </div>

        <div v-if="!statsLoading && statistics" class="grid lg:grid-cols-2 gap-8">
           <!-- Doughnut: User Roles -->
           <div class="card-premium h-[400px] flex flex-col">
              <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Platform Users by Role</h3>
              <div class="flex-1 relative pb-4">
                 <ChartsDoughnutChart v-if="userRolesChartData" :chart-data="userRolesChartData" />
              </div>
           </div>
           
           <!-- Bar: Top Agents -->
           <div class="card-premium h-[400px] flex flex-col">
              <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Top 5 Performing Agents</h3>
              <div class="flex-1 relative pb-4">
                 <ChartsBarChart v-if="topAgentsChartData" :chart-data="topAgentsChartData" />
              </div>
           </div>
           
           <!-- Doughnut: Platform Property Statuses -->
           <div class="card-premium h-[400px] flex flex-col lg:col-span-2">
              <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-[60px]">Total Properties Breakdown</h3>
              <div class="flex-1 relative">
                 <ChartsDoughnutChart v-if="propertyStatusChartData" :chart-data="propertyStatusChartData" :chart-options="{ cutout: '65%' }" />
              </div>
           </div>
        </div>
      </div>

      <!-- Tab Content: Reports -->
      <div v-show="activeTab === 'reports'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">System Transaction Reports</h2>
        </div>

        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property Title</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Type</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Date</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-50">
              <tr v-for="report in reports" :key="report.id" class="hover:bg-primary-50/30 transition-colors">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <LucideFileText class="w-5 h-5 text-primary-400" />
                    <span class="font-bold text-primary-950 text-sm">{{ report.property_title }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span class="text-xs font-medium text-primary-600">{{ report.type }}</span>
                </td>
                <td class="px-6 py-4">
                  <span class="text-xs font-medium text-primary-600">{{ report.date }}</span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button @click="downloadReport(report)" class="px-4 py-2 bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-xl text-[10px] font-bold uppercase transition-all inline-flex items-center gap-2">
                    <LucideDownload class="w-3 h-3" /> Download
                  </button>
                </td>
              </tr>
              <tr v-if="!reports.length">
                <td colspan="2" class="py-12 text-center text-primary-400">
                  No transaction reports found. Reports are generated upon transaction approval.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>



    <!-- User Creation Modal -->
    <div v-if="showUserModal" class="fixed inset-0 z-50 flex items-center justify-center bg-primary-950/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-3xl w-full max-w-md p-8 relative max-h-[90vh] overflow-y-auto">
        <button @click="showUserModal = false" class="absolute top-6 right-6 text-primary-400 hover:text-primary-950">
          <LucideX class="w-6 h-6" />
        </button>
        <h2 class="text-2xl font-bold text-primary-950 mb-6">Create Staff Account</h2>
        
        <form @submit.prevent="handleCreateUser" class="space-y-4">
          <div>
            <label class="block text-sm font-bold text-primary-950 mb-2">Full Name</label>
            <input v-model="userForm.full_name" type="text" required class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500" placeholder="John Doe" />
          </div>
          <div>
            <label class="block text-sm font-bold text-primary-950 mb-2">Email Address</label>
            <input v-model="userForm.email" type="email" required class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500" placeholder="john@agency.com" />
          </div>
          <div>
            <label class="block text-sm font-bold text-primary-950 mb-2">Temporary Password</label>
            <input v-model="userForm.password" type="text" required class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500" placeholder="Must be changed later" />
          </div>
          <div>
            <label class="block text-sm font-bold text-primary-950 mb-2">Role</label>
            <select v-model="userForm.role" required class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500">
              <option value="head_agent">Head Agent</option>
              <option value="agent">Sub-Agent</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
          <div v-if="userForm.role === 'agent'">
            <label class="block text-sm font-bold text-primary-950 mb-2">Assign to Head Agent</label>
            <select v-model="userForm.manager_id" required class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500">
              <option value="" disabled>Select a Head Agent...</option>
              <option v-for="manager in headAgents" :key="manager.id" :value="manager.id">{{ manager.full_name }}</option>
            </select>
          </div>
          <p v-if="userError" class="text-red-500 text-sm font-medium">{{ userError }}</p>
          <button type="submit" class="btn-primary w-full py-3" :disabled="loading">
            Create User Account
          </button>
        </form>
      </div>
    </div>

    <!-- Modals -->
    <PropertyUploadModal 
      v-if="showPropertyModal"
      :show="showPropertyModal" 
      :edit-data="selectedProperty"
      :read-only="true"
      @close="closePropertyModal" 
      @success="handlePropertySuccess"
    />

  </div>
</template>

<script setup>
import { 
  LucideShieldAlert, LucideUsers, LucideBuilding2, 
  LucideHome, LucidePlus, LucideX, LucideEye,
  LucideFileText, LucideDownload, LucidePieChart,
  LucideSearch, LucideFilter, LucideUserCheck, LucideMapPin,
  LucideCalendar, LucideTrendingUp
} from 'lucide-vue-next'

import { useAuthStore } from '~/stores/auth'
import { useAdminDashboard } from '~/composables/useAdminDashboard'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()

// Domain Composable Orchestration
const {
  users, properties, reports, statistics, visits,
  loading, statsLoading,
  userSearchQuery, userRoleFilter, userStatusFilter,
  propSearchQuery, propLocationQuery,
  filteredUsers, filteredProperties,
  userRolesChartData, topAgentsChartData, propertyStatusChartData,
  headAgents, closedDealsCount,
  fetchData, createUser, toggleUserStatus, downloadReport
} = useAdminDashboard()

// UI State
const activeTab = ref('users')

const showUserModal = ref(false)
const userError = ref('')
const userForm = ref({ 
  full_name: '', email: '', password: '', 
  role: 'head_agent', manager_id: '', phone_number: '' 
})

const showPropertyModal = ref(false)
const selectedProperty = ref(null)

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-TN').format(price || 0)
}

// UI Handlers
const handleCreateUser = async () => {
  userError.value = ''
  
  // Format payload
  const payload = { ...userForm.value }
  if (!payload.manager_id || payload.role !== 'agent') {
    payload.manager_id = null
  } else {
    payload.manager_id = parseInt(payload.manager_id)
  }

  try {
    await createUser(payload)
    showUserModal.value = false
    userForm.value = { full_name: '', email: '', password: '', role: 'head_agent', manager_id: '', phone_number: '' }
  } catch (e) {
    userError.value = e.message || "Failed to create user"
  }
}

const viewProperty = (property) => {
  selectedProperty.value = property
  showPropertyModal.value = true
}

const closePropertyModal = () => {
  showPropertyModal.value = false
  selectedProperty.value = null
}

const handlePropertySuccess = () => {
  closePropertyModal()
  fetchData()
}

onMounted(() => {
  // Wait for the auth store to finish loading the token from local storage
  watchEffect(() => {
    if (auth.isInitialized) {
      if (!auth.isAdmin) {
        navigateTo('/')
      } else {
        fetchData()
      }
    }
  })
})

useHead({
  title: 'Admin Dashboard | Elite Real Estate'
})
</script>
