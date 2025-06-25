-- name: get_user_id_by_username
SELECT id FROM users WHERE username = :username;

-- name: create_anon!
INSERT INTO users (username)
VALUES ('anon')
ON CONFLICT (username) DO NOTHING;
