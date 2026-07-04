<template>
  <PageCard title="捐赠数据导入">
    <el-alert
      class="hint"
      type="info"
      show-icon
      :closable="false"
      title="当前导入器支持 donate.xls 这类年度项目明细表。请先预览，确认摘要无误后再导入。"
    />

    <el-upload
      class="upload-box"
      drag
      :auto-upload="false"
      :show-file-list="true"
      :limit="1"
      accept=".xls"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="el-upload__text">拖拽 .xls 文件到此处，或点击选择文件</div>
      <template #tip>
        <div class="el-upload__tip">预览阶段不会写入数据库。</div>
      </template>
    </el-upload>

    <div class="actions">
      <el-button type="primary" :loading="previewing" :disabled="!selectedFile" @click="handlePreview">
        预分析
      </el-button>
      <el-button
        type="success"
        :loading="committing"
        :disabled="!previewResult?.import_token"
        @click="handleCommit"
      >
        确认导入
      </el-button>
    </div>

    <template v-if="previewResult">
      <el-divider content-position="left">预分析结果</el-divider>
      <div class="summary-grid">
        <div class="summary-item">
          <span>捐赠人</span>
          <strong>{{ previewResult.summary.donor_count }}</strong>
        </div>
        <div class="summary-item">
          <span>项目</span>
          <strong>{{ previewResult.summary.target_count }}</strong>
        </div>
        <div class="summary-item">
          <span>记录数</span>
          <strong>{{ previewResult.summary.donation_count }}</strong>
        </div>
        <div class="summary-item">
          <span>总金额</span>
          <strong>{{ money(previewResult.summary.total_amount) }}</strong>
        </div>
      </div>

      <el-row :gutter="16" class="tables">
        <el-col :span="12">
          <h3>按年度统计</h3>
          <el-table :data="yearRows" size="small" border>
            <el-table-column prop="year" label="年份" />
            <el-table-column prop="count" label="记录数" />
            <el-table-column prop="amount" label="金额" align="right">
              <template #default="{ row }">{{ money(row.amount) }}</template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="12">
          <h3>项目统计</h3>
          <el-table :data="previewResult.summary.top_targets" size="small" border max-height="320">
            <el-table-column prop="target_name" label="项目" min-width="120" />
            <el-table-column prop="count" label="记录数" width="90" />
            <el-table-column prop="amount" label="金额" width="130" align="right">
              <template #default="{ row }">{{ money(row.amount) }}</template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>

      <h3>样例记录</h3>
      <el-table :data="previewResult.sample_donations" size="small" border>
        <el-table-column prop="source_sheet" label="来源表" width="100" />
        <el-table-column prop="source_row" label="行号" width="80" />
        <el-table-column prop="donor_name" label="捐赠人" min-width="120" />
        <el-table-column prop="target_name" label="项目" min-width="120" />
        <el-table-column prop="donation_date" label="日期" width="120" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">{{ money(row.amount) }}</template>
        </el-table-column>
      </el-table>

      <template v-if="previewResult.warnings?.length">
        <h3>预警</h3>
        <el-table :data="previewResult.warnings" size="small" border max-height="260">
          <el-table-column prop="sheet" label="工作表" width="120" />
          <el-table-column prop="row" label="行号" width="80" />
          <el-table-column prop="reason" label="原因" min-width="180" />
          <el-table-column prop="donor_name" label="捐赠人" min-width="120" />
          <el-table-column prop="difference" label="差额" width="120" />
        </el-table>
      </template>
    </template>

    <template v-if="commitResult">
      <el-divider content-position="left">导入结果</el-divider>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="新增捐赠人">{{ commitResult.created_donors }}</el-descriptions-item>
        <el-descriptions-item label="新增项目">{{ commitResult.created_targets }}</el-descriptions-item>
        <el-descriptions-item label="成功导入">{{ commitResult.imported }}</el-descriptions-item>
        <el-descriptions-item label="跳过重复">{{ commitResult.skipped_duplicates }}</el-descriptions-item>
        <el-descriptions-item label="失败">{{ commitResult.failed_count }}</el-descriptions-item>
      </el-descriptions>
    </template>
  </PageCard>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageCard from '@/components/PageCard.vue'
import { commitDonationImportApi, previewDonationImportApi } from '@/api/imports'

const selectedFile = ref(null)
const previewing = ref(false)
const committing = ref(false)
const previewResult = ref(null)
const commitResult = ref(null)

const yearRows = computed(() => {
  const byYear = previewResult.value?.summary?.by_year || {}
  return Object.entries(byYear).map(([year, item]) => ({ year, ...item }))
})

function money(value) {
  return Number(value || 0).toFixed(2)
}

function handleFileChange(file) {
  selectedFile.value = file.raw
  previewResult.value = null
  commitResult.value = null
}

function handleFileRemove() {
  selectedFile.value = null
  previewResult.value = null
  commitResult.value = null
}

async function handlePreview() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择 .xls 文件')
    return
  }
  previewing.value = true
  try {
    previewResult.value = await previewDonationImportApi(selectedFile.value)
    commitResult.value = null
    ElMessage.success('预分析完成')
  } finally {
    previewing.value = false
  }
}

async function handleCommit() {
  await ElMessageBox.confirm(
    '确认将预分析结果写入数据库？系统会默认跳过重复记录。',
    '确认导入',
    { type: 'warning' }
  )
  committing.value = true
  try {
    commitResult.value = await commitDonationImportApi({
      import_token: previewResult.value.import_token,
      duplicate_strategy: 'skip',
    })
    if (commitResult.value.imported > 0) {
      ElMessage.success(`导入完成，成功导入 ${commitResult.value.imported} 条`)
    } else if (commitResult.value.skipped_duplicates > 0 && commitResult.value.failed_count === 0) {
      ElMessage.warning(`没有新增记录，已跳过 ${commitResult.value.skipped_duplicates} 条重复数据`)
    } else {
      ElMessage.warning('导入完成，但没有新增记录')
    }
  } finally {
    committing.value = false
  }
}
</script>

<style scoped>
.hint {
  margin-bottom: 16px;
}

.upload-box {
  max-width: 720px;
}

.upload-icon {
  color: #409eff;
  font-size: 42px;
}

.actions {
  display: flex;
  gap: 12px;
  margin: 16px 0 8px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-item {
  padding: 16px;
  background: #f7f9fc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.summary-item span {
  display: block;
  color: #606266;
}

.summary-item strong {
  display: block;
  margin-top: 8px;
  font-size: 24px;
}

.tables {
  margin-top: 18px;
}

h3 {
  margin: 20px 0 10px;
  font-size: 16px;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
