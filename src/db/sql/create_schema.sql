-- name: create_schema!
CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    openlib_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    birth_date TEXT,
    death_date TEXT,
    remote_ids JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author_names TEXT[],
    author_keys TEXT[],
    openlib_description TEXT,
    first_publish_year INT,
    openlib_work_key TEXT UNIQUE NOT NULL,
    publishers TEXT[] DEFAULT '{}',
    isbns_13 TEXT[] DEFAULT '{}',
    isbns_10 TEXT[] DEFAULT '{}',
    openlib_tags TEXT[] DEFAULT '{}',
    cover_id TEXT,
    openlib_cover_ids TEXT[] DEFAULT '{}',
    number_of_pages_median INT DEFAULT 0,
    remote_links JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES authors(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    book_id INTEGER REFERENCES books(id),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_tags (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    book_id INTEGER REFERENCES books(id),
    tag TEXT NOT NULL,
    UNIQUE(user_id, book_id, tag)
);

CREATE TABLE IF NOT EXISTS pending_reviews (
    id SERIAL PRIMARY KEY,
    openlib_id TEXT NOT NULL,
    review TEXT NOT NULL,
    username TEXT NOT NULL,
    status TEXT DEFAULT 'pending'
);
