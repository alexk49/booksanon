import { handleFormSubmission } from "./utils.js";
import { handleResponse } from "./search-form.js";

export function setUpLocalSearch(ui) {
  ui.searchFormEl.addEventListener("submit", async function (e) {
    const response = await handleFormSubmission(
      e,
      this,
      this.action,
      ui.loaderEl,
    );
    const localSearch = true;
    handleResponse(response, ui, localSearch);
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
