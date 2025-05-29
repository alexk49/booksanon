-- name: get_author_by_openlib_id
SELECT * FROM authors WHERE author_openlib_id = :author_openlib_id;

-- name: insert_author!
INSERT INTO authors (
    name,
    author_openlib_id,
    birth_date,
    death_date,
    remote_ids
)
VALUES (
    :name,
    :author_openlib_id,
    :birth_date,
    :death_date,
    :remote_ids
)
RETURNING *;
