# Putting the investing app online

About 30 minutes, once. Everything here is free. Keep a note open: you'll collect 5 values.

| # | Value | Where you get it |
|---|---|---|
| A | Supabase project URL | Step 2 |
| B | Supabase publishable key | Step 2 |
| C | Google client ID | Step 3 |
| D | Google client secret | Step 3 |
| E | Your app's address (…vercel.app) | Step 4 |

---

## Step 1. GitHub (stores the code)

1. At **github.com** click **+ → New repository**. Name it `investe`, set it to **Private**, and don't add a README.
2. Send Claude the name, e.g. `Rookiedevv/investe`. Claude pushes the code into it.

## Step 2. Supabase (database and sign-in)

1. At **supabase.com** click **New project**.
   - Name: `investe`
   - Database password: click *Generate* and store it in your password manager.
   - Region: **Central EU (Frankfurt)**.
2. Wait about 2 minutes.
3. **SQL Editor → New query**: paste all of `supabase/migrations/20261018000001_init.sql` (Claude gives it to you ready to paste) and click **Run**. It should say *Success. No rows returned*.
4. New query, put in your Google address (and anyone else's), then **Run**:
   ```sql
   insert into public.allowed_emails (email, is_admin) values
     ('your.address@gmail.com', true);
   ```
   Lowercase only. You can add more people later in the app under Settings.
5. **Project Settings → Data API**: copy the **Project URL**. That's **A**.
6. **Project Settings → API Keys**: copy the **Publishable key** (`sb_publishable_…`). That's **B**.

## Step 3. Google sign-in

1. At **console.cloud.google.com** create a new project called `investe`.
2. **APIs & Services → OAuth consent screen** (may be called *Google Auth Platform*):
   - App name: `Inwestycje`; support email: yours.
   - Audience: **External**.
   - **Test users**: add the Gmail addresses from step 2.4. Leave the app in *Testing*, so Google doesn't need to review it.
3. **Credentials → Create credentials → OAuth client ID**:
   - Type: **Web application**
   - Authorized redirect URI: `https://<A without https://>/auth/v1/callback`
4. Copy the **Client ID** (**C**) and **Client secret** (**D**).
5. Supabase → **Authentication → Sign In / Providers → Google**: turn it on, paste **C** and **D**, **Save**.

## Step 4. Vercel (hosts the app)

1. At **vercel.com** sign in with **Continue with GitHub**.
2. **Add New → Project** → import `investe`.
3. Under **Environment Variables** add:
   | Name | Value |
   |---|---|
   | `NEXT_PUBLIC_SUPABASE_URL` | **A** |
   | `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | **B** |
4. **Deploy**, wait about 2 minutes, and copy the address it shows. That's **E**.

## Step 5. Connect the address back to Supabase

Supabase → **Authentication → URL Configuration**:
- **Site URL:** **E**
- **Redirect URLs → Add URL:** `E/auth/callback`

Save.

## Step 6. Try it

1. Open **E** on your phone and sign in with Google.
2. Chrome menu (⋮) → **Add to Home screen**, or on iPhone: Share → **Add to Home Screen**.

### If something goes wrong
- **"This account isn't on the list"**: the address in step 2.4 is missing or misspelled (Supabase → Table Editor → `allowed_emails`).
- **Google says "Access blocked"**: the address isn't a *Test user* in step 3.2.
- **Back on the login page after Google**: the redirect URL in step 5 doesn't match **E** exactly.
- Anything else: send Claude a screenshot.
