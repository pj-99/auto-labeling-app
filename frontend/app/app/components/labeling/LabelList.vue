<script setup lang="ts">
import { getClassColor } from '~/utils/tool'

type Label = LabelDetection | LabelSegmentation

interface Props {
  labels: Label[]
  classIdToName: Map<string | number, string>
  defaultOpen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  defaultOpen: true
})

const emit = defineEmits<{
  'delete': [label: Label]
  'hover': [label: Label | null]
  'select': [label: Label]
}>()

// Track hovered label
const hoveredLabelId = ref<string | null>(null)

// Group labels by class
const labelsByClass = computed(() => {
  const grouped = new Map<string | number, Label[]>()
  
  props.labels.forEach(label => {
    if (!grouped.has(label.classId)) {
      grouped.set(label.classId, [])
    }
    grouped.get(label.classId)!.push(label)
  })
  
  return grouped
})

// Handle mouse events
const handleMouseEnter = (label: Label) => {
  hoveredLabelId.value = label.id ?? null
  emit('hover', label)
}

const handleMouseLeave = () => {
  hoveredLabelId.value = null
  emit('hover', null)
}

const open = ref(props.defaultOpen)

const classOpenMap = ref(new Map<string | number, boolean>())

watch(labelsByClass, (newVal) => {
  for (const [classId] of newVal) {
    if (!classOpenMap.value.has(classId)) {
      classOpenMap.value.set(classId, true)
    }
  }
})

</script>

<template>
  <div class="flex flex-col gap-2">
    <UCollapsible 
    v-model:open="open"
    :default-open="defaultOpen"
    >
      <UButton
        variant="ghost"
        class="w-full justify-between"
        :trailing-icon="open ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
      >
        <div class="flex items-center">
          <span class="text-lg font-medium">Label List</span>
          <UBadge
            v-if="labels.length > 0"
            :label="`${labels.length}`"
            variant="soft"
            size="sm"
            class="ml-2"
          />
        </div>
      </UButton>

      <template #content>
        <div class="mt-3 space-y-3 max-h-[calc(100vh-36rem)] overflow-y-auto pr-1">
          <!-- Empty state -->
          <div
            v-if="labels.length === 0"
            class="text-gray-500 text-sm text-center py-4"
          >
            <UIcon name="i-heroicons-inbox" class="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No labels yet</p>
            <p class="text-xs mt-1">Start by drawing boxes or using auto-labeling</p>
          </div>

          <!-- Grouped by class with collapsible -->
          <div v-else class="space-y-3">
            <UCollapsible
              v-for="[classId, classLabels] in labelsByClass"
              :key="classId"
              :open="classOpenMap.get(classId)"
              :default-open="true"
              @update:open="(value) => classOpenMap.set(classId, value)"
              
            >
              <UButton
                variant="soft"
                class="w-full justify-between text-sm font-medium text-gray-600 dark:text-gray-400"
                :trailing-icon="classOpenMap.get(classId) ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
              >
                <div class="flex items-center gap-2">
                  <div
                    class="w-3 h-3 rounded-sm"
                    :style="{ backgroundColor: getClassColor(typeof classId === 'string' ? parseInt(classId) : classId) }"
                  />
                  <span>{{ classIdToName.get(classId) || `Class ${classId}` }}</span>
                  <UBadge
                    :label="`${classLabels.length}`"
                    variant="outline"
                    size="sm"
                  />
                </div>
              </UButton>

              <template #content>
                <div class="ml-3 mt-1 space-y-1">
                  <div
                    v-for="(label, index) in classLabels"
                    :key="label.id"
                    class="group flex items-center justify-between px-2 py-1 rounded-md transition-all duration-150"
                    :class="{
                      'bg-gray-50 dark:bg-gray-800': hoveredLabelId === label.id,
                      'hover:bg-gray-50 dark:hover:bg-gray-800': hoveredLabelId !== label.id,
                    }"
                    @mouseenter="handleMouseEnter(label)"
                    @mouseleave="handleMouseLeave"
                    @click="$emit('select', label)"
                  >
                    <span class="text-xs text-gray-500">#{{ index + 1 }}</span>
                    <UButton
                      icon="i-heroicons-trash"
                      color="error"
                      variant="ghost"
                      size="xs"
                      class="opacity-0 group-hover:opacity-100 transition-opacity"
                      @click.stop="$emit('delete', label as Label)"
                    />
                  </div>
                </div>
              </template>
            </UCollapsible>
          </div>
        </div>
      </template>
    </UCollapsible>
  </div>
</template>

<style scoped>
/* Custom scrollbar for label list */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}
</style>