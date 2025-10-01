import {
  createElWithClass,
  createElWithText,
  createImgWrapperEl,
  createTitleElWithLink,
  createAuthorEl,
  createPublishYearEl,
  createPageNumEl,
  createLinkOutsEl,
  getImgUrl,
} from "./book-cards.js"; 
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
      const reviewArticleEl = renderReviewArticleEl(review);
      bookshelvesEl.appendChild(reviewArticleEl);
      setUpExpandReviewBtn(reviewArticleEl);
    });

    setInputValue("cursor", response.data.next_cursor);
    setInputValue("review-id", response.data.next_review_id);
    fetchFormErrorsEl.innerText = '';

  } else {
    writeErrorsToContainer(response, fetchFormErrorsEl);
  }
}

export function renderReviewArticleEl(review) {
  const article = createElWithClass("article", "compact-book-review-container");
  const wrapper = createElWithClass("div", "review-card-wrapper");

  if (review.book.cover_id) {
    const imgUrl = getImgUrl(review.book.cover_id);
    const imgWrapper = createImgWrapperEl(imgUrl);

    const link = document.createElement("a");
    link.href = `/book/${review.book.id}`;
    link.appendChild(imgWrapper.querySelector("img"));
    imgWrapper.innerHTML = "";
    imgWrapper.appendChild(link);

    wrapper.appendChild(imgWrapper);
  }

  const meta = createElWithClass("div", "book-meta");

  meta.appendChild(createTitleElWithLink(review.book.title, review.book.id));

  if (review.book.author_display) {
    meta.appendChild(createAuthorEl(review.book.author_display));
  }

  meta.appendChild(createPublishYearEl(review.book.first_publish_year || ""));

  const pageNumEl = createPageNumEl(review.book.number_of_pages_median);
  if (pageNumEl) meta.appendChild(pageNumEl);

  if (review.book.filtered_link_outs?.length > 0) {
    meta.appendChild(createLinkOutsEl(review.book.filtered_link_outs));
  }

  wrapper.appendChild(meta);
  article.appendChild(wrapper);

  const section = createElWithClass("section", "review-section");

  const h4 = createElWithClass("h4", "review-header");
  const reviewLink = createElWithText("a", "Review");
  reviewLink.href = `/review/${review.id}`;
  h4.appendChild(reviewLink);
  section.appendChild(h4);

  if (review.content.length > 150) {
    const snippetDiv = createElWithClass("div", "review-content review-content-snippet");
    snippetDiv.textContent = review.content;

    const expandBtn = createElWithClass("button", "expand-btn");
    expandBtn.textContent = "Expand review";

    section.appendChild(snippetDiv);
    section.appendChild(expandBtn);
  } else {
    const contentDiv = createElWithClass("div", "review-content");
    contentDiv.textContent = review.content;
    section.appendChild(contentDiv);
  }

  article.appendChild(section);

  const footer = createElWithClass("footer", "book-review-footer");
  const small = createElWithText(
    "small",
    `First added: ${new Date(review.created_at).toLocaleString([], {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    })}`
  );
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
