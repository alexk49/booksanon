import { getBookDataFromResponse, handleFormSubmission } from "./utils.js";
import { createBookCardEl } from "./book-cards.js";

export function setUpSearchForm(ui) {
  ui.searchFormEl.addEventListener("submit", async function (e) {
    const response = await handleFormSubmission(
      e,
      this,
      this.action,
      ui.loaderEl,
    );
    const books = getBookDataFromResponse(response, ui.resultsContainer);

    if (books) {
      books.forEach((book) => {
        const card = createBookCardEl(book);
        const selectBtnEl = card.querySelector(".select-book-btn");
        setUpSelectBtn(card, selectBtnEl, ui);
        ui.resultsContainer.appendChild(card);
      });
    }
  });
}

export function setUpSelectBtn(card, selectBtnEl, ui) {
  selectBtnEl.addEventListener("click", () => {
    ui.cardViewController.captureCardPosition(card);
    switchToReviewView(ui, card);
  });
}

export function setUpBackBtn(ui, backBtnEl) {
  backBtnEl.addEventListener("click", () => {
    const bookCard = ui.reviewCardContainerEl.querySelector(".book-card");
    ui.cardViewController.restoreCard(bookCard);
    switchToResultsView(ui);
  });
}

export function switchToResultsView({
  searchContainer,
  resultsContainer,
  reviewFormContainerEl,
}) {
  searchContainer.classList.remove("hidden");
  resultsContainer.classList.remove("hidden");
  reviewFormContainerEl.classList.add("hidden");
}

export function switchToReviewView(
  {
    searchContainer,
    resultsContainer,
    reviewCardContainerEl,
    reviewFormContainerEl,
    reviewHiddenIdEl,
  },
  card,
) {
  searchContainer.classList.add("hidden");
  resultsContainer.classList.add("hidden");
  reviewCardContainerEl.innerHTML = "";
  reviewCardContainerEl.appendChild(card);
  reviewFormContainerEl.classList.remove("hidden");
  reviewHiddenIdEl.value = card.querySelector(".openlib_id").innerText;
}
