import { handleFormSubmission, setInputValue, writeErrorsToContainer } from "./utils.js";

export function setUpExpandReviewBtn(reviewArticle) {
  const expandBtn = reviewArticle.querySelector(".expand-btn");
  const reviewContent = reviewArticle.querySelector(".review-content");

  if (!expandBtn || !reviewContent) return;

  expandBtn.addEventListener("click", () => {
    reviewContent.classList.toggle("review-content-expanded");
    reviewArticle.classList.toggle("compact-book-review-container-expanded");

    if (reviewContent.classList.contains("review-content-expanded")) {
      expandBtn.textContent = "Hide review";
    } else {
      expandBtn.textContent = "Expand review";
    }
  });
}

function setUpFetchMoreReviews (fetchReviewsForm, bookshelvesEl, fetchFormErrorsEl, loaderEl) {
  fetchReviewsForm.addEventListener("submit", async function (e) {
    console.log("submitting")
    const response = await handleFormSubmission(
      e,
      this,
      "/api/fetch-more-reviews",
      loaderEl,
    );
    console.log(response)
    handleFetchReviewsResponse(response, bookshelvesEl, fetchFormErrorsEl)
  });
}

function handleFetchReviewsResponse(response, bookshelvesEl, fetchFormErrorsEl) {
  console.log(response.message)
  if (response.success &&
  Array.isArray(response.data.results) &&
  response.data.results.length > 0) {
    const reviews = response.data.results;
    reviews.forEach(review => {
      const reviewEl = renderReviewEl(review);
      bookshelvesEl.appendChild(reviewEl);
      setUpExpandReviewBtn(reviewEl);
    });

    setInputValue("cursor", response.data.next_cursor);
    setInputValue("review-id", response.data.next_review_id);
    fetchFormErrorsEl.innerText = '';

  } else {
    writeErrorsToContainer(response, fetchFormErrorsEl);
  }
}

function renderReviewEl(review) {
  const article = document.createElement("article");
  article.classList.add("compact-book-review-container");

  const wrapper = document.createElement("div");
  wrapper.classList.add("review-card-wrapper");

  if (review.book.cover_id) {
    const imgWrapper = document.createElement("div");
    imgWrapper.classList.add("img-wrapper");

    const link = document.createElement("a");
    link.href = `/book/${review.book.id}`;

    const img = document.createElement("img");
    img.src = `https://covers.openlibrary.org/b/id/${review.book.cover_id}-M.jpg`;
    img.alt = "Book cover";
    img.loading = "lazy";

    link.appendChild(img);
    imgWrapper.appendChild(link);
    wrapper.appendChild(imgWrapper);
  }

  const meta = document.createElement("div");
  meta.classList.add("book-meta");

  const h3 = document.createElement("h3");
  const titleLink = document.createElement("a");
  titleLink.href = `/book/${review.book.id}`;
  titleLink.textContent = review.book.title;
  h3.appendChild(titleLink);
  meta.appendChild(h3);

  if (review.book.author_display) {
    const authorEl = document.createElement("p");
    authorEl.textContent = `by ${review.book.author_display}`;
    meta.appendChild(authorEl);
  }

  const publishEl = document.createElement("p");
  publishEl.textContent = `Published: ${review.book.first_publish_year || ""}`;
  meta.appendChild(publishEl);

  const pagesEl = document.createElement("p");
  pagesEl.textContent = `Pages: ${review.book.number_of_pages_median || ""}`;
  meta.appendChild(pagesEl);

  if (review.book.filtered_link_outs && review.book.filtered_link_outs.length > 0) {
    const linkOutsDiv = document.createElement("div");
    linkOutsDiv.classList.add("link-outs");

    const ul = document.createElement("ul");
    review.book.filtered_link_outs.forEach(link => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = link.url;
      a.textContent = link.text;
      li.appendChild(a);
      ul.appendChild(li);
    });

    linkOutsDiv.appendChild(ul);
    meta.appendChild(linkOutsDiv);
  }

  wrapper.appendChild(meta);
  article.appendChild(wrapper);

  const section = document.createElement("section");
  section.classList.add("review-section");

  const h4 = document.createElement("h4");
  h4.classList.add("review-header");

  const reviewLink = document.createElement("a");
  reviewLink.href = `/review/${review.id}`;
  reviewLink.textContent = "Review";
  h4.appendChild(reviewLink);

  section.appendChild(h4);

  if (review.content.length > 150) {
    const snippetDiv = document.createElement("div");
    snippetDiv.classList.add("review-content", "review-content-snippet");
    snippetDiv.textContent = review.content;

    const expandBtn = document.createElement("button");
    expandBtn.classList.add("expand-btn");
    expandBtn.textContent = "Expand review";

    section.appendChild(snippetDiv);
    section.appendChild(expandBtn);
  } else {
    const contentDiv = document.createElement("div");
    contentDiv.classList.add("review-content");
    contentDiv.textContent = review.content;
    section.appendChild(contentDiv);
  }

  article.appendChild(section);

  const footer = document.createElement("footer");
  footer.classList.add("book-review-footer");

  const small = document.createElement("small");
  small.textContent = `First added: ${new Date(review.created_at).toLocaleString([], {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  })}`;

  footer.appendChild(small);
  article.appendChild(footer);

  return article;
}

function main() {
  const loaderEl = document.getElementById("global-loader");

  const reviewArticles = document.querySelectorAll(".compact-book-review-container");

  if (reviewArticles) {
    reviewArticles.forEach((review) => {
      setUpExpandReviewBtn(review);
    });
  }

  const fetchReviewsForm = document.getElementById("fetch-reviews-form");
  const bookshelvesEl = document.getElementById("review-bookshelves");
  const fetchFormErrorsEl = document.getElementById("fetch-form-errors");

  if (fetchReviewsForm && bookshelvesEl && fetchFormErrorsEl) {
    setUpFetchMoreReviews(fetchReviewsForm,  bookshelvesEl, fetchFormErrorsEl, loaderEl);
  }
}
document.addEventListener("DOMContentLoaded", main);
