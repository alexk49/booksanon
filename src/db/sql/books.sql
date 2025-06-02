-- name: get_book_by_openlib_work_key
SELECT * FROM books WHERE openlib_work_key = :openlib_work_key;

-- name: insert_book!
INSERT INTO books (
    title,
    author_names,
    author_keys,
    openlib_description,
    first_publish_year,
    openlib_work_key,
    known_publishers,
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
    :known_publishers,
    :isbns_13,
    :isbns_10,
    :openlib_tags,
    :openlib_cover_ids,
    :number_of_pages_median,
    :remote_links
)
ON CONFLICT (openlib_work_key) DO NOTHING;
