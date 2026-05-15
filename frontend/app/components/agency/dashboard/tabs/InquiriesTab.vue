<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-primary-950">Transaction Approval Queue</h2>
    </div>
    <div class="grid md:grid-cols-2 gap-6">
      <div v-for="inq in inquiries" :key="inq.id" class="card-premium">
        <div class="flex items-center justify-between mb-4">
          <span class="px-2 py-1 text-[10px] font-bold rounded-lg uppercase bg-amber-100 text-amber-700">
            {{ inq.request_type }} REQUEST
          </span>
          <span class="text-[10px] text-primary-400 font-bold uppercase">{{ inq.status }}</span>
        </div>
        
        <p class="text-sm font-bold text-primary-950 mb-1">{{ inq.subject }}</p>
        <p class="text-xs text-primary-600 mb-4">{{ inq.message }}</p>
        
        <div class="bg-primary-50 rounded-xl p-4 mb-4">
          <div class="flex justify-between items-center mb-2">
            <span class="text-[10px] font-bold text-primary-400 uppercase">Negotiated Price</span>
            <span class="text-sm font-bold text-primary-950">{{ formatPrice(inq.price) }} TND</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-[10px] font-bold text-primary-400 uppercase">Requester</span>
            <span class="text-xs font-medium text-primary-700">{{ inq.name.split(' for ')[0] }}</span>
          </div>
        </div>

        <div class="flex items-center gap-3 pt-4 border-t border-primary-100">
           <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-[10px] font-bold">
             {{ inq.name.split(' for ')[1]?.charAt(0) || 'C' }}
           </div>
           <div>
             <p class="text-[10px] font-bold text-primary-950">Client: {{ inq.name.split(' for ')[1] || inq.name }}</p>
             <p class="text-[10px] text-primary-400">{{ inq.email || 'No email provided' }}</p>
           </div>
        </div>
        
        <!-- Approval Actions -->
        <div class="mt-4 pt-4 border-t border-primary-100 space-y-2">
           <div class="flex gap-2">
             <button 
               @click="$emit('update-status', inq.id, 'replied')" 
               class="flex-1 py-2 bg-primary-900 hover:bg-black text-white rounded-xl text-[10px] font-bold uppercase transition-all"
             >
               ✓ Approve & Finalize
             </button>
             <button 
               @click="$emit('update-status', inq.id, 'closed')" 
               class="flex-1 py-2 bg-primary-50 hover:bg-primary-100 text-primary-600 border border-primary-200 rounded-xl text-[10px] font-bold uppercase transition-all"
             >
               ✗ Reject
             </button>
           </div>
        </div>
      </div>
      <div v-if="!inquiries.length" class="col-span-full py-12 text-center text-primary-400">
         <LucideCheckCircle2 class="w-12 h-12 mx-auto text-primary-100 mb-3" />
         <p>No pending transaction requests found.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { LucideCheckCircle2 } from 'lucide-vue-next'

defineProps<{
  inquiries: any[]
}>()

defineEmits(['update-status'])

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}
</script>
