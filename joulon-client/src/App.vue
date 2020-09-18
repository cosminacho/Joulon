<template>
    <v-app>
        <v-content>
            <v-container>
                <router-view/>
            </v-container>
        </v-content>
        <Menu/>
    </v-app>
</template>

<script>
import Menu from "./components/Menu.vue";
export default {
    name: "App",
    components: {
        Menu
    }
};
</script>
