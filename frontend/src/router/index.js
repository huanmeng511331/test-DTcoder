import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'
import RecordList from '../views/RecordList.vue'
import RecordEdit from '../views/RecordEdit.vue'
import DailyReport from '../views/DailyReport.vue'
import TrendView from '../views/TrendView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      redirect: '/records',
      children: [
        { path: 'records', name: 'record-list', component: RecordList },
        { path: 'records/new', name: 'record-create', component: RecordEdit },
        { path: 'records/:id/edit', name: 'record-edit', component: RecordEdit },
        { path: 'reports', name: 'daily-report', component: DailyReport },
        { path: 'trends', name: 'trend', component: TrendView },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/records' },
  ],
})

export default router
