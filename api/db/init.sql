-- applications table
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- versions table
CREATE TABLE versions (
    id SERIAL PRIMARY KEY,
    version TEXT NOT NULL,
    is_testing BOOLEAN DEFAULT FALSE,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE
);

-- locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    path TEXT NOT NULL, -- can be s3://bucket/path or /local/path
    version_id INTEGER REFERENCES versions(id) ON DELETE CASCADE
);

-- change_logs table
CREATE TABLE change_logs (
    id SERIAL PRIMARY KEY,
    ticket TEXT,
    description TEXT NOT NULL,
    visible BOOLEAN DEFAULT TRUE,
    version_id INTEGER REFERENCES versions(id) ON DELETE CASCADE
);
