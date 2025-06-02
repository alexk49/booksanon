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
    known_publishers TEXT[] DEFAULT '{}',
    isbns_13 TEXT[] DEFAULT '{}',
    isbns_10 TEXT[] DEFAULT '{}',
    openlib_tags TEXT[] DEFAULT '{}',
    openlib_cover_ids TEXT[] DEFAULT '{}',
    number_of_pages_median INT DEFAULT 0,
    remote_links JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
