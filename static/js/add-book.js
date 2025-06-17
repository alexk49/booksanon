import { setUpBackBtn, setUpSearchForm } from "./search-form.js";
import {
  addSubmissionToLocalStorage,
  handleFormSubmission,
  populateCsrfTokens,
} from "./utils.js";

function createCardViewController() {
  let previousCardParent = null;
  let previousCardNextSibling = null;

  function captureCardPosition(card) {
    previousCardParent = card.parentNode;
    previousCardNextSibling = card.nextElementSibling;
  }

  function restoreCard(bookCard) {
    if (bookCard && previousCardParent) {
      if (previousCardNextSibling) {
        previousCardParent.insertBefore(bookCard, previousCardNextSibling);
      } else {
        previousCardParent.appendChild(bookCard);
      }
    }
    previousCardParent = null;
    previousCardNextSibling = null;
  }

  return {
    captureCardPosition,
    restoreCard,
  };
}

function setUpReviewForm(reviewFormContainerEl) {
  reviewFormContainerEl.addEventListener("submit", async function (event) {
    const response = await handleFormSubmission(event, this, "/submit_book");

    if (response.success) {
      const { submission_id } = response;
      const submittedData = new FormData(this);

      const newSubmission = {
        id: submission_id,
        timestamp: Date.now(),
        review: submittedData.get("review"),
        openlib_id: submittedData.get("openlib_id_hidden"),
      };

      addSubmissionToLocalStorage(newSubmission);

      window.location.href = "/submission";
    } else {
      alert("Submission failed.");
      console.log(response);
    }
  });
}

function main() {
  populateCsrfTokens();

  const ui = {
    resultsDivEl: document.getElementById("results"),
    reviewFormContainerEl: document.getElementById("review-form"),
    reviewCardContainerEl: document.getElementById("review-card-container"),
    reviewHiddenIdEl: document.getElementById("openlib-id-hidden"),
    searchFormEl: document.getElementById("search-form"),
    cardViewController: createCardViewController(),
  };

  const backBtnEl = document.getElementById("back-btn");
  if (backBtnEl) {
    setUpBackBtn(ui, backBtnEl);
  }

  if (ui.searchFormEl) {
    setUpSearchForm(ui);
  }

  const submitReviewForm = document.getElementById("submit-form");

  if (submitReviewForm) {
    setUpReviewForm(submitReviewForm);
  }
}

document.addEventListener("DOMContentLoaded", main);
