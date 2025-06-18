-- name: get_most_recent_book_reviews
SELECT reviews.book_id, reviews.user_id, reviews.content, reviews.created_at, books.title, books.author_names, books.openlib_work_key, books.first_publish_year, books.number_of_pages_median, books.known_publishers, books.openlib_tags, books.remote_links, books.openlib_cover_ids FROM reviews JOIN books ON books.id = reviews.book_id ORDER BY updated_at DESC LIMIT 10;

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
