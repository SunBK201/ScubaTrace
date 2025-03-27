import defaultExport from "module-name";
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
    document.write("<b>早上好</b>");
  } else if (time >= 10 && time < 20) {
    document.write("<b>今天好</b>");
  } else {
    document.write("<b>晚上好!</b>");
  }
  return a * b;
}

document.getElementById("demo").innerHTML = myFunction(4, 3);
