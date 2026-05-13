<template>
  <Transition name="modal">
    <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6" @click="close">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-primary-950/40 backdrop-blur-md"></div>
      
      <!-- Modal Content -->
      <div 
        class="relative w-full max-w-2xl bg-white rounded-[2.5rem] shadow-2xl border border-white/20 overflow-hidden flex flex-col sm:flex-row max-h-[90vh]"
        @click.stop
      >
        <!-- Close Button -->
        <button 
          @click="close" 
          class="absolute top-6 right-6 z-10 p-2 bg-white/80 backdrop-blur-md rounded-full text-primary-400 hover:text-primary-950 hover:scale-110 transition-all shadow-sm"
        >
          <LucideX :size="20" />
        </button>

        <!-- Left Side: Property Image -->
        <div class="w-full sm:w-5/12 h-48 sm:h-auto relative overflow-hidden group">
          <img 
            :src="primaryImage" 
            alt="Property" 
            class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
          <div class="absolute bottom-6 left-6 right-6">
            <span class="px-3 py-1 bg-white/20 backdrop-blur-md border border-white/30 rounded-full text-[10px] font-bold text-white uppercase tracking-widest mb-2 inline-block">
              {{ visit.property?.listing_type }}
            </span>
            <h3 class="text-white font-bold text-lg leading-tight truncate">
              {{ visit.property?.title }}
            </h3>
          </div>
        </div>

        <!-- Right Side: Details -->
        <div class="flex-1 p-8 sm:p-10 overflow-y-auto custom-scrollbar">
          <div class="flex items-center gap-2 mb-6">
            <span :class="statusClasses" class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter">
              {{ visit.status }}
            </span>
            <span class="text-xs font-bold text-primary-400">
              {{ formatDate(visit.visit_date) }}
            </span>
          </div>

          <div class="space-y-8">
            <!-- Client Info -->
            <section>
              <h4 class="text-[10px] font-bold text-primary-300 uppercase tracking-[0.2em] mb-4">Client Information</h4>
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 rounded-2xl bg-primary-50 flex items-center justify-center text-primary-600 font-bold text-lg shrink-0">
                  {{ visit.client?.full_name?.charAt(0) || '?' }}
                </div>
                <div class="min-w-0">
                  <p class="text-primary-950 font-bold text-lg mb-1 truncate">{{ visit.client?.full_name || 'Anonymous Visitor' }}</p>
                  <div class="flex flex-col gap-1">
                    <div class="flex items-center gap-2 text-primary-950 transition-colors text-base font-medium">
                      <LucideMail :size="16" class="text-primary-400" />
                      {{ visit.client?.email || 'No email' }}
                    </div>
                    <div class="flex items-center gap-2 text-primary-950 transition-colors text-base font-medium">
                      <LucidePhone :size="16" class="text-primary-400" />
                      {{ visit.client?.phone_number || visit.telegram_chat_id || 'No phone' }}
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <!-- Property Location -->
            <section>
              <h4 class="text-[10px] font-bold text-primary-300 uppercase tracking-[0.2em] mb-4">Location Details</h4>
              <a 
                :href="googleMapsUrl" 
                target="_blank"
                class="bg-primary-50/50 rounded-2xl p-4 border border-primary-100 flex items-start gap-3 hover:bg-primary-100/50 transition-all group block"
              >
                <div class="p-2 bg-white rounded-xl shadow-sm text-primary-400 group-hover:text-primary-600 transition-colors">
                  <LucideMapPin :size="18" />
                </div>
                <div>
                  <p class="text-primary-950 font-bold text-sm">{{ visit.property?.city }}, Tunisia</p>
                  <p class="text-primary-500 text-xs leading-relaxed mt-1">
                    {{ visit.property?.address || 'Private location. Click to view on map.' }}
                  </p>
                  <div class="mt-2 text-[10px] font-bold text-blue-600 uppercase tracking-wider flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    Open in Navigation <LucideExternalLink :size="10" />
                  </div>
                </div>
              </a>
            </section>

            <!-- Agent Assigned -->
            <section v-if="visit.agent">
              <h4 class="text-[10px] font-bold text-primary-300 uppercase tracking-[0.2em] mb-4">Assigned Agent</h4>
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs border border-blue-200">
                  {{ visit.agent.full_name?.charAt(0) }}
                </div>
                <span class="text-primary-800 font-bold text-sm">{{ visit.agent.full_name }}</span>
                <span class="text-[10px] text-primary-400 font-medium">Professional Agent</span>
              </div>
            </section>
          </div>

          <!-- Footer Actions -->
          <div class="mt-10 pt-6 border-t border-primary-50 flex items-center justify-between gap-4">
            <button 
              @click="close"
              class="px-6 py-2.5 text-sm font-bold text-primary-500 hover:text-primary-950 transition-colors"
            >
              Close
            </button>
            <NuxtLink 
              :to="'/properties/' + visit.property?.slug"
              class="flex items-center gap-2 px-6 py-2.5 bg-primary-950 text-white rounded-xl text-sm font-bold hover:bg-primary-800 transition-all shadow-lg shadow-primary-950/20 active:scale-95"
            >
              View Property
              <LucideExternalLink :size="16" />
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { 
  LucideX, 
  LucideMail, 
  LucidePhone, 
  LucideMapPin, 
  LucideExternalLink,
  LucideCalendar
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: Boolean,
  visit: {
    type: Object,
    required: true,
    default: () => ({})
  }
})

const googleMapsUrl = computed(() => {
  const p = props.visit.property
  if (!p) return '#'
  
  // Use Directions API for "Navigation" - it's more exact when using coordinates
  if (p.latitude && p.longitude) {
    return `https://www.google.com/maps/dir/?api=1&destination=${p.latitude},${p.longitude}&travelmode=driving`
  }
  
  // Fallback to searching the address/city if coordinates are missing
  const query = encodeURIComponent(`${p.address || ''} ${p.city}, Tunisia`)
  return `https://www.google.com/maps/search/?api=1&query=${query}`
})

const emit = defineEmits(['close'])

const close = () => emit('close')

const primaryImage = computed(() => {
  if (props.visit.property?.images?.length > 0) {
    const primary = props.visit.property.images.find(img => img.is_primary)
    return primary ? primary.image_url : props.visit.property.images[0].image_url
  }
  return 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80'
})

const statusClasses = computed(() => {
  const status = props.visit.status?.toLowerCase()
  if (status === 'scheduled') return 'bg-blue-100 text-blue-700 border border-blue-200'
  if (status === 'finished' || status === 'completed') return 'bg-emerald-100 text-emerald-700 border border-emerald-200'
  if (status === 'cancelled') return 'bg-rose-100 text-rose-700 border border-rose-200'
  return 'bg-gray-100 text-gray-700 border border-gray-200'
})

const formatDate = (dateString) => {
  if (!dateString) return 'TBD'
  return new Date(dateString).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #f1f5f9;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #e2e8f0;
}
</style>
