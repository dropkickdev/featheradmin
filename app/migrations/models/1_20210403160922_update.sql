-- upgrade --
ALTER TABLE "core_option" ADD "admin_only" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "core_option" DROP COLUMN "admin_only";
