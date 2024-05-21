
// event listener for showing popup for instructions
document.addEventListener("DOMContentLoaded", function () {
  // variables
  var popupLink = document.querySelector(".popup-link");
  var popupOverlay = document.querySelector(".popup-overlay");
  var closeBtn = document.querySelector(".close-btn");

  popupLink.addEventListener("click", function (e) {
    e.preventDefault();
    popupOverlay.style.display = "flex";
  });

  closeBtn.addEventListener("click", function () {
    popupOverlay.style.display = "none";
  });
});

// event listener for showing popup for feedback form
document.addEventListener("DOMContentLoaded", function () {
  var feedbackForm = document.querySelector("#feedbackForm");
  var feedbackFormOverlay = document.querySelector("#feedbackFormOverlay");
  var feedbackClose = document.querySelector(".feedback-close");

  feedbackForm.addEventListener("click", function (e) {
    e.preventDefault();
    feedbackFormOverlay.style.display = "flex";
  });


  feedbackClose.addEventListener("click", function () {
    feedbackFormOverlay.style.display = "none";
  });


});
