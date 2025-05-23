-- name: create_schema!

CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    author_openlib_id TEXT UNIQUE NOT NULL,
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
    author_name TEXT[],
    author_key TEXT[],
    description JSONB,
    first_publish_year INT,
    openlib_work_key TEXT UNIQUE NOT NULL,
    known_publishers TEXT[] DEFAULT '{}',
    isbns_13 TEXT[] DEFAULT '{}',
    isbns_10 TEXT[] DEFAULT '{}',
    openlib_cover_ids TEXT[] DEFAULT '{}',
    number_of_pages_median INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS book_authors (
    book_openlib_work_key TEXT REFERENCES books(openlib_work_key),
    author_openlib_id TEXT REFERENCES authors(author_openlib_id),
    PRIMARY KEY (book_openlib_work_key, author_openlib_id)
);
