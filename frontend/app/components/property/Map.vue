<template>
  <div ref="mapContainer" class="w-full h-full rounded-[2.5rem] overflow-hidden shadow-2xl border border-white/50 relative">
    <div v-if="!isReady" class="absolute inset-0 bg-primary-50 flex items-center justify-center z-10">
       <LucideLoader2 class="w-8 h-8 text-primary-300 animate-spin" />
    </div>
  </div>
</template>

<script setup>
import { LucideLoader2 } from 'lucide-vue-next'

const props = defineProps({
  properties: {
    type: Array,
    default: () => []
  }
})

const mapContainer = ref(null)
const isReady = ref(false)
let map = null
let markers = []

const initMap = async () => {
  if (process.server) return
  
  // Dynamic import of Leaflet
  const L = await import('leaflet')
  
  if (map) return

  map = L.map(mapContainer.value).setView([36.8065, 10.1815], 11) // Default Tunis

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap'
  }).addTo(map)

  isReady.value = true
  updateMarkers(L)
  
  // Fix for Leaflet not knowing container size on early load
  setTimeout(() => {
    map.invalidateSize()
  }, 400)
}

const updateMarkers = (L) => {
  if (!map || !L) return
  
  // Clear old markers
  markers.forEach(m => m.remove())
  markers = []

  props.properties.forEach(prop => {
    // Use actual prop.latitude/longitude if they exist
    let lat = prop.latitude ? parseFloat(prop.latitude) : null
    let lng = prop.longitude ? parseFloat(prop.longitude) : null

    // Fallback only if missing
    if (!lat || !lng) {
      lat = 36.8 + (Math.random() - 0.5) * 0.2
      lng = 10.2 + (Math.random() - 0.5) * 0.2
    }
    
    const icon = L.divIcon({
      className: 'custom-div-icon',
      html: `<div class="bg-primary-950 text-white text-[10px] font-bold px-2 py-1 rounded-lg border border-white shadow-lg">${new Intl.NumberFormat('fr-TN').format(prop.price)}</div>`,
      iconSize: [60, 20]
    })

    const marker = L.marker([lat, lng], { icon }).addTo(map)
    marker.bindPopup(`
      <div class="p-2 font-sans">
        <p class="font-bold text-sm">${prop.title}</p>
        <p class="text-xs text-primary-500">${prop.city}</p>
      </div>
    `)
    markers.push(marker)
  })

  if (markers.length > 0) {
    const group = L.featureGroup(markers)
    map.fitBounds(group.getBounds().pad(0.1))
  }
}

watch(() => props.properties, async () => {
  if (process.client) {
    const L = await import('leaflet')
    updateMarkers(L)
    if (map) {
      setTimeout(() => map.invalidateSize(), 100)
    }
  }
}, { deep: true })

onMounted(() => {
  setTimeout(initMap, 500) // Slight delay for smooth load
})
</script>

<style>
.custom-div-icon {
  background: none !important;
  border: none !important;
}
.leaflet-popup-content-wrapper {
  border-radius: 1rem !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
}
</style>
