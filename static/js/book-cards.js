export function createBookCardEl(book) {
  const card = document.createElement("div");
  card.className = "book-card";

  const imgUrl = getImgUrl(book.cover_id);
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

  const hiddenIdEl = createHiddenIdEl(book.openlib_work_key);
  bookMetaEl.appendChild(hiddenIdEl);

  const selectBtnEl = createSelectBtnEl();
  bookMetaEl.appendChild(selectBtnEl);

  card.appendChild(bookMetaEl);
  return card;
}

export function getImgUrl(coverId) {
  return `https://covers.openlibrary.org/b/id/${coverId}-M.jpg`;
}

export function createImgWrapperEl(imgUrl) {
  const imgWrapperEl = createElWithClass("div", "img-wrapper");

  const coverImg = document.createElement("img");
  coverImg.src = imgUrl;
  coverImg.alt = "book cover";
  coverImg.loading = "lazy";

  imgWrapperEl.appendChild(coverImg);
  return imgWrapperEl;
}

export function createTitleEl(bookTitle) {
  const titleEl = document.createElement("h3");
  titleEl.innerText = bookTitle;
  return titleEl;
}

export function createAuthorEl(authorNames) {
  const authorEl = document.createElement("p");
  authorEl.innerText = `by ${authorNames}`;
  return authorEl;
}

export function getOpenLibLink(openLibWorkKey) {
  return `https://openlibrary.org${openLibWorkKey}`;
}

export function createOpenLibLinkEl(openLibLink) {
  const linkHolderEl = document.createElement("p");

  const link = document.createElement("a");
  link.href = openLibLink;
  link.target = "_blank";
  link.innerText = "OpenLibrary";

  linkHolderEl.appendChild(link);
  return linkHolderEl;
}

export function createSelectBtnEl() {
  const selectBtnEl = createElWithClass("button", "select-book-btn");
  selectBtnEl.innerText = "Select";
  return selectBtnEl;
}

export function createPublishYearEl(firstPublishYear) {
  const publishYearEl = document.createElement("p");
  publishYearEl.innerText = `Published: ${firstPublishYear}`;
  return publishYearEl;
}

export function createPageNumEl(pageNum) {
  if (pageNum !== 0) {
    const pageNumEl = document.createElement("p");
    pageNumEl.innerText = `Pages: ${pageNum}`;
    return pageNumEl;
  } else {
    return null;
  }
}

export function createHiddenIdEl(openLibWorkKey) {
  const hiddenIdEl = createElWithClass("div", "hidden");
  hiddenIdEl.innerText = openLibWorkKey;
  hiddenIdEl.classList.add("openlib_id");
  return hiddenIdEl;
}

export function createElWithClass(tag, className) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  return el;
}

export function createElWithText(tag, text) {
  const el = document.createElement(tag);
  el.innerText = text;
  return el;
}
