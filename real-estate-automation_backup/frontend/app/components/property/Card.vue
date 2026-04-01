<template>
  <div class="card-premium group cursor-pointer overflow-hidden">
    <div class="relative h-64 -mx-6 -mt-6 mb-6 overflow-hidden">
      <img 
        :src="primaryImage" 
        :alt="property.title"
        class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
      />
      <div class="absolute top-4 left-4 flex gap-2">
        <span class="px-3 py-1 bg-white/90 backdrop-blur-sm text-primary-900 text-[10px] font-bold uppercase tracking-widest rounded-full shadow-sm">
          {{ property.property_type }}
        </span>
        <span class="px-3 py-1 bg-accent-500 text-white text-[10px] font-bold uppercase tracking-widest rounded-full shadow-sm">
          For {{ property.listing_type }}
        </span>
      </div>
      <div class="absolute bottom-4 right-4 px-4 py-2 bg-primary-950/80 backdrop-blur-md text-white rounded-2xl border border-white/10">
        <p class="text-xs font-medium opacity-70">Starting From</p>
        <p class="text-lg font-bold leading-none">{{ formatPrice(property.price) }} <span class="text-[10px] uppercase">{{ property.currency }}</span></p>
      </div>
    </div>

    <div class="space-y-4">
      <div>
        <h3 class="text-xl font-bold text-primary-950 mb-1 group-hover:text-primary-700 transition-colors">{{ property.title }}</h3>
        <p class="text-sm text-primary-400 flex items-center gap-1">
          <LucideMapPin class="w-3 h-3" /> {{ property.city }}, {{ property.country }}
        </p>
      </div>

      <div class="flex items-center gap-4 pt-4 border-t border-primary-50">
        <div class="flex items-center gap-1.5 text-primary-900">
          <LucideBedDouble class="w-4 h-4 text-primary-300" />
          <span class="text-xs font-bold">{{ property.bedrooms }} Beds</span>
        </div>
        <div class="flex items-center gap-1.5 text-primary-900">
          <LucideBath class="w-4 h-4 text-primary-300" />
          <span class="text-xs font-bold">{{ property.bathrooms }} Baths</span>
        </div>
        <div class="flex items-center gap-1.5 text-primary-900 ml-auto">
          <LucideMaximize class="w-4 h-4 text-primary-300" />
          <span class="text-xs font-bold">{{ property.area }} m²</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideMapPin, LucideBedDouble, LucideBath, LucideMaximize } from 'lucide-vue-next'

const props = defineProps({
  property: {
    type: Object,
    required: true
  }
})

const { getPublicUrl } = useAssetUrl()

const primaryImage = computed(() => {
  const primary = props.property.images?.find(img => img.is_primary)
  return primary ? getPublicUrl(primary.image_url) : 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80'
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}
</script>
