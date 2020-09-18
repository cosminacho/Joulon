<template>
    <v-card>
        <v-form ref="form" v-model="valid" lazy-validation>
            <v-text-field
                v-model="uuid"
                :rules="uuidRules"
                label="UUID"
                prepend-icon="fas fa-user"
                required
            ></v-text-field>
            <v-text-field
                v-model="public_key"
                :rules="public_keyRules"
                label="Public Key"
                prepend-icon="fas fa-key"
                required
            ></v-text-field>
            <v-text-field
                prepend-icon="fas fa-lock"
                label="Private Key"
                type="password"
                :rules="private_keyRules"
                v-model="private_key"
                required
            ></v-text-field>

            <div class="text-xs-center">
                <v-btn :disabled="!valid" color="accent" @click="validate">Login</v-btn>
            </div>
        </v-form>
    </v-card>
</template>

<script>
import axios from "axios";
import swal from "sweetalert2";
export default {
    data() {
        return {
            uuid: "",
            private_key: "",
            public_key: "",
            valid: false,
            uuidRules: [v => !!v || "UUID is required"],
            private_keyRules: [v => !!v || "Public Key is required"],
            public_keyRules: [v => !!v || "Private Key is required"]
        };
    },
    created() {},
    methods: {
        validate() {
            if (this.$refs.form.validate()) {
                axios
                    .post("/login", {
                        uuid: this.uuid,
                        private_key: this.private_key,
                        public_key: this.public_key
                    })
                    .then(res => {
                        if (res.data.success) {
                            this.$router.push("/");
                            this.$refs.form.reset();
                            this.$store.commit("set_uuid", this.uuid);
                            this.$store.commit(
                                "set_keys",
                                this.private_key,
                                this.public_key
                            );
                        } else {
                            swal.fire(
                                "Erorr",
                                "There was a problem authentificating to your wallet",
                                "error"
                            );
                        }
                    })
                    .catch(err => {
                        console.log(err);
                        swal.fire(
                            "Error",
                            "There was a problem authentificating to your wallet",
                            "error"
                        );
                    });
            }
        }
    }
};
</script>
