<script setup lang="ts">
definePageMeta({
  layout: 'default'
})
</script>

<template>
  <div class="min-h-screen pt-24 pb-16 bg-slate-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Hero Section -->
      <div class="text-center mb-16">
        <h1 class="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
          Elevate Your Career with <span class="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">Elite Estate</span>
        </h1>
        <p class="text-xl text-slate-600 max-w-3xl mx-auto">
          We are redefining the luxury real estate experience in Tunisia. Join our team of visionaries, 
          innovators, and experts as we build the future of AI-driven property discovery.
        </p>
      </div>

      <!-- Values -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
        <div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-6 text-blue-600">
            <LucideStar class="w-6 h-6" />
          </div>
          <h3 class="text-xl font-bold text-slate-900 mb-3">Excellence</h3>
          <p class="text-slate-600 leading-relaxed">
            We don't just meet standards; we set them. Every interaction is an opportunity for perfection.
          </p>
        </div>

        <div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
          <div class="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-6 text-indigo-600">
            <LucideZap class="w-6 h-6" />
          </div>
          <h3 class="text-xl font-bold text-slate-900 mb-3">Innovation</h3>
          <p class="text-slate-600 leading-relaxed">
            Leading with AI and cutting-edge technology to create seamless experiences for our clients.
          </p>
        </div>

        <div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
          <div class="w-12 h-12 bg-sky-100 rounded-xl flex items-center justify-center mb-6 text-sky-600">
            <LucideUsers class="w-6 h-6" />
          </div>
          <h3 class="text-xl font-bold text-slate-900 mb-3">Community</h3>
          <p class="text-slate-600 leading-relaxed">
            We move as one. Our success is built on collaboration, mentorship, and shared ambition.
          </p>
        </div>
      </div>

      <!-- Open Roles Placeholder -->
      <div class="bg-white rounded-3xl overflow-hidden shadow-sm border border-slate-100">
        <div class="p-12 text-center">
          <div class="inline-flex items-center space-x-2 bg-blue-50 text-blue-700 px-4 py-1 rounded-full text-sm font-medium mb-6">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            <span>Hiring Soon</span>
          </div>
          <h2 class="text-3xl font-bold text-slate-900 mb-4">No Open Roles Currently</h2>
          <p class="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
            While we're not currently hiring, we're always looking for exceptional talent. 
            Drop your portfolio or CV, and we'll reach out when the right opportunity arrives.
          </p>
          <div class="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <NuxtLink 
              to="/contact" 
              class="px-8 py-3 bg-slate-900 text-white rounded-full font-medium hover:bg-slate-800 transition-colors inline-flex items-center"
            >
              Get in Touch <LucideArrowRight class="ml-2 w-4 h-4" />
            </NuxtLink>
            <NuxtLink 
              to="/properties" 
              class="px-8 py-3 text-slate-600 font-medium hover:text-slate-900 transition-colors"
            >
              Explore our Work
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
