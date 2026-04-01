<template>
  <div class="min-h-[80vh] flex items-center justify-center px-6">
    <div class="w-full max-w-md space-y-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-primary-950 mb-2">Welcome Back</h1>
        <p class="text-primary-400 font-medium">Access your elite real estate dashboard</p>
      </div>

      <div class="card-premium">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Email Address</label>
            <div class="relative">
              <LucideMail class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-300" />
              <input 
                v-model="email"
                type="email" 
                required
                placeholder="name@company.com"
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

          <button 
            type="submit" 
            class="btn-primary w-full !rounded-2xl py-4 shadow-primary-700/30"
            :disabled="loading"
          >
            <LucideLoader2 v-if="loading" class="w-5 h-5 animate-spin" />
            <span v-else>Sign In</span>
          </button>
        </form>

        <div class="mt-8 pt-8 border-t border-primary-50 text-center">
          <p class="text-sm text-primary-400">
            Don't have an account? 
            <NuxtLink to="/register" class="text-accent-600 font-bold hover:text-accent-700">Join Elite</NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideMail, LucideLock, LucideLoader2 } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    await auth.login(email.value, password.value)
    
    // Redirect based on role
    if (auth.isAdmin) {
      navigateTo('/admin')
    } else if (auth.isHeadAgent) {
      navigateTo('/agency')
    } else if (auth.isAgent) {
      navigateTo('/agent')
    } else {
      navigateTo('/')
    }
    
  } catch (e) {
    error.value = 'Invalid email or password. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
