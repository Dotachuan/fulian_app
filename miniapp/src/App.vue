<script>
export default {
  onLaunch() {
    console.log('Miniapp launched')
  },
}
</script>

<style>
page {
  background: #f7f9fc;
  color: #1a2433;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

view,
text,
button,
input,
textarea {
  box-sizing: border-box;
}

.page {
  min-height: 100vh;
  padding: 28rpx 24rpx 40rpx;
  background:
    radial-gradient(circle at top right, rgba(72, 82, 145, 0.08), transparent 26%),
    linear-gradient(180deg, #f7f9fc 0%, #eef3f9 100%);
}

.page-shell {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}

.card {
  background: rgba(255, 255, 255, 0.98);
  border: 1rpx solid rgba(120, 138, 166, 0.14);
  border-radius: 18rpx;
  padding: 28rpx 26rpx;
  box-shadow: 0 14rpx 32rpx rgba(42, 56, 88, 0.05);
}

.card-soft {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(242, 246, 252, 0.98) 100%);
}

.hero-card {
  color: #f7f9fc;
  background:
    linear-gradient(145deg, #39416f 0%, #485291 44%, #5b67a8 100%);
  border: 1rpx solid rgba(193, 166, 112, 0.18);
  box-shadow: 0 18rpx 42rpx rgba(57, 65, 111, 0.24);
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 18rpx;
}

.section-title {
  color: #1b2536;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.32;
}

.section-subtitle {
  margin-top: 8rpx;
  color: #68778f;
  font-size: 24rpx;
  line-height: 1.72;
}

.hero-eyebrow {
  color: rgba(234, 237, 247, 0.84);
  font-size: 22rpx;
  line-height: 1.5;
  letter-spacing: 1.5rpx;
}

.hero-title {
  margin-top: 14rpx;
  font-size: 42rpx;
  font-weight: 700;
  line-height: 1.24;
}

.hero-desc {
  margin-top: 14rpx;
  color: rgba(247, 249, 252, 0.92);
  font-size: 26rpx;
  line-height: 1.76;
}

.hero-meta {
  margin-top: 20rpx;
  color: rgba(222, 229, 244, 0.78);
  font-size: 23rpx;
  line-height: 1.6;
}

.brand-chip {
  display: inline-flex;
  align-items: center;
  min-height: 42rpx;
  padding: 0 16rpx;
  border-radius: 999rpx;
  color: #3f4b86;
  background: rgba(244, 247, 253, 0.98);
  border: 1rpx solid rgba(91, 103, 168, 0.16);
  font-size: 22rpx;
  font-weight: 600;
}

.status-strip {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 18rpx 20rpx;
  border-radius: 16rpx;
  background: rgba(247, 249, 252, 0.09);
  border: 1rpx solid rgba(222, 229, 244, 0.14);
}

.status-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 999rpx;
  background: #c1a670;
  flex-shrink: 0;
}

.status-text {
  color: rgba(247, 249, 252, 0.92);
  font-size: 24rpx;
  line-height: 1.6;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.badge-success {
  color: #0f5132;
  background: #d7f3e3;
}

.badge-warning {
  color: #8a4b04;
  background: #f6e5bf;
}

.badge-danger {
  color: #8f1d1d;
  background: #f6d8d8;
}

.badge-info {
  color: #475569;
  background: #e6e7e1;
}

.button-primary,
.button-secondary,
.button-ghost {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 88rpx;
  border-radius: 14rpx;
  font-size: 28rpx;
  font-weight: 600;
}

.button-primary {
  color: #f7f9fc;
  background: linear-gradient(135deg, #475291 0%, #5a67aa 100%);
  box-shadow: 0 12rpx 24rpx rgba(71, 82, 145, 0.2);
}

.button-secondary {
  color: #404d86;
  background: #f3f6fc;
  border: 1rpx solid rgba(91, 103, 168, 0.16);
}

.button-ghost {
  color: #334155;
  background: #eff3f8;
}

.button-disabled {
  opacity: 0.5;
}

.field {
  margin-bottom: 24rpx;
}

.field:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  margin-bottom: 12rpx;
  color: #68778f;
  font-size: 24rpx;
}

.field-input,
.field-textarea,
.search-input {
  width: 100%;
  min-height: 88rpx;
  padding: 0 22rpx;
  background: #fbfcfe;
  border: 1rpx solid #d8e0ec;
  border-radius: 14rpx;
  color: #1b2536;
  font-size: 28rpx;
}

.field-textarea {
  min-height: 180rpx;
  padding: 20rpx 22rpx;
}

.field-tip {
  margin-top: 10rpx;
  color: #8390a4;
  font-size: 22rpx;
  line-height: 1.62;
}

.trust-note {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  padding: 18rpx 20rpx;
  border-radius: 16rpx;
  background: #f1f5fb;
  border: 1rpx solid #d9e3f0;
}

.trust-note-mark {
  width: 32rpx;
  height: 32rpx;
  border-radius: 999rpx;
  background: #c1a670;
  color: #2f3966;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  font-weight: 700;
  flex-shrink: 0;
}

.trust-note-text {
  color: #56667d;
  font-size: 23rpx;
  line-height: 1.64;
}

.list-block {
  display: flex;
  flex-direction: column;
}

.list-item {
  position: relative;
  padding: 22rpx 0;
}

.list-item:first-child {
  padding-top: 0;
}

.list-item + .list-item {
  border-top: 1rpx solid #e6edf5;
}

.list-title {
  font-size: 29rpx;
  font-weight: 650;
  line-height: 1.46;
  color: #1b2536;
}

.list-desc {
  margin-top: 8rpx;
  color: #68778f;
  font-size: 24rpx;
  line-height: 1.72;
}

.list-meta {
  margin-top: 10rpx;
  color: #8390a4;
  font-size: 22rpx;
  line-height: 1.5;
}

.row-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.link-text {
  color: #485291;
  font-size: 24rpx;
  font-weight: 600;
}

.value-strong {
  color: #485291;
  font-weight: 700;
}

.money-strong {
  color: #a78752;
  font-weight: 700;
}

.meta-text {
  color: #8b98a7;
  font-size: 23rpx;
  line-height: 1.6;
}

.empty-block {
  padding: 28rpx 0 8rpx;
  color: #8b98a7;
  font-size: 24rpx;
  text-align: center;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18rpx;
}

.summary-tile {
  padding: 22rpx;
  border-radius: 16rpx;
  background: #f7f2ea;
  border: 1rpx solid rgba(154, 122, 78, 0.12);
}

.summary-label {
  color: #5d6b79;
  font-size: 24rpx;
}

.summary-value {
  margin-top: 10rpx;
  color: #16232e;
  font-size: 34rpx;
  font-weight: 700;
}

.soft-divider {
  height: 1rpx;
  margin: 18rpx 0;
  background: #ebe2d5;
}
</style>
