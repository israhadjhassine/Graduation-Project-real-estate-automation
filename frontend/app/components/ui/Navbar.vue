<template>
  <nav class="fixed top-0 left-0 right-0 z-50 flex justify-center p-6">
    <div class="w-full max-w-7xl bg-white/70 backdrop-blur-xl border border-white/40 rounded-full px-8 py-4 flex items-center justify-between shadow-2xl shadow-primary-900/5">
      <NuxtLink to="/" class="flex items-center gap-2 group">
        <div class="w-10 h-10 bg-primary-700 rounded-xl flex items-center justify-center transform group-hover:rotate-12 transition-transform duration-300">
          <LucideHome class="text-white w-6 h-6" />
        </div>
        <span class="text-2xl font-bold tracking-tight text-primary-950">Elite<span class="text-accent-500 font-serif italic font-normal">Estate</span></span>
      </NuxtLink>

      <div class="hidden md:flex items-center gap-8 text-sm font-medium text-primary-900/70">
        <NuxtLink to="/properties" class="hover:text-primary-950 transition-colors">Properties</NuxtLink>
        <NuxtLink to="/about" class="hover:text-primary-950 transition-colors">About Us</NuxtLink>
        <NuxtLink to="/contact" class="hover:text-primary-950 transition-colors">Contact</NuxtLink>
      </div>

      <div class="flex items-center gap-4">
        <template v-if="auth.isAuthenticated">
          <div class="flex items-center gap-3 pr-4 border-r border-primary-100">
            <div class="text-right">
              <p class="text-xs font-bold text-primary-950">{{ auth.user?.full_name }}</p>
              <p class="text-[10px] text-primary-500 uppercase tracking-widest font-bold">{{ auth.user?.role }}</p>
            </div>
            <div class="w-10 h-10 bg-accent-100 rounded-full flex items-center justify-center border-2 border-white shadow-sm">
              <LucideUser class="text-accent-600 w-5 h-5" />
            </div>
          </div>
          <button @click="auth.logout" class="text-primary-400 hover:text-red-500 transition-colors">
            <LucideLogOut class="w-5 h-5" />
          </button>
        </template>
        <template v-else>
          <NuxtLink to="/login" class="text-primary-900 font-medium hover:text-primary-700 transition-colors">Sign In</NuxtLink>
          <NuxtLink to="/register" class="btn-primary !px-5 !py-2.5 !text-sm">Join Elite</NuxtLink>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth'
import { LucideHome, LucideUser, LucideLogOut } from 'lucide-vue-next'

const auth = useAuthStore()
</script>
