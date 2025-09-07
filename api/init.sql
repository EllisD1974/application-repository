-- applications table
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- versions table
CREATE TABLE versions (
    id SERIAL PRIMARY KEY,
    version TEXT NOT NULL,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE
);

-- locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    path TEXT NOT NULL, -- can be s3://bucket/path or /local/path
    version_id INTEGER REFERENCES versions(id) ON DELETE CASCADE
);
