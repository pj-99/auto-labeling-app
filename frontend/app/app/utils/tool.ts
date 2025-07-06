import chroma from "chroma-js"

export function encodeUuidToBase64(uuidStr: string): string {
    // TODO
    return uuidStr
}


export function decodeBase64ToUuid(b64: string): string {
    // TODO
    return b64
}

export const colors = computed(() => chroma.scale('Spectral').mode('lab').colors(10))

// Get a consistent color for a class ID
export const getClassColor = (classId: string) => {
    if (classId == null) return colors.value[colors.value.length - 1]!
    return colors.value[Number(classId) % colors.value.length]!
}
