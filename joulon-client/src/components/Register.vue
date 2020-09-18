<template>
    <v-card>
        <v-form ref="form" v-model="valid" lazy-validation>
            <v-text-field
                v-model="email"
                :rules="emailRules"
                label="E-mail"
                prepend-icon="fas fa-at"
                required
            ></v-text-field>
            <div class="text-xs-center">
                <v-btn :disabled="!valid" color="accent" @click="validate">Create Account</v-btn>
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
            valid: false,
            emailRules: [
                v => !!v || "E-mail is required",
                v => /.+@.+/.test(v) || "E-mail must be valid"
            ],
            email: ""
        };
    },
    created() {},
    methods: {
        validate() {
            if (this.$refs.form.validate()) {
                axios
                    .post("/newUser", {
                        email: this.email
                    })
                    .then(res => {
                        if (res.data.success) {
                            swal.fire(
                                "Wallet created succesfully",
                                "It may take a few minute, please also check your spam folder.",
                                "success"
                            );
                            this.$refs.form.reset();
                        } else {
                            swal.fire(
                                "Error",
                                "THere was a problem with creating your wallet.",
                                "error"
                            );
                        }
                    })
                    .catch(err => {
                        console.log(err);
                        swal.fire(
                            "Error",
                            "THere was a problem with creating your wallet.",
                            "error"
                        );
                    });
            }
        }
    }
};
</script>
