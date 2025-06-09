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

async function setUpSearchForm(searchFormEl) {
    searchFormEl.addEventListener('submit', async function(e) {
      e.preventDefault();

      const formData = new FormData(searchFormEl);
      console.log(formData);
      
      const searchTerm = document.getElementById('search-term').value;
      console.log(searchTerm);

      const result = await fetchFormResponse("/search_book", searchTerm);
      console.log(result);
    });
}

const searchFormEl = document.getElementById('search-form')

if (searchFormEl) {
  setUpSearchForm(searchFormEl);
}
