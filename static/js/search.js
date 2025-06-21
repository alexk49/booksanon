import { getBookDataFromResponse, handleFormSubmission } from "./utils.js";
import { createLocalBookCard } from "./book-cards.js";

export function setUpLocalSearch(ui) {
  ui.searchFormEl.addEventListener("submit", async function (e) {
    const response = await handleFormSubmission(e, this, this.action);
    const books = getBookDataFromResponse(response, ui.resultsContainer);

    books.forEach((book) => {
      const card = createLocalBookCard(book);
      ui.resultsContainer.appendChild(card);
    });
  });
}

function main() {
  const ui = {
    searchFormEl: document.getElementById("search-form"),
    resultsContainer: document.getElementById("results"),
  };

  if (ui.searchFormEl) {
    setUpLocalSearch(ui);
  }
}

document.addEventListener("DOMContentLoaded", main);
