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
    e.preventDefault();
    const formData = new FormData(formDataEl)
    return await fetchFormResponse(apiRoute, formData);
}

function createElWithClass(tag, className) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  return el;
}

function setUpBackBtn ({cardViewController, resultsDivEl, reviewFormEl, reviewCardContainerEl}) {
  const backBtnEl = document.getElementById("back-btn");

  if (backBtnEl) {
    backBtnEl.addEventListener("click", () => {
      const bookCard = reviewCardContainerEl.querySelector(".book-card");
      cardViewController.restoreCard(bookCard);
      switchToResultsView(resultsDivEl, reviewFormEl)
    });
  }
}

function switchToResultsView(resultsDivEl, formEl) {
  resultsDivEl.classList.remove("hidden");
  formEl.classList.add("hidden");
}

function switchToReviewView ({resultsDivEl, reviewCardContainerEl, reviewFormEl}, card) {
  resultsDivEl.classList.add("hidden");
  reviewCardContainerEl.innerHTML = "";
  reviewCardContainerEl.appendChild(card);
  reviewFormEl.classList.remove("hidden");
}

function setUpSelectBtn (card, selectBtnEl, ui) {
  selectBtnEl.addEventListener("click", () => {
    ui.cardViewController.captureCardPosition(card);
    switchToReviewView(ui, card);
  });
}

function getBookDataFromResponse (response, resultsDivEl) {
    if (response && Array.isArray(response.results)) {
      resultsDivEl.innerHTML = ""; 
      return response.results
  } else {
      resultsDivEl.innerText = "No results found.";
    return null
  }

}

function setUpSearchForm (ui) {
  ui.searchFormEl.addEventListener('submit', async function(e) {
      response = await handleFormSubmission(e, this, "/search_books");
      books = getBookDataFromResponse(response, ui.resultsDivEl)

      books.forEach(book => {
        const card = createBookCardEl(book, ui);
        ui.resultsDivEl.appendChild(card);
      });
  });
}

function createBookCardEl (book, ui) {
      // Create card container
      const card = document.createElement("div");
      card.className = "book-card";

      const imgUrl = getImgUrl(book.cover_id)
      const imgWrapperEl = createImgWrapperEl(imgUrl);
      card.appendChild(imgWrapperEl);

      const bookMetaEl = createElWithClass("div", "book-meta");

      bookMetaEl.appendChild(createTitleEl(book.title));

      bookMetaEl.appendChild(createAuthorEl(book.author_names));

      bookMetaEl.appendChild(createPublishYearEl(book.first_publish_year));

      const pageNumEl = createPageNumEl(book.number_of_pages);
      if (pageNumEl) bookMetaEl.appendChild(pageNumEl);

      const openLibLink = getOpenLibLink(book.openlib_work_key);
      bookMetaEl.appendChild(createOpenLibLinkEl(openLibLink));

      const selectBtnEl = createSelectBtnEl();
      setUpSelectBtn (card, selectBtnEl, ui);
      bookMetaEl.appendChild(selectBtnEl);

      card.appendChild(bookMetaEl);
      return card
}

function getImgUrl (coverId) {
  return `https://covers.openlibrary.org/b/id/${coverId}-M.jpg`
}

function createImgWrapperEl (imgUrl) {
    const imgWrapperEl = createElWithClass("div", "img-wrapper");

    const coverImg = document.createElement("img");
    coverImg.src = imgUrl;
    coverImg.alt = "book cover";
    coverImg.loading = "lazy";

    imgWrapperEl.appendChild(coverImg)
    return imgWrapperEl
}

function createTitleEl (bookTitle) {
    const titleEl = document.createElement("h3");
    titleEl.innerText = bookTitle;
    return titleEl
}

function createAuthorEl (authorNames) {
    const authorEl = document.createElement("p");
    authorEl.innerText = `by ${authorNames}`;
    return authorEl
}

function getOpenLibLink (openLibWorkKey) {
  return `https://openlibrary.org${openLibWorkKey}`;
}

function createOpenLibLinkEl (openLibLink) {
  const linkHolderEl = document.createElement("p");
  const link = document.createElement("a");
  link.href = openLibLink;
  link.target = "_blank";
  link.innerText = "OpenLibrary Link";
  linkHolderEl.appendChild(link)
  return linkHolderEl
}

function createSelectBtnEl () {
  const selectBtnEl = document.createElement("button");
  selectBtnEl.innerText = "Select";
  return selectBtnEl
}

function createPublishYearEl (firstPublishYear) {
  const publishYearEl = document.createElement("p");
  publishYearEl.innerText = `Published: ${firstPublishYear}`;
  return publishYearEl
}

function createPageNumEl (pageNum) {
  if (pageNum !== 0) {
    const pageNumEl = document.createElement("p");
    pageNumEl.innerText = `Pages: ${pageNum}`;
    return pageNumEl
  } else {
    return null
  }
}

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
    restoreCard
  };
}

function main () {
  const ui = {
    resultsDivEl: document.getElementById("results"),
    reviewFormEl: document.getElementById("review-form"),
    reviewCardContainerEl: document.getElementById("review-card-container"),
    searchFormEl: document.getElementById("search-form"),
    cardViewController: createCardViewController()
  };

  setUpBackBtn(ui);

  if (ui.searchFormEl) {
      setUpSearchForm(ui);
  }
}

document.addEventListener("DOMContentLoaded", main);
