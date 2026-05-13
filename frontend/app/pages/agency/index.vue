<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Head Agent Header -->
      <div class="flex items-center justify-between mb-10 pb-8 border-b border-primary-100">
        <div>
          <h1 class="text-3xl font-extrabold text-primary-950 !font-sans tracking-tight">Management Workspace</h1>
          <p class="text-primary-500 font-medium mt-1">Agency Operations • Team Oversight • Listing Control</p>
        </div>
        <button @click="showModal = true" class="btn-primary !rounded-lg px-6 py-3">
          <LucidePlus class="w-5 h-5 mr-2" /> List New Property
        </button>
      </div>

      <!-- Quick Stats -->
      <div class="grid md:grid-cols-3 gap-6 mb-10">
        <div class="card-premium border-l-4 border-l-primary-900 !rounded-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
              <LucideHome class="w-6 h-6 text-primary-900" />
            </div>
            <div>
              <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Agency Listings</p>
              <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ properties.length }}</p>
            </div>
          </div>
        </div>

        <div class="card-premium border-l-4 border-l-accent-600 !rounded-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-accent-50 rounded-lg flex items-center justify-center">
              <LucideUsers class="w-6 h-6 text-accent-600" />
            </div>
            <div>
              <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Sub-Agents</p>
              <p class="text-2xl font-bold text-primary-950 mt-0.5">{{ staff.length }}</p>
            </div>
          </div>
        </div>

        <div class="card-premium border-l-4 border-l-green-600 !rounded-lg">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
              <LucideEye class="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p class="text-[10px] font-bold text-primary-400 uppercase tracking-[0.2em]">Total Client Views</p>
              <p class="text-2xl font-bold text-primary-950 mt-0.5">2,492</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex gap-2 border-b border-primary-100 mb-8 overflow-x-auto pb-0">
        <button 
          @click="activeTab = 'properties'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'properties' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideHome class="w-4 h-4 inline-block mr-2" /> Properties Portfolio
        </button>
        <button 
          @click="activeTab = 'staff'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'staff' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideUsers class="w-4 h-4 inline-block mr-2" /> Sub-Agent Team
        </button>
        <button 
          @click="activeTab = 'schedule'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'schedule' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideCalendar class="w-4 h-4 inline-block" /> Team Schedule
        </button>
        <button 
          @click="activeTab = 'sold'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'sold' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideCheckCircle2 class="w-4 h-4 inline-block mr-2" /> Sold Properties
        </button>
        <button 
          @click="activeTab = 'rented'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2', activeTab === 'rented' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideHome class="w-4 h-4 inline-block mr-2" /> Rented Properties
        </button>
        <button 
          @click="activeTab = 'analytics'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'analytics' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucidePieChart class="w-4 h-4 inline-block" /> Team Performance
        </button>
        <button 
          @click="activeTab = 'inquiries'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'inquiries' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideMessageSquare class="w-4 h-4 inline-block" /> Inquiries
          <span v-if="pendingSales.length" class="bg-amber-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center ml-1">{{ pendingSales.length }}</span>
        </button>
        <button 
          v-if="auth.isAdmin || auth.isHeadAgent"
          @click="activeTab = 'reports'" 
          :class="['px-5 py-3 text-sm font-bold transition-all whitespace-nowrap border-b-2 flex items-center gap-2', activeTab === 'reports' ? 'border-primary-950 text-primary-950' : 'border-transparent text-primary-400 hover:text-primary-600']"
        >
          <LucideFileText class="w-4 h-4 inline-block" /> Transaction Reports
        </button>
      </div>

      <!-- Tab Content: Properties -->
      <div v-show="activeTab === 'properties'">
        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Status</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Head Agent</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Assigned Agent</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Price</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-50">
              <tr v-for="prop in activeProperties" :key="prop.id" @click="viewProperty(prop)" class="hover:bg-primary-50/50 transition-colors cursor-pointer group">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-4">
                     <div class="w-12 h-12 rounded-xl overflow-hidden bg-primary-100 flex-shrink-0">
                       <img v-if="prop.images?.length" :src="getPublicUrl(prop.images[0].image_url)" class="w-full h-full object-cover" />
                       <LucideImage v-else class="w-12 h-12 p-3 text-primary-200" />
                    </div>
                    <div>
                    <div>
                      <p class="font-bold text-primary-950 text-sm max-w-xs truncate group-hover:text-accent-600 transition-colors">{{ prop.title }}</p>
                      <p class="text-[10px] text-primary-400">{{ prop.city }}, {{ prop.country }}</p>
                    </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span v-if="prop.status === 'sold'" class="px-2 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded-lg uppercase">Sold</span>
                  <span v-else-if="prop.status === 'pending_sold'" class="px-2 py-1 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-lg uppercase">Pending Sale</span>
                  <span v-else-if="prop.status === 'rented'" class="px-2 py-1 bg-purple-100 text-purple-700 text-[10px] font-bold rounded-lg uppercase block mb-1 w-max">Currently Rented</span>
                  <span v-else-if="prop.status === 'pending_rent'" class="px-2 py-1 bg-amber-100 text-amber-700 text-[10px] font-bold rounded-lg uppercase block mb-1 w-max">Pending Rent</span>
                  <span v-else class="px-2 py-1 bg-blue-100 text-blue-700 text-[10px] font-bold rounded-lg uppercase">Available</span>
                  
                  <div v-if="prop.status === 'rented' && prop.rent_end_date" class="text-[9px] text-primary-500 font-medium mt-1">
                    Available again from: <br/><span class="font-bold text-primary-700">{{ new Date(prop.rent_end_date).toLocaleDateString() }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="flex flex-col">
                    <span class="text-sm font-medium text-primary-950 truncate max-w-[120px]" :title="prop.owner?.full_name">
                      {{ prop.owner?.full_name || 'System' }}
                    </span>
                    <span v-if="prop.owner_id === auth.user?.id" class="text-[8px] text-accent-600 font-bold uppercase tracking-tighter">Your Listing</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <select 
                    v-if="auth.isAdmin || prop.owner_id === auth.user?.id"
                    :value="prop.agent_id" 
                    @change.stop="assignAgent(prop.id, $event.target.value)" 
                    @click.stop
                    class="bg-primary-50 text-primary-950 font-medium text-xs rounded-lg px-2 py-1.5 border border-primary-200 outline-none focus:border-accent-400 w-full"
                  >
                    <option :value="null">Unassigned</option>
                    <option v-for="agent in staff" :key="agent.id" :value="agent.id">{{ agent.full_name }}</option>
                  </select>
                  <span v-else class="text-xs text-primary-400 font-medium italic">
                    {{ prop.agent?.full_name || 'Unassigned' }}
                  </span>
                </td>
                <td class="px-6 py-4 font-bold text-primary-950 text-sm">
                  {{ formatPrice(prop.price) }} <span class="text-[10px]">{{ prop.currency }}</span>
                </td>
                <td class="px-6 py-4">
                    <div class="flex gap-1" @click.stop>
                      <template v-if="auth.isAdmin || prop.owner_id === auth.user?.id">
                        <button @click="editProperty(prop)" class="p-2 hover:bg-primary-100 rounded-lg text-primary-400 transition-colors" title="Edit Property">
                          <LucideEdit class="w-4 h-4" />
                        </button>
                        <button @click="deleteProperty(prop.id)" class="p-2 hover:bg-red-50 rounded-lg text-red-400 transition-colors" title="Delete Property">
                          <LucideTrash2 class="w-4 h-4" />
                        </button>
                      </template>
                      <button v-else @click="viewProperty(prop)" class="p-2 hover:bg-primary-100 rounded-lg text-primary-400 transition-colors" title="View Details">
                        <LucideEye class="w-4 h-4" />
                      </button>
                    </div>
                </td>
              </tr>
              <tr v-if="!properties.length">
                <td colspan="5" class="px-6 py-12 text-center text-primary-500">
                  <LucideHome class="w-12 h-12 mx-auto text-primary-200 mb-3" />
                  <p>No properties found for this manager.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab Content: Staff Team -->
      <div v-show="activeTab === 'staff'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Sub-Agent Management</h2>
        </div>

        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Sub-Agent Name</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Email Address</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Phone Number</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Assigned Properties</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600">Status</th>
                <th class="px-6 py-4 text-xs font-bold text-primary-600 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-100">
              <tr v-for="agent in staff" :key="agent.id" class="hover:bg-primary-50/50">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-950 font-bold text-xs">
                      {{ agent.full_name.charAt(0) }}
                    </div>
                    <span class="text-sm font-bold text-primary-950">{{ agent.full_name }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-primary-600">{{ agent.email }}</td>
                <td class="px-6 py-4 text-sm text-primary-600">{{ agent.phone_number || 'N/A' }}</td>
                <td class="px-6 py-4">
                  <span class="px-3 py-1 bg-primary-100 text-primary-700 text-[10px] font-bold rounded-lg uppercase">
                    {{ properties.filter(p => p.agent_id === agent.id).length }} Listings
                  </span>
                </td>
                <td class="px-6 py-4">
                  <span :class="[
                    'px-2 py-1 text-[10px] font-bold rounded-lg uppercase',
                    agent.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  ]">
                    {{ agent.is_active ? 'Active' : 'Disabled' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button 
                    @click="toggleAgentStatus(agent.id)"
                    :class="[
                      'text-[10px] font-bold uppercase transition-colors',
                      agent.is_active ? 'text-red-500 hover:text-red-700' : 'text-green-500 hover:text-green-700'
                    ]"
                  >
                    {{ agent.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                </td>
              </tr>
              <tr v-if="!staff.length">
                <td colspan="4" class="px-6 py-12 text-center text-primary-500">
                  <LucideUsers class="w-12 h-12 mx-auto text-primary-200 mb-3" />
                  <p>You have not recruited any Sub-Agents yet.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab Content: Team Schedule -->
      <div v-show="activeTab === 'schedule'">
        <div class="mb-6">
          <h2 class="text-xl font-bold text-primary-950">Team Visit Schedule</h2>
          <p class="text-xs text-primary-500 mt-1">Consolidated view of all upcoming visits across your sub-agent team.</p>
        </div>
        
        <AgencyTeamCalendar :visits="visits" :agents="staff" @view-visit="viewVisitDetails" />
      </div>

      <!-- Tab Content: Sold Properties -->
      <div v-show="activeTab === 'sold'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Sold Portfolio</h2>
        </div>

        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Sold By</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Client Email</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Price</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-50">
              <tr v-for="prop in soldProperties" @click="viewProperty(prop)" :key="prop.id" class="hover:bg-primary-50/50 transition-colors cursor-pointer group">
                <td class="px-6 py-4">
                   <p class="font-bold text-primary-950 text-sm group-hover:text-accent-600 transition-colors">{{ prop.title }}</p>
                </td>
                <td class="px-6 py-4">
                   <span class="text-xs font-medium text-primary-600">{{ staff.find(s => s.id === prop.agent_id)?.full_name || 'System' }}</span>
                </td>
                <td class="px-6 py-4">
                   <span class="text-xs font-medium text-primary-600">{{ clients.find(c => c.id === prop.buyer_id)?.email || 'Unknown' }}</span>
                </td>
                <td class="px-6 py-4 font-bold text-primary-950 text-sm">
                  {{ formatPrice(prop.price) }} <span class="text-[10px]">{{ prop.currency }}</span>
                </td>
              </tr>
              <tr v-if="!soldProperties.length">
                <td colspan="3" class="px-6 py-12 text-center text-primary-500">
                  <LucideCheckCircle2 class="w-12 h-12 mx-auto text-primary-200 mb-3" />
                  <p>No properties have been marked as sold yet.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab Content: Rented Properties -->
      <div v-show="activeTab === 'rented'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Rented Portfolio</h2>
        </div>

        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Agent</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Client Email</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Rent Duration</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-50">
              <tr v-for="prop in rentedProperties" @click="viewProperty(prop)" :key="prop.id" class="hover:bg-primary-50/50 transition-colors cursor-pointer group">
                <td class="px-6 py-4">
                   <p class="font-bold text-primary-950 text-sm group-hover:text-accent-600 transition-colors">{{ prop.title }}</p>
                </td>
                <td class="px-6 py-4">
                   <span class="text-xs font-medium text-primary-600">{{ staff.find(s => s.id === prop.agent_id)?.full_name || 'System' }}</span>
                </td>
                <td class="px-6 py-4">
                   <span class="text-xs font-medium text-primary-600">{{ clients.find(c => c.id === prop.buyer_id)?.email || 'Unknown' }}</span>
                </td>
                <td class="px-6 py-4 text-xs font-bold text-primary-950">
                  {{ new Date(prop.rent_start_date).toLocaleDateString() }} to {{ new Date(prop.rent_end_date).toLocaleDateString() }}
                </td>
              </tr>
              <tr v-if="!rentedProperties.length">
                <td colspan="3" class="px-6 py-12 text-center text-primary-500">
                  <LucideHome class="w-12 h-12 mx-auto text-primary-200 mb-3" />
                  <p>No properties have been marked as rented yet.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tab Content: Approvals -->
      <div v-show="activeTab === 'inquiries'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Transaction Approval Queue</h2>
        </div>
        <div class="grid md:grid-cols-2 gap-6">
          <div v-for="inq in inquiries" :key="inq.id" class="card-premium">
            <div class="flex items-center justify-between mb-4">
              <span class="px-2 py-1 text-[10px] font-bold rounded-lg uppercase bg-amber-100 text-amber-700">
                {{ inq.request_type }} REQUEST
              </span>
              <span class="text-[10px] text-primary-400 font-bold uppercase">{{ inq.status }}</span>
            </div>
            
            <p class="text-sm font-bold text-primary-950 mb-1">{{ inq.subject }}</p>
            <p class="text-xs text-primary-600 mb-4">{{ inq.message }}</p>
            
            <div class="bg-primary-50 rounded-xl p-4 mb-4">
              <div class="flex justify-between items-center mb-2">
                <span class="text-[10px] font-bold text-primary-400 uppercase">Negotiated Price</span>
                <span class="text-sm font-bold text-primary-950">{{ formatPrice(inq.price) }} TND</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[10px] font-bold text-primary-400 uppercase">Requester</span>
                <span class="text-xs font-medium text-primary-700">{{ inq.name.split(' for ')[0] }}</span>
              </div>
            </div>

            <div class="flex items-center gap-3 pt-4 border-t border-primary-100">
               <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-[10px] font-bold">
                 {{ inq.name.split(' for ')[1]?.charAt(0) || 'C' }}
               </div>
               <div>
                 <p class="text-[10px] font-bold text-primary-950">Client: {{ inq.name.split(' for ')[1] || inq.name }}</p>
                 <p class="text-[10px] text-primary-400">{{ inq.email || 'No email provided' }}</p>
               </div>
            </div>
            
            <!-- Approval Actions -->
            <div class="mt-4 pt-4 border-t border-primary-100 space-y-2">
               <div class="flex gap-2">
                 <button 
                   @click="updateInquiryStatus(inq.id, 'replied')" 
                   class="flex-1 py-2 bg-primary-900 hover:bg-black text-white rounded-xl text-[10px] font-bold uppercase transition-all"
                 >
                   ✓ Approve & Finalize
                 </button>
                 <button 
                   @click="updateInquiryStatus(inq.id, 'closed')" 
                   class="flex-1 py-2 bg-primary-50 hover:bg-primary-100 text-primary-600 border border-primary-200 rounded-xl text-[10px] font-bold uppercase transition-all"
                 >
                   ✗ Reject
                 </button>
               </div>
            </div>
          </div>
          <div v-if="!inquiries.length" class="col-span-full py-12 text-center text-primary-400">
             <LucideCheckCircle2 class="w-12 h-12 mx-auto text-primary-100 mb-3" />
             <p>No pending transaction requests found.</p>
          </div>
        </div>
      </div>

      <!-- Tab Content: Analytics -->
      <div v-show="activeTab === 'analytics'">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-primary-950">Team Analytics & KPIs</h2>
        </div>
        <div v-if="loading" class="grid md:grid-cols-2 gap-6 animate-pulse">
           <div class="h-64 bg-white rounded-[2rem]"></div>
           <div class="h-64 bg-white rounded-[2rem]"></div>
        </div>
        <div v-else class="grid lg:grid-cols-2 gap-8">
           <!-- Doughnut: Property Statuses -->
           <div class="card-premium h-[400px] flex flex-col">
              <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Agency Portfolio Status</h3>
              <div class="flex-1 relative">
                 <ChartsDoughnutChart v-if="propertyStatusChartData" :chart-data="propertyStatusChartData" />
              </div>
           </div>
           
           <!-- Bar: Agent Performance -->
           <div class="card-premium h-[400px] flex flex-col">
              <h3 class="text-sm font-bold text-primary-400 uppercase tracking-widest mb-4">Sub-Agent Closed Deals</h3>
              <div class="flex-1 relative">
                 <ChartsBarChart v-if="agentPerformanceChartData" :chart-data="agentPerformanceChartData" />
              </div>
           </div>
        </div>
      </div>

      <!-- Tab Content: Reports -->
      <div v-show="activeTab === 'reports' && (auth.isAdmin || auth.isHeadAgent)">
        <div class="card-premium p-0 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-primary-50">
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Property Title</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Type</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest">Date</th>
                <th class="px-6 py-4 text-[10px] font-bold text-primary-400 uppercase tracking-widest text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-primary-50">
              <tr v-for="report in reports" :key="report.id" class="hover:bg-primary-50/30 transition-colors">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <LucideFileText class="w-5 h-5 text-primary-400" />
                    <span class="font-bold text-primary-950 text-sm">{{ report.property_title }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span class="text-xs font-medium text-primary-600">{{ report.type }}</span>
                </td>
                <td class="px-6 py-4">
                  <span class="text-xs font-medium text-primary-600">{{ report.date }}</span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button @click="downloadReport(report)" class="px-4 py-2 bg-primary-100 hover:bg-primary-200 text-primary-700 rounded-xl text-[10px] font-bold uppercase transition-all inline-flex items-center gap-2">
                    <LucideDownload class="w-3 h-3" /> Download
                  </button>
                </td>
              </tr>
              <tr v-if="!reports.length">
                <td colspan="4" class="py-12 text-center text-primary-400">
                  No transaction reports found. Reports are generated upon transaction approval.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <PropertyUploadModal 
      :show="showModal" 
      :edit-data="selectedProperty"
      :read-only="isReadOnly"
      @close="handleClose" 
      @success="handleSuccess"
    />

    <VisitDetailsModal 
      v-if="selectedVisit"
      :isOpen="isVisitModalOpen"
      :visit="selectedVisit"
      @close="isVisitModalOpen = false"
    />

  </div>
</template>

<script setup>
import { 
  LucideBriefcase, LucideHome, LucideUsers, LucideEye,
  LucidePlus, LucideImage, LucideEdit, LucideTrash2,
  LucideUserPlus, LucideX, LucideCheckCircle2,
  LucideMessageSquare, LucideFileText, LucideDownload, LucidePieChart,
  LucideCalendar
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'
import { useAssetUrl } from '~/composables/useAssetUrl'
import { useAlert } from '~/composables/useAlert'
import VisitDetailsModal from '~/components/agency/VisitDetailsModal.vue'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const api = useApi()
const alert = useAlert()
const { getPublicUrl } = useAssetUrl()
const activeTab = ref('properties')
const properties = ref([])
const staff = ref([])
const inquiries = ref([])
const reports = ref([])
const clients = ref([])
const visits = ref([])
const loading = ref(false)

const isVisitModalOpen = ref(false)
const selectedVisit = ref(null)

const soldProperties = computed(() => properties.value.filter(p => p.status === 'sold'))
const rentedProperties = computed(() => properties.value.filter(p => p.status === 'rented'))
const activeProperties = computed(() => properties.value.filter(p => !['sold', 'pending_sold'].includes(p.status)))
const pendingSales = computed(() => properties.value.filter(p => ['pending_sold', 'pending_rent'].includes(p.status)))

// Statistics State
const statistics = ref(null)

const propertyStatusChartData = computed(() => {
  if (!statistics.value || !statistics.value.property_statuses) return null
  const data = statistics.value.property_statuses
  return {
    labels: Object.keys(data).map(k => k.replace('_', ' ').toUpperCase()),
    datasets: [{
      data: Object.values(data),
      backgroundColor: ['#6366f1', '#a855f7', '#ec4899', '#14b8a6', '#f59e0b'],
      borderWidth: 0,
      hoverOffset: 10
    }]
  }
})

const agentPerformanceChartData = computed(() => {
  if (!statistics.value || !statistics.value.team_performance) return null
  const data = statistics.value.team_performance
  
  // Sort by deals desc
  const sorted = [...data].sort((a,b) => b.deals - a.deals)
  
  return {
    labels: sorted.map(d => d.agent),
    datasets: [{
      label: 'Closed Deals',
      data: sorted.map(d => d.deals),
      backgroundColor: '#3b82f6',
      borderRadius: 6
    }]
  }
})

const showModal = ref(false)
const selectedProperty = ref(null)
const isReadOnly = ref(false)

const editProperty = (prop) => {
  isReadOnly.value = false
  selectedProperty.value = prop
  showModal.value = true
}

const viewProperty = (prop) => {
  isReadOnly.value = true
  selectedProperty.value = prop
  showModal.value = true
}

const viewVisitDetails = (visit) => {
  selectedVisit.value = visit
  isVisitModalOpen.value = true
}

const deleteProperty = async (propertyId) => {
  const result = await alert.confirm('Delete Property?', 'Are you sure you want to permanently delete this property listing?', 'Delete')
  if (result.isConfirmed) {
    try {
      await api.delete(`/properties/${propertyId}`)
      alert.success('Deleted', 'Property listing has been removed.')
      fetchData()
    } catch (e) {
      console.error("Failed to delete property", e)
      alert.error('Delete Failed', 'Could not remove the property.')
    }
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [propsRes, staffRes, inqRes, clientsRes, statsRes, visitsRes] = await Promise.all([
      api.get('/agency/properties'),
      api.get('/agency/staff'),
      api.get('/agent/inquiries'),
      api.get('/agency/clients'),
      api.get('/statistics/agency'),
      api.get('/agent/visits')
    ])
    
    properties.value = propsRes.data
    staff.value = staffRes.data
    inquiries.value = inqRes.data
    clients.value = clientsRes.data
    statistics.value = statsRes.data
    visits.value = visitsRes.data
    
    if (auth.isAdmin || auth.isHeadAgent) {
      try {
        const reportsRes = await api.get('/admin/reports')
        reports.value = reportsRes.data
      } catch (e) {
        console.error("Failed to fetch reports", e)
      }
    }
    
    // console.log("Agency Dashboard Sync Success:", { ... })
  } catch (e) {
    console.error("Dashboard fetch error:", e)
  } finally {
    loading.value = false
  }
}

const handleSuccess = () => {
  showModal.value = false
  selectedProperty.value = null
  fetchData()
}

const handleClose = () => {
  showModal.value = false
  selectedProperty.value = null
  isReadOnly.value = false
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}

const assignAgent = async (propertyId, newAgentId) => {
  try {
    const payload = newAgentId ? { agent_id: parseInt(newAgentId) } : { agent_id: null }
    await api.put(`/properties/${propertyId}/assign`, payload)
    fetchData()
  } catch (e) {
    console.error("Failed to assign agent", e)
  }
}

const updateInquiryStatus = async (inquiryId, status) => {
  try {
    await api.put(`/agent/inquiries/${inquiryId}/status?status=${status}`)
    alert.success('Updated', 'Inquiry status has been updated.')
    fetchData()
  } catch (e) {
    console.error("Failed to update inquiry status", e)
    alert.error('Update Failed', "Could not update status.")
  }
}

const toggleAgentStatus = async (agentId) => {
  try {
    await api.patch(`/agency/staff/${agentId}/toggle-status`, {})
    fetchData()
  } catch (e) {
    console.error("Failed to toggle agent status", e)
    alert.error('Status Update Failed', e.response?.data?.detail || 'Failed to update status')
  }
}

const downloadReport = async (report) => {
  try {
    const config = useRuntimeConfig()
    let apiUrl = config.public.apiUrl
    if (process.client && apiUrl.includes('backend')) {
      apiUrl = 'http://localhost:8000'
    }
    const res = await fetch(`${apiUrl}/admin/reports/${report.id}/download`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    if (!res.ok) throw new Error("Failed to download")
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const filename = `Report_${report.type}_${report.property_title.replace(/\s+/g, '_')}.pdf`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
  } catch (e) {
    console.error("Failed to download report", e)
    alert.error('Download Failed', "Could not download report.")
  }
}

onMounted(() => {
  watchEffect(() => {
    if (auth.isInitialized) {
      if (!auth.isHeadAgent && !auth.isAdmin) {
        navigateTo('/')
      } else {
        fetchData()
      }
    }
  })
})

useHead({
  title: 'Agency Dashboard | Elite Real Estate'
})
</script>
