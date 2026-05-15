<template>
  <div class="card-premium p-0 overflow-hidden">
    <table class="w-full text-left">
      <thead>
        <tr class="bg-primary-50">
          <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property Title</th>
          <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Type</th>
          <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Date</th>
          <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest text-right">Actions</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-primary-50">
        <tr v-for="report in reports" :key="report.id" class="hover:bg-primary-50/30 transition-colors">
          <td class="px-6 py-4">
            <div class="flex items-center gap-3">
              <LucideFileText class="w-5 h-5 text-primary-400" />
              <span class="font-bold text-primary-950 text-sm">{{ report.property_title }}</span>
            </div>
          </td>
          <td class="px-6 py-4">
            <span class="text-xs font-medium text-primary-600">{{ report.type }}</span>
          </td>
          <td class="px-6 py-4">
            <span class="text-xs font-medium text-primary-600">{{ report.date }}</span>
          </td>
          <td class="px-6 py-4 text-right">
            <button @click="$emit('download-report', report)" class="px-4 py-2 bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-xl text-[10px] font-bold uppercase transition-all inline-flex items-center gap-2">
              <LucideDownload class="w-3 h-3" /> Download
            </button>
          </td>
        </tr>
        <tr v-if="!reports.length">
          <td colspan="4" class="py-12 text-center text-primary-400">
            No transaction reports found. Reports are generated upon transaction approval.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { LucideFileText, LucideDownload } from 'lucide-vue-next'

defineProps<{
  reports: any[]
}>()

defineEmits(['download-report'])
</script>
