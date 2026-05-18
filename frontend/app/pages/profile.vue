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
          @click="activeTab = 'telegram'"
          :class="['px-6 py-3 text-sm font-bold transition-all border-b-2', activeTab === 'telegram' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideSend class="w-4 h-4 inline-block mr-2" /> Telegram Integration
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

      <!-- Tab Content: Telegram Integration -->
      <div v-show="activeTab === 'telegram'" class="card-premium">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-bold text-primary-950">Telegram Integration</h2>
            <p class="text-primary-500 text-sm mt-1">Connect your account with Telegram to easily inquire and manage visits with our AI Assistant.</p>
          </div>
          <div class="p-3 bg-[#0088cc]/10 rounded-2xl">
            <LucideSend class="w-8 h-8 text-[#0088cc]" />
          </div>
        </div>

        <!-- Case 1: Already Connected -->
        <div v-if="auth.user?.telegram_chat_id" class="space-y-6">
          <div class="p-6 bg-green-50/55 border border-green-100 rounded-2xl flex items-start gap-4">
            <div class="p-2 bg-green-600 text-white rounded-xl">
              <LucideShieldCheck class="w-5 h-5" />
            </div>
            <div>
              <h3 class="font-bold text-green-800 text-base">Linked Successfully</h3>
              <p class="text-green-600 text-sm mt-1">Your account is connected to Telegram.</p>
              <div class="mt-4 inline-flex items-center gap-2 px-3 py-1.5 bg-white border border-green-200 rounded-xl text-xs font-bold text-green-700">
                <span>Chat ID:</span>
                <span class="font-mono text-green-800">{{ auth.user.telegram_chat_id }}</span>
              </div>
            </div>
          </div>

          <div v-if="telegramMessage" :class="['p-3 rounded-xl text-xs font-medium border', telegramSuccess ? 'bg-green-50 border-green-100 text-green-600' : 'bg-red-50 border-red-100 text-red-600']">
            {{ telegramMessage }}
          </div>

          <div class="flex justify-end pt-4 border-t border-primary-50">
            <button 
              @click="disconnectTelegram" 
              class="bg-red-50 hover:bg-red-100 text-red-600 border border-red-100 px-6 py-3 rounded-xl text-sm font-bold transition-all flex items-center gap-2"
              :disabled="telegramLoading"
              type="button"
            >
              <LucideLoader2 v-if="telegramLoading" class="w-4 h-4 animate-spin" />
              <LucideTrash2 v-else class="w-4 h-4" /> Disconnect Telegram
            </button>
          </div>
        </div>

        <!-- Case 2: Not Connected -->
        <div v-else class="space-y-6">
          <div class="p-6 bg-primary-50/40 border border-primary-100 rounded-2xl">
            <h3 class="font-bold text-primary-950 mb-4 flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-primary-950 text-white text-xs flex items-center justify-center font-bold">1</span>
              How to Link your Account:
            </h3>
            <ul class="space-y-3 text-sm text-primary-600 ml-8 list-decimal font-medium">
              <li>Click the <strong>"Generate Pairing Code"</strong> button below.</li>
              <li>You will receive a temporary 6-digit numeric pairing token.</li>
              <li>Click the <strong>"Open Telegram Chat"</strong> button or launch the bot <a href="https://t.me/Pfe_rea_bot" target="_blank" class="text-accent-500 hover:underline font-bold">@Pfe_rea_bot</a> on Telegram.</li>
              <li>Press <strong>Start</strong> or send the pairing command sent automatically via deep-link.</li>
            </ul>
          </div>

          <!-- Generation Action -->
          <div v-if="!pairingCode" class="flex flex-col items-center justify-center py-8">
            <button 
              @click="generatePairingCode" 
              class="bg-primary-950 hover:bg-primary-900 text-white px-8 py-3.5 rounded-xl text-sm font-bold transition-all shadow-lg shadow-primary-900/20 flex items-center gap-2"
              :disabled="telegramLoading"
              type="button"
            >
              <LucideLoader2 v-if="telegramLoading" class="w-4 h-4 animate-spin" />
              <LucideKey v-else class="w-4 h-4" /> Generate Pairing Code
            </button>
            <p v-if="telegramMessage" :class="['mt-4 p-3 rounded-xl text-xs font-medium border', telegramSuccess ? 'bg-green-50 border-green-100 text-green-600' : 'bg-red-50 border-red-100 text-red-600']">
              {{ telegramMessage }}
            </p>
          </div>

          <!-- Code Generated Card -->
          <div v-else class="p-6 border border-accent-100 bg-accent-50/20 rounded-2xl text-center space-y-6 max-w-md mx-auto">
            <div class="space-y-2">
              <label class="text-xs font-bold text-primary-400 uppercase tracking-widest block">Your Pairing Code</label>
              <div class="text-4xl font-extrabold text-primary-950 tracking-wider font-mono bg-white border border-accent-100 py-4 px-6 rounded-2xl shadow-inner inline-block">
                {{ formatCode(pairingCode) }}
              </div>
            </div>

            <!-- Countdown Timer -->
            <div class="flex items-center justify-center gap-2 text-xs font-bold text-primary-500">
              <LucideClock class="w-4 h-4 text-accent-500 animate-pulse" />
              <span>Code expires in <span class="text-accent-600 font-mono">{{ formatTime(countdown) }}</span></span>
            </div>

            <!-- Direct deep-link redirect button -->
            <a 
              :href="`https://t.me/Pfe_rea_bot?start=pair_${pairingCode}`" 
              target="_blank" 
              class="bg-[#0088cc] hover:bg-[#0077b5] text-white w-full py-4 rounded-xl text-sm font-bold transition-all shadow-lg shadow-[#0088cc]/20 flex items-center justify-center gap-2 cursor-pointer text-decoration-none"
            >
              <LucideSend class="w-4 h-4" /> Open Telegram Chat
            </a>

            <button 
              @click="pairingCode = ''; countdown = 0" 
              class="text-xs text-primary-400 hover:text-primary-600 font-bold transition-all"
              type="button"
            >
              Cancel & Reset
            </button>
          </div>
        </div>
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
  LucideSave, LucideLoader2, LucideKey, LucideShieldCheck,
  LucideSend, LucideClock, LucideTrash2
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import axios from 'axios'

