<script setup lang="ts">
import type { Image } from '~/types/image'
import LabeledImage from '~/components/dataset/LabeledImage.vue'
import type { DatasetTrainingType } from '~/types/dataset'

interface Props {
  images: Image[]
  labels: Map<string, LabelDetection[] | LabelSegmentation[]>
  datasetId: string
  trainingType: DatasetTrainingType
  columns?: {
    default?: number
    sm?: number
    md?: number
    lg?: number
  }
}

const props = withDefaults(defineProps<Props>(), {
  columns: () => ({
    default: 2,
    sm: 3,
    md: 4,
    lg: 4
  })
})

const gridClasses = computed(() => {
  const cols = props.columns
  return [
    `grid-cols-${cols.default || 2}`,
    cols.sm ? `sm:grid-cols-${cols.sm}` : '',
    cols.md ? `md:grid-cols-${cols.md}` : '',
    cols.lg ? `lg:grid-cols-${cols.lg}` : ''
  ].filter(Boolean).join(' ')
})
</script>

<template>
  <div
    class="grid gap-4"
    :class="gridClasses"
  >
    <NuxtLink
      v-for="image in images"
      :key="image.id"
      :to="`/dataset/${datasetId}/image/${encodeUuidToBase64(image.id)}/${trainingType.toLowerCase()}`"
      class="aspect-square relative overflow-hidden rounded-md bg-gray-100 group hover:ring-1 hover:ring-primary transition-all duration-200"
    >
      <LabeledImage
        :image-url="image.imageUrl"
        :alt="image.imageName"
        :labels="labels.get(image.id) || []"
        :type="trainingType"
      />
      <div
        class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/50 to-transparent px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
      >
        <p class="text-white text-xs truncate">{{ image.imageName }}</p>
      </div>
    </NuxtLink>
  </div>
</template>