-- Fix RLS policy for site_pages table to allow inserts

-- Drop the existing restrictive policy
DROP POLICY IF EXISTS "Allow public read access" ON site_pages;

-- Create a policy that allows both read and write access
CREATE POLICY "Allow public read and write access"
  ON site_pages
  FOR ALL
  TO public
  USING (true)
  WITH CHECK (true);

-- Alternative: If you want to be more restrictive, you can create separate policies
-- CREATE POLICY "Allow public read access"
--   ON site_pages
--   FOR SELECT
--   TO public
--   USING (true);

-- CREATE POLICY "Allow service role insert access"
--   ON site_pages
--   FOR INSERT
--   TO service_role
--   WITH CHECK (true);

-- CREATE POLICY "Allow service role update access"
--   ON site_pages
--   FOR UPDATE
--   TO service_role
--   USING (true)
--   WITH CHECK (true);

-- CREATE POLICY "Allow service role delete access"
--   ON site_pages
--   FOR DELETE
--   TO service_role
--   USING (true);
