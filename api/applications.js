import { supabase } from "./_lib/supabase.js";
import { requireUser } from "./_lib/auth.js";

export default async function handler(req, res) {
  const auth = await requireUser(req);
  if (auth.error) {
    return res.status(auth.error.status).json({ error: auth.error.message });
  }

  const userId = auth.userId;

  if (req.method === "GET") {
    const { data, error } = await supabase
      .from("applications")
      .select("*")
      .eq("user_id", userId)
      .order("updated_at", { ascending: false });

    if (error) {
      return res.status(500).json({ error: error.message });
    }

    return res.status(200).json({ applications: data });
  }

  if (req.method === "POST") {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    const payload = {
      user_id: userId,
      job_id: body.job_id,
      company: body.company,
      title: body.title,
      location: body.location,
      source: body.source,
      apply_link: body.apply_link,
      stage: body.stage || "Applied",
      notes: body.notes || "",
      applied_date: body.applied_date || new Date().toISOString(),
    };

    const { data, error } = await supabase
      .from("applications")
      .upsert(payload, { onConflict: "user_id,job_id" })
      .select("*")
      .single();

    if (error) {
      return res.status(500).json({ error: error.message });
    }

    return res.status(200).json({ application: data });
  }

  if (req.method === "PATCH") {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    if (!body.id) {
      return res.status(400).json({ error: "Missing application id" });
    }

    const updates = {};
    if (body.stage) updates.stage = body.stage;
    if (body.notes !== undefined) updates.notes = body.notes;

    const { data, error } = await supabase
      .from("applications")
      .update(updates)
      .eq("id", body.id)
      .eq("user_id", userId)
      .select("*")
      .single();

    if (error) {
      return res.status(500).json({ error: error.message });
    }

    return res.status(200).json({ application: data });
  }

  return res.status(405).json({ error: "Method not allowed" });
}
