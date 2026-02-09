import { requireUser } from "./_lib/auth.js";

const GEMINI_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash"];

function safeParseBody(req) {
  if (!req.body) return {};
  if (typeof req.body === "string") {
    try {
      return JSON.parse(req.body);
    } catch {
      return {};
    }
  }
  return req.body;
}

function extractTextFromGemini(payload) {
  const parts = payload?.candidates?.[0]?.content?.parts || [];
  return parts
    .map((part) => (typeof part.text === "string" ? part.text : ""))
    .join("\n")
    .trim();
}

function parseGeminiErrorDetails(raw) {
  const text = String(raw || "").trim();
  if (!text) return "Empty Gemini error response";
  try {
    const payload = JSON.parse(text);
    return payload?.error?.message || text.slice(0, 600);
  } catch {
    return text.slice(0, 600);
  }
}

function extractJsonObject(text) {
  const cleaned = String(text || "")
    .replace(/```json/gi, "")
    .replace(/```/g, "")
    .trim();
  const first = cleaned.indexOf("{");
  const last = cleaned.lastIndexOf("}");
  if (first < 0 || last < 0 || last <= first) return null;
  try {
    return JSON.parse(cleaned.slice(first, last + 1));
  } catch {
    return null;
  }
}

async function requestGemini({ model, prompt, apiKey }) {
  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 1800,
        },
      }),
    }
  );

  const responseText = await response.text();
  if (!response.ok) {
    return {
      ok: false,
      status: response.status,
      model,
      details: parseGeminiErrorDetails(responseText),
    };
  }

  let data = null;
  try {
    data = JSON.parse(responseText);
  } catch {
    return {
      ok: false,
      status: 502,
      model,
      details: "Gemini returned invalid JSON payload",
    };
  }

  const raw = extractTextFromGemini(data);
  const parsed = extractJsonObject(raw);
  if (!parsed) {
    return {
      ok: false,
      status: 502,
      model,
      details: "Could not parse structured JSON from Gemini output",
    };
  }

  return {
    ok: true,
    parsed,
  };
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const auth = await requireUser(req);
  if (auth.error) {
    return res.status(auth.error.status).json({ error: auth.error.message });
  }

  if (!process.env.GEMINI_API_KEY) {
    return res.status(500).json({ error: "Missing GEMINI_API_KEY" });
  }

  const body = safeParseBody(req);
  const jobDescription = String(body.jobDescription || "").trim();
  const resumeText = String(body.resumeText || "").trim();
  const profile = body.profile || {};

  if (!jobDescription) {
    return res.status(400).json({ error: "jobDescription is required" });
  }

  const candidateFacts = {
    name: String(profile.name || "").trim(),
    education: String(profile.education || "").trim(),
    currentCompany: String(profile.currentCompany || "").trim(),
    experienceSummary: String(profile.experienceSummary || "").trim(),
    skills: String(profile.skills || "").trim(),
    baseResume: resumeText,
  };

  const prompt = [
    "You are an ATS resume tailoring assistant.",
    "Hard constraints:",
    "1) Never invent facts, companies, education, years, or achievements.",
    "2) Use only information provided in CANDIDATE_FACTS and BASE_RESUME.",
    "3) If missing information is needed, add it under missing_information instead of fabricating.",
    "4) Keep output concise, ATS-safe, and keyword-aligned to JD.",
    "Return ONLY valid JSON matching this schema:",
    "{",
    '  "headline": "string",',
    '  "professional_summary": "string",',
    '  "tailored_experience_bullets": ["string"],',
    '  "tailored_skills": ["string"],',
    '  "ats_keywords": ["string"],',
    '  "changes_made": ["string"],',
    '  "missing_information": ["string"],',
    '  "tailored_resume_text": "string"',
    "}",
    "",
    "JOB_DESCRIPTION:",
    jobDescription,
    "",
    "CANDIDATE_FACTS:",
    JSON.stringify(candidateFacts, null, 2),
  ].join("\n");

  let lastFailure = null;
  for (const model of GEMINI_MODELS) {
    const attempt = await requestGemini({
      model,
      prompt,
      apiKey: process.env.GEMINI_API_KEY,
    });

    if (attempt.ok) {
      const parsed = attempt.parsed;
      return res.status(200).json({
        result: {
          headline: parsed.headline || "",
          professional_summary: parsed.professional_summary || "",
          tailored_experience_bullets: Array.isArray(parsed.tailored_experience_bullets) ? parsed.tailored_experience_bullets : [],
          tailored_skills: Array.isArray(parsed.tailored_skills) ? parsed.tailored_skills : [],
          ats_keywords: Array.isArray(parsed.ats_keywords) ? parsed.ats_keywords : [],
          changes_made: Array.isArray(parsed.changes_made) ? parsed.changes_made : [],
          missing_information: Array.isArray(parsed.missing_information) ? parsed.missing_information : [],
          tailored_resume_text: parsed.tailored_resume_text || "",
        },
      });
    }

    lastFailure = attempt;
  }

  return res.status(lastFailure?.status || 502).json({
    error: "Gemini request failed",
    details: `${lastFailure?.details || "Unknown Gemini failure"}${lastFailure?.model ? ` (model: ${lastFailure.model})` : ""}`,
  });
}
