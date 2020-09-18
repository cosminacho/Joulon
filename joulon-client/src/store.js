import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        uuid: '',
        private_key: '',
        public_key: '',
        isLoggedIn: false
    },
    getters: {
        get_uuid: state => {
            return state.uuid;
        },
        get_private_key: state => {
            return state.private_key;
        },
        get_public_key: state => {
            return state.public_key;
        },
        getStatus: state => {
            return state.isLoggedIn;
        }
    },
    mutations: {
        set_uuid(state, value) {
            state.uuid = value;
            state.isLoggedIn = true;
        },
        set_keys(state, private_key, public_key) {
            state.private_key = private_key;
            state.public_key = public_key;
        }
    }
})