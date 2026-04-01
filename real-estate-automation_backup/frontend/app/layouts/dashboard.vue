<template>
  <div class="min-h-screen bg-primary-50 selection:bg-accent-200 selection:text-accent-950">
    
    <!-- Simple Top Bar for Dashboards to allow logout/navigation back home -->
    <nav class="bg-white border-b border-primary-100 flex items-center justify-between px-6 py-4">
      <NuxtLink :to="auth.authenticatedHomeLink" class="flex items-center gap-2">
         <div class="w-8 h-8 bg-primary-950 rounded-lg flex items-center justify-center">
            <LucideHome class="text-white w-4 h-4" />
          </div>
          <span class="text-xl font-bold tracking-tight text-primary-950">Elite<span class="text-accent-600 font-serif italic font-normal">Estate</span></span>
      </NuxtLink>

      <div class="flex items-center gap-4">
        <NuxtLink to="/dashboard/profile" class="text-sm font-bold text-primary-500 hover:text-primary-950 transition-colors">My Profile</NuxtLink>
        <button @click="auth.logout()" class="text-sm font-bold text-red-500 hover:text-red-700 transition-colors bg-red-50 hover:bg-red-100 px-4 py-2 rounded-lg">
          Sign Out
        </button>
      </div>
    </nav>

    <main class="min-h-screen">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { LucideHome } from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
</script>
