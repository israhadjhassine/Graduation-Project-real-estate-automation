<template>
  <div class="flex items-center justify-between mb-10 pb-8 border-b border-primary-100">
    <div>
      <h1 class="text-3xl font-extrabold text-primary-950 !font-sans tracking-tight">Management Workspace</h1>
      <p class="text-primary-500 font-medium mt-1">Agency Operations • Team Oversight • Listing Control</p>
    </div>
    <button @click="$emit('list-new')" class="btn-primary !rounded-lg px-6 py-3">
      <LucidePlus class="w-5 h-5 mr-2" /> List New Property
    </button>
  </div>
</template>

<script setup lang="ts">
import { LucidePlus } from 'lucide-vue-next'

defineEmits(['list-new'])
</script>
