<template>
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
          <select v-model="form.city" :disabled="readOnly" class="form-input !pl-16 appearance-none cursor-pointer" style="padding-left: 4rem !important;">
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
            <option value="studio">Studio</option>
            <option value="office">Office</option>
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
      <div v-if="isAdmin || isHeadAgent">
        <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Assign Agent</label>
        <select v-model="form.agent_id" :disabled="readOnly" class="form-input">
          <option :value="null">Unassigned</option>
          <option v-for="agent in staff" :key="agent.id" :value="agent.id">{{ agent.full_name }}</option>
        </select>
      </div>
      
      <!-- Owner Assignment (Admin only) -->
      <div v-if="isAdmin">
        <label class="block text-xs font-bold text-primary-400 uppercase tracking-widest mb-3">Team Assignment (Head Agent)</label>
        <select v-model="form.owner_id" :disabled="readOnly" class="form-input">
          <option :value="null">No Team (Admin Managed)</option>
          <option v-for="head in heads" :key="head.id" :value="head.id">{{ head.full_name }}</option>
        </select>
      </div>
    </div>
  </section>
</template>

<script setup>
import { LucideMapPin } from 'lucide-vue-next'
import { tunisianGovernorates } from '../../../constants/location'

const props = defineProps({
  form: Object,
  readOnly: Boolean,
  isAdmin: Boolean,
  isHeadAgent: Boolean,
  staff: Array,
  heads: Array
})
</script>

<style scoped>
.form-input {
  @apply w-full bg-primary-50/50 border border-primary-100 rounded-2xl px-5 py-4 text-sm focus:ring-4 focus:ring-primary-500/5 focus:border-primary-500 outline-none transition-all placeholder:text-primary-200;
}
</style>
