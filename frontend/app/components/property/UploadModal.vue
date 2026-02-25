<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-6">
    <div class="absolute inset-0 bg-primary-950/60 backdrop-blur-sm" @click="$emit('close')"></div>
    
    <div class="relative w-full max-w-4xl bg-white rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="p-8 border-b border-primary-50 flex items-center justify-between bg-primary-50/30">
        <div>
          <h2 class="text-3xl font-bold text-primary-950">List New Property</h2>
          <p class="text-primary-400 text-sm">Fill in the details for your exclusive listing</p>
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
               <input v-model="form.title" type="text" placeholder="Luxury Penthouse in Gammarth" class="form-input" />
             </div>
             <div>
               <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Address / City</label>
               <input v-model="form.city" type="text" placeholder="Gammarth, Tunis" class="form-input" />
             </div>
             <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Type</label>
                  <select v-model="form.property_type" class="form-input">
                    <option value="apartment">Apartment</option>
                    <option value="house">House</option>
                    <option value="villa">Villa</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Listing</label>
                  <select v-model="form.listing_type" class="form-input">
                    <option value="sale">For Sale</option>
                    <option value="rent">For Rent</option>
                  </select>
                </div>
             </div>
           </div>
           
           <div class="space-y-6">
             <div>
                <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Description</label>
                <textarea v-model="form.description" rows="4" placeholder="Describe the property... High-quality descriptions improve AI matching." class="form-input resize-none"></textarea>
             </div>
             <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Price (TND)</label>
                  <input v-model="form.price" type="number" class="form-input" />
                </div>
                <div>
                  <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Area (m²)</label>
                  <input v-model="form.area" type="number" class="form-input" />
                </div>
             </div>
           </div>
        </section>

        <!-- Specs -->
        <section class="grid grid-cols-3 gap-6 pt-10 border-t border-primary-50">
           <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
              <LucideBedDouble class="w-6 h-6 text-primary-300" />
              <div class="flex-1">
                <p class="text-[10px] uppercase font-bold text-primary-300">Bedrooms</p>
                <input v-model="form.bedrooms" type="number" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
              </div>
           </div>
           <div class="flex items-center gap-4 bg-primary-50/50 p-4 rounded-3xl border border-primary-100/50">
              <LucideBath class="w-6 h-6 text-primary-300" />
              <div class="flex-1">
                <p class="text-[10px] uppercase font-bold text-primary-300">Bathrooms</p>
                <input v-model="form.bathrooms" type="number" class="bg-transparent border-none p-0 focus:ring-0 text-xl font-bold w-full" />
              </div>
           </div>
        </section>

        <!-- Gallery Upload -->
        <section class="space-y-6 pt-10 border-t border-primary-50">
           <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest">Property Gallery</label>
           <div class="grid grid-cols-4 gap-4">
              <div v-for="(img, i) in previews" :key="i" class="relative group aspect-square rounded-2xl overflow-hidden border border-primary-100">
                 <img :src="img" class="w-full h-full object-cover" />
                 <button @click="removeImage(i)" class="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                    <LucideX class="w-3 h-3" />
                 </button>
              </div>
              <label class="aspect-square rounded-2xl border-2 border-dashed border-primary-200 flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-primary-50 hover:border-primary-400 transition-all text-primary-300 hover:text-primary-600">
                 <LucidePlus class="w-6 h-6" />
                 <span class="text-[10px] font-bold uppercase tracking-widest">Add Photos</span>
                 <input type="file" multiple @change="handleFileChange" class="hidden" accept="image/*" />
              </label>
           </div>
        </section>
      </div>

      <!-- Footer -->
      <div class="p-8 bg-primary-50/50 border-t border-primary-50 flex justify-end gap-4">
        <button @click="$emit('close')" class="px-8 py-3 text-sm font-bold text-primary-400 hover:text-primary-950 transition-colors">Cancel</button>
        <button @click="handleSubmit" class="btn-primary !px-12" :disabled="loading">
          <LucideLoader2 v-if="loading" class="w-5 h-5 animate-spin" />
          <span v-else>List Property</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideX, LucideBedDouble, LucideBath, LucideLoader2, LucidePlus } from 'lucide-vue-next'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['close', 'success'])
const api = useApi()
const loading = ref(false)
const selectedFiles = ref([])
const previews = ref([])

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
  country: 'Tunisia'
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
  // Generate slug simple version
  form.value.slug = form.value.title.toLowerCase().replace(/ /g, '-') + '-' + Date.now()
  
  try {
    // 1. Create Property
    const propRes = await api.post('/properties', form.value)
    const propertyId = propRes.data.id
    
    // 2. Upload Images if any
    if (selectedFiles.value.length > 0) {
      const formData = new FormData()
      selectedFiles.value.forEach(file => {
        formData.append('files', file)
      })
      await api.post(`/properties/${propertyId}/images`, formData)
    }
    
    emit('success')
  } catch (e) {
    console.error(e)
    alert('Failed to list property. Check if fields are correct.')
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
