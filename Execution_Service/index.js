"use strict";
const app = require("./configs/app.config")
const path = require("path");
const PORT = process.env.port || process.env.PORT || 4003

console.log("Current working directory:", path.resolve("."));
app.listen(PORT, () => console.log("Server started on port:", PORT))