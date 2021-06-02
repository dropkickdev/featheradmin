-- upgrade --
ALTER TABLE "core_option" ADD "deleted_at" TIMESTAMPTZ;
-- downgrade --
ALTER TABLE "core_option" DROP COLUMN "deleted_at";
