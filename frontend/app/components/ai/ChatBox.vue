<template>
  <div class="card-premium h-[500px] flex flex-col p-0 overflow-hidden relative">
    <!-- Header -->
    <div class="p-6 bg-primary-950 text-white flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-accent-500 rounded-xl flex items-center justify-center">
          <LucideBot class="w-6 h-6 text-white" />
        </div>
        <div>
          <h4 class="font-bold text-sm">Property Assistant</h4>
          <p class="text-[10px] text-accent-300 uppercase tracking-widest font-bold">Powered by Gemini Pro</p>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="messageContainer">
      <div v-for="(msg, i) in messages" :key="i" 
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div :class="[
          'max-w-[80%] px-4 py-3 rounded-2xl text-sm shadow-sm transition-all animate-in fade-in slide-in-from-bottom-2',
          msg.role === 'user' 
            ? 'bg-primary-700 text-white rounded-tr-none' 
            : 'bg-primary-50 text-primary-950 rounded-tl-none border border-primary-100'
        ]">
          {{ msg.content }}
        </div>
      </div>
      <div v-if="loading" class="flex justify-start">
        <div class="bg-primary-50 px-4 py-3 rounded-2xl rounded-tl-none border border-primary-100 italic text-primary-300 text-xs flex items-center gap-2">
          <LucideLoader2 class="w-3 h-3 animate-spin" />
          Thinking...
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="p-4 border-t border-primary-100 bg-primary-50/50">
      <div class="relative flex items-center">
        <input 
          v-model="input"
          @keyup.enter="sendMessage"
          placeholder="Ask anything about this property..."
          class="w-full bg-white border border-primary-200 rounded-full pl-6 pr-14 py-3 text-sm focus:ring-4 focus:ring-accent-50 focus:border-accent-400 transition-all outline-none"
        />
        <button 
          @click="sendMessage"
          class="absolute right-1.5 w-10 h-10 bg-accent-500 rounded-full flex items-center justify-center text-white hover:bg-accent-600 active:scale-90 transition-all shadow-lg shadow-accent-500/30"
        >
          <LucideSend class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { LucideBot, LucideSend, LucideLoader2 } from 'lucide-vue-next'

const props = defineProps({
  propertyId: {
    type: Number,
    required: true
  }
})

const api = useApi()
const input = ref('')
const loading = ref(false)
const messages = ref([
  { role: 'assistant', content: "Hello! I'm your Elite Assistant. I've studied the details of this property. How can I help you today?" }
])
const messageContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!input.value || loading.value) return
  
  const userMsg = input.value
  input.value = ''
  messages.value.push({ role: 'user', content: userMsg })
  await scrollToBottom()
  
  loading.value = true
  try {
    const res = await api.post(`/properties/${props.propertyId}/ask`, {
      question: userMsg
    })
    messages.value.push({ role: 'assistant', content: res.data.answer })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: "I'm having trouble connecting to my brain right now. Please try again later." })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}
</script>
