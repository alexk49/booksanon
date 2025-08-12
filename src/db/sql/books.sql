-- name: get_book_by_openlib_work_key^
SELECT 
    b.id AS book_id,
    b.updated_at
FROM books b
WHERE b.openlib_work_key = :openlib_work_key;

-- name: get_book_by_id^
SELECT * FROM books WHERE id = :book_id;

-- name: get_most_recent_books
SELECT 
    books.*, 
    json_agg(json_build_object(
        'id', author.id,
        'name', author.name
        'openlib_id', author.openlib_id
    ) ORDER BY author.name) AS authors
FROM books
LEFT JOIN book_authors ON book_author.book_id = book.id
LEFT JOIN authors ON author.id = book_author.author_id
GROUP BY book_.id
ORDER BY book.updated_at DESC
LIMIT 10;

-- name: search_books
SELECT 
    b.id AS book_id,
    b.title,
    b.openlib_work_key,
    b.cover_id,
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
FROM books b
JOIN book_authors ba ON ba.book_id = b.id
JOIN authors a ON a.id = ba.author_id
WHERE
    b.title ILIKE '%' || :search_query || '%'
    OR a.name ILIKE '%' || :search_query || '%'
GROUP BY 
    b.id,
    b.title,
    b.openlib_work_key,
    b.cover_id,
    b.openlib_cover_ids,
    b.openlib_description,
    b.author_names,
    b.author_keys,
    b.publishers,
    b.number_of_pages_median,
    b.openlib_tags,
    b.remote_links,
    b.first_publish_year
ORDER BY b.title
LIMIT 100;

-- name: get_books_by_author
SELECT 
    b.id AS book_id,
    b.title,
    b.openlib_work_key,
    b.cover_id,
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
FROM books b
JOIN book_authors ba ON ba.book_id = b.id
JOIN authors a ON a.id = ba.author_id
WHERE ba.author_id = :author_id
GROUP BY b.id
ORDER BY b.updated_at DESC;

-- name: insert_book<!
INSERT INTO books (
    title,
    author_names,
    author_keys,
    openlib_description,
    first_publish_year,
    openlib_work_key,
    publishers,
    isbns_13,
    isbns_10,
    openlib_tags,
    cover_id,
    openlib_cover_ids,
    number_of_pages_median,
    remote_links
) VALUES (
    :title,
    :author_names,
    :author_keys,
    :openlib_description,
    :first_publish_year,
    :openlib_work_key,
    :publishers,
    :isbns_13,
    :isbns_10,
    :openlib_tags,
    :cover_id,
    :openlib_cover_ids,
    :number_of_pages_median,
    :remote_links
)
ON CONFLICT (openlib_work_key) DO UPDATE SET
    author_names = EXCLUDED.author_names,
    author_keys = EXCLUDED.author_keys,
    openlib_description = EXCLUDED.openlib_description,
    first_publish_year = EXCLUDED.first_publish_year,
    publishers = EXCLUDED.publishers,
    isbns_13 = EXCLUDED.isbns_13,
    isbns_10 = EXCLUDED.isbns_10,
    openlib_tags = EXCLUDED.openlib_tags,
    cover_id = EXCLUDED.cover_id,
    openlib_cover_ids = EXCLUDED.openlib_cover_ids,
    number_of_pages_median = EXCLUDED.number_of_pages_median,
    remote_links = EXCLUDED.remote_links,
    updated_at = CURRENT_TIMESTAMP
RETURNING id;

-- name: link_book_author!
INSERT INTO book_authors (book_id, author_id) VALUES (:book_id, :author_id) ON CONFLICT DO NOTHING;
