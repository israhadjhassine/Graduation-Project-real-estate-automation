<template>
  <nav class="fixed top-0 left-0 right-0 z-[9999] flex justify-center p-6 transition-all duration-300">
    <div class="w-full max-w-7xl bg-white/80 backdrop-blur-xl border border-white/60 rounded-full px-8 py-3.5 flex items-center justify-between shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-shadow">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-3 group">
        <div class="w-11 h-11 bg-gradient-to-br from-primary-800 to-primary-950 rounded-[14px] flex items-center justify-center transform group-hover:rotate-12 transition-transform duration-300 shadow-lg shadow-primary-900/20">
          <LucideBuilding2 class="text-white w-5 h-5" stroke-width="2.5" />
        </div>
        <span class="text-2xl font-bold tracking-tight text-primary-950">Elite<span class="text-accent-500 font-serif italic font-normal">Estate</span></span>
      </NuxtLink>

      <!-- Navigation Links -->
      <div class="hidden md:flex items-center gap-2 bg-primary-50/50 p-1.5 rounded-full border border-primary-100/50">
        <NuxtLink to="/properties" class="flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-bold text-primary-600 hover:text-primary-950 hover:bg-white transition-all">
          <LucideSearch class="w-4 h-4" /> Properties
        </NuxtLink>
        <NuxtLink to="/about" class="flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-bold text-primary-600 hover:text-primary-950 hover:bg-white transition-all">
          <LucideInfo class="w-4 h-4" /> About Us
        </NuxtLink>
        <NuxtLink to="/contact" class="flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-bold text-primary-600 hover:text-primary-950 hover:bg-white transition-all">
          <LucidePhone class="w-4 h-4" /> Contact
        </NuxtLink>
      </div>

      <div class="flex items-center gap-4">
        <template v-if="auth.isAuthenticated">
          <NuxtLink :to="profileLink" class="flex items-center gap-4 pr-5 border-r border-primary-100 hover:opacity-80 transition-opacity cursor-pointer">
            <div class="text-right">
              <p class="text-sm font-bold text-primary-950 leading-none mb-1">{{ auth.user?.full_name }}</p>
              <p class="text-[10px] text-accent-600 uppercase tracking-[0.2em] font-bold leading-none">{{ auth.user?.role }}</p>
            </div>
            <div class="w-10 h-10 bg-primary-50 rounded-full flex items-center justify-center border border-primary-100 shadow-inner group-hover:bg-primary-100 transition-colors">
               <LucideUser class="text-primary-600 w-5 h-5" />
            </div>
          </NuxtLink>
          <button @click="auth.logout" class="w-10 h-10 flex items-center justify-center text-primary-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-all">
            <LucideLogOut class="w-5 h-5" />
          </button>
        </template>
        <template v-else>
          <NuxtLink to="/login" class="text-sm font-bold text-primary-600 hover:text-primary-950 transition-colors px-2">Sign In</NuxtLink>
          <NuxtLink to="/register" class="bg-primary-950 hover:bg-primary-900 text-white px-6 py-2.5 rounded-full text-sm font-bold transition-all shadow-lg shadow-primary-900/20 transform hover:-translate-y-0.5">
            Join Elite
          </NuxtLink>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth'
import { 
  LucideBuilding2, LucideSearch, LucideInfo, 
  LucidePhone, LucideUser, LucideLogOut 
} from 'lucide-vue-next'

const auth = useAuthStore()

const profileLink = computed(() => {
  if (auth.isAdmin || auth.isHeadAgent || auth.isAgent) {
    return '/dashboard/profile'
  }
  return '/profile'
})
</script>
