-- name: get_author_by_id^
SELECT * FROM authors WHERE id = :author_id;

-- name: get_author_by_openlib_id^
SELECT * FROM authors WHERE openlib_id = :openlib_id;

-- name: get_author_id_by_openlib_id^
SELECT id FROM authors WHERE openlib_id = :openlib_id;

-- name: insert_author<!
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
