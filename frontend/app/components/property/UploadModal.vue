<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-6">
    <div class="absolute inset-0 bg-primary-950/60 backdrop-blur-sm" @click="$emit('close')"></div>
    
    <div class="relative w-full max-w-4xl bg-white rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="p-8 border-b border-primary-50 flex items-center justify-between bg-primary-50/30">
        <div>
          <h2 class="text-3xl font-bold text-primary-950">{{ isEdit ? 'Edit Property Details' : 'List New Property' }}</h2>
          <p class="text-primary-400 text-sm">{{ isEdit ? 'Update the information for this listing' : 'Fill in the details for your exclusive listing' }}</p>
        </div>
        <button @click="$emit('close')" class="w-12 h-12 rounded-full hover:bg-white transition-colors flex items-center justify-center">
          <LucideX class="w-6 h-6 text-primary-400" />
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-10 space-y-12">
        <!-- Basic Info -->
        <section class="grid md:grid-cols-2 gap-8">
           <div class="space-y-6">
             <div>
               <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Property Title</label>
               <input v-model="form.title" type="text" :disabled="readOnly" placeholder="Luxury Penthouse in Gammarth" class="form-input" />
             </div>
             <div>
               <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Neighborhood</label>
               <input v-model="form.neighborhood" type="text" :disabled="readOnly" placeholder="Zone Touristique / Upper Marsa" class="form-input" />
             </div>
             <div>
               <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Governorate</label>
               <div class="relative">
                 <LucideMapPin class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-400 z-10 pointer-events-none" />
                 <select v-model="form.city" :disabled="readOnly" class="form-input pl-10 appearance-none cursor-pointer">
                   <option value="" disabled>Select Governorate...</option>
                   <option v-for="gov in tunisianGovernorates" :key="gov" :value="gov">{{ gov }}</option>
                 </select>
               </div>
             </div>
             <div>
               <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Detailed Address</label>
               <input v-model="form.address" type="text" :disabled="readOnly" placeholder="Street, Building, Area..." class="form-input" />
             </div>
             <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Type</label>
                  <select v-model="form.property_type" :disabled="readOnly" class="form-input">
                    <option value="apartment">Apartment</option>
                    <option value="house">House</option>
                    <option value="villa">Villa</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Listing</label>
                  <select v-model="form.listing_type" :disabled="readOnly" class="form-input">
                    <option value="sale">For Sale</option>
                    <option value="rent">For Rent</option>
                  </select>
                </div>
             </div>
           </div>
           
           <div class="space-y-6">
             <div>
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Public Description</label>
                <textarea v-model="form.description" :disabled="readOnly" rows="3" placeholder="Description for public viewing..." class="form-input resize-none"></textarea>
             </div>

             <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Price (TND)</label>
                  <input v-model="form.price" type="number" :disabled="readOnly" class="form-input" />
                </div>
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Total Area (m²)</label>
                  <input v-model="form.area" type="number" :disabled="readOnly" class="form-input" />
                </div>
             </div>
             <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Built Area (m²)</label>
                  <input v-model="form.built_area" type="number" :disabled="readOnly" class="form-input" />
                </div>
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Postal Code</label>
                  <input v-model="form.postal_code" type="text" :disabled="readOnly" placeholder="2070" class="form-input" />
                </div>
             </div>
             
             <!-- Agent Assignment -->
             <div v-if="auth.isAdmin || auth.isHeadAgent">
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Assign Agent</label>
                <select v-model="form.agent_id" :disabled="readOnly" class="form-input">
                   <option :value="null">Unassigned</option>
                   <option v-for="agent in staff" :key="agent.id" :value="agent.id">{{ agent.full_name }}</option>
                </select>
             </div>
             
             <!-- Owner Assignment (Admin only) -->
             <div v-if="auth.isAdmin">
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Team Assignment (Head Agent)</label>
                <select v-model="form.owner_id" :disabled="readOnly" class="form-input">
                   <option :value="null">No Team (Admin Managed)</option>
                   <option v-for="head in heads" :key="head.id" :value="head.id">{{ head.full_name }}</option>
                </select>
             </div>
           </div>
        </section>

        <!-- Specs -->
        <section class="grid grid-cols-3 gap-6 pt-10 border-t border-primary-50">
           <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
              <LucideBedDouble class="w-6 h-6 text-primary-300" />
              <div class="flex-1">
                <p class="text-[10px] uppercase font-bold text-primary-300">Bedrooms</p>
                <input v-model="form.bedrooms" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
              </div>
           </div>
           <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
              <LucideBath class="w-6 h-6 text-primary-300" />
              <div class="flex-1">
                <p class="text-[10px] uppercase font-bold text-primary-300">Bathrooms</p>
                <input v-model="form.bathrooms" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
              </div>
           </div>
           <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
              <LucideMaximize class="w-6 h-6 text-primary-300" />
              <div class="flex-1">
                <p class="text-[10px] uppercase font-bold text-primary-300">Land Area</p>
                <input v-model="form.land_area" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
              </div>
           </div>
           
           <!-- New Detailed Specs -->
           <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
              <LucideChefHat class="w-6 h-6 text-primary-300" />
              <div class="flex-1">
                <p class="text-[10px] uppercase font-bold text-primary-300">Kitchens</p>
                <input v-model="form.kitchens" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
              </div>
           </div>
           <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
              <LucideLayout class="w-6 h-6 text-primary-300" />
              <div class="flex-1">
                <p class="text-[10px] uppercase font-bold text-primary-300">Living Rooms</p>
                <input v-model="form.living_rooms" type="number" :disabled="readOnly" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
              </div>
           </div>
           
           <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
              <LucideLayers class="w-6 h-6 text-primary-300" />
              <div class="flex-1">
                <p class="text-[10px] uppercase font-bold text-primary-300">Floor info</p>
                <div class="flex items-center">
                  <input v-model="form.floor_number" type="number" :disabled="readOnly" placeholder="No." class="bg-transparent border-none p-0 focus:ring-0 text-lg font-bold w-12" />
                   <span class="mx-1 text-primary-200">/</span>
                   <input v-model="form.floors" type="number" :disabled="readOnly" placeholder="Total" class="bg-transparent border-none p-0 focus:ring-0 text-lg font-bold w-12" />
                </div>
              </div>
           </div>
        </section>

        <!-- Location & GPS -->
        <section class="space-y-6 pt-10 border-t border-primary-50">
          <div class="flex items-center justify-between">
            <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest">📍 Location & GPS Coordinates</label>
            <button 
              v-if="!readOnly"
              @click="showMapPicker = !showMapPicker" 
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
          <div v-if="showMapPicker" class="rounded-2xl overflow-hidden border border-primary-100 shadow-inner" style="height: 320px;">
            <div id="location-picker-map" style="width: 100%; height: 100%;"></div>
          </div>
          <p v-if="showMapPicker" class="text-xs text-primary-400 text-center">
            Click anywhere on the map to set the property location. The pin will update the coordinates above.
          </p>
        </section>

        <!-- Amenities Selection -->
        <section class="space-y-6 pt-10 border-t border-primary-50">
           <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest">Amenities & Features</label>
           <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <label 
                v-for="feature in availableFeatures" 
                :key="feature.id"
                class="flex items-center gap-3 p-4 rounded-2xl border cursor-pointer transition-all"
                :class="[
                  form.feature_ids.includes(feature.id) 
                    ? 'bg-primary-50 border-primary-200 text-primary-950' 
                    : 'bg-white border-primary-50 text-primary-400 hover:border-primary-100'
                ]"
              >
                <input 
                  type="checkbox" 
                  :value="feature.id" 
                  v-model="form.feature_ids"
                  :disabled="readOnly"
                  class="hidden"
                />
                <LucideCheckCircle2 
                  class="w-4 h-4" 
                  :class="form.feature_ids.includes(feature.id) ? 'text-primary-600' : 'text-primary-100'"
                />
                <span class="text-sm font-medium">{{ feature.name }}</span>
              </label>
           </div>
           <div v-if="!availableFeatures.length" class="text-xs text-primary-300 italic">
              Loading amenities...
           </div>
        </section>

        <!-- Gallery Upload -->
        <section class="space-y-6 pt-10 border-t border-primary-50">
           <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest">Property Gallery</label>
           <div class="grid grid-cols-4 gap-4">
              <div v-for="(img, i) in previews" :key="i" class="relative group aspect-square rounded-2xl overflow-hidden border border-primary-100">
                 <img :src="img" class="w-full h-full object-cover" />
                 <button v-if="!readOnly" @click="removeImage(i)" class="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                    <LucideX class="w-3 h-3" />
                 </button>
              </div>
              <label v-if="!readOnly" class="aspect-square rounded-2xl border-2 border-dashed border-primary-200 flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-primary-50 hover:border-primary-400 transition-all text-primary-300 hover:text-primary-600">
                 <LucidePlus class="w-6 h-6" />
                 <span class="text-[10px] font-bold uppercase tracking-widest">Add Photos</span>
                 <input type="file" multiple @change="handleFileChange" class="hidden" accept="image/*" />
              </label>
           </div>
        </section>
      </div>

      <!-- Footer -->
      <div class="p-8 bg-primary-50/50 border-t border-primary-50 flex justify-end gap-4">
        <button @click="$emit('close')" class="px-8 py-3 text-sm font-bold text-primary-400 hover:text-primary-950 transition-colors">{{ readOnly ? 'Close' : 'Cancel' }}</button>
        <button v-if="!readOnly" @click="handleSubmit" class="btn-primary !px-12" :disabled="loading">
          <LucideLoader2 v-if="loading" class="w-5 h-5 animate-spin" />
          <span v-else>{{ isEdit ? 'Save Changes' : 'List Property' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  LucideX, LucideBedDouble, LucideBath, LucideLoader2, 
  LucidePlus, LucideMaximize, LucideChefHat, LucideLayout,
  LucideLayers, LucideCheckCircle2, LucideMapPin, LucideMap
} from 'lucide-vue-next'

const props = defineProps({
  show: Boolean,
  editData: {
    type: Object,
    default: null
  },
  readOnly: {
    type: Boolean,
    default: false
  }
})

const auth = useAuthStore()

const emit = defineEmits(['close', 'success'])
const api = useApi()
const loading = ref(false)
const selectedFiles = ref([])
const previews = ref([])
const staff = ref([])
const heads = ref([])
const availableFeatures = ref([])
const isEdit = computed(() => !!props.editData)

const showMapPicker = ref(false)
let leafletMap = null
let leafletMarker = null

const tunisianGovernorates = [
  'Ariana', 'Béja', 'Ben Arous', 'Bizerte', 'Gabès', 'Gafsa',
  'Jendouba', 'Kairouan', 'Kasserine', 'Kébili', 'Le Kef', 'Mahdia',
  'La Manouba', 'Médenine', 'Monastir', 'Nabeul', 'Sfax', 'Sidi Bouzid',
  'Siliana', 'Sousse', 'Tataouine', 'Tozeur', 'Tunis', 'Zaghouan'
]

const form = ref({
  title: '',
  slug: '',
  description: '',
  property_type: 'villa',
  listing_type: 'sale',
  price: 0,
  area: 0,
  bedrooms: 0,
  bathrooms: 0,
  city: '',
  country: 'Tunisia',
  neighborhood: '',
  address: '',
  postal_code: '',
  built_area: 0,
  land_area: 0,
  latitude: null,
  longitude: null,
  agent_id: null,
  owner_id: null,
  kitchens: 1,
  living_rooms: 1,
  floors: null,
  floor_number: null,
  feature_ids: []
})

watch(() => props.editData, (newVal) => {
  if (newVal) {
    const data = { ...newVal }
    data.feature_ids = newVal.features?.map(f => f.id) || []
    form.value = data
  } else {
    form.value = {
      title: '', slug: '', description: '',
      property_type: 'villa', listing_type: 'sale', price: 0, 
      area: 0, built_area: 0, land_area: 0, 
      bedrooms: 0, bathrooms: 0, kitchens: 1, living_rooms: 1,
      neighborhood: '', address: '', city: '', country: 'Tunisia', postal_code: '',
      floors: null, floor_number: null, latitude: null, longitude: null,
      agent_id: null, owner_id: null, feature_ids: []
    }
  }
}, { immediate: true })

// Initialize Leaflet map when map picker is shown
watch(showMapPicker, async (visible) => {
  if (!visible) {
    if (leafletMap) { leafletMap.remove(); leafletMap = null; leafletMarker = null; }
    return
  }
  await nextTick()
  if (typeof window === 'undefined') return
  
  const L = await import('leaflet')
  if (leafletMap) return
  
  const defaultLat = form.value.latitude || 33.8869
  const defaultLng = form.value.longitude || 9.5375
  
  leafletMap = L.map('location-picker-map').setView([defaultLat, defaultLng], form.value.latitude ? 13 : 6)
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(leafletMap)

  // Custom marker icon
  const icon = L.divIcon({
    html: '<div style="background:#1e1b4b;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.4)"></div>',
    iconAnchor: [8, 8],
    className: ''
  })

  if (form.value.latitude && form.value.longitude) {
    leafletMarker = L.marker([form.value.latitude, form.value.longitude], { icon }).addTo(leafletMap)
  }

  leafletMap.on('click', (e) => {
    const { lat, lng } = e.latlng
    form.value.latitude = parseFloat(lat.toFixed(6))
    form.value.longitude = parseFloat(lng.toFixed(6))
    if (leafletMarker) { leafletMarker.setLatLng([lat, lng]) }
    else { leafletMarker = L.marker([lat, lng], { icon }).addTo(leafletMap) }
  })
})

const fetchData = async () => {
   if (auth.isAdmin || auth.isHeadAgent) {
      try {
         const [staffRes, featuresRes] = await Promise.all([
           api.get('/agency/staff'),
           api.get('/features')
         ])
         staff.value = staffRes.data
         availableFeatures.value = featuresRes.data
         
         if (auth.isAdmin) {
           const headsRes = await api.get('/admin/head_agents')
           heads.value = headsRes.data
         }
      } catch (e) {
         console.error("Failed to load staff/features", e)
      }
   } else {
     // Even sub agents might need features for read-only view
     try {
       const res = await api.get('/features')
       availableFeatures.value = res.data
     } catch (e) {}
   }
}

onMounted(() => {
   fetchData()
})

const handleFileChange = (e) => {
  const files = Array.from(e.target.files)
  selectedFiles.value.push(...files)
  
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => previews.value.push(e.target.result)
    reader.readAsDataURL(file)
  })
}

