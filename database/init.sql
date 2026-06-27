CREATE TABLE IF NOT EXISTS app_status (

    id SERIAL PRIMARY KEY,

    label TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT NOW()

);

INSERT INTO app_status(label)

VALUES ('Démarrage Application');