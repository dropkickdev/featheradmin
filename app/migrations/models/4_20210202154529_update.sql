-- upgrade --
ALTER TABLE "auth_hash" ADD "is_used" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "auth_hash" DROP COLUMN "is_used";
