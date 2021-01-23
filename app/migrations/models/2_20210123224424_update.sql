-- upgrade --
ALTER TABLE "auth_hash" ALTER COLUMN "user_id" SET NOT NULL;
-- downgrade --
ALTER TABLE "hashmod" ALTER COLUMN "user_id" DROP NOT NULL;
