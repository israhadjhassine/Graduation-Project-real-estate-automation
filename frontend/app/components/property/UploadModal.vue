<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-6">
    <div class="absolute inset-0 bg-primary-950/60 backdrop-blur-sm" @click="$emit('close')"></div>
    
    <div class="relative w-full max-w-4xl bg-white rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="p-8 border-b border-primary-50 flex items-center justify-between bg-primary-50/30">
        <div>
          <h2 class="text-3xl font-bold text-primary-950">
            {{ readOnly ? 'Property Details' : (isEdit ? 'Edit Property Details' : 'List New Property') }}
          </h2>
          <p class="text-primary-400 text-sm">
            {{ readOnly ? 'Viewing full property information' : (isEdit ? 'Update the information for this listing' : 'Fill in the details for your exclusive listing') }}
          </p>
        </div>
        <button type="button" @click.stop="$emit('close')" class="w-12 h-12 rounded-full hover:bg-white transition-colors flex items-center justify-center">
          <LucideX class="w-6 h-6 text-primary-400" />
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-10 space-y-12">
        <BasicInfo 
          :form="form" 
          :readOnly="readOnly" 
          :isAdmin="auth.isAdmin" 
          :isHeadAgent="auth.isHeadAgent"
          :staff="staff"
          :heads="heads"
        />

        <Specs 
          :form="form" 
          :readOnly="readOnly" 
        />

        <LocationPicker 
          :form="form" 
          :readOnly="readOnly" 
        />

        <AmenitiesSelector 
          :form="form" 
          :availableFeatures="availableFeatures" 
          :readOnly="readOnly" 
        />

        <GalleryUpload 
          :previews="previews" 
          :readOnly="readOnly" 
          @change="handleFileChange"
          @remove="removeImage"
        />
      </div>

      <!-- Footer -->
      <div class="p-8 bg-primary-50/50 border-t border-primary-50 flex justify-end gap-4">
        <button type="button" @click.stop="$emit('close')" class="px-8 py-3 text-sm font-bold text-primary-400 hover:text-primary-950 transition-colors">{{ readOnly ? 'Close' : 'Cancel' }}</button>
        <button v-if="!readOnly" type="button" @click="handleSave" class="btn-primary !px-12" :disabled="loading">
          <LucideLoader2 v-if="loading" class="w-5 h-5 animate-spin" />
          <span v-else>{{ isEdit ? 'Save Changes' : 'List Property' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideX, LucideLoader2 } from 'lucide-vue-next'
import BasicInfo from './sections/BasicInfo.vue'
import Specs from './sections/Specs.vue'
import LocationPicker from './sections/LocationPicker.vue'
import AmenitiesSelector from './sections/AmenitiesSelector.vue'
import GalleryUpload from './sections/GalleryUpload.vue'
import { useAlert } from '../../composables/useAlert'

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

const emit = defineEmits(['close', 'success'])
const auth = useAuthStore()
const alert = useAlert()
const isEdit = computed(() => !!props.editData)

const {
  form, loading, staff, heads, availableFeatures, previews,
  fetchDependencies, handleFileChange, removeImage, submitForm
} = usePropertyForm(() => props.editData)

onMounted(() => {
  fetchDependencies(auth.isAdmin, auth.isHeadAgent)
})

const handleSave = async () => {
  const result = await submitForm(isEdit.value)
  if (result.success) {
    alert.success('Success!', `Property ${isEdit.value ? 'updated' : 'created'} successfully.`)
    emit('success')
  } else {
    alert.error('Failed to save property', result.error)
  }
}
</script>
