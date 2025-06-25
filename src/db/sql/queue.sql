-- name: insert_review_submission<!
INSERT INTO pending_reviews (
    openlib_id,
    review,
    username
) VALUES (
    :openlib_id,
    :review,
    :username
)
RETURNING id;

-- name: read_form_submission^
SELECT * FROM pending_reviews WHERE id = :submission_id; 

-- name: complete_form_submission!
UPDATE pending_reviews SET status = 'complete' WHERE id = :submission_id;
