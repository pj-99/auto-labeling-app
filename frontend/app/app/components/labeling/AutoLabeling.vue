<script setup lang="ts">
import { computed, ref } from 'vue'

export type ModelType = 'SAM' | 'YOLO(coco)'
export type SAMMode = 'add' | 'remove'

const props = defineProps<{
  modelValue: ModelType | null
  samMode?: SAMMode
  isLoading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ModelType | null): void
  (e: 'update:samMode', value: SAMMode): void
  (e: 'runAutoLabeling'): void
}>()

const value = computed({
  get: () => props.modelValue ?? undefined,
  set: (val) => emit('update:modelValue', val ?? null),
})

const samModeValue = computed({
  get: () => props.samMode ?? 'add',
  set: (val) => emit('update:samMode', val),
})

const enabled = ref(false)

const items = ref<ModelType[]>(['SAM', 'YOLO(coco)'])
const descriptions = ref<Record<ModelType, string>>({
  SAM: 'Click to add points, Shift+Click to remove',
  'YOLO(coco)': 'Automatically label the image by YOLO(coco)',
})

const samModeOptions: Array<{
  label: string;
  value: SAMMode;
  icon: string;
  selectedIcon: string;
}> = [
  {
    label: 'Add',
    value: 'add',
    icon: 'i-heroicons-plus-circle',
    selectedIcon: 'i-heroicons-plus-circle-solid',
  },
  {
    label: 'Remove',
    value: 'remove',
    icon: 'i-heroicons-minus-circle',
    selectedIcon: 'i-heroicons-minus-circle-solid',
  },
]

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

      <!-- SAM Mode Toggle -->
      <div v-if="value === 'SAM'" class="space-y-2">
        <label class="text-sm font-medium">Point Mode</label>
        <UButtonGroup size="sm" class="w-full">
          <UButton
            v-for="option in samModeOptions"
            :key="option.value"
            :color="samModeValue === option.value ? 'primary' : 'neutral'"
            :variant="samModeValue === option.value ? 'solid' : 'outline'"
            class="flex-1"
            @click="samModeValue = option.value"
          >
            <template #leading>
              <UIcon 
                :name="samModeValue === option.value ? option.selectedIcon : option.icon" 
                class="w-4 h-4"
              />
            </template>
            {{ option.label }}
          </UButton>
        </UButtonGroup>
        
        <!-- Visual Indicator -->
        <div 
          class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm"
          :class="{
            'bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300': samModeValue === 'add',
            'bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300': samModeValue === 'remove'
          }"
        >
          <UIcon 
            :name="samModeValue === 'add' ? 'i-heroicons-information-circle' : 'i-heroicons-exclamation-circle'" 
            class="w-4 h-4"
          />
          <span v-if="samModeValue === 'add'">
            Click to add to selection
          </span>
          <span v-else>
            Click to remove from selection
          </span>
        </div>
      </div>

      <UButton
        v-if="value === 'YOLO(coco)'"
        class="w-full"
        variant="solid"
        icon="i-heroicons-play"
        :loading="isLoading"
        :disabled="isLoading"
        @click="handleRun"
      >
        {{ isLoading ? 'Running YOLO...' : 'Run' }}
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