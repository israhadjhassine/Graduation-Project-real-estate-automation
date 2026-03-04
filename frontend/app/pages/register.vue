<template>
  <div class="min-h-[80vh] flex items-center justify-center px-6 py-12">
    <div class="w-full max-w-md space-y-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-primary-950 mb-2">Join Elite</h1>
        <p class="text-primary-400 font-medium">Create your exclusive client account</p>
      </div>

      <div class="card-premium">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <div>
            <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Full Name</label>
            <div class="relative">
              <LucideUser class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
              <input 
                v-model="fullName"
                type="text" 
                required
                placeholder="John Doe"
                class="w-full bg-primary-50/50 border border-primary-100 rounded-2xl pl-12 pr-4 py-3 text-sm focus:ring-4 focus:ring-primary-500/5 focus:border-primary-500 outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Phone Number</label>
            <div class="relative">
              <LucidePhone class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
              <input 
                v-model="phoneNumber"
                type="tel" 
                required
                placeholder="+216 00 000 000"
                class="w-full bg-primary-50/50 border border-primary-100 rounded-2xl pl-12 pr-4 py-3 text-sm focus:ring-4 focus:ring-primary-500/5 focus:border-primary-500 outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Email Address</label>
            <div class="relative">
              <LucideMail class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
              <input 
                v-model="email"
                type="email" 
                required
                placeholder="name@example.com"
                class="w-full bg-primary-50/50 border border-primary-100 rounded-2xl pl-12 pr-4 py-3 text-sm focus:ring-4 focus:ring-primary-500/5 focus:border-primary-500 outline-none transition-all"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Password</label>
            <div class="relative">
              <LucideLock class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
              <input 
                v-model="password"
                type="password" 
                required
                placeholder="••••••••"
                class="w-full bg-primary-50/50 border border-primary-100 rounded-2xl pl-12 pr-4 py-3 text-sm focus:ring-4 focus:ring-primary-500/5 focus:border-primary-500 outline-none transition-all"
              />
            </div>
          </div>

          <div v-if="error" class="p-3 bg-red-50 border border-red-100 rounded-xl text-red-600 text-xs font-medium">
            {{ error }}
          </div>
          
          <div v-if="success" class="p-3 bg-green-50 border border-green-100 rounded-xl text-green-600 text-xs font-medium">
            Account created successfully! Redirecting to login...
          </div>

          <button 
            type="submit" 
            class="btn-primary w-full !rounded-2xl py-4 shadow-primary-700/30"
            :disabled="loading"
          >
            <LucideLoader2 v-if="loading" class="w-5 h-5 animate-spin" />
            <span v-else>Create Account</span>
          </button>
        </form>

        <div class="mt-8 pt-8 border-t border-primary-50 text-center">
          <p class="text-sm text-primary-400">
            Already have an account? 
            <NuxtLink to="/login" class="text-accent-600 font-bold hover:text-accent-700">Sign In</NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideUser, LucideMail, LucideLock, LucideLoader2, LucidePhone } from 'lucide-vue-next'
import axios from 'axios'

const email = ref('')
const fullName = ref('')
const phoneNumber = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  
  const config = useRuntimeConfig()
  let apiUrl = config.public.apiUrl
  if (process.client && apiUrl.includes('backend')) {
      apiUrl = 'http://localhost:8000'
  }

  try {
    await axios.post(`${apiUrl}/auth/register`, {
      email: email.value,
      full_name: fullName.value,
      phone_number: phoneNumber.value,
      password: password.value,
      role: 'client' // Explicitly sign up as client
    })
    
    success.value = true
    setTimeout(() => {
      navigateTo('/login')
    }, 2000)
    
  } catch (e) {
    if (e.response?.data?.detail) {
      error.value = e.response.data.detail
    } else {
      error.value = 'Failed to create account. Please try again.'
    }
  } finally {
    loading.value = false
  }
}

useHead({
  title: 'Join Elite | Registration'
})
</script>
