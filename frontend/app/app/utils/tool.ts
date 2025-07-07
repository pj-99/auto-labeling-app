import chroma from "chroma-js"
import type { Canvas as FabricCanvas } from "fabric"

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
export const getClassColor = (classId: number) => {
    if (classId == null) return colors.value[colors.value.length - 1]!
    return colors.value[classId % colors.value.length]!
}


export const xyxyToXCenterYCenter = (xyxy: number[], imageWidth: number, imageHeight: number): {
    xCenter: number,
    yCenter: number
    width: number
    height: number
} => {
    if (xyxy.length !== 4) {
        throw new Error("xyxy must be an array of 4 numbers")
    }
    return {
        xCenter: (xyxy[0]! + xyxy[2]!) / 2 / imageWidth,
        yCenter: (xyxy[1]! + xyxy[3]!) / 2 / imageHeight,
        width: (xyxy[2]! - xyxy[0]!) / imageWidth,
        height: (xyxy[3]! - xyxy[1]!) / imageHeight
    }
}

export const getImageDimensions = (file: File): Promise<{ width: number; height: number }> => {
    return new Promise((resolve, reject) => {
        const img = new Image();

        img.onload = () => {
            resolve({
                width: img.naturalWidth,
                height: img.naturalHeight
            });
        };

        img.onerror = () => {
            reject(new Error('Failed to load image'));
        };

        // Create object URL for the file
        const objectUrl = URL.createObjectURL(file);
        img.src = objectUrl;

        // Clean up object URL after image loads
        img.onload = () => {
            URL.revokeObjectURL(objectUrl);
            resolve({
                width: img.naturalWidth,
                height: img.naturalHeight
            });
        };
    });
};


/**
 * Get the mouse point in real image size
 * @param e - The mouse event
 * @param fabricCanvas - The fabric canvas
 * @param imageWidth - The width of the image
 * @returns The mouse point in real image size
 */
export const getMousePoint = (e: MouseEvent, fabricCanvas: FabricCanvas, imageWidth: number): {
    x: number,
    y: number
} => {

    const pointer = fabricCanvas.getPointer(e)
    const scaleFactor = imageWidth / fabricCanvas.width
    const normalizedX = Math.round(pointer.x * scaleFactor)
    const normalizedY = Math.round(pointer.y * scaleFactor)
    return { x: normalizedX, y: normalizedY }
}