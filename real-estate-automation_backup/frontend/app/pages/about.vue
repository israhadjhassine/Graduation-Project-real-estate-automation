<template>
  <div class="bg-primary-50/20 min-h-screen">
    <!-- Hero Section -->
    <div class="relative bg-primary-950 py-24 overflow-hidden">
      <div class="absolute inset-0 z-0 opacity-10">
        <div class="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      </div>
      <div class="max-w-7xl mx-auto px-6 relative z-10 text-center">
        <h1 class="text-5xl md:text-7xl font-bold text-white mb-6">About <span class="text-accent-500">Elite</span></h1>
        <p class="text-xl text-primary-300 max-w-2xl mx-auto font-medium">
          We are redefining the standard of luxury real estate in Tunisia, combining cutting-edge technology with unparalleled exclusive service.
        </p>
      </div>
    </div>

    <!-- Mission Section -->
    <div class="max-w-7xl mx-auto px-6 py-20">
      <div class="grid md:grid-cols-2 gap-16 items-center">
        <div class="space-y-6">
          <div class="flex items-center gap-4 text-accent-600 font-bold uppercase tracking-widest text-sm">
            <LucideStar class="w-5 h-5" /> Our Mission
          </div>
          <h2 class="text-4xl font-bold text-primary-950 leading-tight">Setting a New Benchmark for Excellence.</h2>
          <p class="text-lg text-primary-600 leading-relaxed">
            At Elite Estate, we believe that finding a home is more than just a transaction; it is the realization of a vision. Our agency curation process ensures that only the most exceptional properties across Tunisia make it to our portfolio.
          </p>
          <p class="text-lg text-primary-600 leading-relaxed">
            By leveraging advanced AI semantic search and personalized automation, we provide our clients with a seamless, intuitive, and highly exclusive property discovery experience.
          </p>
        </div>
        <div class="relative">
          <div class="absolute inset-0 bg-accent-500/10 blur-3xl rounded-full transform translate-x-10 translate-y-10"></div>
          <img src="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80" alt="Luxury Villa" class="rounded-3xl shadow-2xl relative z-10 border border-white" />
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="bg-white border-y border-primary-100 py-16">
      <div class="max-w-7xl mx-auto px-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div v-for="(stat, i) in stats" :key="i" class="space-y-2">
            <h3 class="text-4xl md:text-5xl font-black text-primary-950">{{ stat.value }}</h3>
            <p class="text-sm font-bold text-primary-400 uppercase tracking-widest">{{ stat.label }}</p>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { LucideStar } from 'lucide-vue-next'

const stats = [
  { value: '15+', label: 'Years Experience' },
  { value: '500+', label: 'Luxury Properties' },
  { value: '24', label: 'Governorates' },
  { value: '100%', label: 'Client Satisfaction' },
]

useHead({
  title: 'About Us | Elite Real Estate'
})
</script>
