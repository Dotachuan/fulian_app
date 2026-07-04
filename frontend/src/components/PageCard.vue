<template>
  <el-card v-bind="$attrs" shadow="never" class="page-card">
    <template v-if="$slots.header" #header>
      <slot name="header" />
    </template>
    <slot />
  </el-card>
</template>

<script setup>
defineOptions({ inheritAttrs: false })
</script>

<style scoped>
.page-card {
  border-radius: 8px;
}
</style>
