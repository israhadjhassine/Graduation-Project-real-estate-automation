<template>
  <section class="space-y-6 pt-10 border-t border-primary-50">
    <div class="flex items-center justify-between">
      <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest">📍 Location & GPS Coordinates</label>
      <button 
        v-if="!readOnly"
        @click="toggleMap" 
        type="button"
        class="flex items-center gap-2 px-4 py-2 bg-primary-50 hover:bg-primary-100 rounded-xl text-xs font-bold text-primary-700 border border-primary-200 transition-all"
      >
        <LucideMap class="w-3.5 h-3.5" />
        {{ showMapPicker ? 'Hide Map' : 'Pick on Map' }}
      </button>
    </div>
    
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Latitude</label>
        <input 
          v-model="form.latitude" 
          type="number" 
          step="0.000001"
          :disabled="readOnly" 
          placeholder="e.g. 36.8189" 
          class="form-input" 
        />
      </div>
      <div>
        <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-2">Longitude</label>
        <input 
          v-model="form.longitude" 
          type="number" 
          step="0.000001"
          :disabled="readOnly" 
          placeholder="e.g. 10.1658" 
          class="form-input" 
        />
      </div>
    </div>

    <!-- Interactive Map Picker -->
    <div v-show="showMapPicker" class="rounded-2xl overflow-hidden border border-primary-100 shadow-inner" style="height: 320px;">
      <div id="location-picker-map" style="width: 100%; height: 100%;"></div>
    </div>
    <p v-if="showMapPicker" class="text-xs text-primary-400 text-center">
      Click anywhere on the map to set the property location. The pin will update the coordinates above.
    </p>
  </section>
</template>

<script setup>
import { LucideMap } from 'lucide-vue-next'
import { defaultMapCenter, focusedMapZoom, defaultMapZoom } from '../../../constants/location'

const props = defineProps({
  form: Object,
  readOnly: Boolean
})

const showMapPicker = ref(false)
let leafletMap = null
let leafletMarker = null

const toggleMap = () => {
  showMapPicker.value = !showMapPicker.value
}

watch(showMapPicker, async (visible) => {
  if (!visible) {
    if (leafletMap) {
      leafletMap.remove()
      leafletMap = null
      leafletMarker = null
    }
    return
  }

  await nextTick()
  if (typeof window === 'undefined') return
  
  const L = await import('leaflet')
  if (leafletMap) return
  
  const defaultLat = props.form.latitude || defaultMapCenter.lat
  const defaultLng = props.form.longitude || defaultMapCenter.lng
  
  leafletMap = L.map('location-picker-map').setView(
    [defaultLat, defaultLng], 
    props.form.latitude ? focusedMapZoom : defaultMapZoom
  )
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(leafletMap)

  const icon = L.divIcon({
    html: '<div style="background:#1e1b4b;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.4)"></div>',
    iconAnchor: [8, 8],
    className: ''
  })

  if (props.form.latitude && props.form.longitude) {
    leafletMarker = L.marker([props.form.latitude, props.form.longitude], { icon }).addTo(leafletMap)
  }

  leafletMap.on('click', (e) => {
    const { lat, lng } = e.latlng
    props.form.latitude = parseFloat(lat.toFixed(6))
    props.form.longitude = parseFloat(lng.toFixed(6))
    if (leafletMarker) {
      leafletMarker.setLatLng([lat, lng])
    } else {
      leafletMarker = L.marker([lat, lng], { icon }).addTo(leafletMap)
    }
  })
})

onBeforeUnmount(() => {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
    leafletMarker = null
  }
})
</script>

<style scoped>
.form-input {
  @apply w-full bg-primary-50/50 border border-primary-100 rounded-2xl px-5 py-4 text-sm focus:ring-4 focus:ring-primary-500/5 focus:border-primary-500 outline-none transition-all placeholder:text-primary-200;
}
</style>
