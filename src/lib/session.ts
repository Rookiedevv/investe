import "server-only";
import { redirect } from "next/navigation";
import { cache } from "react";
import { getDict, type Lang } from "./i18n";
import { createClient } from "./supabase/server";

export type Profile = {
  id: string;
  email: string;
  display_name: string | null;
  is_admin: boolean;
  language: Lang;
};

/** The signed-in user's Supabase client, profile and text. Redirects when signed out. */
export const requireUser = cache(async () => {
  const supabase = await createClient();
  const { data: claims } = await supabase.auth.getClaims();
  const userId = claims?.claims?.sub;
  if (!userId) redirect("/login");

  const { data: profile } = await supabase.from("profiles").select("*").eq("id", userId).single<Profile>();
  if (!profile) redirect("/login");
  return { supabase, profile, t: getDict(profile.language) };
});
