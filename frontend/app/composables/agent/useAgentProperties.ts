import { ref } from 'vue'
import { useAgentService } from '~/services/agentService'
import { usePropertyService } from '~/services/propertyService'
import { useAgencyService } from '~/services/agencyService'

export const useAgentProperties = () => {
  const agentService = useAgentService()
  const propertyService = usePropertyService()
  const agencyService = useAgencyService()

  // State
  const myProperties = ref<any[]>([])
  const clients = ref<any[]>([])
  const loading = ref(false)

  // Methods
  const fetchPropertiesAndClients = async () => {
    loading.value = true
    try {
      const [propsRes, clientsRes] = await Promise.all([
        agentService.getProperties(),
        agencyService.getClients()
      ])
      myProperties.value = propsRes.data || []
      clients.value = clientsRes.data || []
    } catch (e) {
      console.error("Failed to fetch agent properties and clients:", e)
    } finally {
      loading.value = false
    }
  }

  const submitSaleRequest = async (propertyId: number | string, clientId: number | string) => {
    const prop = myProperties.value.find(p => p.id === propertyId)
    if (!prop) {
      throw new Error("Property not found")
    }
    await propertyService.requestTransaction(propertyId, { 
      type: 'Sale',
      price: prop.price,
      client_id: clientId 
    })
  }

  const submitRentRequest = async (
    propertyId: number | string, 
    clientId: number | string, 
    startDate: string, 
    endDate: string
  ) => {
    const prop = myProperties.value.find(p => p.id === propertyId)
    if (!prop) {
      throw new Error("Property not found")
    }
    await propertyService.requestTransaction(propertyId, { 
      type: 'Rent',
      price: prop.price,
      client_id: clientId,
      rent_start_date: new Date(startDate).toISOString(),
      rent_end_date: new Date(endDate).toISOString()
    })
  }

  return {
    myProperties,
    clients,
    loading,
    fetchPropertiesAndClients,
    submitSaleRequest,
    submitRentRequest
  }
}
