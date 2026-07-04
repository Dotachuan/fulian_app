<template>
  <div class="image-upload-field">
    <div class="input-row">
      <el-input
        :model-value="modelValue"
        :placeholder="placeholder"
        @update:model-value="emit('update:modelValue', $event)"
      />
      <el-upload
        class="upload-trigger"
        :show-file-list="false"
        :auto-upload="true"
        :http-request="handleUpload"
        accept=".jpg,.jpeg,.png,.gif"
      >
        <el-button :loading="uploading" type="primary" plain>上传图片</el-button>
      </el-upload>
    </div>

    <div v-if="modelValue" class="preview-row">
      <el-image
        :src="modelValue"
        fit="cover"
        class="preview-image"
        :preview-src-list="[modelValue]"
        preview-teleported
      />
      <el-link :href="modelValue" target="_blank" type="primary">查看原图</el-link>
    </div>

    <div class="hint">支持 jpg、png、gif，单张不超过 8MB，建议优先使用 jpg 或 png</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadImageApi } from '@/api/upload'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  folder: {
    type: String,
    default: 'misc',
  },
  placeholder: {
    type: String,
    default: '可手填图片 URL，也可直接上传图片',
  },
})

const emit = defineEmits(['update:modelValue'])
const uploading = ref(false)

async function handleUpload(option) {
  uploading.value = true
  try {
    const res = await uploadImageApi(props.folder, option.file)
    emit('update:modelValue', res.url)
    ElMessage.success('图片上传成功')
    option.onSuccess?.(res)
  } catch (error) {
    option.onError?.(error)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.image-upload-field {
  width: 100%;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.input-row :deep(.el-input) {
  flex: 1;
}

.upload-trigger {
  flex: none;
}

.preview-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
}

.preview-image {
  width: 88px;
  height: 56px;
  border-radius: 8px;
  border: 1px solid #dbe3f0;
  background: #f6f8fc;
}

.hint {
  margin-top: 8px;
  color: #7f8ba3;
  font-size: 12px;
}
</style>
