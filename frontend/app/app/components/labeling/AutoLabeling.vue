<script setup lang="ts">
import { computed, ref } from 'vue'

export type ModelType = 'SAM' | 'YOLO(coco)'

const props = defineProps<{
  modelValue: ModelType | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ModelType | null): void
  (e: 'runAutoLabeling'): void
}>()

const value = computed({
  get: () => props.modelValue ?? undefined,
  set: (val) => emit('update:modelValue', val ?? null),
})

const enabled = ref(false)

const items = ref<ModelType[]>(['SAM', 'YOLO(coco)'])
const descriptions = ref<Record<ModelType, string>>({
  SAM: 'Clicking a point to get a box prediction by SAM',
  'YOLO(coco)': 'Automatically label the image by YOLO(coco)',
})

const handleRun = () => {
  emit('runAutoLabeling')
}

const handleToggle = (val: boolean) => {
  enabled.value = val
  if (!val) {
    emit('update:modelValue', null)
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-medium">Auto Labeling</h2>
      <USwitch :model-value="enabled" @update:model-value="handleToggle" />
    </div>

    <div v-if="enabled" class="space-y-4 mt-4">
      <USelect
        v-model="value"
        placeholder="Select model"
        icon="i-heroicons-sparkles"
        :items="items"
        class="w-full"
      />

      <UButton
        v-if="value === 'YOLO(coco)'"
        class="w-full"
        variant="solid"
        icon="i-heroicons-play"
        @click="handleRun"
      >
        Run
      </UButton>

      <p
        v-if="value && descriptions[value]"
        class="text-sm text-muted-foreground"
      >
        {{ descriptions[value] }}
      </p>
    </div>
  </div>
</template>
