function show_hide_review_box() {
  if (document.getElementById("yes-review-button").checked) {
    // show review box
    document.getElementById("review-box").style.display = "block";
    // when review box showing, get count of characters
    const textarea = document.getElementById("review-box");
    textarea.addEventListener("input", (event) => {
      const target = event.currentTarget;
      // get set max length
      const maxLength = target.getAttribute("maxlength");
      // get current value in box
      const currentLength = target.value.length;

      const counter = document.getElementById("counter");

      counter.innerHTML = `${currentLength}/${maxLength}`;
    });
  } else {
    document.getElementById("review-box").style.display = "none";
  }
}
