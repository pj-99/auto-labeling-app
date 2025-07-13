interface InsertClassParams {
  datasetId: string
  name: string
}

interface ClassManagementOptions {
  insertClass: (params: InsertClassParams) => Promise<unknown>
  refetchClasses: () => Promise<unknown>
  datasetId: string
}

export const useClassManagement = (options: ClassManagementOptions) => {
  const { insertClass, refetchClasses, datasetId } = options
  
  const newClassName = ref('')
  const isAddingClass = ref(false)

  const createNewClass = async () => {
    if (!newClassName.value.trim()) return

    isAddingClass.value = true
    try {
      await insertClass({
        datasetId,
        name: newClassName.value.trim(),
      })
      newClassName.value = ''
      await refetchClasses()
    } finally {
      isAddingClass.value = false
    }
  }

  return {
    newClassName,
    isAddingClass,
    createNewClass
  }
}