<script setup lang="ts">
export interface ClassItem {
  value: number
  label: string
}
const selectedClass = defineModel<number | undefined>('selected-class')
const newClassName = defineModel<string | null>('new-class-name')

defineProps<{
  classItems: ClassItem[]
  isAddingClass: boolean
  createNewClass: () => void
}>()
</script>

<template>
  <!-- Class List -->
  <div class="flex flex-col gap-2">
    <h2 class="text-lg font-medium mb-2">Class Selector</h2>
    <!-- Class Selection -->
    <USelect
      v-model="selectedClass"
      :items="classItems"
      placeholder="Select a class"
      icon="i-heroicons-tag"
      :loading="isAddingClass"
      class="mb-2"
    >
      <template #item="{ item }">
        <div class="flex items-center gap-2">
          <div
            class="w-2 h-2 rounded-full"
            :style="{ backgroundColor: getClassColor(item.value) }"
          />
          <span>{{ item.label }}</span>
        </div>
      </template>
    </USelect>
    <!-- Add New Class -->
    <div class="flex gap-2">
      <UInput
        v-model="newClassName"
        placeholder="New class name"
        size="sm"
        class="flex-1"
        @keyup.enter="createNewClass"
      />
      <UButton
        icon="i-heroicons-plus"
        color="primary"
        variant="soft"
        size="sm"
        :loading="isAddingClass"
        :disabled="!newClassName"
        @click="createNewClass"
      />
    </div>
  </div>
</template>
