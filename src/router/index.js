import { createRouter, createWebHistory } from 'vue-router'
import ScanView from '../views/ScanView.vue'
import CollectionView from '../views/CollectionView.vue'
import SettingsView from '../views/SettingsView.vue'

const routes = [
  { path: '/', name: 'Scan', component: ScanView },
  { path: '/collection', name: 'Collection', component: CollectionView },
  { path: '/settings', name: 'Settings', component: SettingsView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
