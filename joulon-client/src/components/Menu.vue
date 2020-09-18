<template>
    <v-bottom-nav
        :active.sync="bottomNav"
        :color="color"
        :value="true"
        fixed
        dark
        :shift="getStatus"
    >
        <v-btn dark icon v-if="getStatus" to="/send">
            <span>Send</span>
            <v-icon>fas fa-share-square</v-icon>
        </v-btn>

        <v-btn dark icon v-if="getStatus" to="/recieve">
            <span>Recieve</span>
            <v-icon>fas fa-hand-holding</v-icon>
        </v-btn>

        <v-btn dark icon v-if="getStatus" to="/balance">
            <span>Wallet</span>
            <v-icon>fas fa-wallet</v-icon>
        </v-btn>

        <v-btn dark icon v-if="getStatus" to="/connect">
            <span>Connect</span>
            <v-icon>fas fa-network-wired</v-icon>
        </v-btn>

        <v-btn dark icon v-if="getStatus" to="/stats">
            <span>Home</span>
            <v-icon>fas fa-home</v-icon>
        </v-btn>

        <v-btn dark to="/register" v-if="!getStatus">
            <span>Register</span>
        </v-btn>

        <v-btn dark to="/login" v-if="!getStatus">
            <span>Login</span>
        </v-btn>
    </v-bottom-nav>
</template>

<script>
import { mapGetters } from "vuex";
export default {
    name: "Menu",
    data() {
        return {
            bottomNav: 3,
            isLoggedIn: false
        };
    },
    computed: {
        ...mapGetters(["getStatus"]),
        color() {
            switch (this.bottomNav) {
                case 0:
                    return "#26477F";
                case 1:
                    return "#004ACC";
                case 2:
                    return "#002E7F";
                case 3:
                    return "#0059D6";
            }
            return "#213D6E";
        }
    }
};
</script>