const removeImage = (index) => {
  selectedFiles.value.splice(index, 1)
  previews.value.splice(index, 1)
}

const handleSubmit = async () => {
  loading.value = true
  
  const cleanForm = { ...form.value }
  const numericFields = ['price', 'area', 'bedrooms', 'bathrooms', 'kitchens', 'living_rooms', 'floors', 'floor_number']
  const floatFields = ['latitude', 'longitude']
  
  numericFields.forEach(field => {
    if (cleanForm[field] === "" || cleanForm[field] === undefined) {
      cleanForm[field] = null
    } else if (cleanForm[field] !== null) {
      cleanForm[field] = Number(cleanForm[field])
    }
  })
  
  floatFields.forEach(field => {
    if (cleanForm[field] === "" || cleanForm[field] === undefined || cleanForm[field] === null) {
      cleanForm[field] = null
    } else {
      cleanForm[field] = parseFloat(cleanForm[field])
    }
  })

  try {
    let propertyId
    if (isEdit.value) {
      await api.put(`/properties/${props.editData.id}`, cleanForm)
      propertyId = props.editData.id
    } else {
      cleanForm.slug = cleanForm.title.toLowerCase().replace(/ /g, '-') + '-' + Date.now()
      const propRes = await api.post('/properties', cleanForm)
      propertyId = propRes.data.id
    }
    
    if (selectedFiles.value.length > 0) {
      const formData = new FormData()
      selectedFiles.value.forEach(file => {
        formData.append('files', file)
      })
      await api.post(`/properties/${propertyId}/images`, formData)
    }
    
    emit('success')
  } catch (e) {
    console.error("Property save error:", e)
    const errorMsg = e.response?.data?.detail 
      ? (typeof e.response.data.detail === 'string' ? e.response.data.detail : JSON.stringify(e.response.data.detail))
      : 'Failed to save property. Check if fields are correct.'
    alert(errorMsg)
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  if (leafletMap) { leafletMap.remove(); leafletMap = null; leafletMarker = null; }
})
</script>

<style scoped>
.form-input {
  @apply w-full bg-primary-50/50 border border-primary-100 rounded-2xl px-5 py-4 text-sm focus:ring-4 focus:ring-primary-500/5 focus:border-primary-500 outline-none transition-all placeholder:text-primary-200;
}
</style>
