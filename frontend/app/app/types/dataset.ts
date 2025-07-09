export enum DatasetTrainingType {
    DETECT = 'DETECT',
    SEGMENT = 'SEGMENT'
}

export interface Dataset {
    id: string
    name: string
    createdAt: string
    updatedAt: string
    createdBy: string
    images: Image[]
    trainingType: DatasetTrainingType
}

export interface Class {
    id: number
    name: string
}