<template>
    <v-card>
        <v-form ref="form" v-model="valid" lazy-validation>
            <qrcode-stream v-if="camera" @decode="onDecode"></qrcode-stream>
            <v-layout row wrap>
                <v-flex xs10 offset-xs1>
                    <v-text-field
                        prepend-icon="fas fa-key"
                        required
                        append-outer-icon="fas fa-camera"
                        v-model="public_key"
                        label="Insert recipient public key"
                        :rules="rules"
                        @click:append-outer="openCamera"
                    ></v-text-field>
                </v-flex>

                <v-flex xs8 offset-xs1>
                    <v-text-field
                        prepend-icon="fas fa-balance-scale"
                        v-model="amount"
                        required
                        :rules="rules"
                        label="Insert the amount you want to send"
                    ></v-text-field>
                </v-flex>
                <v-flex xs1>
                    <v-card-text>Joulons Balance:</v-card-text>
                </v-flex>
                <v-flex xs1>
                    <v-text-field disabled readonly :label="balance.toString()"></v-text-field>
                </v-flex>

                <hr>
                <v-flex xs10 offset-xs1>
                    <v-textarea
                        prepend-icon="fas fa-signature"
                        v-model="description"
                        required
                        :rules="rules"
                        label="Insert a short description"
                    ></v-textarea>
                </v-flex>
                <v-flex xs10 offset-xs1>
                    <div class="text-xs-center">
                        <v-btn
                            :disabled="!valid"
                            color="accent"
                            @click="sendTransaction"
                        >Send Transaction</v-btn>
                    </div>
                </v-flex>
            </v-layout>
        </v-form>
    </v-card>
</template>

<script>
import { QrcodeStream } from "vue-qrcode-reader";
import axios from "axios";
import swal from "sweetalert2";
export default {
    name: "Send",
    components: {
        QrcodeStream
    },
    data() {
        return {
            rules: [v => !!v || "Item is required"],
            public_key: "",
            description: "",
            amount: 0,
            valid: false,
            camera: false,
            balance: 10
        };
    },
    methods: {
        sendTransaction() {
            if (this.$refs.form.validate()) {
                axios
                    .post({
                        wallet_id: this.$store.getters.get_uuid,
                        private_key: this.$store.getters.get_private_key,
                        public_key: this.$store.getters.get_public_key,
                        sender: this.$store.getters.get_public_key,
                        recipient: this.public_key,
                        amount: this.amount,
                        description: this.description
                    })
                    .then(res => {
                        if (res.data.success) {
                            swal.fire(
                                "Transaction accepted",
                                "Your transaction will be processed in a few minute",
                                "success"
                            );
                        }
                    })
                    .catch(err => {
                        console.log(err);
                        swal.fire(
                            "Transaction rejected",
                            "Your transaction was invalid",
                            "error"
                        );
                    });
            }
        },
        onDecode(result) {
            this.public_key = result;
            this.camera = false;
        },
        openCamera() {
            this.camera = true;
        },
        async onInit(promise) {
            try {
                await promise;
            } catch (error) {
                if (error.name === "NotAllowedError") {
                    this.error =
                        "ERROR: you need to grant camera access permisson";
                } else if (error.name === "NotFoundError") {
                    this.error = "ERROR: no camera on this device";
                } else if (error.name === "NotSupportedError") {
                    this.error =
                        "ERROR: secure context required (HTTPS, localhost)";
                } else if (error.name === "NotReadableError") {
                    this.error = "ERROR: is the camera already in use?";
                } else if (error.name === "OverconstrainedError") {
                    this.error = "ERROR: installed cameras are not suitable";
                } else if (error.name === "StreamApiNotSupportedError") {
                    this.error =
                        "ERROR: Stream API is not supported in this browser";
                }
            }
        }
    }
};
</script>
