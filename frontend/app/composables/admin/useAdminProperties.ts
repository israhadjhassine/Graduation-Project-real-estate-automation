import { ref, computed } from 'vue'
import { usePropertyService } from '~/services/propertyService'

export const useAdminProperties = () => {
  const propertyService = usePropertyService()

  const properties = ref<any[]>([])
  const loading = ref(false)
  const propSearchQuery = ref('')
  const propLocationQuery = ref('')

  const filteredProperties = computed(() => {
    return properties.value.filter(p => {
      const matchesSearch = !propSearchQuery.value || 
        p.title.toLowerCase().includes(propSearchQuery.value.toLowerCase())
      
      const matchesLocation = !propLocationQuery.value || 
        p.city?.toLowerCase().includes(propLocationQuery.value.toLowerCase())
        
      return matchesSearch && matchesLocation
    })
  })

  const closedDealsCount = computed(() => 
    properties.value.filter(p => ['sold', 'rented'].includes(p.status)).length
  )

  const fetchProperties = async () => {
    loading.value = true
    try {
      const res = await propertyService.getProperties()
      properties.value = res.data || []
    } catch (e) {
      console.error("Failed to load properties", e)
    } finally {
      loading.value = false
    }
  }

  return {
    properties,
    loading,
    propSearchQuery,
    propLocationQuery,
    filteredProperties,
    closedDealsCount,
    fetchProperties
  }
}
