<script setup lang="ts">
import { DatasetTrainingType } from '~/types/dataset'

interface DatasetTrainingInfo {
  icon: string
}

const DatasetTrainingInfoMap = new Map<
  DatasetTrainingType,
  DatasetTrainingInfo
>([
  [
    DatasetTrainingType.DETECT,
    {
      icon: 'i-heroicons-eye',
    },
  ],
  [
    DatasetTrainingType.SEGMENT,
    {
      icon: 'i-heroicons-scissors',
    },
  ],
])

defineProps<{
  trainingType: DatasetTrainingType
}>()
</script>

<template>
  <UBadge
    :label="trainingType?.toUpperCase()"
    color="neutral"
    :icon="DatasetTrainingInfoMap.get(trainingType)?.icon"
    variant="subtle"
    size="sm"
  />
</template>
