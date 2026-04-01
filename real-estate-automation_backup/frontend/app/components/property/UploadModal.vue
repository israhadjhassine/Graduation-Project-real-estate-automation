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
               <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Address / City</label>
               <input v-model="form.city" type="text" :disabled="readOnly" placeholder="Gammarth, Tunis" class="form-input" />
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
             <div>
                <label class="block text-xs font-bold text-accent-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                  AI Detailed Intel
                  <span class="bg-accent-100 text-accent-600 px-2 py-0.5 rounded text-[8px]">AI Only</span>
                </label>
                <textarea v-model="form.ai_description" :disabled="readOnly" rows="3" placeholder="Technical internal notes for the AI assistant..." class="form-input !bg-accent-50/10 border-accent-100/50 resize-none"></textarea>
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
  LucideLayers, LucideCheckCircle2
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
  postal_code: '',
  built_area: 0,
  land_area: 0,
  ai_description: '',
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
    // Map to form structure and extract feature IDs
    const data = { ...newVal }
    data.feature_ids = newVal.features?.map(f => f.id) || []
    form.value = data
  } else {
    form.value = {
      title: '', slug: '', description: '', ai_description: '', 
      property_type: 'villa', listing_type: 'sale', price: 0, 
      area: 0, built_area: 0, land_area: 0, 
      bedrooms: 0, bathrooms: 0, kitchens: 1, living_rooms: 1,
      neighborhood: '', city: '', country: 'Tunisia', postal_code: '',
      floors: null, floor_number: null,
      agent_id: null, owner_id: null, feature_ids: []
    }
  }
}, { immediate: true })

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
  
  // 1. Sanitize numeric fields (Convert "" to null, ensure numbers)
  const cleanForm = { ...form.value }
  const numericFields = ['price', 'area', 'bedrooms', 'bathrooms', 'kitchens', 'living_rooms', 'floors', 'floor_number']
  
  numericFields.forEach(field => {
    if (cleanForm[field] === "" || cleanForm[field] === undefined) {
      cleanForm[field] = null
    } else if (cleanForm[field] !== null) {
      cleanForm[field] = Number(cleanForm[field])
    }
  })

  try {
    let propertyId
    if (isEdit.value) {
      // Update existing
      await api.put(`/properties/${props.editData.id}`, cleanForm)
      propertyId = props.editData.id
    } else {
      // Generate slug simple version for new props only
      cleanForm.slug = cleanForm.title.toLowerCase().replace(/ /g, '-') + '-' + Date.now()
      // Create Property
      const propRes = await api.post('/properties', cleanForm)
      propertyId = propRes.data.id
    }
    
    // 2. Upload Images if any NEW ones were selected
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
</script>

<style scoped>
.form-input {
  @apply w-full bg-primary-50/50 border border-primary-100 rounded-2xl px-5 py-4 text-sm focus:ring-4 focus:ring-primary-500/5 focus:border-primary-500 outline-none transition-all placeholder:text-primary-200;
}
</style>
