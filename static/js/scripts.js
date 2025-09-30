import { writeErrorsToContainer } from "./add-book.js";
import { handleFormSubmission, hideEl, showHiddenEl, populateCsrfTokens } from "./utils.js";

function setUpNavToggle(navToggleBtn, navMenu) {
  navToggleBtn.addEventListener("click", () => {
    const isOpen = navMenu.classList.toggle("open");
    navToggleBtn.setAttribute("aria-expanded", isOpen);
  });
}

function setUpNavSearchForm(navSearchFormEl, loaderEl) {
  if (navSearchFormEl) {
    navSearchFormEl.addEventListener("submit", () => {
      showHiddenEl(loaderEl);
    });
  }
}

function setUpExpandReviewBtn(reviewArticle) {
  const expandBtn = reviewArticle.querySelector(".expand-btn");
  const reviewContent = reviewArticle.querySelector(".review-content");

  if (!expandBtn || !reviewContent) return;

  expandBtn.addEventListener("click", () => {
    reviewContent.classList.toggle("review-content-expanded");
    reviewArticle.classList.toggle("compact-book-review-container-expanded");

    // Change the button text based on the expanded state
    if (reviewContent.classList.contains("review-content-expanded")) {
      expandBtn.textContent = "Hide review";
    } else {
      expandBtn.textContent = "Expand review";
    }
  });
}

function setUpFetchMoreReviews (fetchReviewsForm, bookshelvesEl, loaderEl) {
  fetchReviewsForm.addEventListener("submit", async function (e) {
    console.log("submitting")
    const response = await handleFormSubmission(
      e,
      this,
      "/api/fetch-more-reviews",
      loaderEl,
    );
    handleFetchReviewsResponse(response, bookshelvesEl)
  });
}

function handleFetchReviewsResponse(response, bookshelvesEl) {
  if (response.success && Array.isArray(response.data.results)) {
    const reviews = response.data.results;
    console.log(reviews);
    reviews.forEach(review => {
      console.log(review);
      const reviewsHtml = renderReviewHtml(review);
      bookshelvesEl.insertAdjacentHTML('beforeend', reviewsHtml);
    });

    const cursorInput = document.getElementById("cursor");
    cursorInput.value = response.data.next_cursor || "";
  } else {
    writeErrorsToContainer(response, bookshelvesEl);
  }
}


function renderReviewHtml(review) {
  // Create the book cover HTML if it exists
  const coverHtml = review.book.cover_id
    ? `<div class="img-wrapper">
         <a href="/book/${review.book.id}">
           <img src="https://covers.openlibrary.org/b/id/${review.book.cover_id}-M.jpg"
                alt="Book cover"
                loading="lazy" />
         </a>
       </div>`
    : "";

  const authorHtml = review.book.author_display ? `<p>by ${review.book.author_display}</p>` : "";

  const linkOutsHtml = (review.book.filtered_link_outs && review.book.filtered_link_outs.length > 0)
    ? `<div class="link-outs"><ul>` +
      review.book.filtered_link_outs.map(link => `<li><a href="${link.url}">${link.text}</a></li>`).join("") +
      `</ul></div>`
    : "";

  // Review content snippet vs full
  const reviewContentHtml = review.content.length > 150
    ? `<div class="review-content review-content-snippet">${review.content}</div>
       <button class="expand-btn">Expand review</button>`
    : `<div class="review-content">${review.content}</div>`;

    const footerHtml = `<footer class="book-review-footer">
      <small>First added: ${new Date(review.created_at).toLocaleString([], {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      })}</small>
    </footer>`;

  return `<article class="compact-book-review-container">
            <div class="review-card-wrapper">
              ${coverHtml}
              <div class="book-meta">
                <h3><a href="/book/${review.book.id}">${review.book.title}</a></h3>
                ${authorHtml}
                <p>Published: ${review.book.first_publish_year || ""}</p>
                <p>Pages: ${review.book.number_of_pages_median || ""}</p>
                ${linkOutsHtml}
              </div>
            </div>
            <section class="review-section">
              <h4 class="review-header"><a href="/review/${review.id}">Review</a></h4>
              ${reviewContentHtml}
            </section>
            ${footerHtml}
          </article>`;
}


function main() {
  populateCsrfTokens();

  const navToggleBtn = document.getElementById("nav-toggle");
  const navMenu = document.getElementById("nav-menu");

  setUpNavToggle(navToggleBtn, navMenu);

  const loaderEl = document.getElementById("global-loader");
  const navSearchFormEl = document.getElementById("nav-search-form");

  setUpNavSearchForm(navSearchFormEl, loaderEl);

  const reviewArticles = document.querySelectorAll(".compact-book-review-container");

  if (reviewArticles) {
    reviewArticles.forEach((review) => {
      setUpExpandReviewBtn(review);
    });
  }

  const fetchReviewsForm = document.getElementById("fetch-reviews-form");
  const bookshelvesEl = document.getElementById("review-bookshelves");

  if (fetchReviewsForm && bookshelvesEl) {
    setUpFetchMoreReviews(fetchReviewsForm,  bookshelvesEl, loaderEl);
  }

  window.addEventListener("pageshow", () => {
    hideEl(loaderEl);
  });
}

document.addEventListener("DOMContentLoaded", main);
