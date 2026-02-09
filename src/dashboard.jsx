import React from "react";
import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton, useAuth } from "@clerk/clerk-react";

const STALE_DAYS = 45;
const VERY_FRESH_DAYS = 3;
const FRESH_DAYS = 14;
const STOPWORDS = new Set(["the","and","for","with","from","into","over","under","a","an","to","of","in","on","by","at","as","or","is","are","be","this","that","these","those","it","we","you","your","our","their"]);

const SKILL_TAXONOMY = {
  product: ["product management", "product manager", "prd", "roadmap", "go to market", "gtm", "user research", "a b testing", "ab testing", "funnel", "retention", "stakeholder management"],
  analytics: ["sql", "tableau", "power bi", "mixpanel", "amplitude", "analytics", "kpi", "cohort", "dashboard", "excel"],
  engineering: ["python", "javascript", "typescript", "java", "react", "node", "api", "graphql", "docker", "kubernetes", "aws", "gcp"],
  process: ["agile", "scrum", "jira", "confluence", "kanban", "sprint planning"],
};

const SYNONYM_MAP = {
  "pm": "product manager",
  "prod manager": "product manager",
  "apm": "associate product manager",
  "sde": "software engineer",
  "devops engineer": "devops",
  "restful": "rest",
  "k8s": "kubernetes",
  "js": "javascript",
  "ts": "typescript",
  "ai ml": "machine learning",
  "ml": "machine learning",
  "gen ai": "generative ai",
  "a/b": "ab testing",
  "g tm": "gtm",
};

const SENIORITY_BANDS = [
  { rank: 0, label: "intern", patterns: ["intern", "trainee"] },
  { rank: 1, label: "junior", patterns: ["junior", "associate", "entry level"] },
  { rank: 2, label: "mid", patterns: ["ii", "2", "specialist"] },
  { rank: 3, label: "senior", patterns: ["senior", "sr", "lead"] },
  { rank: 4, label: "staff", patterns: ["staff", "principal", "architect", "manager"] },
  { rank: 5, label: "director", patterns: ["director", "head", "vp", "chief"] },
];

function toTimestamp(value) {
  if (!value) return 0;
  const ts = new Date(value).getTime();
  return Number.isFinite(ts) ? ts : 0;
}

function normalizeLink(link) {
  if (!link) return "";
  return String(link).trim().replace(/\/+$/, "").toLowerCase();
}

function freshnessMeta(job) {
  const ts = toTimestamp(job.postedDate || job.fetchedAt);
  if (!ts) return { ageDays: 999, freshness: "Unknown", stale: true, freshnessScore: 0 };

  const ageDays = Math.max(0, Math.floor((Date.now() - ts) / (1000 * 60 * 60 * 24)));
  if (ageDays <= VERY_FRESH_DAYS) return { ageDays, freshness: "New", stale: false, freshnessScore: 100 };
  if (ageDays <= FRESH_DAYS) return { ageDays, freshness: "Fresh", stale: false, freshnessScore: 80 };
  if (ageDays <= STALE_DAYS) return { ageDays, freshness: "Recent", stale: false, freshnessScore: 55 };
  return { ageDays, freshness: "Stale", stale: true, freshnessScore: 20 };
}

function dedupeAndEnhanceJobs(rawJobs) {
  const unique = new Map();

  rawJobs.forEach((job) => {
    const linkKey = normalizeLink(job.applyLink);
    const titleKey = String(job.title || "").trim().toLowerCase();
    const companyKey = String(job.company || "").trim().toLowerCase();
    const locationKey = String(job.location || "").trim().toLowerCase();
    const dedupeKey = linkKey || `${companyKey}::${titleKey}::${locationKey}`;
    if (!dedupeKey || dedupeKey === "::::") return;

    const existing = unique.get(dedupeKey);
    if (!existing) {
      unique.set(dedupeKey, job);
      return;
    }

    const existingTs = toTimestamp(existing.postedDate || existing.fetchedAt);
    const nextTs = toTimestamp(job.postedDate || job.fetchedAt);
    const existingScore = Number(existing.score || 0);
    const nextScore = Number(job.score || 0);

    if (nextTs > existingTs || (nextTs === existingTs && nextScore > existingScore)) {
      unique.set(dedupeKey, job);
    }
  });

  return Array.from(unique.values()).map((job) => ({
    ...job,
    ...freshnessMeta(job),
  }));
}

