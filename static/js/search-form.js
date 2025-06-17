import { handleFormSubmission } from "./utils.js";
import { createBookCardEl } from "./book-cards.js";

export function setUpSearchForm(ui) {
  ui.searchFormEl.addEventListener("submit", async function (e) {
    const response = await handleFormSubmission(e, this, "/search_books");
    const books = getBookDataFromResponse(response, ui.resultsDivEl);

    books.forEach((book) => {
      const card = createBookCardEl(book);
      const selectBtnEl = card.querySelector(".select-book-btn");
      setUpSelectBtn(card, selectBtnEl, ui);
      ui.resultsDivEl.appendChild(card);
    });
  });
}

export function setUpSelectBtn(card, selectBtnEl, ui) {
  selectBtnEl.addEventListener("click", () => {
    ui.cardViewController.captureCardPosition(card);
    switchToReviewView(ui, card);
  });
}

export function getBookDataFromResponse(response, resultsDivEl) {
  if (response && Array.isArray(response.results)) {
    resultsDivEl.innerHTML = "";
    return response.results;
  } else {
    resultsDivEl.innerText = "No results found.";
    return null;
  }
}

export function setUpBackBtn(
  {
    cardViewController,
    resultsDivEl,
    reviewFormContainerEl,
    reviewCardContainerEl,
  },
  backBtnEl,
) {
  backBtnEl.addEventListener("click", () => {
    const bookCard = reviewCardContainerEl.querySelector(".book-card");
    cardViewController.restoreCard(bookCard);
    switchToResultsView(resultsDivEl, reviewFormContainerEl);
  });
}

export function switchToResultsView(resultsDivEl, formEl) {
  resultsDivEl.classList.remove("hidden");
  formEl.classList.add("hidden");
}

export function switchToReviewView(
  {
    resultsDivEl,
    reviewCardContainerEl,
    reviewFormContainerEl,
    reviewHiddenIdEl,
  },
  card,
) {
  resultsDivEl.classList.add("hidden");
  reviewCardContainerEl.innerHTML = "";
  reviewCardContainerEl.appendChild(card);
  reviewFormContainerEl.classList.remove("hidden");
  reviewHiddenIdEl.value = card.querySelector(".openlib_id").innerText;
}
