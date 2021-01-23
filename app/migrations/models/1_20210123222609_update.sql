-- upgrade --
CREATE TABLE IF NOT EXISTS "hashmod" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "hash" VARCHAR(199) NOT NULL,
    "use_type" VARCHAR(20) NOT NULL,
    "expires" TIMESTAMPTZ,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID REFERENCES "auth_user" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "hashmod";
