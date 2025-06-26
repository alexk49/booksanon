-- name: get_book_by_openlib_work_key^
SELECT * FROM books WHERE openlib_work_key = :openlib_work_key;

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
SELECT *
FROM books
WHERE
  title ILIKE '%' || :search_query || '%'
  OR array_to_string(author_names, ', ') ILIKE '%' || :search_query || '%'
LIMIT 100;

-- name: get_books_by_author
SELECT 
  b.* 
FROM books b
JOIN book_authors ba ON ba.book_id = b.id
WHERE ba.author_id = :author_id
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
    :openlib_cover_ids,
    :number_of_pages_median,
    :remote_links
)
ON CONFLICT (openlib_work_key) DO UPDATE SET openlib_work_key = EXCLUDED.openlib_work_key
RETURNING id;

-- name: link_book_author!
INSERT INTO book_authors (book_id, author_id) VALUES (:book_id, :author_id) ON CONFLICT DO NOTHING;

