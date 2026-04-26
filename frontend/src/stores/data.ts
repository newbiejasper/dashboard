import { defineStore } from 'pinia'
import { ref } from 'vue'
import { datasourceAPI, datasetAPI } from '@/api/endpoints'
import type { DataSource, Dataset } from '@/types'

export const useDataStore = defineStore('data', () => {
  const datasources = ref<DataSource[]>([])
  const datasets = ref<Dataset[]>([])
  const isLoading = ref(false)

  async function loadDatasources() {
    const res = await datasourceAPI.list()
    datasources.value = res.data
  }

  async function loadDatasets(params?: { dataset_type?: string; datasource_id?: number }) {
    const res = await datasetAPI.list(params)
    datasets.value = res.data
  }

  return { datasources, datasets, isLoading, loadDatasources, loadDatasets }
})
