<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Admin Header -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-6">
          <div class="w-20 h-20 bg-gradient-to-br from-red-600 to-red-900 rounded-2xl flex items-center justify-center shadow-lg shadow-red-900/20 text-white">
            <LucideShieldAlert class="w-10 h-10" />
          </div>
          <div>
            <h1 class="text-3xl font-bold text-primary-950">System Administration</h1>
            <p class="text-primary-500 font-medium mt-1">Superuser Control Panel</p>
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="grid md:grid-cols-3 gap-6 mb-8">

        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <LucideUsers class="w-6 h-6 text-primary-600" />
            </div>
          </div>
          <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">Total Users</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">{{ users.length }}</p>
        </div>

        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <LucideUsers class="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <p class="text-xs font-bold text-purple-400 uppercase tracking-widest">Managers</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">{{ headAgents.length }}</p>
        </div>

        <div class="card-premium">
          <div class="flex items-center justify-between mb-4">
            <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <LucideHome class="w-6 h-6 text-green-600" />
            </div>
          </div>
          <p class="text-xs font-bold text-primary-400 uppercase tracking-widest">Total Listings</p>
          <p class="text-3xl font-bold text-primary-950 mt-1">{{ properties.length }}</p>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex gap-4 border-b border-primary-100 mb-8 overflow-x-auto pb-2">
        <button 
          @click="activeTab = 'users'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'users' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucideUsers class="w-4 h-4 inline-block mr-2" /> Manage Users
        </button>
        <button 
          @click="activeTab = 'properties'" 
          :class="['px-6 py-3 rounded-full text-sm font-bold transition-all whitespace-nowrap', activeTab === 'properties' ? 'bg-primary-950 text-white shadow-md' : 'text-primary-600 hover:bg-primary-100']"
        >
          <LucideHome class="w-4 h-4 inline-block mr-2" /> All Properties
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
              <tr v-for="user in users" :key="user.id" class="hover:bg-primary-50/50">
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
                    {{ user.role }}
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

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
           <div v-for="prop in properties" :key="prop.id" class="relative group">
             <PropertyCard :property="prop" @click="editProperty(prop)" />
             <div class="absolute inset-x-0 bottom-0 p-4 translate-y-2 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all flex gap-2">

                <button 
                  @click.stop="editProperty(prop)"
                  class="flex-1 bg-white/90 backdrop-blur-md py-2 px-3 rounded-xl text-xs font-bold text-primary-950 hover:bg-white flex items-center justify-center gap-2 shadow-xl"
                >
                  <LucideEdit class="w-3.5 h-3.5" /> Edit Details
                </button>
                <button 
                  @click.stop="deleteProperty(prop.id)"
                  class="bg-red-500/90 backdrop-blur-md p-2 rounded-xl text-white hover:bg-red-500 shadow-xl"
                >
                  <LucideTrash2 class="w-3.5 h-3.5" />
                </button>
             </div>
           </div>
           <div v-if="!properties.length" class="col-span-full text-center py-12 text-primary-400">
             No properties listed yet.
           </div>
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
        
        <form @submit.prevent="createUser" class="space-y-4">
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
              <option value="head_agent">Head Agent (Manager)</option>
              <option value="agent">Sub-Agent</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
          <div v-if="userForm.role === 'agent'">
            <label class="block text-sm font-bold text-primary-950 mb-2">Assign to Head Agent (Manager)</label>
            <select v-model="userForm.manager_id" required class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500">
              <option value="" disabled>Select a Manager...</option>
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
      @close="closePropertyModal" 
      @success="handlePropertySuccess"
    />

  </div>
</template>

<script setup>
import { 
  LucideShieldAlert, LucideUsers, LucideBuilding2, 
  LucideHome, LucidePlus, LucideX, LucideTrash2,
  LucideEdit
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import axios from 'axios'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const activeTab = ref('users')
const loading = ref(false)

const users = ref([])
const properties = ref([])
const headAgents = computed(() => users.value.filter(u => u.role === 'head_agent'))

const showUserModal = ref(false)
const userError = ref('')

const userForm = ref({ 
  full_name: '', email: '', password: '', 
  role: 'head_agent', manager_id: '', phone_number: '' 
})

const showPropertyModal = ref(false)
const selectedProperty = ref(null)

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
    const [usersRes, propsRes] = await Promise.all([
      axios.get(`${getApiUrl()}/admin/users`, { headers: { Authorization: `Bearer ${auth.token}` } }),
      axios.get(`${getApiUrl()}/admin/properties`, { headers: { Authorization: `Bearer ${auth.token}` } })
    ])
    users.value = usersRes.data
    properties.value = propsRes.data
  } catch (e) {
    console.error("Failed to load admin data", e)
  }
}

const createUser = async () => {
  loading.value = true
  userError.value = ''

  // Format payload
  const payload = { ...userForm.value }
  if (!payload.manager_id || payload.role !== 'agent') {
    payload.manager_id = null
  } else {
    payload.manager_id = parseInt(payload.manager_id)
  }

  try {
    await axios.post(`${getApiUrl()}/admin/users`, payload, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    showUserModal.value = false
    userForm.value = { full_name: '', email: '', password: '', role: 'head_agent', manager_id: '', phone_number: '' }
    fetchData()
  } catch (e) {
    userError.value = e.response?.data?.detail || "Failed to create user"
  } finally {
    loading.value = false
  }
}
const toggleUserStatus = async (userId) => {
  try {
    await axios.patch(`${getApiUrl()}/admin/users/${userId}/toggle-status`, {}, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    fetchData()
  } catch (e) {
    console.error("Failed to toggle user status", e)
    alert(e.response?.data?.detail || "Failed to update account status")
  }
}

const editProperty = (property) => {
  selectedProperty.value = property
  showPropertyModal.value = true
}

const deleteProperty = async (propertyId) => {
  if (!confirm("Delete this property?")) return
  
  try {
    await axios.delete(`${getApiUrl()}/properties/${propertyId}`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    fetchData()
  } catch (e) {
    console.error("Failed to delete property", e)
  }
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
