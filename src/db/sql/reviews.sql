-- name: get_most_recent_book_reviews
SELECT
    r.id AS review_id,
    r.book_id,
    r.user_id,
    r.content,
    r.created_at,
    r.updated_at,
    b.id AS book_id,
    b.title,
    b.openlib_work_key,
    b.openlib_cover_ids,
    b.author_names,
    b.author_keys,
    b.publishers,
    b.number_of_pages_median,
    b.openlib_tags,
    b.remote_links,
    b.first_publish_year,

    json_agg(json_build_object(
        'id', a.id,
        'name', a.name,
        'openlib_id', a.openlib_id
    ) ORDER BY a.id) AS authors
FROM reviews r
JOIN books b ON b.id = r.book_id
LEFT JOIN book_authors ba ON ba.book_id = b.id
LEFT JOIN authors a ON a.id = ba.author_id
GROUP BY r.id, b.id
ORDER BY r.created_at DESC
LIMIT 10;

-- name: get_reviews_by_book_id
SELECT * FROM reviews JOIN books ON books.id = reviews.book_id WHERE reviews.book_id = :book_id;

-- name: get_book_by_id_with_authors
SELECT 
    b.id AS book_id,
    b.title,
    b.openlib_work_key,
    b.openlib_cover_ids,
    b.openlib_description,
    b.author_names,
    b.author_keys,
    b.publishers,
    b.number_of_pages_median,
    b.openlib_tags,
    b.remote_links,
    b.first_publish_year,
    b.created_at,
    json_agg(json_build_object(
        'id', a.id,
        'name', a.name,
        'openlib_id', a.openlib_id
    ) ORDER BY a.name) AS authors
FROM books b
LEFT JOIN book_authors ba ON ba.book_id = b.id
LEFT JOIN authors a ON a.id = ba.author_id
WHERE b.id = :book_id
GROUP BY b.id;

-- name: get_reviews_by_book_id
SELECT 
    id AS review_id,
    book_id,
    user_id,
    content,
    created_at,
    updated_at
FROM reviews
WHERE book_id = :book_id
ORDER BY created_at DESC;

-- name: get_reviews_for_books
SELECT 
    r.id AS review_id,
    r.book_id,
    r.user_id,
    r.content,
    r.created_at,
    r.updated_at
FROM reviews r
WHERE r.book_id = ANY(:book_ids) 
ORDER BY r.created_at DESC;

-- name: get_review_and_book_by_review_id^
SELECT
    r.id AS review_id,
    r.book_id,
    r.user_id,
    r.content,
    r.created_at,
    r.updated_at,
    b.id AS book_id,
    b.title,
    b.openlib_work_key,
    b.openlib_cover_ids,
    b.openlib_description,
    b.author_names,
    b.author_keys,
    b.publishers,
    b.number_of_pages_median,
    b.openlib_tags,
    b.remote_links,
    b.first_publish_year,
    json_agg(json_build_object(
        'id', a.id,
        'name', a.name,
        'openlib_id', a.openlib_id
    ) ORDER BY a.name) AS authors
FROM reviews r
JOIN books b ON b.id = r.book_id
LEFT JOIN book_authors ba ON ba.book_id = b.id
LEFT JOIN authors a ON a.id = ba.author_id
WHERE r.id = :review_id
GROUP BY r.id, b.id;

-- name: insert_review!
INSERT INTO reviews (
        user_id,
        book_id,
        content
) VALUES (
        :user_id,
        :book_id,
        :content
        );
