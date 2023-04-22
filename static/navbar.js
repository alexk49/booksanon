/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function toggleNav() {
  var x = document.getElementById("nav-bar");
  if (x.className === "nav-bar") {
    x.className += " responsive";
  } else {
    x.className = "nav-bar";
  }
  var navitems = document.getElementsByClassName("nav-item");
  var lengthNavItems = navitems.length;
  for (var i = 0; i < lengthNavItems; i++) {
    if (navitems[i].className === "nav-item") {
      navitems[i].className += " responsive";
    } else {
      navitems[i].className = "nav-item";
    }
  }
}
