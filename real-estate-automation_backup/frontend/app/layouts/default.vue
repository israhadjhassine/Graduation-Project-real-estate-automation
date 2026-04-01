<template>
  <div class="min-h-screen bg-primary-50 selection:bg-accent-200 selection:text-accent-950">
    <UiNavbar />
    <main class="pt-24 min-h-screen">
      <slot />
    </main>
    
    <footer class="bg-primary-950 py-16 px-6 text-white mt-20">
      <div class="max-w-7xl mx-auto grid md:grid-cols-4 gap-12">
        <div class="col-span-2">
          <div class="flex items-center gap-2 mb-6">
             <div class="w-10 h-10 bg-primary-700 rounded-xl flex items-center justify-center">
                <LucideHome class="text-white w-6 h-6" />
              </div>
              <span class="text-2xl font-bold tracking-tight text-white">Elite<span class="text-accent-400 font-serif italic font-normal">Estate</span></span>
          </div>
          <p class="text-primary-300 max-w-sm">
            Revolutionizing real estate through artificial intelligence. Search smarter, find your home faster, and experience a new standard of luxury automation.
          </p>
        </div>
        <div>
          <h4 class="font-bold mb-6 text-white uppercase tracking-widest text-xs">Resources</h4>
          <ul class="space-y-4 text-primary-400 text-sm">
            <li><NuxtLink to="/properties" class="hover:text-white transition-colors">Listings</NuxtLink></li>
            <li><NuxtLink to="/about" class="hover:text-white transition-colors">Our Story</NuxtLink></li>
         </ul>
        </div>
        <div>
          <h4 class="font-bold mb-6 text-white uppercase tracking-widest text-xs">Connect</h4>
          <ul class="space-y-4 text-primary-400 text-sm">
            <li class="flex items-center gap-2 font-mono italic">@elite.estate.luxury</li>
            <li class="flex items-center gap-2">contact@elite.tn</li>
          </ul>
        </div>
      </div>
      <div class="max-w-7xl mx-auto mt-16 pt-8 border-t border-white/10 flex justify-between items-center text-[10px] text-white/30 uppercase tracking-[0.2em] font-bold">
        <span>&copy; 2026 Elite Estate Automation. All Rights Reserved.</span>
      
      </div>
    </footer>
  </div>
</template>

<script setup>
import { LucideHome } from 'lucide-vue-next'
</script>
