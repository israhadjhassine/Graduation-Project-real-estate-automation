<template>
  <div class="flex gap-2 border-b border-primary-100 mb-8 overflow-x-auto pb-0">
    <button 
      @click="$emit('update:activeTab', 'users')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'users' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideUsers class="w-4 h-4 inline-block mr-2" /> Manage Users
    </button>
    <button 
      @click="$emit('update:activeTab', 'properties')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'properties' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideHome class="w-4 h-4 inline-block mr-2" /> All Properties
    </button>
    <button 
      @click="$emit('update:activeTab', 'reports')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'reports' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideFileText class="w-4 h-4 inline-block" /> Transaction Reports
    </button>
    <button 
      @click="$emit('update:activeTab', 'analytics')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'analytics' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucidePieChart class="w-4 h-4 inline-block" /> Platform Analytics
    </button>
  </div>
</template>

<script setup lang="ts">
import { 
  LucideUsers, LucideHome, LucideFileText, LucidePieChart 
} from 'lucide-vue-next'

defineProps<{
  activeTab: string
}>()

defineEmits(['update:activeTab'])
</script>
