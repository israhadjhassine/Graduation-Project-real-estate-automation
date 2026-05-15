import { ref, watch, computed, nextTick, type Ref } from 'vue'
import { usePropertyService } from '../services/propertyService'

export const usePropertyForm = (editData: Ref<any> | any = null) => {
    const propertyService = usePropertyService()
    const loading = ref(false)
    const selectedFiles = ref<File[]>([])
    const previews = ref<string[]>([])
    const existingImages = ref<any[]>([])
    const imagesToDelete = ref<number[]>([])
    const staff = ref<any[]>([])
    const heads = ref<any[]>([])
    const availableFeatures = ref<any[]>([])

    const initialForm = {
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
        country: 'Tunisia',
        neighborhood: '',
        address: '',
        postal_code: '',
        latitude: null as number | null,
        longitude: null as number | null,
        agent_id: null as number | null,
        owner_id: null as number | null,
        kitchens: 1,
        living_rooms: 1,
        floors: null as number | null,
        floor_number: null as number | null,
        feature_ids: [] as number[]
    }

    const form = ref({ ...initialForm })

    const resetForm = () => {
        form.value = { ...initialForm }
        selectedFiles.value = []
        previews.value = []
        existingImages.value = []
        imagesToDelete.value = []
    }

    // Handle both Ref and plain object for editData
    const editDataVal = computed(() => {
        return typeof editData === 'function' ? editData() : (editData?.value !== undefined ? editData.value : editData)
    })

    watch(editDataVal, (newVal) => {
        if (newVal) {
            const data = { ...newVal }
            // Ensure feature_ids is populated from features relation if available
            if (newVal.features && !data.feature_ids) {
                data.feature_ids = newVal.features.map((f: any) => f.id)
            }
            if (newVal.images) {
                existingImages.value = newVal.images
            }
            form.value = { ...initialForm, ...data }
        } else {
            resetForm()
        }
    }, { immediate: true, deep: true })

    const fetchDependencies = async (isAdmin: boolean, isHeadAgent: boolean) => {
        try {
            const promises: Promise<any>[] = [
                propertyService.getFeatures()
            ]

            if (isAdmin || isHeadAgent) {
                promises.push(propertyService.getStaff())
            }

            const results = await Promise.all(promises)
            availableFeatures.value = results[0].data

            if (isAdmin || isHeadAgent) {
                staff.value = results[1].data
            }

            if (isAdmin) {
                const headsRes = await propertyService.getHeads()
                heads.value = headsRes.data
            }
        } catch (e) {
            console.error("Failed to load dependency data", e)
        }
    }

    const handleFileChange = (e: Event) => {
        const target = e.target as HTMLInputElement
        if (!target.files) return

        const files = Array.from(target.files)
        selectedFiles.value.push(...files)

        files.forEach(file => {
            const reader = new FileReader()
            reader.onload = (e) => previews.value.push(e.target?.result as string)
            reader.readAsDataURL(file)
        })
    }

    const removeImage = async (index: number) => {
        const totalExisting = existingImages.value.length
        if (index < totalExisting) {
            const img = existingImages.value[index]
            imagesToDelete.value.push(img.id)
            existingImages.value.splice(index, 1)
        } else {
            const fileIndex = index - totalExisting
            selectedFiles.value.splice(fileIndex, 1)
            previews.value.splice(fileIndex, 1)
        }
    }

    const allPreviews = computed(() => {
        return [
            ...existingImages.value.map(img => img.image_url),
            ...previews.value
        ]
    })

    const prepareFormData = () => {
        const cleanForm = { ...form.value } as Record<string, any>
        const numericFields = ['price', 'area', 'bedrooms', 'bathrooms', 'kitchens', 'living_rooms', 'floors', 'floor_number']
        const floatFields = ['latitude', 'longitude']

        numericFields.forEach(field => {
            if (cleanForm[field] === "" || cleanForm[field] === undefined) {
                cleanForm[field] = null
            } else if (cleanForm[field] !== null) {
                cleanForm[field] = Number(cleanForm[field])
            }
        })

        floatFields.forEach(field => {
            if (cleanForm[field] === "" || cleanForm[field] === undefined || cleanForm[field] === null) {
                cleanForm[field] = null
            } else {
                cleanForm[field] = parseFloat(cleanForm[field])
            }
        })

        return cleanForm
    }

    const submitForm = async (isEdit: boolean) => {
        loading.value = true
        const data = prepareFormData()

        try {
            let propertyId
            if (imagesToDelete.value.length > 0) {
                await Promise.all(imagesToDelete.value.map(id => propertyService.deleteImage(id)))
            }

            if (isEdit && editDataVal.value) {
                await propertyService.updateProperty(editDataVal.value.id, data)
                propertyId = editDataVal.value.id
            } else {
                if (!data.slug) {
                    data.slug = data.title.toLowerCase().replace(/ /g, '-') + '-' + Date.now()
                }
                const propRes = await propertyService.createProperty(data)
                propertyId = propRes.data.id
            }

            if (selectedFiles.value.length > 0) {
                await propertyService.uploadImages(propertyId, selectedFiles.value)
            }

            return { success: true, id: propertyId }
        } catch (e: any) {
            console.error("Property save error:", e)
            const errorMsg = e.response?.data?.detail
                ? (typeof e.response.data.detail === 'string' ? e.response.data.detail : JSON.stringify(e.response.data.detail))
                : 'Failed to save property.'
            return { success: false, error: errorMsg }
        } finally {
            loading.value = false
        }
    }

    return {
        form,
        loading,
        staff,
        heads,
        availableFeatures,
        previews: allPreviews,
        existingImages,
        fetchDependencies,
        handleFileChange,
        removeImage,
        submitForm,
        resetForm
    }
}
