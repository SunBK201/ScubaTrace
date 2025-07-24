import "./admin.js";
import { admin } from "./admin.js";
var fs = require("fs");

admin.name = "Pete";

class Runoob {
  constructor(name, url) {
    this.name = name;
    this.url = url;
  }
}

function myFunction(a, b) {
  var d = new Date();
  d = d.getHours();
  var time = d;
  if (time < 10) {
    document.write("<b>hi</b>");
  } else if (time >= 10 && time < 20) {
    document.write("<b>hi</b>");
  } else {
    document.write("<b>hi</b>");
  }
  return a * b;
}

document.getElementById("demo").innerHTML = myFunction(4, 3);
