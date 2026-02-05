import { supabase } from "./_lib/supabase.js";
import { requireUser } from "./_lib/auth.js";

export default async function handler(req, res) {
  const auth = await requireUser(req);
  if (auth.error) {
    return res.status(auth.error.status).json({ error: auth.error.message });
  }

  const userId = auth.userId;

  const { data, error } = await supabase
    .from("applications")
    .select("stage, applied_date")
    .eq("user_id", userId);

  if (error) {
    return res.status(500).json({ error: error.message });
  }

  const totals = {
    total: data.length,
    applied: 0,
    interview: 0,
    offer: 0,
    rejected: 0,
    interested: 0,
  };

  data.forEach(row => {
    const stage = (row.stage || "").toLowerCase();
    if (stage === "applied") totals.applied += 1;
    else if (stage === "interview") totals.interview += 1;
    else if (stage === "offer") totals.offer += 1;
    else if (stage === "rejected") totals.rejected += 1;
    else if (stage === "interested") totals.interested += 1;
  });

  const interviewRate = totals.total
    ? Math.round((totals.interview / totals.total) * 100)
    : 0;

  return res.status(200).json({
    totals,
    interviewRate,
  });
}
