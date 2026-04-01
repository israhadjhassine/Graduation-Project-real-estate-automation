<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-4xl mx-auto px-6">
      <!-- Profile Header -->
      <div class="flex items-center gap-6 mb-8">
        <div class="w-20 h-20 bg-gradient-to-br from-primary-800 to-primary-950 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-900/20 text-white text-2xl font-bold">
          {{ userInitials }}
        </div>
        <div>
          <h1 class="text-3xl font-bold text-primary-950">{{ auth.user?.full_name }}</h1>
          <p class="text-primary-500 font-medium capitalize mt-1">{{ auth.user?.role }} Account</p>
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div class="flex border-b border-primary-100 mb-8">
        <button 
          @click="activeTab = 'personal'"
          :class="['px-6 py-3 text-sm font-bold transition-all border-b-2', activeTab === 'personal' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideUser class="w-4 h-4 inline-block mr-2" /> Personal Information
        </button>
        <button 
          @click="activeTab = 'security'"
          :class="['px-6 py-3 text-sm font-bold transition-all border-b-2', activeTab === 'security' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideLock class="w-4 h-4 inline-block mr-2" /> Security Settings
        </button>
      </div>

      <!-- Tab Content: Personal Information -->
      <div v-show="activeTab === 'personal'" class="card-premium">
        <h2 class="text-xl font-bold text-primary-950 mb-6">Update Profile</h2>
        <form @submit.prevent="updateProfile" class="space-y-6">
          <div class="grid md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <label class="text-xs font-bold text-primary-400 uppercase tracking-widest">Full Name</label>
              <div class="relative">
                <LucideUser class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
                <input v-model="profileForm.full_name" type="text" class="w-full bg-primary-50 border border-primary-100 rounded-xl pl-12 pr-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" />
              </div>
            </div>
            
            <div class="space-y-2">
              <label class="text-xs font-bold text-primary-400 uppercase tracking-widest">Email Address</label>
              <div class="relative">
                <LucideMail class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
                <input v-model="profileForm.email" type="email" class="w-full bg-primary-50 border border-primary-100 rounded-xl pl-12 pr-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" />
              </div>
            </div>
          </div>

          <div class="space-y-2 md:w-1/2 pr-3">
            <label class="text-xs font-bold text-primary-400 uppercase tracking-widest">Phone Number</label>
            <div class="relative">
              <LucidePhone class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
              <input v-model="profileForm.phone_number" type="tel" placeholder="+216 00 000 000" class="w-full bg-primary-50 border border-primary-100 rounded-xl pl-12 pr-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" />
            </div>
          </div>

          <div v-if="profileMessage" :class="['p-3 rounded-xl text-xs font-medium border', profileSuccess ? 'bg-green-50 border-green-100 text-green-600' : 'bg-red-50 border-red-100 text-red-600']">
            {{ profileMessage }}
          </div>

          <div class="flex justify-end pt-4 border-t border-primary-50">
            <button type="submit" class="bg-primary-950 hover:bg-primary-900 text-white px-8 py-3 rounded-xl text-sm font-bold transition-all shadow-lg shadow-primary-900/20 flex items-center gap-2" :disabled="profileLoading">
              <LucideLoader2 v-if="profileLoading" class="w-4 h-4 animate-spin" />
              <LucideSave v-else class="w-4 h-4" /> Save Changes
            </button>
          </div>
        </form>
      </div>

      <!-- Tab Content: Security Settings -->
      <div v-show="activeTab === 'security'" class="card-premium">
        <h2 class="text-xl font-bold text-primary-950 mb-2">Change Password</h2>
        <p class="text-primary-500 text-sm mb-6">Ensure your account is using a long, random password to stay secure.</p>
        
        <form @submit.prevent="updatePassword" class="space-y-6 md:w-2/3">
          <div class="space-y-2">
            <label class="text-xs font-bold text-primary-400 uppercase tracking-widest">Current Password</label>
            <div class="relative">
              <LucideKey class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
              <input v-model="passwordForm.current" type="password" required class="w-full bg-primary-50 border border-primary-100 rounded-xl pl-12 pr-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" />
            </div>
          </div>
          
          <div class="grid md:grid-cols-2 gap-6 pt-4">
            <div class="space-y-2">
              <label class="text-xs font-bold text-primary-400 uppercase tracking-widest">New Password</label>
              <div class="relative">
                <LucideLock class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
                <input v-model="passwordForm.new" type="password" required class="w-full bg-primary-50 border border-primary-100 rounded-xl pl-12 pr-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" />
              </div>
            </div>
            
            <div class="space-y-2">
              <label class="text-xs font-bold text-primary-400 uppercase tracking-widest">Confirm New</label>
              <div class="relative">
                <LucideLock class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
                <input v-model="passwordForm.confirm" type="password" required class="w-full bg-primary-50 border border-primary-100 rounded-xl pl-12 pr-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" />
              </div>
            </div>
          </div>

          <div v-if="passwordMessage" :class="['p-3 rounded-xl text-xs font-medium border', passwordSuccess ? 'bg-green-50 border-green-100 text-green-600' : 'bg-red-50 border-red-100 text-red-600']">
            {{ passwordMessage }}
          </div>

          <div class="flex justify-start pt-4 border-t border-primary-50">
            <button type="submit" class="bg-primary-950 hover:bg-primary-900 text-white px-8 py-3 rounded-xl text-sm font-bold transition-all shadow-lg shadow-primary-900/20 flex items-center gap-2" :disabled="passwordLoading">
              <LucideLoader2 v-if="passwordLoading" class="w-4 h-4 animate-spin" />
              <LucideShieldCheck v-else class="w-4 h-4" /> Update Password
            </button>
          </div>
        </form>
      </div>

    </div>
  </div>
