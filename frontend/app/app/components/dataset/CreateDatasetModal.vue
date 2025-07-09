
<script setup lang="ts">
import { useMutation } from '@vue/apollo-composable'
import { gql } from 'graphql-tag'
import * as v from 'valibot'
import type { FormSubmitEvent } from '@nuxt/ui'
import { DatasetTrainingType } from '~/types/dataset'

// Form Schema
const createDatasetSchema = v.object({
  name: v.pipe(v.string(), v.minLength(1, 'Dataset name is required')),
  type: v.pipe(v.string(), v.enum(DatasetTrainingType, 'Invalid dataset type')),
})

type CreateDatasetSchema = v.InferOutput<typeof createDatasetSchema>

const formState = reactive({
  name: '',
  type: DatasetTrainingType.DETECT,
})

const openModal = ref(false)
const isCreating = ref(false)
const showSuccess = ref(false)

const toast = useToast()

const CREATE_DATASET_MUTATION = gql`
  mutation CreateDataset(
    $userId: UUID!
    $name: String!
    $trainingType: TrainingType!
  ) {
    createDataset(userId: $userId, name: $name, trainingType: $trainingType) {
      id
      name
      trainingType
      createdAt
      updatedAt
      createdBy
      images {
        id
      }
    }
  }
`

// TODO: Replace with actual user ID from auth system
const userId = '123e4567-e89b-12d3-a456-426614174000'

const { mutate: createDatasetMutation } = useMutation(CREATE_DATASET_MUTATION)

const emit = defineEmits<{
  refresh: []
}>()

async function onSubmit(event: FormSubmitEvent<CreateDatasetSchema>) {
  isCreating.value = true

  try {
    await createDatasetMutation({
      userId,
      name: event.data.name,
      trainingType: event.data.type,
    })

    // Reset form and show success
    formState.name = ''
    formState.type = DatasetTrainingType.DETECT
    showSuccess.value = true
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
    openModal.value = false
    toast.add({
      title: 'Success',
      description: 'Dataset created successfully',
      color: 'success',
    })
    // Refetch datasets
    emit('refresh')
  } catch (error) {
    toast.add({
      title: 'Error',
      description: 'Failed to create dataset',
      color: 'error',
    })
    console.error('Error creating dataset:', error)
  } finally {
    isCreating.value = false
  }
}
</script>

<template>
  <UModal v-model:open="openModal">
    <UButton label="Create Dataset" color="secondary" variant="subtle" />
    <template #content>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-medium">Create New Dataset</h2>
          </div>
        </template>

        <UForm
          :schema="createDatasetSchema"
          :state="formState"
          class="space-y-4"
          @submit="onSubmit"
        >
          <UFormField label="Dataset Name" name="name">
            <UInput v-model="formState.name" />
          </UFormField>

          <UFormField label="Dataset Type" name="type">
            <USelect
              v-model="formState.type"
              :items="[
                { label: 'Object Detection', value: DatasetTrainingType.DETECT },
                { label: 'Segmentation', value: DatasetTrainingType.SEGMENT },
              ]"
            />
          </UFormField>

          <div class="flex justify-end mt-4">
            <UButton type="submit" :loading="isCreating">
              Create Dataset
            </UButton>
          </div>
        </UForm>

        <!-- Success Message -->
        <UAlert
          v-if="showSuccess"
          color="success"
          variant="soft"
          title="Success!"
          class="mt-4"
        >
          <template #description> Dataset created successfully </template>
        </UAlert>
      </UCard>
    </template>
  </UModal>
</template>