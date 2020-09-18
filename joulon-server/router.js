const express = require("express");
const router = express.Router();
const mqtt = require("mqtt");
const axios = require("axios");
const uuidv5 = require("uuid/v5");
const validate = require("uuid-validate");
const nodemailer = require("nodemailer");
const sendgridTransport = require("nodemailer-sendgrid-transport");

axios.defaults.baseURL = process.env.PK_SERVER;

const transporter = nodemailer.createTransport(
    sendgridTransport({
        auth: {
            api_user: process.env.SENDGRID_USER,
            api_key: process.env.SENDGRID_PASSWORD
        }
    })
);

const client = mqtt.connect("mqtts://" + process.env.MQTT_SERVER, {
    port: process.env.MQTT_SSLPORT,
    username: process.env.MQTT_USER,
    password: process.env.MQTT_PASSWORD
});

client.on("connect", () => {
    console.log("Connected to the MQTT server.");
});

router.post("/newUser", (req, res) => {
    let email = req.body.email;
    let UUID = uuidv5(email, uuidv5.DNS);

    axios
        .post("/new_wallet", {})
        .then(res2 => {
            let data = res2.data;
            private_key = data.private_key;
            public_key = data.public_key;
            html_doc = `<div><h1>Your wallet has been created succesfully. Here are your credetials:</h1>
            <h2>UUID: <div id="uuid">${UUID}</div></h2><button onclick="myFunction("uuid")">Copy UUID</button>
            <h2>Public Key: <div id="public">${public_key}</div></h2><button onclick="myFunction("public")">Copy Public Key</button>
            <h2>Private Key: <div id="private">${private_key}</div></h2><button onclick="myFunction("private")">Copy Private Key</button>
            </div>`;

            transporter
                .sendMail({
                    to: email,
                    from: "server@joulon.org",
                    subject: "Joulon wallet created succesfully",
                    html: html_doc
                })
                .then(res3 => {
                    res.send({
                        success: true
                    });
                })
                .catch(err => {
                    console.log(err);
                });
        })
        .catch(err => {
            console.log(err);
        });
});

router.post("/login", (req, res) => {
    let data = req.body;
    UUID = data.uuid;
    if (validate(UUID, 5)) {
        res.send({
            success: true
        });
    } else {
        res.send({
            success: false
        });
    }
});

router.post("/newTransaction", (req, res) => {
    let data = req.body;
    let transaction = {
        wallet: {
            private_key: data.private_key,
            public_key: data.public_key,
            wallet_id: data.wallet_id
        },
        transaction: {
            sender: data.sender,
            recipient: data.recipient,
            amount: data.amount,
            description: data.description
        }
    };
    axios
        .post("/sign_transaction", transaction)
        .then(res => {
            client.publish("/new_transaction", JSON.stringify(transaction));
            res.send({
                success: true
            });
        })
        .catch(err => {
            console.log(err);
        });
});

router.post("/getBalance", (req, res) => {
    let UUID = req.body.uuid;
    client.subscribe(`get_balance/${UUID}`);
    client.on("message", (topic, message) => {
        if (topic == `get_balance/${UUID}`) {
            let amount = parseInt(message.toString());
            client.unsubscribe(`get_balance/${UUID}`);
            res.send({
                success: true,
                amount: amount
            });
        }
    });
});

module.exports = router;
