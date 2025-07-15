export async function fetchServerData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
  } catch (error) {
    let err_msg = `Error fetching data from: ${url}, ${error}`;
    console.error(err_msg);
    return { success: "false", message: err_msg };
  }
}

/* form utils using API end points */

export async function fetchFormResponse(url, formData) {
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

export async function handleFormSubmission(
  e,
  formDataEl,
  apiRoute,
  loaderEl = null,
) {
  if (loaderEl) {
    showHiddenEl(loaderEl);
  }
  e.preventDefault();
  const formData = new FormData(formDataEl);

  try {
    return await fetchFormResponse(apiRoute, formData);
  } catch (err) {
    console.error("Form submission failed:", err);
    throw err;
  } finally {
    if (loaderEl) {
      hideEl(loaderEl);
    }
  }
}

export function hideEl(el) {
  el.classList.add("hidden");
}

export function showHiddenEl(el) {
  el.classList.remove("hidden");
}

export function getBookDataFromResponse(response, resultsContainer) {
  if (response && Array.isArray(response.results)) {
    resultsContainer.innerHTML = "";
    return response.results;
  } else {
    resultsContainer.innerText = "No results found.";
    return null;
  }
}

/* csrf token utils */

export async function getCSRF() {
  const result = await fetchServerData("/api/csrf-token");
  return result.csrf_token;
}

export async function populateCsrfTokens() {
  const tokenEls = document.querySelectorAll(".csrf-token");

  if (tokenEls) {
    const token = await getCSRF();
    tokenEls.forEach((tokenEl) => {
      tokenEl.value = token;
    });
  }
}

/* local storage utils */

export function getSubmissionsFromLocalStorage() {
  return JSON.parse(localStorage.getItem("submissions") || "[]");
}

export function addSubmissionToLocalStorage(newSubmission) {
  const submissions = getSubmissionsFromLocalStorage();

  // Check if a submission with the same ID already exists
  const isDuplicate = submissions.some(
    (submission) => submission.id === newSubmission.id,
  );

  if (!isDuplicate) {
    submissions.push(newSubmission);
    localStorage.setItem("submissions", JSON.stringify(submissions));
  }
}

export function clearSubmissionsFromLocalStorage() {
  localStorage.removeItem("submissions");
}
