<template>
  <div class="bg-primary-50/20 min-h-screen">
    <!-- Header -->
    <div class="bg-primary-950 py-16 text-center border-b border-primary-900">
      <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">Get in Touch</h1>
      <p class="text-primary-300 font-medium max-w-lg mx-auto">
        Whether you are looking to buy, sell, or simply explore your options, our elite agents are here to assist you.
      </p>
    </div>

    <div class="max-w-7xl mx-auto px-6 py-16">
      <div class="grid lg:grid-cols-3 gap-12">
        
        <!-- Contact Information -->
        <div class="lg:col-span-1 space-y-8">
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

            <div class="mt-8 pt-8 border-t border-primary-50">
              <h4 class="font-bold text-primary-950 mb-4">Follow Us</h4>
              <div class="flex gap-4">
                <a href="#" class="w-10 h-10 border border-primary-200 rounded-full flex items-center justify-center text-primary-600 hover:bg-primary-950 hover:text-white hover:border-primary-950 transition-all">
                  <LucideFacebook class="w-4 h-4" />
                </a>
                <a href="#" class="w-10 h-10 border border-primary-200 rounded-full flex items-center justify-center text-primary-600 hover:bg-primary-950 hover:text-white hover:border-primary-950 transition-all">
                  <LucideInstagram class="w-4 h-4" />
                </a>
                <a href="#" class="w-10 h-10 border border-primary-200 rounded-full flex items-center justify-center text-primary-600 hover:bg-primary-950 hover:text-white hover:border-primary-950 transition-all">
                  <LucideLinkedin class="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Contact Form -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-3xl p-8 md:p-12 border border-primary-100 shadow-xl shadow-primary-900/5">
            <h3 class="text-2xl font-bold text-primary-950 mb-8">Send us a Message</h3>
            
            <form @submit.prevent="submitForm" class="space-y-6">
              <!-- Unauthenticated Fields -->
              <div v-if="!auth.isAuthenticated" class="space-y-6">
                <div class="grid md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="text-sm font-bold text-primary-950">First Name</label>
                    <input type="text" class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" placeholder="John" />
                  </div>
                  <div class="space-y-2">
                    <label class="text-sm font-bold text-primary-950">Last Name</label>
                    <input type="text" class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" placeholder="Doe" />
                  </div>
                </div>

                <div class="grid md:grid-cols-2 gap-6">
                  <div class="space-y-2">
                    <label class="text-sm font-bold text-primary-950">Email Address</label>
                    <input type="email" class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" placeholder="john@example.com" />
                  </div>
                  <div class="space-y-2">
                    <label class="text-sm font-bold text-primary-950">Phone Number</label>
                    <input type="tel" class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none" placeholder="+216 00 000 000" />
                  </div>
                </div>
              </div>

              <!-- Authenticated User Banner -->
              <div v-else class="flex items-center gap-4 p-4 bg-primary-50/50 border border-primary-100 rounded-2xl mb-6">
                <div class="w-12 h-12 bg-white rounded-xl shadow-sm border border-primary-100 flex items-center justify-center text-primary-900 font-bold text-lg">
                  {{ auth.user?.full_name?.charAt(0) }}
                </div>
                <div>
                  <p class="font-bold text-primary-950">{{ auth.user?.full_name }}</p>
                  <p class="text-sm text-primary-500">Sending as Client</p>
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-bold text-primary-950">Subject</label>
                <select class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none appearance-none">
                  <option>Property Inquiry</option>
                  <option>List my Property</option>
                  <option>Career Opportunities</option>
                  <option>General Support</option>
                </select>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-bold text-primary-950">Message</label>
                <textarea rows="5" class="w-full bg-primary-50 border border-primary-100 rounded-xl px-4 py-3 text-sm font-medium focus:border-accent-400 focus:bg-white focus:ring-4 focus:ring-accent-500/10 transition-all outline-none resize-none" placeholder="How can we help you?"></textarea>
              </div>

              <button type="submit" class="w-full py-4 bg-primary-950 hover:bg-primary-900 text-white rounded-xl font-bold transition-all shadow-lg flex items-center justify-center gap-2">
                <LucideSend class="w-4 h-4" /> Send Message
              </button>
            </form>
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

const submitForm = () => {
  // In a real implementation, this would connect to an API backend
  alert("Thank you for your message. An agent will contact you shortly.")
}

useHead({
  title: 'Contact Us | Elite Real Estate'
})
</script>
