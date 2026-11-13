<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">油气生产日报系统</div>
      <el-menu router :default-active="activeMenu" background-color="#001529" text-color="#cfd8e3" active-text-color="#ffffff">
        <el-menu-item index="/records">生产数据管理</el-menu-item>
        <el-menu-item index="/reports">生产日报</el-menu-item>
        <el-menu-item index="/trends">趋势分析</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">油气生产日报自动生成（演示系统 · 模拟数据）</el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => (route.path.startsWith('/records') ? '/records' : route.path))
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.aside {
  background-color: #001529;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
}

.header {
  background-color: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  font-size: 15px;
  color: #303133;
}

.main {
  background-color: #f5f7fa;
}

.el-menu {
  border-right: none;
}
</style>
