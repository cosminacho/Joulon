require("dotenv").config();

const express = require("express");
const bodyParser = require("body-parser");
const router = require("./router");

const path = require("path");
// const fs = require('fs');
const port = process.env.PORT || 3000;

const cors = require("cors");
const history = require("connect-history-api-fallback");
const compression = require("compression");
const helmet = require("helmet");

const app = express();
app.use(bodyParser.json());
app.use(history());
app.use(helmet());
app.use(cors());
app.use(compression());

app.use("/", router);
app.use(express.static(path.join(__dirname, "dist")));

app.listen(port, () => {
    console.log(`App listening on port ${port}`);
});
