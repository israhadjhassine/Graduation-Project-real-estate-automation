<template>
  <div class="flex gap-2 border-b border-primary-100 mb-8 overflow-x-auto pb-0">
    <button 
      @click="$emit('update:activeTab', 'properties')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'properties' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideHome class="w-4 h-4 inline-block mr-2" /> Properties Portfolio
    </button>
    <button 
      @click="$emit('update:activeTab', 'staff')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'staff' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideUsers class="w-4 h-4 inline-block mr-2" /> Sub-Agent Team
    </button>
    <button 
      @click="$emit('update:activeTab', 'schedule')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'schedule' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideCalendar class="w-4 h-4 inline-block" /> Team Schedule
    </button>
    <button 
      @click="$emit('update:activeTab', 'sold')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'sold' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideCheckCircle2 class="w-4 h-4 inline-block mr-2" /> Sold Properties
    </button>
    <button 
      @click="$emit('update:activeTab', 'rented')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'rented' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideHome class="w-4 h-4 inline-block mr-2" /> Rented Properties
    </button>
    <button 
      @click="$emit('update:activeTab', 'analytics')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'analytics' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucidePieChart class="w-4 h-4 inline-block" /> Team Performance
    </button>
    <button 
      @click="$emit('update:activeTab', 'inquiries')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'inquiries' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideMessageSquare class="w-4 h-4 inline-block" /> Inquiries
      <span v-if="pendingSalesCount" class="bg-amber-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center ml-1">{{ pendingSalesCount }}</span>
    </button>
    <button 
      v-if="showReportsTab"
      @click="$emit('update:activeTab', 'reports')" 
      :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'reports' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
    >
      <LucideFileText class="w-4 h-4 inline-block" /> Transaction Reports
    </button>
  </div>
</template>

<script setup lang="ts">
import { 
  LucideHome, LucideUsers, LucideCalendar, 
  LucideCheckCircle2, LucidePieChart, 
  LucideMessageSquare, LucideFileText 
} from 'lucide-vue-next'

defineProps<{
  activeTab: string
  pendingSalesCount: number
  showReportsTab: boolean
}>()

defineEmits(['update:activeTab'])
</script>
