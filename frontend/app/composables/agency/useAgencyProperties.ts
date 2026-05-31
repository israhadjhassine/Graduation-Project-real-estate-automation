import { ref, computed } from 'vue'
import { useAgencyService } from '~/services/agencyService'
import { usePropertyService } from '~/services/propertyService'
import { useAlert } from '~/composables/useAlert'

export const useAgencyProperties = (onSuccess?: () => void) => {
  const agencyService = useAgencyService()
  const propertyService = usePropertyService()
  const alert = useAlert()

  // State
  const properties = ref<any[]>([])
  const loading = ref(false)

  // Computed properties
  const soldProperties = computed(() => properties.value.filter(p => p.status === 'sold'))
  const rentedProperties = computed(() => properties.value.filter(p => p.status === 'rented'))
  const activeProperties = computed(() => properties.value.filter(p => !['sold', 'pending_sold'].includes(p.status)))
  const pendingSales = computed(() => properties.value.filter(p => ['pending_sold', 'pending_rent'].includes(p.status)))
  const closedDealsCount = computed(() => soldProperties.value.length + rentedProperties.value.length)

  // Methods
  const fetchProperties = async () => {
    loading.value = true
    try {
      const res = await agencyService.getProperties()
      properties.value = res.data || []
    } catch (e) {
      console.error("Failed to fetch agency properties:", e)
    } finally {
      loading.value = false
    }
  }

  const deleteProperty = async (propertyId: number | string) => {
    const result = await alert.confirm(
      'Delete Property?', 
      'Are you sure you want to permanently delete this property listing?', 
      'Delete'
    )
    if (result.isConfirmed) {
      try {
        await propertyService.deleteProperty(propertyId)
        alert.success('Deleted', 'Property listing has been removed.')
        if (onSuccess) {
          onSuccess()
        } else {
          await fetchProperties()
        }
      } catch (e) {
        console.error("Failed to delete property:", e)
        alert.error('Delete Failed', 'Could not remove the property.')
      }
    }
  }

  const assignAgent = async (
    propertyId: number | string, 
    newAgentId: number | string | null,
    staffList: any[]
  ) => {
    try {
      const payload = newAgentId ? { agent_id: parseInt(newAgentId as string) } : { agent_id: null }
      await propertyService.assignProperty(propertyId, payload)
      
      const agentName = newAgentId ? staffList.find(s => s.id == newAgentId)?.full_name : 'Unassigned'
      alert.success('Agent Assigned', `Property successfully assigned to ${agentName}.`)
      
      if (onSuccess) {
        onSuccess()
      } else {
        await fetchProperties()
      }
    } catch (e) {
      console.error("Failed to assign agent:", e)
      alert.error('Assignment Failed', 'Could not update agent assignment.')
    }
  }

  return {
    properties,
    loading,
    soldProperties,
    rentedProperties,
    activeProperties,
    pendingSales,
    closedDealsCount,
    fetchProperties,
    deleteProperty,
    assignAgent
  }
}
