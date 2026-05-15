<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-6 bg-primary-950/40 backdrop-blur-sm transition-all" @click="$emit('close')">
    <div class="bg-white rounded-3xl w-full max-w-md p-8 shadow-2xl relative border border-primary-50" @click.stop>
      <button @click="$emit('close')" class="absolute top-6 right-6 text-primary-400 hover:text-primary-950 transition-colors">
        <LucideX class="w-6 h-6" />
      </button>
      <h3 class="text-2xl font-bold text-primary-950 mb-3">Request Rent Approval</h3>
      <p class="text-primary-600 mb-6 leading-relaxed">Select the rental duration for this property.</p>
      
      <div class="space-y-4 mb-8">
        <div>
          <label class="block text-sm font-bold text-primary-950 mb-2">Registered Client (Tenant)</label>
          <select :value="selectedClientId" @change="$emit('update:selectedClientId', ($event.target as HTMLSelectElement).value)" class="w-full bg-primary-50 p-3 rounded-xl border border-primary-200 outline-none focus:border-accent-500">
            <option value="" disabled>Select a client...</option>
            <option v-for="client in clients" :key="client.id" :value="client.id">
              {{ client.email }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-bold text-primary-950 mb-2">Start Date</label>
          <input type="date" :value="rentStartDate" @input="$emit('update:rentStartDate', ($event.target as HTMLInputElement).value)" class="w-full bg-primary-50 p-3 rounded-xl border border-primary-200 outline-none focus:border-accent-500" />
        </div>
        <div>
          <label class="block text-sm font-bold text-primary-950 mb-2">End Date</label>
          <input type="date" :value="rentEndDate" @input="$emit('update:rentEndDate', ($event.target as HTMLInputElement).value)" class="w-full bg-primary-50 p-3 rounded-xl border border-primary-200 outline-none focus:border-accent-500" />
        </div>
      </div>
      
      <button @click="$emit('submit')" class="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-colors shadow-lg shadow-blue-600/30">
        Submit Request
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LucideX } from 'lucide-vue-next'

defineProps<{
  show: boolean
  selectedClientId: string
  clients: any[]
  rentStartDate: string
  rentEndDate: string
}>()

defineEmits(['update:selectedClientId', 'update:rentStartDate', 'update:rentEndDate', 'close', 'submit'])
</script>
