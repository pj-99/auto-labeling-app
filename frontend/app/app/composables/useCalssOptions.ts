import type { Class } from "~/types/dataset"

export function useClassOptions(
  classesData: Ref<{ classes?: Class[] } | undefined>
) {
  const classes = computed(() => classesData.value?.classes || [])

  const classItems = computed(() =>
    classes.value.map((cls) => ({
      label: cls.name,
      value: cls.id,
    }))
  )

  const classIdToName = computed(() => {
    const map = new Map<number, string>()
    classes.value.forEach((cls) => {
      map.set(cls.id, cls.name)
    })
    return map
  })

  return {
    classes,
    classItems,
    classIdToName,
  }
}
