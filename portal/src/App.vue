<template>
  <div class="app-shell">
    <header class="site-header">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">F</span>
        <span class="brand-text">基金会服务平台</span>
      </RouterLink>

      <nav class="site-nav" aria-label="主导航">
        <RouterLink to="/donation-query">捐赠查询</RouterLink>
        <RouterLink to="/fund-usage">基金使用</RouterLink>
        <RouterLink to="/news">最新动态</RouterLink>
        <RouterLink to="/invoice-request">开票申请</RouterLink>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>
