<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-primary-950 to-slate-900 text-white p-6">
    <div class="text-center max-w-2xl">
      <h1 class="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-white">
        Real Estate Automation
      </h1>
      <p class="text-xl text-slate-300 mb-8">
        AI-Powered Real Estate Platform. Connecting buyers and agents through smart automation.
      </p>
      <div class="flex gap-4 justify-center">
        <button class="px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-semibold transition-all">
          Browse Properties
        </button>
        <button class="px-6 py-3 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg font-semibold transition-all">
          Contact Sales
        </button>
      </div>
    </div>
    
    <div class="mt-12 p-4 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-md">
      <p class="text-sm text-slate-400 font-mono">
        Backend URL: {{ apiUrl }} | Status: <span class="text-green-400">Ready</span>
      </p>
    </div>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const apiUrl = config.public.apiUrl || 'http://localhost:8000'
</script>

<style>
/* Nuxt automatically imports colors from tailwind.config.js */
</style>
