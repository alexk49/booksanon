import { handleBookSearchResponse } from "./add-book.js";
import { handleFormSubmission } from "./utils.js";

export function setUpLocalSearch(ui) {
  ui.searchFormEl.addEventListener("submit", async function (e) {
    const response = await handleFormSubmission(
      e,
      this,
      this.action,
      ui.loaderEl,
    );
    const localSearch = true;
    handleBookSearchResponse(response, ui, localSearch);
  });
}

function main() {
  const ui = {
    loaderEl: document.getElementById("global-loader"),
    searchFormEl: document.getElementById("search-form"),
    resultsContainer: document.getElementById("results"),
  };

  if (ui.searchFormEl) {
    setUpLocalSearch(ui);
  }
}

document.addEventListener("DOMContentLoaded", main);
