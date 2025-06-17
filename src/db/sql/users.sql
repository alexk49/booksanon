-- name: get_user_id_by_username
SELECT id FROM users WHERE username = :username;
