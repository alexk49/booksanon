-- name: get_author_books_and_reviews
SELECT
  json_build_object(
    'id', a.id,
    'name', a.name,
    'birth_date', a.birth_date,
    'death_date', a.death_date
  ) AS author,
  json_agg(
    json_build_object(
      'id', b.id,
      'title', b.title,
      'reviews', COALESCE(rv.reviews, '[]'::json)
    )
    ORDER BY b.updated_at DESC
  ) AS books
FROM authors a
LEFT JOIN (
  SELECT 
    ba.author_id, 
    b.id, b.title, b.updated_at
  FROM book_authors ba
  JOIN books b ON b.id = ba.book_id
) b ON b.author_id = a.id
LEFT JOIN (
  -- aggregate reviews per book
  SELECT 
    r.book_id,
    json_agg(json_build_object(
      'id', r.id,
      'user_id', r.user_id,
      'content', r.content,
      'created_at', r.created_at
    ) ORDER BY r.created_at DESC) AS reviews
  FROM reviews r
  GROUP BY r.book_id
) rv ON rv.book_id = b.id
WHERE a.id = :author_id
GROUP BY a.id;

-- name: get_author_by_id^
SELECT * FROM authors WHERE id = :author_id;

-- name: get_author_by_openlib_id
SELECT * FROM authors WHERE openlib_id = :openlib_id;

-- name: get_author_id_by_openlib_id
SELECT id FROM authors WHERE openlib_id = :openlib_id;

-- name: insert_author<!
-- returns: id
INSERT INTO authors (
    name,
    openlib_id,
    birth_date,
    death_date,
    remote_ids
)
VALUES (
    :name,
    :openlib_id,
    :birth_date,
    :death_date,
    :remote_ids
)
ON CONFLICT (openlib_id) DO UPDATE SET openlib_id = EXCLUDED.openlib_id
RETURNING id;