function normalizeTerms(text) {
  if (!text) return [];
  const cleaned = text
    .toLowerCase()
    .replace(/[_-]+/g, " ")
    .replace(/[^a-z0-9+/#\s.-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (!cleaned) return [];
  return cleaned.split(" ").filter(Boolean);
}

function normalizePhrase(text) {
  if (!text) return "";
  const compact = normalizeTerms(text).join(" ");
  return SYNONYM_MAP[compact] || compact;
}

function buildKeywordSet(terms) {
  return new Set(terms.filter(Boolean));
}

function buildNgrams(tokens, maxN = 3) {
  const grams = [];
  for (let n = 2; n <= maxN; n += 1) {
    for (let i = 0; i <= tokens.length - n; i += 1) {
      grams.push(tokens.slice(i, i + n).join(" "));
    }
  }
  return grams;
}

function overlapScore(targetTerms, candidateSet) {
  if (!targetTerms.length) return 0;
  let hits = 0;
  for (const t of targetTerms) {
    if (candidateSet.has(t)) hits += 1;
  }
  return hits / targetTerms.length;
}

function detectSeniorityRank(text) {
  const haystack = ` ${normalizePhrase(text)} `;
  let best = 2;
  SENIORITY_BANDS.forEach((band) => {
    if (band.patterns.some((pattern) => haystack.includes(` ${pattern} `))) {
      best = Math.max(best, band.rank);
    }
  });
  return best;
}

function parseYears(text) {
  if (!text) return null;
  const pattern = /(\d{1,2})\s*(\+)?\s*(years?|yrs?)/i;
  const match = String(text).match(pattern);
  if (!match) return null;
  const value = Number(match[1]);
  if (!Number.isFinite(value)) return null;
  return value;
}

function extractResumeSignals(resumeText) {
  const tokens = normalizeTerms(resumeText).filter((t) => !STOPWORDS.has(t) && t.length > 1);
  const canonicalTokens = tokens.map((token) => normalizePhrase(token));
  const ngrams = buildNgrams(canonicalTokens, 3).map((gram) => normalizePhrase(gram));
  const baseSet = buildKeywordSet([...canonicalTokens, ...ngrams]);

  Object.values(SKILL_TAXONOMY).flat().forEach((term) => {
    const normalized = normalizePhrase(term);
    if (baseSet.has(normalized)) return;
    if (` ${normalizePhrase(resumeText)} `.includes(` ${normalized} `)) {
      baseSet.add(normalized);
    }
  });

  return {
    set: baseSet,
    years: parseYears(resumeText),
    seniorityRank: detectSeniorityRank(resumeText),
  };
}

function extractJobSignals(job) {
  const skills = (job.requirements?.skills || []).map((s) => normalizePhrase(s));
  const keywords = (job.requirements?.keywords || []).map((k) => normalizePhrase(k));
  const titleTokens = normalizeTerms(job.title || "").map((t) => normalizePhrase(t));
  const roleTokens = normalizeTerms(job.role || "").map((t) => normalizePhrase(t));
  const ngrams = buildNgrams([...titleTokens, ...roleTokens], 3).map((gram) => normalizePhrase(gram));
  const all = buildKeywordSet([...skills, ...keywords, ...titleTokens, ...roleTokens, ...ngrams]);

  Object.values(SKILL_TAXONOMY).flat().forEach((term) => {
    const normalized = normalizePhrase(term);
    if (` ${normalizePhrase(`${job.title || ""} ${keywords.join(" ")} ${skills.join(" ")}`)} `.includes(` ${normalized} `)) {
      all.add(normalized);
    }
  });

  const minYears = Number(job.requirements?.experience_years || 0) || parseYears((job.requirements?.keywords || []).join(" ")) || null;
  const seniorityRank = detectSeniorityRank(`${job.title || ""} ${job.role || ""}`);

  return {
    set: all,
    skills,
    keywords,
    titleTokens,
    roleTokens,
    minYears,
    seniorityRank,
  };
}

function locationGate(jobLocation, resumeText) {
  const loc = String(jobLocation || "").toLowerCase();
  const resume = String(resumeText || "").toLowerCase();

  if (!loc) return 0.95;
  if (loc.includes("remote")) return 1;
  if (loc.includes("india")) return 1;

  const hasIndiaSignal = /india|bangalore|bengaluru|mumbai|pune|hyderabad|delhi|gurgaon|gurugram|chennai|noida/.test(resume);
  const likelyForeign = /united states|usa|canada|london|uk|europe|singapore|tokyo|germany|france|australia/.test(loc);

  if (likelyForeign && hasIndiaSignal) return 0.75;
  return 0.95;
}

function computeMatch(job, resumeText) {
  const resume = extractResumeSignals(resumeText);
  const jobSignals = extractJobSignals(job);
  const resumeSet = resume.set;

  const skillScore = overlapScore(jobSignals.skills, resumeSet);
  const keywordScore = overlapScore(jobSignals.keywords, resumeSet);
  const titleScore = overlapScore(jobSignals.titleTokens, resumeSet);
  const roleScore = overlapScore(jobSignals.roleTokens, resumeSet);
  const taxonomyTerms = Object.values(SKILL_TAXONOMY).flat().map((t) => normalizePhrase(t));
  const taxonomyScore = overlapScore(taxonomyTerms.filter((term) => jobSignals.set.has(term)), resumeSet);

  const seniorityGap = Math.abs((resume.seniorityRank ?? 2) - (jobSignals.seniorityRank ?? 2));
  const seniorityGate = seniorityGap <= 1 ? 1 : 0.85;
  const yearsGate = resume.years && jobSignals.minYears ? (resume.years >= jobSignals.minYears ? 1 : 0.8) : 0.95;
  const geoGate = locationGate(job.location, resumeText);

  const weightedBase = (skillScore * 0.32) + (keywordScore * 0.23) + (titleScore * 0.16) + (roleScore * 0.09) + (taxonomyScore * 0.2);
  const gated = weightedBase * seniorityGate * yearsGate * geoGate;
  const matchScore = Math.max(0, Math.min(100, Math.round(gated * 100)));

  const signalCoverage = Math.min(1, (jobSignals.set.size || 0) / 14);
  const structuredData = jobSignals.skills.length > 0 ? 1 : 0.5;
  const confidence = Math.max(1, Math.min(100, Math.round(((signalCoverage * 0.5) + (structuredData * 0.3) + ((1 - seniorityGap / 6) * 0.2)) * 100)));

  const explain = [];
  const addMatches = (label, terms, limit = 4) => {
    const hits = terms.filter((term) => resumeSet.has(term)).slice(0, limit);
    if (hits.length) explain.push({ label, hits });
  };

  addMatches("Skills", jobSignals.skills);
  addMatches("Keywords", jobSignals.keywords);
  addMatches("Title", jobSignals.titleTokens, 3);
  addMatches("Role", jobSignals.roleTokens, 3);
  explain.push({ label: "Seniority", hits: [seniorityGap <= 1 ? "Aligned" : "Partial Match"] });
  explain.push({ label: "Location", hits: [geoGate >= 0.95 ? "Good Fit" : "Limited Fit"] });
  explain.push({ label: "Confidence", hits: [`${confidence}%`] });

  return { matchScore, matchExplain: explain, matchConfidence: confidence };
}

function computeQuickPlatformMatch(job, resumeText) {
  const resumeTokens = normalizeTerms(resumeText)
    .map((token) => normalizePhrase(token))
    .filter((token) => token && !STOPWORDS.has(token) && token.length > 2);
  const uniqueResume = Array.from(new Set(resumeTokens)).slice(0, 120);

  const jobText = [
    job.title || "",
    job.company || "",
    job.role || "",
    job.location || "",
    (job.requirements?.skills || []).join(" "),
    (job.requirements?.keywords || []).join(" "),
  ].join(" ");

  const jobTokenSet = new Set(
    normalizeTerms(jobText)
      .map((token) => normalizePhrase(token))
      .filter(Boolean)
  );

  const hits = uniqueResume.filter((token) => jobTokenSet.has(token));
  if (hits.length === 0) return null;

  const base = Math.min(1, hits.length / Math.max(8, Math.min(uniqueResume.length, 35)));
  const matchScore = Math.max(1, Math.min(99, Math.round(base * 100)));

  return {
    ...job,
    matchScore,
    matchConfidence: Math.min(95, 50 + hits.length * 5),
    matchExplain: [{ label: "Keyword Match", hits: hits.slice(0, 6) }],
  };
}

export default function Dashboard() {
  const brandName = "ApplyPulse";
  const [jobs, setJobs] = React.useState([]);
  const [filteredJobs, setFilteredJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedRole, setSelectedRole] = React.useState("all");
  const [selectedEmploymentType, setSelectedEmploymentType] = React.useState("all");
  const [sourceQuery, setSourceQuery] = React.useState("");
  const [companyQuery, setCompanyQuery] = React.useState("");
  const [locationQuery, setLocationQuery] = React.useState("");

  const [activeSection, setActiveSection] = React.useState("all");
  const [resumeMatchEnabled, setResumeMatchEnabled] = React.useState(false);
  const [matcherResumeText, setMatcherResumeText] = React.useState("");
  const [matcherResults, setMatcherResults] = React.useState([]);
  const [matcherRunning, setMatcherRunning] = React.useState(false);

  const [savedJobs, setSavedJobs] = React.useState([]);
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const [applications, setApplications] = React.useState([]);
  const [expandedJob, setExpandedJob] = React.useState(null);
  const [currentPage, setCurrentPage] = React.useState(1);
  const [itemsPerPage] = React.useState(20);
  const [sortBy, setSortBy] = React.useState("score");
  const [resumeText, setResumeText] = React.useState("");
  const [resumeKeywords, setResumeKeywords] = React.useState([]);
  const [showFilters, setShowFilters] = React.useState(false);
  const [hideStale, setHideStale] = React.useState(true);
  const [theme, setTheme] = React.useState(() => localStorage.getItem("app_theme") || "dark");
  const [feedbackOpen, setFeedbackOpen] = React.useState(false);
  const [feedbackText, setFeedbackText] = React.useState("");
  const [feedbackEmail, setFeedbackEmail] = React.useState("");
  const [feedbackSent, setFeedbackSent] = React.useState(false);
  const [feedbackSubmitting, setFeedbackSubmitting] = React.useState(false);
  const { getToken, isSignedIn, isLoaded } = useAuth();
  const isLight = theme === "light";

  React.useEffect(() => {
    localStorage.setItem("app_theme", theme);
  }, [theme]);

  React.useEffect(() => {
    if (!feedbackOpen) return;
    const onEsc = (event) => {
      if (event.key === "Escape") setFeedbackOpen(false);
    };
    window.addEventListener("keydown", onEsc);
    return () => window.removeEventListener("keydown", onEsc);
  }, [feedbackOpen]);

  const submitFeedback = React.useCallback(async () => {
    if (!feedbackText.trim()) return;
    setFeedbackSubmitting(true);
    try {
      // lightweight client-side queue so feedback survives refresh
      const queued = JSON.parse(localStorage.getItem("feedback_queue") || "[]");
      queued.unshift({
        text: feedbackText.trim(),
        email: feedbackEmail.trim(),
        at: new Date().toISOString(),
      });
      localStorage.setItem("feedback_queue", JSON.stringify(queued.slice(0, 100)));
      setFeedbackSent(true);
      setFeedbackText("");
      setFeedbackEmail("");
    } finally {
      setFeedbackSubmitting(false);
    }
  }, [feedbackText, feedbackEmail]);

  const formatLabel = React.useCallback((value) => {
    if (!value) return "";
    const text = String(value).replace(/[_-]+/g, " ").trim();
    if (!text) return "";
    return text.replace(/\b\w/g, (char) => char.toUpperCase());
  }, []);

  const authFetch = React.useCallback(
    async (url, options = {}) => {
      const token = await getToken();
      if (!token) throw new Error("Missing auth token");
      const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
      };
      const response = await fetch(url, { ...options, headers });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.error || "Request failed");
      }
      return response.json();
    },
    [getToken]
  );

  /* ---------------- FETCH JOBS ---------------- */
  React.useEffect(() => {
    fetch("https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json")
      .then(res => res.json())
      .then(data => {
        const cleaned = dedupeAndEnhanceJobs(Array.isArray(data) ? data : []);
        setJobs(cleaned);
        setFilteredJobs(cleaned);
      })
      .finally(() => setLoading(false));
  }, []);

  React.useEffect(() => {
    if (!isSignedIn) {
      setApplications([]);
      return;
    }

    const load = async () => {
      try {
        const apps = await authFetch("/api/applications");
        setApplications(apps.applications || []);
      } catch (error) {
        console.error("Failed to load applications", error);
      }
    };

    load();
  }, [isSignedIn, authFetch]);

  React.useEffect(() => {
    if (!isSignedIn) return;
    const interested = applications
      .filter(app => (app.stage || "").toLowerCase() === "interested")
      .map(app => app.job_id)
      .filter(Boolean);
    setSavedJobs(interested);
  }, [applications, isSignedIn]);

  /* ---------------- FILTER VALUES ---------------- */
  const sources = [...new Set(jobs.map(j => j?.source).filter(Boolean))].sort();
  const roles = [...new Set(jobs.map(j => j?.role).filter(Boolean))];
  const locations = [...new Set(jobs.map(j => j?.location).filter(Boolean))].sort();
  const employmentTypes = [...new Set(jobs.map(j => j?.employment_type).filter(Boolean))].sort();
  const companies = [...new Set(jobs.map(j => j?.company).filter(Boolean))].sort();
  const topCompanies = React.useMemo(() => {
    const counts = {};
    jobs.forEach(j => {
      if (!j.company) return;
      counts[j.company] = (counts[j.company] || 0) + 1;
    });
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([name]) => name);
  }, [jobs]);

  /* ---------------- FILTER LOGIC ---------------- */
  React.useEffect(() => {
    let data = [...jobs];

    // Apply ALL filters together (not independently)
    if (searchQuery) {
      data = data.filter(j =>
        j.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        j.company?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (sourceQuery) {
      data = data.filter(j => j.source?.toLowerCase().includes(sourceQuery.toLowerCase()));
    }

    if (companyQuery) {
      data = data.filter(j => j.company?.toLowerCase().includes(companyQuery.toLowerCase()));
    }

    if (selectedRole !== "all") {
      data = data.filter(j => j.role === selectedRole);
    }

    if (locationQuery) {
      data = data.filter(j => j.location?.toLowerCase().includes(locationQuery.toLowerCase()));
    }

    if (selectedEmploymentType !== "all") {
      const target = selectedEmploymentType.toLowerCase();
      data = data.filter(j => (j.employment_type || "").toLowerCase().includes(target));
    }

    if (hideStale) {
      data = data.filter(j => !j.stale);
    }

    setFilteredJobs(data);
    setCurrentPage(1); // Reset to page 1 when filters change
  }, [jobs, searchQuery, sourceQuery, companyQuery, selectedRole, locationQuery, selectedEmploymentType, hideStale]);

  /* ---------------- SECTION FILTER ---------------- */
  const applicationsByJobId = React.useMemo(() => {
    const map = new Map();
    applications.forEach(app => {
      if (app.job_id) map.set(app.job_id, app);
    });
    return map;
  }, [applications]);

  const displayJobs = React.useMemo(() => {
    if (activeSection === "saved") return filteredJobs.filter(j => savedJobs.includes(j.id));
    if (activeSection === "applied") return filteredJobs.filter(j => applicationsByJobId.has(j.id));
    if (activeSection === "top") return filteredJobs.filter(j => j.matchScore >= 75);
    return filteredJobs;
  }, [filteredJobs, activeSection, savedJobs, applicationsByJobId]);

  /* ---------------- SORT JOBS ---------------- */
  const sortedJobs = React.useMemo(() => {
    const data = [...displayJobs];
    const locationPriority = (loc) => {
      const l = (loc || "").toLowerCase();
      if (l.includes("remote")) return 2;
      if (l.includes("hybrid")) return 1;
      return 0;
    };
    
    switch(sortBy) {
      case "matchScore":
        return data.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
      case "date":
        return data.sort((a, b) => new Date(b.postedDate || b.fetchedAt) - new Date(a.postedDate || a.fetchedAt));
      case "remote":
        return data.sort((a, b) => {
          const pa = locationPriority(a.location);
          const pb = locationPriority(b.location);
          if (pb !== pa) return pb - pa;
          return (b.score || 0) - (a.score || 0);
        });
      case "score":
      default:
        return data.sort((a, b) => (b.score || 0) - (a.score || 0));
    }
  }, [displayJobs, sortBy]);

  /* ---------------- PAGINATE JOBS ---------------- */
  const paginatedJobs = React.useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return sortedJobs.slice(startIndex, endIndex);
  }, [sortedJobs, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(sortedJobs.length / itemsPerPage);

  /* ---------------- ACTIONS ---------------- */
  const toggleSaveJob = async (id) => {
    if (!isSignedIn) {
      alert("Please sign in to save jobs.");
      return;
    }

    setSavedJobs(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);

    const job = jobs.find(j => j.id === id);
    if (!job) return;

    const existing = applicationsByJobId.get(id);
    if (existing) return;

    try {
      const response = await authFetch("/api/applications", {
        method: "POST",
        body: JSON.stringify({
          job_id: id,
          company: job.company,
          title: job.title,
          location: job.location,
          source: job.source,
          apply_link: job.applyLink,
          stage: "Interested",
        }),
      });

      setApplications(prev => [response.application, ...prev]);
    } catch (error) {
      console.error("Failed to save job as interested", error);
    }
  };

  const markJobAsApplied = async (id, applyLink) => {
    if (!isSignedIn) {
      alert("Please sign in to track applications.");
      return;
    }

    const job = jobs.find(j => j.id === id);
    if (!job) return;

    try {
      const response = await authFetch("/api/applications", {
        method: "POST",
        body: JSON.stringify({
          job_id: id,
          company: job.company,
          title: job.title,
          location: job.location,
          source: job.source,
          apply_link: job.applyLink,
          stage: "Applied",
        }),
      });

      setApplications(prev => {
        const next = [...prev];
        const index = next.findIndex(app => app.job_id === id);
        if (index >= 0) {
          next[index] = response.application;
        } else {
          next.unshift(response.application);
        }
        return next;
      });
    } catch (error) {
      console.error("Failed to create application", error);
    }

    if (applyLink) {
      window.open(applyLink, "_blank", "noopener,noreferrer");
    }
  };

  const updateApplication = async (id, updates) => {
    if (!isSignedIn) return;
    try {
      const response = await authFetch("/api/applications", {
        method: "PATCH",
        body: JSON.stringify({ id, ...updates }),
      });
      setApplications(prev =>
        prev.map(app => (app.id === id ? response.application : app))
      );
    } catch (error) {
      console.error("Failed to update application", error);
    }
  };

  const handleResumeUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    extractTextFromResumeFile(file)
      .then((text) => {
        setResumeText(text);
        const words = text.match(/\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b/g) || [];
        const techTerms = text.match(/\b(python|javascript|react|java|aws|docker|kubernetes|sql|mongodb|node|typescript|vue|angular|django|flask|spring|express|postgres|redis|git|agile|scrum|api|rest|graphql|ci\/cd|devops|machine learning|ml|ai|data science|analytics|tableau|power bi|excel|powerpoint)\b/gi) || [];
        setResumeKeywords([...new Set([...words, ...techTerms])]);
      })
      .catch((error) => {
        console.error("Resume parse failed", error);
        alert(error.message || "Unable to parse resume file.");
      });
  };

  const handleMatcherResumeUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    extractTextFromResumeFile(file)
      .then((text) => setMatcherResumeText(text))
      .catch((error) => {
        console.error("Matcher resume parse failed", error);
        alert(error.message || "Unable to parse resume file.");
      });
  };

  const extractTextFromResumeFile = async (file) => {
    const fileType = String(file.type || "").toLowerCase();
    const fileName = String(file.name || "").toLowerCase();
    const isPdf = fileType === "application/pdf" || fileName.endsWith(".pdf");
    const isTxt = fileType === "text/plain" || fileName.endsWith(".txt");

    if (isTxt) {
      return await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(String(e.target?.result || ""));
        reader.onerror = () => reject(new Error("Could not read TXT file."));
        reader.readAsText(file);
      });
    }

    if (!isPdf) {
      throw new Error("Please upload PDF or TXT resume.");
    }

    const pdfjsLib = window?.pdfjsLib;
    if (!pdfjsLib) {
      throw new Error("PDF parser unavailable. Refresh once and try again.");
    }

    const bytes = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: bytes }).promise;
    const maxPages = Math.min(pdf.numPages, 40);
    let fullText = "";

    for (let i = 1; i <= maxPages; i += 1) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items.map((item) => item.str).join(" ");
      fullText += `${pageText}\n`;
      // Yield so browser stays responsive on large PDFs.
      if (i % 3 === 0) await new Promise((resolve) => setTimeout(resolve, 0));
    }

    return fullText.trim();
  };

  const runResumeMatcher = () => {
    const text = matcherResumeText.trim();
    if (!text) return;
    setMatcherRunning(true);
    setMatcherResults([]);

    const batchSize = 150;
    let index = 0;
    const nextResults = [];

    const processBatch = () => {
      const end = Math.min(index + batchSize, jobs.length);
      for (let i = index; i < end; i += 1) {
        const matched = computeQuickPlatformMatch(jobs[i], text);
        if (matched && matched.matchScore >= 12) nextResults.push(matched);
      }
      index = end;

      if (index < jobs.length) {
        setTimeout(processBatch, 0);
        return;
      }

      nextResults.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
      setMatcherResults(nextResults.slice(0, 300));
      setResumeMatchEnabled(true);
      setMatcherRunning(false);
    };

    processBatch();
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-[#0b0b0d] text-gray-100 flex items-center justify-center">
        <div className="text-gray-400">Loading...</div>
      </div>
    );
  }

  if (!isSignedIn) {
    return (
      <div className={`min-h-screen p-5 md:p-8 ${isLight ? "bg-[#eef3fb] text-[#111827]" : "bg-[#090a0d] text-gray-100"}`}>
        <div className={`mx-auto max-w-7xl min-h-[calc(100vh-3rem)] grid grid-cols-1 lg:grid-cols-2 rounded-3xl overflow-hidden border ${isLight ? "border-[#d5e0f0] bg-white" : "border-[#1e2230] bg-[#0f1320]"}`}>
          <section className={`p-8 md:p-12 flex flex-col justify-between ${isLight ? "bg-white" : "bg-[#111522]"}`}>
            <div>
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-3">
                  <div className="h-11 w-11 rounded-xl bg-pink-500/20 border border-pink-500/40 text-pink-400 flex items-center justify-center font-semibold">AP</div>
                  <div className="text-2xl font-semibold">{brandName}</div>
                </div>
                <button
                  onClick={() => setTheme((prev) => (prev === "dark" ? "light" : "dark"))}
                  className={`px-3 py-1.5 rounded-lg text-sm border ${isLight ? "bg-[#f8fbff] border-[#d8e2ef] text-[#1f2937]" : "bg-[#181d2b] border-[#2b3142] text-gray-200"}`}
                >
                  {isLight ? "Dark Mode" : "Light Mode"}
                </button>
              </div>
              <h1 className="text-4xl md:text-5xl font-semibold leading-tight">
                Stop tab-hopping.
                <br />
                Start getting interviews.
              </h1>
              <p className={`text-base mt-4 max-w-xl ${isLight ? "text-[#475569]" : "text-gray-400"}`}>
                Discover roles from verified hiring boards, track your pipeline, and apply with direct links from one workspace.
              </p>
              <div className="mt-8 grid grid-cols-2 gap-3 max-w-md">
                <StatTile label="Verified Sources" value="100+" isLight={isLight} />
                <StatTile label="Live Jobs" value="8.8k+" isLight={isLight} />
                <StatTile label="Direct Apply" value="Yes" isLight={isLight} />
                <StatTile label="Resume Match" value="Built-in" isLight={isLight} />
              </div>
            </div>
            <div className="mt-10 flex items-center gap-3">
              <SignInButton mode="modal">
                <button className="px-6 py-3 rounded-xl bg-pink-500 text-[#111827] font-semibold hover:bg-pink-400 transition-colors">Sign In</button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className={`px-6 py-3 rounded-xl border font-semibold ${isLight ? "border-[#cbd5e1] text-[#1f2937] hover:bg-[#f8fafc]" : "border-[#30384d] text-gray-200 hover:bg-[#1b2233]"} transition-colors`}>Create Free Account</button>
              </SignUpButton>
            </div>
          </section>
          <section className={`p-8 md:p-12 relative ${isLight ? "bg-gradient-to-br from-[#f4f8ff] to-[#eef2ff]" : "bg-gradient-to-br from-[#11162a] to-[#0f1120]"}`}>
            <div className="absolute inset-0 pointer-events-none opacity-40" style={{ background: "radial-gradient(circle at 20% 15%, #ec489955 0, transparent 45%), radial-gradient(circle at 85% 85%, #3b82f655 0, transparent 38%)" }} />
            <div className={`relative rounded-2xl border p-6 ${isLight ? "bg-white/80 border-[#dce6f6]" : "bg-[#0c1222]/80 border-[#26304a]"}`}>
              <p className={`text-sm uppercase tracking-wider mb-2 ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>Why candidates use {brandName}</p>
              <h2 className="text-3xl font-semibold leading-tight">Find and manage your entire job search in one place.</h2>
              <ul className={`mt-6 space-y-3 text-sm ${isLight ? "text-[#334155]" : "text-gray-300"}`}>
                <li>Direct links to real applications, no dead-end listings.</li>
                <li>Pipeline board to track Interested, Applied, Interview, Offer.</li>
                <li>Fast filters for source, role, location, and company.</li>
                <li>Resume matcher with confidence and skill-gap signals.</li>
              </ul>
              <div className={`mt-7 rounded-xl border p-4 ${isLight ? "bg-[#f8fbff] border-[#dbe7f8]" : "bg-[#11182c] border-[#2b3653]"}`}>
                <p className={`text-xs ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>Today’s outcome</p>
                <p className="text-2xl font-semibold mt-1">12 relevant roles found in under 60 seconds</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen flex ${isLight ? "bg-[#f3f6fb] text-[#0f172a]" : "bg-[#0b0b0d] text-gray-100"}`}>
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      {/* SIDEBAR */}
      <aside className={`${sidebarOpen ? "w-72" : "w-14"} transition-all border-r ${isLight ? "bg-white border-[#dbe4f0]" : "bg-[#121216] border-[#1f1f24]"}`}>
        <div className="p-4 flex justify-between items-center">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-pink-500/20 border border-pink-500/30 text-pink-300 flex items-center justify-center text-sm font-semibold">
                AP
              </div>
              <h1 className="text-xl font-semibold text-pink-300">{brandName}</h1>
            </div>
          )}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className={isLight ? "text-pink-600" : "text-pink-400"}>
            {sidebarOpen ? "✕" : "☰"}
          </button>
        </div>

        {sidebarOpen && (
          <div className="px-4 space-y-6">
            {/* NAV */}
            <nav className="space-y-2">
              <Nav icon="▦" label="Overview" active={activeSection === "all"} onClick={() => setActiveSection("all")} />
              <Nav icon="↻" label="My Pipeline" active={activeSection === "pipeline"} onClick={() => setActiveSection("pipeline")} />
              <Nav icon="🔖" label="Saved" active={activeSection === "saved"} onClick={() => setActiveSection("saved")} />
              <Nav icon="📄" label="My Applications" active={activeSection === "applied"} onClick={() => setActiveSection("applied")} />
              <Nav icon="🧾" label="Resume Matcher" active={activeSection === "resume_matcher"} onClick={() => setActiveSection("resume_matcher")} />
              <Nav icon="✦" label="JD Tailor (AI)" active={activeSection === "jd_tailor"} onClick={() => setActiveSection("jd_tailor")} />
            </nav>

            {/* RESUME MATCHER CARD */}
            <div className={`rounded-lg p-4 border ${isLight ? "bg-[#fff1f8] border-[#f3c2d8]" : "bg-[#1b121a] border-[#2b1a24]"}`}>
              <h4 className="text-sm font-semibold text-pink-300 mb-1">Resume Matcher</h4>
              <p className={`text-xs mb-3 ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>
                Upload your resume to find best-fit roles
              </p>
              <button
                onClick={() => setActiveSection("resume_matcher")}
                className="w-full bg-pink-500 text-gray-900 py-1.5 rounded text-sm font-semibold hover:bg-pink-400 transition-colors"
              >
                See Your Fit →
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* MAIN */}
      <main className="flex-1 flex flex-col">
        {/* TOP BAR */}
        <header className={`p-5 border-b ${isLight ? "bg-white border-[#dbe4f0]" : "bg-[#0f1014] border-[#1f1f24]"}`}>
          <div className="flex items-center justify-end">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setTheme((prev) => (prev === "dark" ? "light" : "dark"))}
                className={`h-9 px-3 rounded-lg text-xs border transition-colors ${isLight ? "bg-[#f7f9fc] border-[#d6e0ee] text-[#1f2937]" : "bg-[#1b1b20] border-[#30303a] text-gray-200"}`}
              >
                {isLight ? "Dark" : "Light"}
              </button>
              <button
                onClick={() => {
                  setFeedbackOpen(true);
                  setFeedbackSent(false);
                }}
                className={`h-9 px-3 rounded-lg text-xs border transition-colors ${isLight ? "bg-[#f7f9fc] border-[#d6e0ee] text-[#1f2937]" : "bg-[#1b1b20] border-[#30303a] text-gray-200"}`}
              >
                Feedback
              </button>
              <button className="h-9 w-9 rounded-full bg-[#1b1b20] text-gray-300 hover:text-white transition-colors">?</button>
              <button className="h-9 w-9 rounded-full bg-[#1b1b20] text-gray-300 hover:text-white transition-colors">🔔</button>
              <SignedIn>
                <UserButton appearance={{ elements: { userButtonAvatarBox: "h-9 w-9" } }} />
              </SignedIn>
            </div>
          </div>
        </header>

        {/* FILTERS BAR */}
        {activeSection !== "resume_matcher" && activeSection !== "jd_tailor" && activeSection !== "pipeline" && (
          <div className={`p-6 border-b ${isLight ? "bg-white border-[#dbe4f0]" : "bg-[#0f1014] border-[#1f1f24]"}`}>
            <div className="flex items-center justify-between gap-4 mb-4">
              <div>
                <h2 className={`text-2xl font-semibold ${isLight ? "text-[#0f172a]" : "text-white"}`}>Job Intelligence</h2>
                <p className={`text-sm ${isLight ? "text-[#475569]" : "text-gray-400"}`}>Find the jobs from 100+ verified companies.</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowFilters(prev => !prev)}
                  className={`rounded-xl px-4 py-2 text-sm transition-colors border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a] hover:border-pink-500" : "bg-[#16161b] border-[#26262d] text-gray-200 hover:border-pink-500"}`}
                >
                  Filters
                </button>
                <button
                  onClick={() => setActiveSection("jd_tailor")}
                  className="bg-pink-500 text-gray-900 rounded-xl px-4 py-2 text-sm font-semibold hover:bg-pink-400 transition-colors"
                >
                  AI Match
                </button>
              </div>
            </div>
            <div className="flex flex-col lg:flex-row gap-3 items-stretch lg:items-center">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search jobs, companies, or keywords..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className={`w-full rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-pink-500 transition-colors border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-100"}`}
                />
              </div>
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
                className={`rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-pink-500 cursor-pointer transition-colors border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-100"}`}
              >
                <option value="score">Most Relevant</option>
                <option value="date">Newest</option>
                <option value="remote">Remote First</option>
                {resumeMatchEnabled && <option value="matchScore">Match %</option>}
              </select>
              <label className={`text-xs inline-flex items-center gap-2 px-3 ${isLight ? "text-[#334155]" : "text-gray-300"}`}>
                <input
                  type="checkbox"
                  checked={hideStale}
                  onChange={(e) => setHideStale(e.target.checked)}
                  className="accent-pink-500"
                />
                Hide Stale
              </label>
            </div>

            {showFilters && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
                <div>
                  <input
                    list="source-options"
                    placeholder="Source"
                    value={sourceQuery}
                    onChange={e => setSourceQuery(e.target.value)}
                    className={`w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 transition-colors border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-100"}`}
                  />
                  <datalist id="source-options">
                    {sources.map(source => (
                      <option key={source} value={source} />
                    ))}
                  </datalist>
                </div>

                <select
                  value={selectedRole}
                  onChange={e => setSelectedRole(e.target.value)}
                  className={`rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 cursor-pointer transition-colors border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-100"}`}
                >
                  <option value="all">All Roles</option>
                  {roles.map(role => (
                    <option key={role} value={role}>{formatLabel(role)}</option>
                  ))}
                </select>

                <div>
                  <input
                    list="location-options"
                    placeholder="Location"
                    value={locationQuery}
                    onChange={e => setLocationQuery(e.target.value)}
                    className={`w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 transition-colors border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-100"}`}
                  />
                  <datalist id="location-options">
                    {locations.map(location => (
                      <option key={location} value={location} />
                    ))}
                  </datalist>
                </div>

                <select
                  value={selectedEmploymentType}
                  onChange={e => setSelectedEmploymentType(e.target.value)}
                  className={`rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 cursor-pointer transition-colors border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-100"}`}
                >
                  <option value="all">All Types</option>
                  {employmentTypes.map(type => (
                    <option key={type} value={type}>{formatLabel(type)}</option>
                  ))}
                </select>

                <div className="lg:col-span-2">
                  <div className="flex items-center gap-2">
                    <input
                      list="company-options"
                      placeholder="Company"
                      value={companyQuery}
                      onChange={e => setCompanyQuery(e.target.value)}
                      className={`w-full rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 transition-colors border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-100"}`}
                    />
                    {companyQuery && (
                      <button
                        onClick={() => setCompanyQuery("")}
                        className={`px-2 py-2 text-xs rounded border hover:border-pink-500 ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#1f1f25] border-[#2a2a33] text-gray-100"}`}
                      >
                        Clear
                      </button>
                    )}
                    <datalist id="company-options">
                      {companies.map(company => (
                        <option key={company} value={company} />
                      ))}
                    </datalist>
                  </div>
                </div>
              </div>
            )}

            {/* Company quick chips */}
            <div className="mt-3 flex flex-wrap gap-2">
              {topCompanies.map(name => (
                <button
                  key={name}
                  onClick={() => setCompanyQuery(name)}
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    companyQuery === name
                      ? "bg-pink-500 text-gray-900 border-pink-400"
                      : isLight
                      ? "bg-white text-[#334155] border-[#d8e2ef] hover:border-pink-500"
                      : "bg-[#16161b] text-gray-300 border-[#2a2a33] hover:border-pink-500"
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>

            {/* Active Filters Display */}
            {(searchQuery || sourceQuery || companyQuery || selectedRole !== "all" || locationQuery || selectedEmploymentType !== "all") && (
              <div className="mt-4 flex flex-wrap gap-2 items-center">
                <span className="text-xs text-gray-500">Active filters:</span>
                {searchQuery && (
                  <span className="text-xs bg-pink-900/30 text-pink-300 px-2 py-1 rounded">
                    Search: "{searchQuery}"
                  </span>
                )}
                {sourceQuery && (
                  <span className="text-xs bg-pink-900/30 text-pink-300 px-2 py-1 rounded">
                    Source: {sourceQuery}
                  </span>
                )}
                {companyQuery && (
                  <span className="text-xs bg-pink-900/30 text-pink-300 px-2 py-1 rounded">
                    Company: {companyQuery}
                  </span>
                )}
                {selectedRole !== "all" && (
                  <span className="text-xs bg-pink-900/30 text-pink-300 px-2 py-1 rounded">
                    Role: {formatLabel(selectedRole)}
                  </span>
                )}
                {locationQuery && (
                  <span className="text-xs bg-pink-900/30 text-pink-300 px-2 py-1 rounded">
                    Location: {locationQuery}
                  </span>
                )}
                {selectedEmploymentType !== "all" && (
                  <span className="text-xs bg-pink-900/30 text-pink-300 px-2 py-1 rounded">
                    Type: {formatLabel(selectedEmploymentType)}
                  </span>
                )}
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setSelectedRole("all");
                    setSelectedEmploymentType("all");
                    setSourceQuery("");
                    setCompanyQuery("");
                    setLocationQuery("");
                    setHideStale(true);
                  }}
                  className="text-xs text-pink-400 hover:text-pink-300 underline"
                >
                  Clear all
                </button>
              </div>
            )}
          </div>
        )}

        {/* CONTENT */}
        <section className="flex-1 overflow-y-auto p-6">
          {activeSection === "resume_matcher" ? (
            <div className="space-y-6">
              <div className={`rounded-2xl p-6 border ${isLight ? "bg-white border-[#d8e2ef]" : "bg-[#121216] border-[#1f1f24]"}`}>
                <h3 className="text-2xl font-bold text-pink-300 mb-2">Resume Matcher</h3>
                <p className={`mb-4 ${isLight ? "text-[#475569]" : "text-gray-400"}`}>
                  Upload or paste your resume. We will rank matching jobs from this platform only.
                </p>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <label className={`text-xs ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>Upload resume (.pdf or .txt)</label>
                    <input type="file" accept=".pdf,.txt" onChange={handleMatcherResumeUpload} className={`mt-2 text-sm ${isLight ? "text-[#0f172a]" : "text-gray-300"}`} />
                  </div>
                  <div>
                    <label className={`text-xs ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>Or paste resume text</label>
                    <textarea
                      value={matcherResumeText}
                      onChange={(e) => setMatcherResumeText(e.target.value)}
                      rows={6}
                      className={`w-full mt-2 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
                      placeholder="Paste resume text..."
                    />
                  </div>
                </div>
                <div className="mt-4 flex items-center gap-3">
                  <button
                    onClick={runResumeMatcher}
                    disabled={matcherRunning || !matcherResumeText.trim()}
                    className="px-4 py-2 rounded-lg bg-pink-500 text-gray-900 text-sm font-semibold hover:bg-pink-400 disabled:opacity-60"
                  >
                    {matcherRunning ? "Matching..." : "Find Matching Jobs"}
                  </button>
                  <span className={`text-xs ${isLight ? "text-[#64748b]" : "text-gray-500"}`}>
                    {matcherResults.length ? `${matcherResults.length} matches found` : "No matches yet"}
                  </span>
                </div>
              </div>

              {matcherResults.length > 0 && (
                <div className="space-y-4">
                  {matcherResults.slice(0, 60).map((job, index) => (
                    <JobCard
                      key={`matcher-${job.id}-${index}`}
                      job={job}
                      index={index}
                      saved={savedJobs.includes(job.id)}
                      applied={applicationsByJobId.has(job.id)}
                      appliedDetails={applicationsByJobId.get(job.id)}
                      isExpanded={expandedJob === job.id}
                      onSave={toggleSaveJob}
                      onApply={markJobAsApplied}
                      onUpdateNotes={(appId, notes) => updateApplication(appId, { notes })}
                      onToggleDetails={(id) => setExpandedJob(expandedJob === id ? null : id)}
                      resumeMatchEnabled={true}
                      isLight={isLight}
                    />
                  ))}
                </div>
              )}
            </div>
          ) : activeSection === "jd_tailor" ? (
            <ResumeTailorScreen
              onMatch={() => setResumeMatchEnabled(true)}
              onFileUpload={handleResumeUpload}
              authFetch={authFetch}
              resumeText={resumeText}
              onResumeTextChange={setResumeText}
              isLight={isLight}
            />
          ) : activeSection === "pipeline" ? (
            <>
              <SignedIn>
                <PipelineBoard
                  applications={applications}
                  onMoveStage={(id, stage) => updateApplication(id, { stage })}
                  isLight={isLight}
                />
              </SignedIn>
              <SignedOut>
                <div className="max-w-xl mx-auto text-center bg-[#121216] border border-[#1f1f24] rounded-2xl p-10">
                  <h3 className="text-2xl font-bold text-pink-300 mb-2">Sign in to track applications</h3>
                  <p className="text-gray-400 mb-6">
                    Your pipeline is saved per account.
                  </p>
                  <SignInButton mode="modal">
                    <button className="px-4 py-2 rounded-lg bg-pink-500 text-gray-900 text-sm font-semibold hover:bg-pink-400 transition-colors">
                      Sign in to continue
                    </button>
                  </SignInButton>
                </div>
              </SignedOut>
            </>
          ) : (
            <div className="space-y-4">
              {displayJobs.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg mb-2">No jobs found matching your filters</p>
                  <button
                    onClick={() => {
                      setSearchQuery("");
                      setSelectedRole("all");
                    setSelectedEmploymentType("all");
                    setSourceQuery("");
                    setCompanyQuery("");
                    setLocationQuery("");
                    setHideStale(true);
                  }}
                className="text-pink-400 hover:text-pink-300 underline"
                  >
                    Clear all filters
                  </button>
                </div>
              ) : (
                <>
                  {paginatedJobs.map((job, index) => (
                    <JobCard
                      key={job.id}
                      job={job}
                      index={index}
                      saved={savedJobs.includes(job.id)}
                      applied={applicationsByJobId.has(job.id)}
                      appliedDetails={applicationsByJobId.get(job.id)}
                      isExpanded={expandedJob === job.id}
                      onSave={toggleSaveJob}
                      onApply={markJobAsApplied}
                      onUpdateNotes={(appId, notes) => updateApplication(appId, { notes })}
                      onToggleDetails={(id) => {
                        setExpandedJob(expandedJob === id ? null : id);
                      }}
                      resumeMatchEnabled={resumeMatchEnabled}
                      isLight={isLight}
                    />
                  ))}

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex justify-center items-center gap-3 mt-8">
                      <button
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(p => p - 1)}
                        className="px-4 py-2 bg-gray-800 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
                      >
                        ← Previous
                      </button>
                      
                      <span className="text-gray-400">
                        Page {currentPage} of {totalPages}
                      </span>
                      
                      <button
                        disabled={currentPage === totalPages}
                        onClick={() => setCurrentPage(p => p + 1)}
                        className="px-4 py-2 bg-gray-800 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700 transition-colors"
                      >
                        Next →
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </section>
      </main>
      {feedbackOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
          onClick={() => setFeedbackOpen(false)}
        >
          <div
            className={`w-full max-w-lg rounded-2xl border p-6 ${isLight ? "bg-white border-[#dbe4f0]" : "bg-[#111522] border-[#26304a]"}`}
            onClick={(event) => event.stopPropagation()}
          >
            <h3 className="text-xl font-semibold">Share feedback</h3>
            <p className={`text-sm mt-1 ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>Tell us what should be improved next.</p>
            <div className="mt-4 space-y-3">
              <textarea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder="What felt broken, slow, or missing?"
                rows={5}
                className={`w-full rounded-xl border px-3 py-2 text-sm focus:outline-none focus:border-pink-500 ${isLight ? "bg-[#f8fbff] border-[#dbe4f0]" : "bg-[#161b2a] border-[#2b3653]"}`}
              />
              <input
                type="email"
                value={feedbackEmail}
                onChange={(e) => setFeedbackEmail(e.target.value)}
                placeholder="Email (optional)"
                className={`w-full rounded-xl border px-3 py-2 text-sm focus:outline-none focus:border-pink-500 ${isLight ? "bg-[#f8fbff] border-[#dbe4f0]" : "bg-[#161b2a] border-[#2b3653]"}`}
              />
              {feedbackSent && (
                <div className="text-sm text-emerald-400">Thanks. Feedback saved.</div>
              )}
            </div>
            <div className="mt-5 flex items-center justify-end gap-2">
              <button
                onClick={() => setFeedbackOpen(false)}
                className={`px-4 py-2 rounded-lg border text-sm ${isLight ? "border-[#dbe4f0] hover:bg-[#f8fbff]" : "border-[#2b3653] hover:bg-[#161b2a]"}`}
              >
                Cancel
              </button>
              <button
                onClick={submitFeedback}
                disabled={!feedbackText.trim() || feedbackSubmitting}
                className="px-4 py-2 rounded-lg text-sm font-semibold bg-pink-500 text-[#111827] hover:bg-pink-400 disabled:opacity-50"
              >
                {feedbackSubmitting ? "Sending..." : "Send Feedback"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ---------------- UI COMPONENTS ---------------- */

function Nav({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-2 rounded transition-colors flex items-center gap-2 ${
        active ? "bg-[#231824] text-pink-300" : "text-gray-400 hover:bg-[#1b1b20]"
      }`}
    >
      <span className="w-4 text-center">{icon || "•"}</span>
      {label}
    </button>
  );
}

function StatTile({ label, value, isLight }) {
  return (
    <div className={`rounded-xl border px-3 py-3 ${isLight ? "bg-[#f8fbff] border-[#dbe7f8]" : "bg-[#151c2f] border-[#2b3653]"}`}>
      <div className={`text-[11px] ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>{label}</div>
      <div className="text-base font-semibold mt-1">{value}</div>
    </div>
  );
}

function ResumeTailorScreen({ onMatch, onFileUpload, authFetch, resumeText, onResumeTextChange, isLight }) {
  const [jobDescription, setJobDescription] = React.useState("");
  const [profile, setProfile] = React.useState({
    name: "",
    education: "",
    currentCompany: "",
    experienceSummary: "",
    skills: "",
  });
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const [result, setResult] = React.useState(null);

  const generateTailoredResume = async () => {
    setError("");
    setResult(null);
    if (!jobDescription.trim()) {
      setError("Paste a job description first.");
      return;
    }
    if (!resumeText.trim() && !profile.experienceSummary.trim()) {
      setError("Upload/paste your base resume or add experience summary.");
      return;
    }

    setLoading(true);
    try {
      const payload = await authFetch("/api/resume-tailor", {
        method: "POST",
        body: JSON.stringify({
          jobDescription,
          resumeText,
          profile,
        }),
      });
      setResult(payload.result || null);
      onMatch();
    } catch (e) {
      setError(e.message || "Failed to generate tailored resume.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className={`rounded-2xl p-6 border ${isLight ? "bg-white border-[#d8e2ef]" : "bg-[#121216] border-[#1f1f24]"}`}>
        <h3 className="text-2xl font-bold text-pink-300 mb-2">Resume Matcher + Tailor (AI)</h3>
        <p className={`mb-4 ${isLight ? "text-[#475569]" : "text-gray-400"}`}>
          Upload your resume, paste a job description, and generate a JD-tailored resume draft using Gemini.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-3">
            <label className={`text-xs ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>Base resume upload</label>
            <input type="file" accept=".pdf,.txt" onChange={onFileUpload} className={`text-sm ${isLight ? "text-[#0f172a]" : "text-gray-300"}`} />
            <label className={`text-xs ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>Or paste base resume text</label>
            <textarea
              value={resumeText}
              onChange={(e) => onResumeTextChange(e.target.value)}
              rows={10}
              placeholder="Paste your existing resume text..."
              className={`w-full rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
            />
          </div>

          <div className="space-y-3">
            <label className={`text-xs ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>Job description</label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={10}
              placeholder="Paste target job description..."
              className={`w-full rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
            />
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <input
            value={profile.name}
            onChange={(e) => setProfile((prev) => ({ ...prev, name: e.target.value }))}
            placeholder="Name"
            className={`rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
          />
          <input
            value={profile.education}
            onChange={(e) => setProfile((prev) => ({ ...prev, education: e.target.value }))}
            placeholder="Education"
            className={`rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
          />
          <input
            value={profile.currentCompany}
            onChange={(e) => setProfile((prev) => ({ ...prev, currentCompany: e.target.value }))}
            placeholder="Current company"
            className={`rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
          />
          <input
            value={profile.skills}
            onChange={(e) => setProfile((prev) => ({ ...prev, skills: e.target.value }))}
            placeholder="Skills (comma separated)"
            className={`md:col-span-2 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
          />
          <input
            value={profile.experienceSummary}
            onChange={(e) => setProfile((prev) => ({ ...prev, experienceSummary: e.target.value }))}
            placeholder="Experience summary"
            className={`rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
          />
        </div>

        <div className="mt-5 flex items-center gap-3">
          <button
            onClick={generateTailoredResume}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-pink-500 text-gray-900 text-sm font-semibold hover:bg-pink-400 disabled:opacity-60"
          >
            {loading ? "Generating..." : "Generate Tailored Resume"}
          </button>
          <span className={`text-xs ${isLight ? "text-[#64748b]" : "text-gray-500"}`}>Uses Gemini with strict no-fabrication guardrails.</span>
        </div>

        {error && <div className="mt-3 text-sm text-rose-400">{error}</div>}
      </div>

      {result && (
        <div className={`rounded-2xl p-6 space-y-4 border ${isLight ? "bg-white border-[#d8e2ef]" : "bg-[#121216] border-[#1f1f24]"}`}>
          <h4 className={`text-xl font-semibold ${isLight ? "text-[#0f172a]" : "text-white"}`}>{result.headline || "Tailored Resume Draft"}</h4>
          {result.professional_summary && (
            <p className={`text-sm ${isLight ? "text-[#334155]" : "text-gray-300"}`}>{result.professional_summary}</p>
          )}

          <ResultList title="Changes Made" items={result.changes_made} />
          <ResultList title="Tailored Experience Bullets" items={result.tailored_experience_bullets} />
          <ResultList title="Tailored Skills" items={result.tailored_skills} inline />
          <ResultList title="ATS Keywords" items={result.ats_keywords} inline />
          <ResultList title="Missing Information" items={result.missing_information} warn />

          <div>
            <div className={`text-sm font-medium mb-2 ${isLight ? "text-[#0f172a]" : "text-gray-200"}`}>Tailored Resume (editable)</div>
            <textarea
              value={result.tailored_resume_text || ""}
              onChange={(e) => setResult((prev) => ({ ...prev, tailored_resume_text: e.target.value }))}
              rows={16}
              className={`w-full rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-pink-500 border ${isLight ? "bg-white border-[#d8e2ef] text-[#0f172a]" : "bg-[#16161b] border-[#26262d] text-gray-200"}`}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function ResultList({ title, items, inline = false, warn = false }) {
  if (!Array.isArray(items) || items.length === 0) return null;
  return (
    <div>
      <div className={`text-sm font-medium mb-2 ${warn ? "text-amber-300" : "text-gray-200"}`}>{title}</div>
      {inline ? (
        <div className="flex flex-wrap gap-2">
          {items.map((item, idx) => (
            <span key={`${title}-${idx}`} className="text-xs px-2 py-1 rounded bg-[#1e1e25] text-gray-300">
              {item}
            </span>
          ))}
        </div>
      ) : (
        <ul className="space-y-1">
          {items.map((item, idx) => (
            <li key={`${title}-${idx}`} className={`text-sm ${warn ? "text-amber-200" : "text-gray-300"}`}>
              • {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function PipelineBoard({ applications, onMoveStage, isLight }) {
  const stages = ["Interested", "Applied", "Interview", "Offer", "Rejected"];
  const [draggedAppId, setDraggedAppId] = React.useState(null);
  const [dragOverStage, setDragOverStage] = React.useState("");
  const grouped = stages.reduce((acc, stage) => {
    acc[stage] = [];
    return acc;
  }, {});

  applications.forEach(app => {
    const stage = app.stage || "Applied";
    if (!grouped[stage]) grouped[stage] = [];
    grouped[stage].push(app);
  });

  const stageIndex = (stage) => stages.indexOf(stage);

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-xl font-semibold text-white">Application Pipeline</h3>
        <p className="text-sm text-gray-400">Move applications across stages as you progress.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {stages.map(stage => (
          <div
            key={stage}
            onDragOver={(event) => {
              event.preventDefault();
              setDragOverStage(stage);
            }}
            onDragLeave={() => setDragOverStage((current) => (current === stage ? "" : current))}
            onDrop={() => {
              if (draggedAppId) {
                onMoveStage(draggedAppId, stage);
              }
              setDraggedAppId(null);
              setDragOverStage("");
            }}
            className={`bg-[#121216] border rounded-2xl p-3 min-h-[240px] transition-colors ${
              dragOverStage === stage ? "border-pink-500/70 bg-[#16131a]" : "border-[#1f1f24]"
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-white">{stage}</span>
              <span className="text-xs text-gray-500">{grouped[stage]?.length || 0}</span>
            </div>
            <div className="space-y-3">
              {(grouped[stage] || []).map(app => (
                <div
                  key={app.id}
                  draggable
                  onDragStart={() => setDraggedAppId(app.id)}
                  onDragEnd={() => {
                    setDraggedAppId(null);
                    setDragOverStage("");
                  }}
                  className="bg-[#15151a] border border-[#23232a] rounded-xl p-3 cursor-grab active:cursor-grabbing"
                >
                  <div className="text-sm font-semibold text-white">{app.title}</div>
                  <div className="text-xs text-gray-400 mt-1">{app.company}</div>
                  <div className="text-xs text-gray-500 mt-1">{app.location || "Location"}</div>
                  <div className="flex items-center gap-2 mt-3">
                    <button
                      disabled={stageIndex(stage) === 0}
                      onClick={() => onMoveStage(app.id, stages[stageIndex(stage) - 1])}
                      className="px-2 py-1 text-xs rounded bg-[#1e1e25] text-gray-300 disabled:opacity-40"
                    >
                      ←
                    </button>
                    <button
                      disabled={stageIndex(stage) === stages.length - 1}
                      onClick={() => onMoveStage(app.id, stages[stageIndex(stage) + 1])}
                      className="px-2 py-1 text-xs rounded bg-[#1e1e25] text-gray-300 disabled:opacity-40"
                    >
                      →
                    </button>
                  </div>
                </div>
              ))}
              {grouped[stage]?.length === 0 && (
                <div className="text-xs text-gray-500">No applications</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function JobCard({ job, index, saved, applied, onSave, onApply, resumeMatchEnabled, appliedDetails, onUpdateNotes, onToggleDetails, isExpanded, isLight }) {
  const [notes, setNotes] = React.useState(appliedDetails?.notes || "");
  React.useEffect(() => {
    setNotes(appliedDetails?.notes || "");
  }, [appliedDetails?.notes]);
  const pill = (() => {
    const loc = (job.location || "").toLowerCase();
    if (loc.includes("remote")) return "Remote";
    if (loc.includes("hybrid")) return "Hybrid";
    if (loc.includes("india")) return "India";
    return "";
  })();
  const initial = (job.company || "?").trim().charAt(0).toUpperCase();
  
  return (
    <div
      className={`rounded-2xl p-5 hover:-translate-y-[1px] transition-all duration-300 animate-[fadeInUp_.35s_ease_forwards] border ${
        isLight
          ? "bg-white border-[#d8e2ef] hover:border-[#c5d4ea] shadow-[0_4px_12px_rgba(15,23,42,0.06)]"
          : "bg-[#15151a] border-[#23232a] hover:border-[#2f2f39] shadow-[0_6px_20px_rgba(0,0,0,0.25)]"
      }`}
      style={{ animationDelay: `${Math.min(index, 8) * 40}ms` }}
    >
      <div className="flex gap-5">
        {resumeMatchEnabled && job.matchScore !== undefined && (
          <div className="w-24 flex-shrink-0 text-center">
            <div className="w-20 h-20 mx-auto rounded-full border-4 border-pink-400 flex items-center justify-center">
              <span className="text-xl font-bold text-pink-300">{job.matchScore}%</span>
            </div>
            {job.matchConfidence !== undefined && (
              <div className="text-[11px] text-gray-400 mt-1">Conf {job.matchConfidence}%</div>
            )}
          </div>
        )}

        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className={`w-11 h-11 rounded-xl border text-pink-300 flex items-center justify-center text-sm font-semibold ${isLight ? "bg-[#f8fbff] border-[#d8e2ef]" : "bg-[#1e1e25] border-[#2a2a33]"}`}>
              {initial}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`text-xs px-2 py-1 rounded ${isLight ? "bg-[#f8fbff] text-[#334155]" : "bg-[#1e1e25] text-gray-300"}`}>{job.company}</span>
              {job.source && (
                <span className={`text-xs px-2 py-1 rounded ${isLight ? "bg-[#eef4ff] text-[#64748b]" : "bg-[#1e1e25]/60 text-gray-400"}`}>{job.source}</span>
              )}
              {pill && (
                <span className="text-xs bg-emerald-900/30 text-emerald-300 px-2 py-1 rounded">{pill}</span>
              )}
              <span
                className={`text-xs px-2 py-1 rounded ${
                  job.freshness === "New"
                    ? "bg-pink-900/30 text-pink-300"
                    : job.freshness === "Fresh"
                    ? "bg-blue-900/30 text-blue-300"
                    : job.freshness === "Recent"
                    ? "bg-gray-700/60 text-gray-300"
                    : "bg-rose-900/30 text-rose-300"
                }`}
              >
                {job.freshness || "Unknown"}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 mb-1">
            <h3 className={`text-lg font-semibold ${isLight ? "text-[#0f172a]" : "text-white"}`}>{job.title}</h3>
          </div>
          <p className={`text-sm mb-2 ${isLight ? "text-[#64748b]" : "text-gray-400"}`}>{job.location} · {job.employment_type || "Full-time"} · {job.postedDate || job.fetchedAt || "Recently"}</p>
          
          <div className="flex gap-2 flex-wrap">
            {job.employment_type && (
                <span className={`inline-block text-xs px-2 py-1 rounded-full ${isLight ? "bg-[#eef4ff] text-[#64748b]" : "bg-[#1e1e25] text-gray-400"}`}>
                  {job.employment_type}
                </span>
              )}
              {job.role && (
                <span className={`inline-block text-xs px-2 py-1 rounded-full ${isLight ? "bg-[#eef4ff] text-[#64748b]" : "bg-[#1e1e25] text-gray-400"}`}>
                  {job.role}
                </span>
              )}
              {job.requirements?.skills && job.requirements.skills.length > 0 && (
                <span className={`inline-block text-xs px-2 py-1 rounded-full ${isLight ? "bg-[#f8fbff] text-[#334155]" : "bg-[#1e1e25] text-gray-300"}`}>
                  {job.requirements.skills.slice(0, 3).join(", ")}
                </span>
              )}
          </div>

          {resumeMatchEnabled && job.matchExplain && job.matchExplain.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-gray-300">
              {job.matchExplain.map((item) => (
                <span
                  key={item.label}
                  className="bg-emerald-900/20 text-emerald-300 px-2 py-1 rounded"
                >
                  {item.label}: {item.hits.join(", ")}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 flex-shrink-0 items-end">
          {job.salary && (
            <div className="text-sm font-semibold text-white">{job.salary}</div>
          )}
          <button
            onClick={() => onSave(job.id)}
            className={`h-9 w-9 rounded-lg transition-colors ${
              saved ? "bg-pink-500/20 text-pink-300" : "bg-[#1e1e25] text-gray-400 hover:bg-[#26262f]"
            }`}
            title={saved ? "Unsave job" : "Save job"}
          >
            🔖
          </button>
          <button
            onClick={() => onApply(job.id, job.applyLink)}
            className="px-4 py-2 rounded font-semibold transition-colors bg-pink-500 text-gray-900 hover:bg-pink-400 shadow-md shadow-pink-900/30"
          >
            Apply →
          </button>
          
          {applied && (
            <button
              onClick={() => onToggleDetails(job.id)}
              className="px-3 py-1.5 rounded bg-gray-800 text-gray-300 text-sm hover:bg-gray-700 transition-colors"
            >
              {isExpanded ? "Hide ▲" : "Details ▼"}
            </button>
          )}
        </div>
      </div>
      
      {/* Expanded Details */}
          {applied && isExpanded && appliedDetails && (
        <div className="mt-4 pt-4 border-t border-gray-800 space-y-3">
          <div>
            <p className="text-xs text-gray-500 mb-1">Applied on:</p>
            <p className="text-sm text-gray-300">
              {new Date(appliedDetails.applied_date || appliedDetails.appliedDate || new Date().toISOString()).toLocaleDateString('en-US', { 
                year: 'numeric', month: 'long', day: 'numeric' 
              })}
            </p>
          </div>
          
          {job.requirements && (
            <div>
              <p className="text-xs text-gray-500 mb-2">Job Requirements:</p>
              <div className="bg-gray-800/50 rounded p-3 text-sm space-y-2">
                {job.requirements.skills && job.requirements.skills.length > 0 && (
                  <div>
                    <span className="text-gray-400">Skills:</span>
                    <span className="text-gray-300 ml-2">{job.requirements.skills.join(", ")}</span>
                  </div>
                )}
                {job.requirements.experience_years > 0 && (
                  <div>
                    <span className="text-gray-400">Experience:</span>
                    <span className="text-gray-300 ml-2">{job.requirements.experience_years} years</span>
                  </div>
                )}
                {job.requirements.education && job.requirements.education !== 'not_specified' && (
                  <div>
                    <span className="text-gray-400">Education:</span>
                    <span className="text-gray-300 ml-2 capitalize">{job.requirements.education}</span>
                  </div>
                )}
              </div>
            </div>
          )}
          
          <div>
            <p className="text-xs text-gray-500 mb-1">Your Notes:</p>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              onBlur={() => onUpdateNotes(appliedDetails.id, notes)}
              placeholder="Add notes about your application..."
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-pink-500 resize-none"
              rows={3}
            />
          </div>
        </div>
      )}
    </div>
  );
}
