<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-primary-950/50 backdrop-blur-sm p-4">
    <div class="bg-white rounded-3xl w-full max-w-md p-8 relative max-h-[90vh] overflow-y-auto">
      <button @click="$emit('close')" class="absolute top-6 right-6 text-primary-400 hover:text-primary-950">
        <LucideX class="w-6 h-6" />
      </button>
      <h2 class="text-2xl font-bold text-primary-950 mb-6">Create Staff Account</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-bold text-primary-950 mb-2">Full Name</label>
          <input 
            v-model="userForm.full_name" 
            type="text" 
            required 
            class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500" 
            placeholder="John Doe" 
          />
        </div>
        <div>
          <label class="block text-sm font-bold text-primary-950 mb-2">Email Address</label>
          <input 
            v-model="userForm.email" 
            type="email" 
            required 
            class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500" 
            placeholder="john@agency.com" 
          />
        </div>
        <div>
          <label class="block text-sm font-bold text-primary-950 mb-2">Temporary Password</label>
          <input 
            v-model="userForm.password" 
            type="text" 
            required 
            class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500" 
            placeholder="Must be changed later" 
          />
        </div>
        <div>
          <label class="block text-sm font-bold text-primary-950 mb-2">Role</label>
          <select 
            v-model="userForm.role" 
            required 
            class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500"
          >
            <option value="head_agent">Head Agent</option>
            <option value="agent">Sub-Agent</option>
            <option value="admin">Administrator</option>
          </select>
        </div>
        <div v-if="userForm.role === 'agent'">
          <label class="block text-sm font-bold text-primary-950 mb-2">Assign to Head Agent</label>
          <select 
            v-model="userForm.manager_id" 
            required 
            class="w-full bg-primary-50 border border-primary-200 rounded-xl px-4 py-3 outline-none focus:border-accent-500"
          >
            <option value="" disabled>Select a Head Agent...</option>
            <option v-for="manager in headAgents" :key="manager.id" :value="manager.id">{{ manager.full_name }}</option>
          </select>
        </div>
        <p v-if="error" class="text-red-500 text-sm font-medium">{{ error }}</p>
        <button type="submit" class="btn-primary w-full py-3" :disabled="loading">
          Create User Account
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { LucideX } from 'lucide-vue-next'

const props = defineProps<{
  show: boolean
  headAgents: any[]
  loading: boolean
  error?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', form: any): void
}>()

const userForm = ref({ 
  full_name: '', 
  email: '', 
  password: '', 
  role: 'head_agent', 
  manager_id: '', 
  phone_number: '' 
})

// Reset form when modal opens
watch(() => props.show, (newVal) => {
  if (newVal) {
    userForm.value = { 
      full_name: '', 
      email: '', 
      password: '', 
      role: 'head_agent', 
      manager_id: '', 
      phone_number: '' 
    }
  }
})

const handleSubmit = () => {
  emit('submit', { ...userForm.value })
}
</script>
