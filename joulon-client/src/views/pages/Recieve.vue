<template>
    <v-card>
        <v-layout>
            <h1 class="jtitle">Recieve</h1>
            <v-flex class="jalgn"></v-flex>
            <v-btn icon @click="showQR = !showQR">
                <v-icon>fas fa-qrcode</v-icon>
            </v-btn>
            <v-flex class="jalgn-qr" v-if="showQR">
                <qr-code :text="public_key"></qr-code>
            </v-flex>
        </v-layout>
    </v-card>
</template>



<script>
import VueQRCodeComponent from "vue-qrcode-component";
export default {
    name: "Recieve",
    components: {
        "qr-code": VueQRCodeComponent
    },
    created() {},
    data() {
        return {
            valid: false,
            showQR: false,
            public_key:
                "30819f300d06092a864886f70d010101050003818d0030818902818100ab1a5fee44eb0f91a87d1994490dfd5a8d4b32cd9bb1590c5354523723ad6720ef26d3064cca97bc351d8b157c55ce9b8daa9d868635eaa204fbd344c6404443aa26dd07beec4e970128adbc1a35cf7f1a0ecaa392d1eba8f48e0b98dd3f8536a8b101455924a51f65688d9c6068dccdd1d86437cf6fc689e3ddcc7ce2fb610f0203010001"
        };
    }
};
</script>
<style scoped>
.jalgn-qr {
    margin: 20px;
}
.jalgn {
    display: inline-block;
    text-align: center;
    margin: auto;
}
h1.jtitle {
    padding: 20px;
}
</style>