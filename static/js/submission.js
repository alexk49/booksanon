import { getSubmissionsFromLocalStorage } from "./utils.js";
import {
  createElWithClass,
  createElWithText,
  getOpenLibLink,
  createOpenLibLinkEl,
} from "./book-cards.js";

function renderSubmissions(submissionsEl) {
  const submissions = getSubmissionsFromLocalStorage();
  submissions.sort((a, b) => b.timestamp - a.timestamp);

  if (submissions.length === 0) {
    submissionsEl.textContent = "No submissions found.";
    return;
  }

  submissions.forEach((submission) => {
    const submissionEl = createSubmissionEl(submission);
    submissionsEl.appendChild(submissionEl);
  });
}

function createSubmissionEl(submission) {
  const container = createElWithClass("div", "submission-container");
  const date = new Date(submission.timestamp).toLocaleString();

  const heading = createElWithText("h3", `Submitted on ${date}`);
  const review = createElWithText("p", submission.review);
  const link = createOpenLibLinkEl(getOpenLibLink(submission.openlib_id));

  container.append(heading, review, link);
  return container;
}

function main() {
  const submissionsEl = document.getElementById("submissions-container");

  if (submissionsEl) {
    renderSubmissions(submissionsEl);
  }
}

document.addEventListener("DOMContentLoaded", main);
