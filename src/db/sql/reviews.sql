-- name: get_most_recent_book_reviews
SELECT
    reviews.book_id,
    reviews.user_id,
    reviews.content,
    reviews.created_at,
    books.title,
    books.author_names,
    books.openlib_work_key,
    books.first_publish_year,
    books.number_of_pages_median,
    books.known_publishers,
    books.openlib_tags,
    books.remote_links,
    books.openlib_cover_ids
FROM reviews
JOIN books on books.id = reviews.book_id
ORDER by updated_at desc
LIMIT 10
;

-- name: get_reviews_by_book_id
SELECT * FROM reviews JOIN books ON books.id = reviews.book_id WHERE reviews.book_id = :book_id;

-- name: get_book_and_reviews_by_book_id
SELECT books.*, reviews.*
FROM books
LEFT JOIN reviews ON books.id = reviews.book_id
WHERE books.id = :book_id;

-- name: insert_review!
INSERT INTO reviews (
        user_id,
        book_id,
        content
) VALUES (
        :user_id,
        :book_id,
        :content
        )
