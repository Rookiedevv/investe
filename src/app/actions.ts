"use server";

import { revalidatePath } from "next/cache";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { z } from "zod";
import { requireUser } from "@/lib/session";
import { createClient } from "@/lib/supabase/server";

// Every write is validated here and protected again by row-level security.

// ───────────────────────── Auth ─────────────────────────

export async function signInWithGoogle() {
  const supabase = await createClient();
  const h = await headers();
  const origin = h.get("origin") ?? `${h.get("x-forwarded-proto") ?? "https"}://${h.get("host")}`;
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: { redirectTo: `${origin}/auth/callback`, queryParams: { prompt: "select_account" } },
  });
  if (error || !data.url) redirect("/login?error=1");
  redirect(data.url);
}

export async function signOut() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/login");
}

// ───────────────────────── Helpers ─────────────────────────

const blankToUndef = (v: unknown) => (v === "" || v === null ? undefined : v);
const opt = <T extends z.ZodType>(s: T) => z.preprocess(blankToUndef, s.optional());

function fail(path: string): never {
  redirect(`${path}?error=1`);
}

// ───────────────────────── Events ─────────────────────────

const eventSchema = z.object({
  date: z.iso.date(),
  time: opt(z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/)),
  session_timing: z.enum(["before", "during", "after", "unknown"]),
  ticker: z.string().trim().toUpperCase().regex(/^[A-Z0-9_]{2,16}$/),
  category: z.string().trim().min(1).max(40),
  event_type: z.string().trim().min(1).max(60),
  status: z.enum(["published", "planned_only", "scheduled"]),
  severity: opt(z.coerce.number().int().min(1).max(5)),
  direction: opt(z.enum(["positive", "negative", "mixed"])),
  description: z.string().trim().max(2000),
  source_url: opt(z.url()),
});

export async function addEvent(form: FormData) {
  const { supabase } = await requireUser();
  const parsed = eventSchema.safeParse(Object.fromEntries(form));
  if (!parsed.success) fail("/events");
  const { error } = await supabase.from("events").insert({
    ...parsed.data,
    time: parsed.data.time ?? null,
    severity: parsed.data.severity ?? null,
    direction: parsed.data.direction ?? null,
    source_url: parsed.data.source_url ?? null,
  });
  if (error) fail("/events");
  revalidatePath("/events");
  revalidatePath("/");
  redirect("/events");
}

export async function deleteEvent(form: FormData) {
  const { supabase } = await requireUser();
  const id = z.coerce.number().int().positive().safeParse(form.get("id"));
  if (!id.success) fail("/events");
  await supabase.from("events").delete().eq("id", id.data);
  revalidatePath("/events");
  revalidatePath("/");
}

// ───────────────────────── Paper trades ─────────────────────────

const price = z.coerce.number().positive().max(1_000_000);

const openSchema = z.object({
  ticker: z.string().trim().toUpperCase().regex(/^[A-Z0-9_]{2,12}$/),
  opened_on: z.iso.date(),
  shares: z.coerce.number().int().positive().max(1_000_000),
  entry_price: price,
  reason: z.string().trim().max(1000),
});

export async function openTrade(form: FormData) {
  const { supabase } = await requireUser();
  const parsed = openSchema.safeParse(Object.fromEntries(form));
  if (!parsed.success) fail("/journal");
  const { error } = await supabase.from("paper_trades").insert(parsed.data);
  if (error) fail("/journal");
  revalidatePath("/journal");
  revalidatePath("/");
  redirect("/journal");
}

const closeSchema = z.object({
  id: z.coerce.number().int().positive(),
  closed_on: z.iso.date(),
  exit_price: price,
});

export async function closeTrade(form: FormData) {
  const { supabase } = await requireUser();
  const parsed = closeSchema.safeParse(Object.fromEntries(form));
  if (!parsed.success) fail("/journal");
  const { id, ...rest } = parsed.data;
  const { error } = await supabase.from("paper_trades").update(rest).eq("id", id).is("closed_on", null);
  if (error) fail("/journal");
  revalidatePath("/journal");
  revalidatePath("/");
  redirect("/journal");
}

export async function deleteTrade(form: FormData) {
  const { supabase } = await requireUser();
  const id = z.coerce.number().int().positive().safeParse(form.get("id"));
  if (!id.success) fail("/journal");
  await supabase.from("paper_trades").delete().eq("id", id.data);
  revalidatePath("/journal");
  revalidatePath("/");
}

// ───────────────────────── Settings ─────────────────────────

export async function setLanguage(form: FormData) {
  const { supabase, profile } = await requireUser();
  const lang = z.enum(["pl", "en"]).safeParse(form.get("language"));
  if (!lang.success) fail("/settings");
  await supabase.from("profiles").update({ language: lang.data }).eq("id", profile.id);
  revalidatePath("/", "layout");
}

export async function addAllowedEmail(form: FormData) {
  const { supabase, profile } = await requireUser();
  if (!profile.is_admin) fail("/settings");
  const parsed = z.object({ email: z.email().transform((e) => e.toLowerCase()), is_admin: z.literal("on").optional() })
    .safeParse(Object.fromEntries(form));
  if (!parsed.success) fail("/settings");
  const { error } = await supabase
    .from("allowed_emails")
    .upsert({ email: parsed.data.email, is_admin: parsed.data.is_admin === "on" });
  if (error) fail("/settings");
  revalidatePath("/settings");
}

export async function removeAllowedEmail(form: FormData) {
  const { supabase, profile } = await requireUser();
  const email = z.email().safeParse(form.get("email"));
  // Admins can't lock themselves out by removing their own address.
  if (!profile.is_admin || !email.success || email.data === profile.email) fail("/settings");
  await supabase.from("allowed_emails").delete().eq("email", email.data);
  revalidatePath("/settings");
}
