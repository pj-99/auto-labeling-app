<template>
<UBadge
:label="trainingType?.toUpperCase()"
color="neutral" 
:icon="DatasetTrainingInfoMap.get(trainingType)?.icon"
variant="subtle" size="sm" />
</template>

<script setup lang="ts">
import { DatasetTrainingType } from './dataset';


interface DatasetTrainingInfo {
    icon: string;
}

const DatasetTrainingInfoMap = new Map<DatasetTrainingType, DatasetTrainingInfo>([
  [DatasetTrainingType.DETECT, { 
    icon: 'i-heroicons-eye'
  }],
  [DatasetTrainingType.SEGMENT, { 
    icon: 'i-heroicons-scissors'
  }]
]);

defineProps<{
  trainingType: DatasetTrainingType
}>();
</script>