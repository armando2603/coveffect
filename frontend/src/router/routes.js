
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('pages/Home.vue') }
    ]
  },
  {
    path: '/start',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'paperList', component: () => import('pages/Start.vue') }
    ]
  },
  {
    path: '/label',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/Label.vue') }
    ]
  },
  {
    path: '/al',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'AL', component: () => import('pages/AL.vue') }
    ]
  },
  {
    path: '/annotations',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'annotations', component: () => import('pages/Annotations.vue') }
    ]
  },
  {
    path: '/about',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'annotations', component: () => import('pages/About.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/Error404.vue')
  }
]

export default routes
