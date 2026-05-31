<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-primary-950">Platform Users</h2>
      <button @click="$emit('create-user')" class="btn-primary text-sm">
        <LucidePlus class="w-4 h-4 mr-2" /> Create Staff / Admin
      </button>
    </div>

    <!-- Filters Bar -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="relative">
        <LucideSearch class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <input 
          :value="searchQuery"
          @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
          type="text" 
          placeholder="Search by full name..."
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm"
        />
      </div>

      <div class="relative">
        <LucideFilter class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <select 
          :value="roleFilter"
          @change="$emit('update:roleFilter', ($event.target as HTMLSelectElement).value)"
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm appearance-none cursor-pointer"
        >
          <option value="all">All Roles</option>
          <option value="admin">Administrators</option>
          <option value="head_agent">Head Agents</option>
          <option value="agent">Sub-Agents</option>
        </select>
      </div>

      <div class="relative">
        <LucideUserCheck class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400" />
        <select 
          :value="statusFilter"
          @change="$emit('update:statusFilter', ($event.target as HTMLSelectElement).value)"
          class="w-full pl-11 pr-4 py-3 bg-white border border-primary-100 rounded-2xl text-sm focus:ring-2 focus:ring-primary-900/10 focus:border-primary-900 outline-none transition-all font-medium text-primary-950 shadow-sm appearance-none cursor-pointer"
        >
          <option value="all">Account Status: All</option>
          <option value="active">Active Accounts</option>
          <option value="disabled">Disabled Accounts</option>
        </select>
      </div>
    </div>

    <div class="card-premium p-0 overflow-hidden">
      <table class="w-full text-left">
        <thead>
          <tr class="bg-primary-50">
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Name</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Email</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Role</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
            <th class="px-6 py-4 text-xs font-bold text-primary-600 text-right">Account Control</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-primary-100">
          <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-primary-50/50 transition-colors">
            <td class="px-6 py-4 text-sm font-bold text-primary-950">{{ user.full_name }}</td>
            <td class="px-6 py-4 text-sm text-primary-600">{{ user.email }}</td>
            <td class="px-6 py-4">
              <span :class="[
                'px-3 py-1 text-xs font-bold rounded-full uppercase',
                user.role === 'admin' ? 'bg-red-100 text-red-700' :
                user.role === 'head_agent' ? 'bg-purple-100 text-purple-700' :
                user.role === 'agent' ? 'bg-blue-100 text-blue-700' :
                'bg-gray-100 text-gray-700'
              ]">
                {{ user.role === 'head_agent' ? 'Head Agent' : user.role === 'agent' ? 'Sub-Agent' : user.role === 'admin' ? 'Admin' : user.role }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span :class="[
                'px-3 py-1 text-[10px] font-bold rounded-lg uppercase',
                user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              ]">
                {{ user.is_active ? 'Active' : 'Disabled' }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <button 
                v-if="user.id !== auth?.user?.id"
                @click="$emit('toggle-status', user.id)" 
                :class="[
                  'px-4 py-2 rounded-xl text-[10px] font-bold uppercase transition-all shadow-md',
                  user.is_active ? 'bg-red-50 text-red-600 hover:bg-red-100 shadow-red-900/5' : 'bg-green-50 text-green-600 hover:bg-green-100 shadow-green-900/5'
                ]"
              >
                {{ user.is_active ? 'Disable' : 'Enable' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  LucidePlus, LucideSearch, LucideFilter, LucideUserCheck 
} from 'lucide-vue-next'

defineProps<{
  filteredUsers: any[]
  searchQuery: string
  roleFilter: string
  statusFilter: string
  auth: any
}>()

defineEmits<{
  (e: 'update:searchQuery', val: string): void
  (e: 'update:roleFilter', val: string): void
  (e: 'update:statusFilter', val: string): void
  (e: 'create-user'): void
  (e: 'toggle-status', userId: number): void
}>()
</script>
