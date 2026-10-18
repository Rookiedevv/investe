import "server-only";
import { createClient } from "@supabase/supabase-js";

/**
 * Server-only client that bypasses row-level security, for price import jobs.
 * Never import this into anything that runs in the browser.
 */
export function createAdminClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SECRET_KEY;
  if (!url || !key) throw new Error("Missing SUPABASE_SECRET_KEY (only needed for price imports).");
  return createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
}
