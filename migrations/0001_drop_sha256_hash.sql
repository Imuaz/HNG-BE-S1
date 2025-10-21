-- Migration: Drop sha256_hash column from strings table
-- Run this on your PostgreSQL database to remove the deprecated column.

ALTER TABLE IF EXISTS strings
    DROP COLUMN IF EXISTS sha256_hash;
