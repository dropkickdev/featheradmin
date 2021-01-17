-- upgrade --
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "auth_user" (
    "deleted_at" TIMESTAMPTZ,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL  PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_verified" BOOL NOT NULL  DEFAULT False,
    "username" VARCHAR(50),
    "first_name" VARCHAR(191) NOT NULL  DEFAULT '',
    "middle_name" VARCHAR(191) NOT NULL  DEFAULT '',
    "last_name" VARCHAR(191) NOT NULL  DEFAULT '',
    "civil" VARCHAR(20) NOT NULL  DEFAULT '',
    "bday" DATE,
    "mobile" VARCHAR(50) NOT NULL  DEFAULT '',
    "telephone" VARCHAR(50) NOT NULL  DEFAULT '',
    "avatar" VARCHAR(191) NOT NULL  DEFAULT '',
    "status" VARCHAR(20) NOT NULL  DEFAULT '',
    "bio" VARCHAR(191) NOT NULL  DEFAULT '',
    "address1" VARCHAR(191) NOT NULL  DEFAULT '',
    "address2" VARCHAR(191) NOT NULL  DEFAULT '',
    "country" VARCHAR(2) NOT NULL  DEFAULT '',
    "zipcode" VARCHAR(20) NOT NULL  DEFAULT '',
    "timezone" VARCHAR(10) NOT NULL  DEFAULT '+00:00',
    "website" VARCHAR(20) NOT NULL  DEFAULT '',
    "last_login" TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS "idx_auth_user_email_1e0e57" ON "auth_user" ("email");
CREATE TABLE IF NOT EXISTS "auth_group" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(191) NOT NULL UNIQUE,
    "summary" TEXT NOT NULL,
    "deleted_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_auth_group_name_eb59d9" ON "auth_group" ("name");
CREATE TABLE IF NOT EXISTS "auth_permission" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(191) NOT NULL UNIQUE,
    "code" VARCHAR(191) NOT NULL UNIQUE,
    "deleted_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "group_id" INT NOT NULL REFERENCES "auth_group" ("id") ON DELETE CASCADE,
    "permission_id" INT NOT NULL REFERENCES "auth_permission" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_auth_group__group_i_cc817e" UNIQUE ("group_id", "permission_id")
);
CREATE TABLE IF NOT EXISTS "core_taxonomy" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "deleted_at" TIMESTAMPTZ,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(191) NOT NULL,
    "type" VARCHAR(20) NOT NULL,
    "sort" SMALLINT NOT NULL  DEFAULT 100,
    "author_id" UUID NOT NULL REFERENCES "auth_user" ("id") ON DELETE CASCADE,
    "parent_id" INT NOT NULL REFERENCES "core_taxonomy" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "auth_user_groups" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "deleted_at" TIMESTAMPTZ,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "group_id" INT NOT NULL REFERENCES "auth_group" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "auth_user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_auth_user_g_user_id_e50bb9" UNIQUE ("user_id", "group_id")
);
CREATE TABLE IF NOT EXISTS "auth_user_permissions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "deleted_at" TIMESTAMPTZ,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID NOT NULL REFERENCES "auth_user" ("id") ON DELETE CASCADE,
    "permission_id" INT NOT NULL REFERENCES "auth_permission" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_auth_user_p_user_id_f7a940" UNIQUE ("user_id", "permission_id")
);
CREATE TABLE IF NOT EXISTS "core_option" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(20) NOT NULL,
    "value" VARCHAR(191) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID REFERENCES "auth_user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "auth_user_groups" (
    "user_id" UUID NOT NULL REFERENCES "auth_user" ("id") ON DELETE CASCADE,
    "group_id" INT NOT NULL REFERENCES "auth_group" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "auth_user_permissions" (
    "user_id" UUID NOT NULL REFERENCES "auth_user" ("id") ON DELETE CASCADE,
    "permission_id" INT NOT NULL REFERENCES "auth_permission" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
    "auth_group_id" INT NOT NULL REFERENCES "auth_group" ("id") ON DELETE CASCADE,
    "permission_id" INT NOT NULL REFERENCES "auth_permission" ("id") ON DELETE CASCADE
);
