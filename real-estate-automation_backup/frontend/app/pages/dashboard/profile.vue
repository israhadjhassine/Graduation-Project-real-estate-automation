<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-4xl mx-auto px-6">
      <div class="flex items-center gap-6 mb-8">
        <div class="w-20 h-20 bg-primary-950 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-primary-900/20">
          <LucideUser class="w-10 h-10" />
        </div>
        <div>
          <h1 class="text-3xl font-bold text-primary-950">Staff Profile</h1>
          <p class="text-primary-500 font-medium">Manage your account and security settings</p>
        </div>
      </div>

      <div class="grid md:grid-cols-3 gap-8">
        <!-- Sidebar -->
        <div class="space-y-2">
          <button 
            @click="activeTab = 'personal'" 
            :class="['w-full text-left px-6 py-3 rounded-xl text-sm font-bold transition-all', activeTab === 'personal' ? 'bg-primary-950 text-white shadow-lg shadow-primary-900/20' : 'text-primary-600 hover:bg-primary-100']"
          >
            Personal Info
          </button>
          <button 
            @click="activeTab = 'security'" 
            :class="['w-full text-left px-6 py-3 rounded-xl text-sm font-bold transition-all', activeTab === 'security' ? 'bg-primary-950 text-white shadow-lg shadow-primary-900/20' : 'text-primary-600 hover:bg-primary-100']"
          >
            Security
          </button>
        </div>

        <!-- Main Content -->
        <div class="md:col-span-2">
          <div v-if="activeTab === 'personal'" class="card-premium space-y-6">
            <h2 class="text-xl font-bold text-primary-950">Personal Information</h2>
            
            <form @submit.prevent="updateProfile" class="space-y-4">
              <div>
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Full Name</label>
                <input v-model="profileForm.full_name" type="text" class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm focus:border-accent-500 outline-none" />
              </div>
              <div>
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Email Address</label>
                <input v-model="profileForm.email" type="email" class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm focus:border-accent-500 outline-none" />
              </div>
              <div>
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Phone Number</label>
                <input v-model="profileForm.phone_number" type="tel" class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm focus:border-accent-500 outline-none" />
              </div>
              
              <div v-if="message" :class="['p-3 rounded-xl text-xs font-medium', isError ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600']">
                {{ message }}
              </div>

              <button type="submit" class="btn-primary w-full py-3" :disabled="loading">
                <LucideLoader2 v-if="loading" class="w-4 h-4 animate-spin mr-2" />
                Save Changes
              </button>
            </form>
          </div>

          <div v-if="activeTab === 'security'" class="card-premium space-y-6">
            <h2 class="text-xl font-bold text-primary-950">Security Settings</h2>
            
            <form @submit.prevent="updatePassword" class="space-y-4">
              <div>
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Current Password</label>
                <input v-model="passForm.current_password" type="password" required class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm focus:border-accent-500 outline-none" />
              </div>
              <div>
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">New Password</label>
                <input v-model="passForm.new_password" type="password" required class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm focus:border-accent-500 outline-none" />
              </div>
              <div>
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Confirm New Password</label>
                <input v-model="passForm.confirm_password" type="password" required class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm focus:border-accent-500 outline-none" />
              </div>
              
              <div v-if="message" :class="['p-3 rounded-xl text-xs font-medium', isError ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600']">
                {{ message }}
              </div>

              <button type="submit" class="btn-primary w-full py-3" :disabled="loading">
                <LucideLoader2 v-if="loading" class="w-4 h-4 animate-spin mr-2" />
                Update Password
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideUser, LucideLoader2 } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import axios from 'axios'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const activeTab = ref('personal')
const loading = ref(false)
const message = ref('')
const isError = ref(false)

const profileForm = ref({
  full_name: auth.user?.full_name || '',
  email: auth.user?.email || '',
  phone_number: auth.user?.phone_number || ''
})

const passForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const config = useRuntimeConfig()
const getApiUrl = () => {
    let url = config.public.apiUrl
    if (process.client && url.includes('backend')) {
        url = 'http://localhost:8000'
    }
    return url
}

const updateProfile = async () => {
  loading.value = true
  message.value = ''
  isError.value = false
  
  try {
    const res = await axios.put(`${getApiUrl()}/auth/profile`, profileForm.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    auth.user = res.data
    message.value = 'Profile updated successfully!'
  } catch (e) {
    isError.value = true
    message.value = e.response?.data?.detail || 'Failed to update profile'
  } finally {
    loading.value = false
  }
}

const updatePassword = async () => {
  if (passForm.value.new_password !== passForm.value.confirm_password) {
    isError.value = true
    message.value = 'Passwords do not match'
    return
  }

  loading.value = true
  message.value = ''
  isError.value = false
  
  try {
    await axios.put(`${getApiUrl()}/auth/password`, {
      current_password: passForm.value.current_password,
      new_password: passForm.value.new_password
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    message.value = 'Password updated successfully!'
    passForm.value = { current_password: '', new_password: '', confirm_password: '' }
  } catch (e) {
    isError.value = true
    message.value = e.response?.data?.detail || 'Failed to update password'
  } finally {
    loading.value = false
  }
}
</script>