</template>

<script setup>
import { 
  LucideUser, LucideLock, LucideMail, LucidePhone,
  LucideSave, LucideLoader2, LucideKey, LucideShieldCheck
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import axios from 'axios'

const auth = useAuthStore()
const activeTab = ref('personal')

// Ensure user is authenticated, otherwise redirect
onMounted(() => {
  if (!auth.isAuthenticated) {
    navigateTo('/login')
  }
})

const userInitials = computed(() => {
  if (!auth.user?.full_name) return '?'
  return auth.user.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
})

// Profile Form State
const profileForm = ref({
  full_name: auth.user?.full_name || '',
  email: auth.user?.email || '',
  phone_number: auth.user?.phone_number || ''
})
const profileLoading = ref(false)
const profileMessage = ref('')
const profileSuccess = ref(false)

// Password Form State
const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})
const passwordLoading = ref(false)
const passwordMessage = ref('')
const passwordSuccess = ref(false)

// Config
const config = useRuntimeConfig()
const getApiUrl = () => {
    let url = config.public.apiUrl
    if (process.client && url.includes('backend')) {
        url = 'http://localhost:8000'
    }
    return url
}

// Handlers
const updateProfile = async () => {
  profileLoading.value = true
  profileMessage.value = ''
  
  try {
    const res = await axios.put(`${getApiUrl()}/auth/profile`, profileForm.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    
    // Update local store with new data
    auth.user = res.data
    profileSuccess.value = true
    profileMessage.value = "Profile updated successfully!"
    setTimeout(() => profileMessage.value = '', 3000)
    
  } catch (err) {
    profileSuccess.value = false
    profileMessage.value = err.response?.data?.detail || "Failed to update profile."
  } finally {
    profileLoading.value = false
  }
}

const updatePassword = async () => {
  if (passwordForm.value.new !== passwordForm.value.confirm) {
    passwordSuccess.value = false
    passwordMessage.value = "New passwords do not match."
    return
  }
  
  passwordLoading.value = true
  passwordMessage.value = ''
  
  try {
    await axios.put(`${getApiUrl()}/auth/password`, {
      current_password: passwordForm.value.current,
      new_password: passwordForm.value.new
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    
    passwordSuccess.value = true
    passwordMessage.value = "Password updated securely!"
    passwordForm.value = { current: '', new: '', confirm: '' }
    setTimeout(() => passwordMessage.value = '', 3000)
    
  } catch (err) {
    passwordSuccess.value = false
    passwordMessage.value = err.response?.data?.detail || "Failed to update password."
  } finally {
    passwordLoading.value = false
  }
}

useHead({
  title: 'My Profile | Elite Real Estate'
})
</script>
