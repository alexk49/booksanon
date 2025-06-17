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
