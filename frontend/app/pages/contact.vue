<template>
  <div class="bg-primary-50/20 min-h-screen">
    <!-- Header -->
    <div class="bg-primary-950 py-16 text-center border-b border-primary-900">
      <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Get in Touch</h1>
      <p class="text-primary-300 font-medium max-w-lg mx-auto">
        Whether you are looking to buy, sell, or simply explore your options, our elite agents are here to assist you.
      </p>
    </div>

    <div class="max-w-4xl mx-auto px-6 py-16">
      <div class="flex justify-center">
        
        <!-- Contact Information -->
        <div class="w-full max-w-xl space-y-8">
          <div class="bg-white rounded-3xl p-8 border border-primary-100 shadow-xl shadow-primary-900/5">
            <h3 class="text-2xl font-bold text-primary-950 mb-6">Contact Information</h3>
            
            <div class="space-y-6">
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-accent-50 rounded-2xl flex items-center justify-center shrink-0">
                  <LucideMapPin class="w-6 h-6 text-accent-600" />
                </div>
                <div>
                  <p class="font-bold text-primary-950">Head Office</p>
                  <p class="text-primary-600 mt-1">Les Berges du Lac 2,<br>1053 Tunis, Tunisia</p>
                </div>
              </div>

              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-accent-50 rounded-2xl flex items-center justify-center shrink-0">
                  <LucidePhone class="w-6 h-6 text-accent-600" />
                </div>
                <div>
                  <p class="font-bold text-primary-950">Phone</p>
                  <p class="text-primary-600 mt-1">+216 71 123 456<br>+216 22 987 654</p>
                </div>
              </div>

              <div class="flex items-start gap-4">
                <div class="w-12 h-12 bg-accent-50 rounded-2xl flex items-center justify-center shrink-0">
                  <LucideMail class="w-6 h-6 text-accent-600" />
                </div>
                <div>
                  <p class="font-bold text-primary-950">Email</p>
                  <p class="text-primary-600 mt-1">contact@elite-estate.tn<br>support@elite-estate.tn</p>
                </div>
              </div>
            </div>

            
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  LucideMapPin, LucidePhone, LucideMail,
  LucideFacebook, LucideInstagram, LucideLinkedin,
  LucideSend
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()

useHead({
  title: 'Contact Us | Elite Real Estate'
})
</script>
