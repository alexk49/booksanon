export async function fetchServerData(url) {
  try {
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
      },
    });
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    return await response.json();
  } catch (error) {
    let err_msg = `Error fetching data from: ${url}, ${error}`;
    console.error(err_msg);
    return {
      success: false,
      message: err_msg,
      data: null,
    };
  }
}

/* form utils using API end points */

export async function fetchFormResponse(url, formData) {
  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        Accept: "application/json",
      },
    });
    return await response.json();
  } catch (error) {
    const err_msg = `Unexpected error posting form data to: ${url} - ${error}`;
    console.error(err_msg);
    return {
      success: false,
      message: err_msg,
      data: null,
      errors: null,
    };
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
    const err_msg = `Form submission failed: ${err}`;
    console.error(err_msg);
    return {
      success: false,
      message: err_msg,
      data: null,
      errors: null,
    };
  } finally {
    if (loaderEl) {
      hideEl(loaderEl);
    }
  }
}

/* DOM utils */

export function setInputValue(id, value) {
  const el = document.getElementById(id);
  if (el && value !== undefined && value !== null) {
    el.value = value;
  }
}

export function hideEl(el) {
  el.classList.add("hidden");
}

export function showHiddenEl(el) {
  el.classList.remove("hidden");
}

export function writeErrorsToContainer(response, resultsContainer) {
  resultsContainer.innerText = response.message || "An error occurred.";

  if (response.errors && typeof response.errors === "object") {
    const errorMessages = Object.entries(response.errors)
      .map(([field, error]) => {
        return `${field}: ${error}`;
      })
      .join(", ");

    resultsContainer.innerText += `\nErrors: ${errorMessages}`;
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