const auth = useAuthStore()
const activeTab = ref('personal')
const route = useRoute()

// Ensure user is authenticated, otherwise redirect
onMounted(() => {
  if (!auth.isAuthenticated) {
    navigateTo('/login')
    return
  }
  
  if (route.query.tab === 'telegram' || route.query.tab === 'security') {
    activeTab.value = route.query.tab
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

// Telegram State
const telegramLoading = ref(false)
const telegramMessage = ref('')
const telegramSuccess = ref(false)
const pairingCode = ref('')
const countdown = ref(0)
let timerId = null

// Disconnect Telegram Handler
const disconnectTelegram = async () => {
  telegramLoading.value = true
  telegramMessage.value = ''
  try {
    await axios.post(`${getApiUrl()}/auth/telegram/disconnect`, {}, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    auth.user.telegram_chat_id = null
    telegramSuccess.value = true
    telegramMessage.value = "Telegram unlinked successfully!"
    pairingCode.value = ''
    countdown.value = 0
    if (timerId) clearInterval(timerId)
    setTimeout(() => telegramMessage.value = '', 3000)
  } catch (err) {
    telegramSuccess.value = false
    telegramMessage.value = err.response?.data?.detail || "Failed to disconnect Telegram."
  } finally {
    telegramLoading.value = false
  }
}

// Generate Code Handler
const generatePairingCode = async () => {
  telegramLoading.value = true
  telegramMessage.value = ''
  pairingCode.value = ''
  
  try {
    const res = await axios.post(`${getApiUrl()}/auth/telegram/generate-code`, {}, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    
    pairingCode.value = res.data.code
    countdown.value = res.data.expires_in_seconds || 600
    
    if (timerId) clearInterval(timerId)
    timerId = setInterval(() => {
      if (countdown.value > 0) {
        countdown.value--
      } else {
        clearInterval(timerId)
        pairingCode.value = ''
      }
    }, 1000)
    
  } catch (err) {
    telegramSuccess.value = false
    telegramMessage.value = err.response?.data?.detail || "Failed to generate pairing code."
  } finally {
    telegramLoading.value = false
  }
}

// Format Countdown Timer
const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s < 10 ? '0' : ''}${s}`
}

// Format Pairing Code (adds a space in the middle for readability like: 123 456)
const formatCode = (code) => {
  if (!code || code.length !== 6) return code
  return `${code.slice(0, 3)} ${code.slice(3)}`
}

onBeforeUnmount(() => {
  if (timerId) clearInterval(timerId)
})

useHead({
  title: 'My Profile | Elite Real Estate'
})
</script>
