import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Send from './views/pages/Send.vue'
import Recieve from './views/pages/Recieve.vue'
import Balance from './views/pages/Balance.vue'
import Stats from './views/pages/Stats.vue'
import Connect from './views/pages/Connect.vue'
import Register from './components/Register.vue'
import Login from './components/Login.vue'
import store from './store'

Vue.use(Router)

export default new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [{
            path: '/',
            name: 'home',
            component: Home,
            beforeEnter(to, from, next) {
                let info = store.state.isLoggedIn
                if (info) {
                    next();
                } else {
                    next('/about')
                }
            },
            children: [{
                    path: '/send',
                    component: Send

                },
                {
                    path: '/recieve',
                    component: Recieve

                },
                {
                    path: '/balance',
                    component: Balance

                },
                {
                    path: '/stats',
                    component: Stats

                },
                {
                    path: '/connect',
                    component: Connect

                }
            ]
        },
        {
            path: '/about',
            name: 'about',
            component: () => import('./views/About.vue'),

            children: [{
                    path: '/register',
                    component: Register
                },
                {
                    path: '/login',
                    component: Login
                }
            ]
        }

    ]
})