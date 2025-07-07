<script setup lang="ts">
import { computed } from 'vue'

export type ModelType = 'SAM' | 'YOLO(coco)' | 'none'

const props = defineProps<{
  modelValue: ModelType
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ModelType): void
  (e: 'runAutoLabeling'): void
}>()

const value = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const items = ref<ModelType[]>(['SAM', 'YOLO(coco)', 'none'])
const descriptions = ref<Record<ModelType, string>>({
    'SAM': 'Clicking a point to get a box prediction by SAM',
    'YOLO(coco)': 'Automatically label the image by YOLO(coco)',
    'none': 'None',
})

const handleRun = () => {
  emit('runAutoLabeling')
}
</script>

<template>
  <div>
    <h2 class="text-lg font-medium mb-2">Auto Labeling</h2>
    <div class="space-y-4">
      <USelect 
        v-model="value" 
        placeholder="Select model" 
        icon="i-heroicons-sparkles" 
        :items="items"
        class="w-full"
      />
      
      <UButton 
        v-if="value == 'YOLO(coco)'" 
        class="w-full"
        variant="solid"
        icon="i-heroicons-play"
        @click="handleRun"
      >
        Run
      </UButton>

      <p v-if="value != 'none' && descriptions[value]" class="text-sm text-muted-foreground">
        {{ descriptions[value] }}
      </p>
    </div>

  </div>
</template>