async function fetchFormResponse(url, formData) {
  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
  } catch (error) {
    let err_msg = `Error posting form data to: ${url} - ${error}`;
    console.error(err_msg);
    return { success: "false", message: err_msg };
  }
}

async function handleFormSubmission(e, formDataEl, apiRoute) {
      e.preventDefault(e);
      const formData = new FormData(formDataEl)
      return await fetchFormResponse(apiRoute, formData);
}

const searchFormEl = document.getElementById('search-form')

if (searchFormEl) {
    searchFormEl.addEventListener('submit', async function(e) {
      response = await handleFormSubmission(e, this, "/search_books")
      console.log(response)
      const resultsDiv = document.getElementById("results")

      if (response && Array.isArray(response.results)) {
        response.results.forEach(book => {
          const item = document.createElement("div");
          const imgDiv = document.createElement("div");
          imgDiv.innerHTML = `<img loading="lazy" class="cover" src="https://covers.openlibrary.org/b/id/${book.cover_id}-S.jpg" alt="book cover">`
          item.innerText = `${book.title} by ${book.author_names} - published: ${book.first_publish_year} - pages: ${book.number_of_pages} - key - ${book.openlib_work_key} - openlib link - https://openlibrary.org${book.openlib_work_key}`;
          resultsDiv.appendChild(imgDiv);
          resultsDiv.appendChild(item);
        });
      } else {
        resultsDiv.innerText = "No results found.";
      }
    });
}
