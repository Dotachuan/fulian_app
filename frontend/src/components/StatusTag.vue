<template>
  <div class="status-tag-wrap">
    <el-tag :type="config.type" size="small">{{ config.label }}</el-tag>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
  map: {
    type: Object,
    default: () => ({
      normal: { label: '正常', type: 'success' },
      pending: { label: '待审核', type: 'warning' },
      void: { label: '作废', type: 'danger' },
      active: { label: '启用', type: 'success' },
      inactive: { label: '停用', type: 'info' },
    }),
  },
})

const config = computed(() => props.map[props.status] || { label: props.status, type: 'info' })
</script>
