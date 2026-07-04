import { useUserStore } from '@/stores/user'

/**
 * 检查当前用户是否拥有指定权限
 * @param {string|string[]} roles
 */
export function hasPermission(roles) {
  const userStore = useUserStore()
  const userRole = userStore.role
  if (!roles) return true
  if (Array.isArray(roles)) return roles.includes(userRole)
  return userRole === roles
}

/**
 * v-permission 自定义指令
 * 用法：v-permission="'admin'" 或 v-permission="['admin','operator']"
 */
export const permissionDirective = {
  mounted(el, binding) {
    if (!hasPermission(binding.value)) {
      el.parentNode?.removeChild(el)
    }
  },
}
