import React from "react";
import { SignedIn, SignedOut, SignInButton, UserButton, useAuth } from "@clerk/clerk-react";

const STALE_DAYS = 45;
const VERY_FRESH_DAYS = 3;
const FRESH_DAYS = 14;

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

  const [savedJobs, setSavedJobs] = React.useState([]);
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const [applications, setApplications] = React.useState([]);
  const [metrics, setMetrics] = React.useState(null);
  const [expandedJob, setExpandedJob] = React.useState(null);
  const [currentPage, setCurrentPage] = React.useState(1);
  const [itemsPerPage] = React.useState(20);
  const [sortBy, setSortBy] = React.useState("score");
  const [resumeText, setResumeText] = React.useState("");
  const [resumeKeywords, setResumeKeywords] = React.useState([]);
  const [showFilters, setShowFilters] = React.useState(false);
  const [hideStale, setHideStale] = React.useState(true);
  const [workspaceSearch, setWorkspaceSearch] = React.useState("");
  const { getToken, isSignedIn } = useAuth();

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

  const refreshMetrics = React.useCallback(async () => {
    if (!isSignedIn) return;
    try {
      const stats = await authFetch("/api/metrics");
      setMetrics(stats);
    } catch (error) {
      console.error("Failed to refresh metrics", error);
    }
  }, [authFetch, isSignedIn]);

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
      setMetrics(null);
      return;
    }

    const load = async () => {
      try {
        const apps = await authFetch("/api/applications");
        setApplications(apps.applications || []);
      } catch (error) {
        console.error("Failed to load applications", error);
      }

      try {
        const stats = await authFetch("/api/metrics");
        setMetrics(stats);
      } catch (error) {
        console.error("Failed to load metrics", error);
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

  const sourceHealth = React.useMemo(() => {
    const sourceMap = new Map();
    jobs.forEach((job) => {
      const source = job.source || "Unknown";
      const row = sourceMap.get(source) || { source, total: 0, fresh: 0, stale: 0 };
      row.total += 1;
      if ((job.ageDays ?? 999) <= FRESH_DAYS) row.fresh += 1;
      if (job.stale) row.stale += 1;
      sourceMap.set(source, row);
    });

    return Array.from(sourceMap.values())
      .map((row) => {
        const freshRatio = row.total ? row.fresh / row.total : 0;
        let status = "Failing";
        if (row.total >= 10 && freshRatio >= 0.45) status = "Healthy";
        else if (row.total >= 3 && freshRatio >= 0.2) status = "Partial";
        return { ...row, status };
      })
      .sort((a, b) => b.total - a.total);
  }, [jobs]);

  /* ---------------- QUICK FILTERS ---------------- */
  const quickFilters = [
    {
      label: "Remote Only",
      action: () => {
        setSearchQuery("");
        setSelectedRole("all");
        setSelectedEmploymentType("all");
        setSourceQuery("");
        setCompanyQuery("");
        setLocationQuery("");
        setFilteredJobs(jobs.filter(j => j.location?.toLowerCase().includes("remote")));
      }
    },
    {
      label: "Full-time",
      action: () => {
        setSearchQuery("");
        setSelectedRole("all");
        setSelectedEmploymentType("all");
        setSourceQuery("");
        setCompanyQuery("");
        setLocationQuery("");
        setFilteredJobs(jobs.filter(j => j.employment_type === "Full-time"));
      }
    },
    {
      label: "Engineering",
      action: () => {
        setSearchQuery("");
        setSelectedRole("all");
        setSelectedEmploymentType("all");
        setSourceQuery("");
        setCompanyQuery("");
        setLocationQuery("");
        setFilteredJobs(jobs.filter(j => j.role === "Engineering"));
      }
    },
    {
      label: "Reset Filters",
      action: () => {
        setSearchQuery("");
        setSelectedRole("all");
        setSelectedEmploymentType("all");
        setSourceQuery("");
        setCompanyQuery("");
        setLocationQuery("");
        setFilteredJobs(jobs);
      }
    }
  ];

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

    // Apply resume matching scores if enabled
    if (resumeMatchEnabled && resumeText) {
      data = data.map(job => ({
        ...job,
        matchScore: calculateMatchScore(job, resumeText),
        matchExplain: getMatchExplanation(job, resumeText)
      }));
    }

    setFilteredJobs(data);
    setCurrentPage(1); // Reset to page 1 when filters change
  }, [jobs, searchQuery, sourceQuery, companyQuery, selectedRole, locationQuery, selectedEmploymentType, resumeMatchEnabled, resumeText, hideStale]);

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
      refreshMetrics();
    } catch (error) {
      console.error("Failed to save job as interested", error);
    }
  };

  const normalizeTerms = (text) => {
    if (!text) return [];
    const cleaned = text
      .toLowerCase()
      .replace(/[^a-z0-9+/#\s.-]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    if (!cleaned) return [];
    return cleaned.split(" ").filter(Boolean);
  };

  const buildKeywordSet = (terms) => new Set(terms.filter(Boolean));

  const overlapScore = (targetTerms, candidateSet) => {
    if (!targetTerms.length) return 0;
    let hits = 0;
    for (const t of targetTerms) {
      if (candidateSet.has(t)) hits += 1;
    }
    return hits / targetTerms.length;
  };

  const extractResumeSignals = (text) => {
    const tokens = normalizeTerms(text);
    const stopwords = new Set(["the","and","for","with","from","into","over","under","a","an","to","of","in","on","by","at","as","or","is","are","be","this","that","these","those","it","we","you","your","our","their"]);
    const filtered = tokens.filter(t => !stopwords.has(t) && t.length > 1);

    const bigrams = [];
    for (let i = 0; i < filtered.length - 1; i += 1) {
      bigrams.push(`${filtered[i]} ${filtered[i + 1]}`);
    }

    const rolePhrases = [
      "product manager", "product management", "program manager",
      "project manager", "product owner", "growth", "strategy"
    ];
    const skillPhrases = [
      "sql", "python", "javascript", "react", "java", "aws", "docker",
      "kubernetes", "node", "typescript", "figma", "jira", "agile",
      "scrum", "analytics", "tableau", "power bi", "a/b", "ab"
    ];

    const phraseHits = rolePhrases
      .concat(skillPhrases)
      .filter(p => filtered.includes(p) || bigrams.includes(p));

    return buildKeywordSet([...filtered, ...bigrams, ...phraseHits]);
  };

  const getMatchExplanation = (job, resumeTextValue) => {
    if (!resumeTextValue) return [];

    const resumeSet = extractResumeSignals(resumeTextValue);
    const jobSkills = (job.requirements?.skills || []).map(s => s.toLowerCase());
    const jobKeywords = (job.requirements?.keywords || []).map(k => k.toLowerCase());
    const titleTokens = normalizeTerms(job.title || "");
    const roleTokens = normalizeTerms(job.role || "");

    const explain = [];

    const addMatches = (label, terms, limit = 4) => {
      const hits = terms.filter(t => resumeSet.has(t)).slice(0, limit);
      if (hits.length) {
        explain.push({ label, hits });
      }
    };

    addMatches("Skills", jobSkills);
    addMatches("Keywords", jobKeywords);
    addMatches("Title", titleTokens, 3);
    addMatches("Role", roleTokens, 3);

    return explain;
  };

  const calculateMatchScore = (job, resumeTextValue) => {
    if (!resumeTextValue) return 0;

    const resumeSet = extractResumeSignals(resumeTextValue);

    const jobSkills = (job.requirements?.skills || []).map(s => s.toLowerCase());
    const jobKeywords = (job.requirements?.keywords || []).map(k => k.toLowerCase());
    const titleTokens = normalizeTerms(job.title || "");
    const roleTokens = normalizeTerms(job.role || "");

    const skillScore = overlapScore(jobSkills, resumeSet);
    const keywordScore = overlapScore(jobKeywords, resumeSet);
    const titleScore = overlapScore(titleTokens, resumeSet);
    const roleScore = overlapScore(roleTokens, resumeSet);

    const weighted = (skillScore * 0.5) + (keywordScore * 0.3) + (titleScore * 0.15) + (roleScore * 0.05);
    return Math.min(100, Math.round(weighted * 100));
  };

  const locationPill = (location) => {
    const loc = (location || "").toLowerCase();
    if (loc.includes("remote")) return "Remote";
    if (loc.includes("hybrid")) return "Hybrid";
    if (loc.includes("india")) return "India";
    return "";
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
      refreshMetrics();
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
      refreshMetrics();
    } catch (error) {
      console.error("Failed to update application", error);
    }
  };

  const handleResumeUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  const fileType = file.type;
  
  // Handle PDF files
  if (fileType === 'application/pdf' || file.name.endsWith('.pdf')) {
    // Using pdf.js library (works in browser)
    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        // Load PDF.js library dynamically
        const pdfjsLib = window['pdfjs-dist/build/pdf'];
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        
        const typedArray = new Uint8Array(e.target.result);
        const pdf = await pdfjsLib.getDocument(typedArray).promise;
        
        let fullText = '';
        
        // Extract text from all pages
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const textContent = await page.getTextContent();
          const pageText = textContent.items.map(item => item.str).join(' ');
          fullText += pageText + ' ';
        }
        
        setResumeText(fullText);
        
        // Extract keywords
        const words = fullText.match(/\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b/g) || [];
        const techTerms = fullText.match(/\b(python|javascript|react|java|aws|docker|kubernetes|sql|mongodb|node|typescript|vue|angular|django|flask|spring|express|postgres|redis|git|agile|scrum|api|rest|graphql|ci\/cd|devops|machine learning|ml|ai|data science|analytics|tableau|power bi|excel|powerpoint)\b/gi) || [];
        
        const allKeywords = [...new Set([...words, ...techTerms])];
        setResumeKeywords(allKeywords);
        setResumeMatchEnabled(true);
        setActiveSection("all");
      } catch (error) {
        alert('Error reading PDF. Please try a different file or convert to TXT.');
        console.error('PDF parsing error:', error);
      }
    };
    reader.readAsArrayBuffer(file);
  } 
  // Handle TXT files
  else if (fileType === 'text/plain' || file.name.endsWith('.txt')) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      setResumeText(text);
      
      // Extract keywords
      const words = text.match(/\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b/g) || [];
      const techTerms = text.match(/\b(python|javascript|react|java|aws|docker|kubernetes|sql|mongodb|node|typescript|vue|angular|django|flask|spring|express|postgres|redis|git|agile|scrum|api|rest|graphql|ci\/cd|devops|machine learning|ml|ai|data science|analytics|tableau|power bi|excel|powerpoint)\b/gi) || [];
      
      const allKeywords = [...new Set([...words, ...techTerms])];
      setResumeKeywords(allKeywords);
      setResumeMatchEnabled(true);
      setActiveSection("all");
    };
    reader.readAsText(file);
  } else {
    alert('Please upload a PDF or TXT file');
  }
};

  return (
    <div className="min-h-screen bg-[#0b0b0d] text-gray-100 flex">
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      {/* SIDEBAR */}
      <aside className={`${sidebarOpen ? "w-72" : "w-14"} bg-[#121216] border-r border-[#1f1f24] transition-all`}>
        <div className="p-4 flex justify-between items-center">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-pink-500/20 border border-pink-500/30 text-pink-300 flex items-center justify-center text-sm font-semibold">
                AP
              </div>
              <h1 className="text-xl font-semibold text-pink-300">{brandName}</h1>
            </div>
          )}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-pink-400">
            {sidebarOpen ? "✕" : "☰"}
          </button>
        </div>

        {sidebarOpen && (
          <div className="px-4 space-y-6">
            {/* NAV */}
            <nav className="space-y-2">
              <Nav label="Overview" active={activeSection === "all"} onClick={() => setActiveSection("all")} />
              <Nav label="My Pipeline" active={activeSection === "pipeline"} onClick={() => setActiveSection("pipeline")} />
              <Nav label="Saved" active={activeSection === "saved"} onClick={() => setActiveSection("saved")} />
              <Nav label="Applied" active={activeSection === "applied"} onClick={() => setActiveSection("applied")} />
              <Nav label="Resume Matches" active={activeSection === "resume"} onClick={() => setActiveSection("resume")} />
            </nav>

            {/* QUICK FILTERS */}
            <div>
              <h4 className="text-xs uppercase text-gray-500 mb-2">Quick Filters</h4>
              <div className="space-y-1">
                {quickFilters.map(q => (
                  <button
                    key={q.label}
                    onClick={q.action}
                    className="w-full text-left px-3 py-2 rounded bg-[#18181d] hover:bg-[#1f1f26] text-sm transition-colors"
                  >
                    {q.label}
                  </button>
                ))}
              </div>
            </div>

            {/* RESUME MATCHER CARD */}
            <div className="bg-[#1b121a] border border-[#2b1a24] rounded-lg p-4">
              <h4 className="text-sm font-semibold text-pink-300 mb-1">Resume Matcher</h4>
              <p className="text-xs text-gray-400 mb-3">
                Upload your resume to find best-fit roles
              </p>
              <button
                onClick={() => setActiveSection("resume")}
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
        <header className="p-5 border-b border-[#1f1f24] bg-[#0f1014]">
          <div className="flex items-center gap-4">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="h-9 w-9 rounded-lg bg-[#1b1b20] text-pink-300 hover:text-pink-200 hover:bg-[#24242b] transition-colors"
                aria-label="Open menu"
              >
                ☰
              </button>
            )}
            <div className="flex-1">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search across your workspace..."
                  value={workspaceSearch}
                  onChange={(e) => setWorkspaceSearch(e.target.value)}
                  className="w-full bg-[#14151b] border border-[#26262d] rounded-xl px-4 py-3 text-sm text-gray-300 focus:outline-none focus:border-pink-500 transition-colors"
                />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="h-9 w-9 rounded-full bg-[#1b1b20] text-gray-300 hover:text-white transition-colors">?</button>
              <button className="h-9 w-9 rounded-full bg-[#1b1b20] text-gray-300 hover:text-white transition-colors">🔔</button>
              <SignedOut>
                <SignInButton mode="modal">
                  <button className="px-4 py-2 rounded-lg bg-pink-500 text-gray-900 text-sm font-semibold hover:bg-pink-400 transition-colors">
                    Sign in
                  </button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <UserButton appearance={{ elements: { userButtonAvatarBox: "h-9 w-9" } }} />
              </SignedIn>
            </div>
          </div>
        </header>

        {/* FILTERS BAR */}
        {activeSection !== "resume" && activeSection !== "pipeline" && (
          <div className="p-6 bg-[#0f1014] border-b border-[#1f1f24]">
            <div className="flex items-center justify-between gap-4 mb-4">
              <div>
                <h2 className="text-2xl font-semibold text-white">Job Intelligence</h2>
                <p className="text-sm text-gray-400">New opportunities match your profile today.</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowFilters(prev => !prev)}
                  className="bg-[#16161b] border border-[#26262d] rounded-xl px-4 py-2 text-sm text-gray-200 hover:border-pink-500 transition-colors"
                >
                  Filters
                </button>
                <button className="bg-pink-500 text-gray-900 rounded-xl px-4 py-2 text-sm font-semibold hover:bg-pink-400 transition-colors">
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
                  className="w-full bg-[#16161b] border border-[#26262d] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-pink-500 transition-colors"
                />
              </div>
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
                className="bg-[#16161b] border border-[#26262d] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-pink-500 cursor-pointer transition-colors"
              >
                <option value="score">Most Relevant</option>
                <option value="date">Newest</option>
                <option value="remote">Remote First</option>
                {resumeMatchEnabled && <option value="matchScore">Match %</option>}
              </select>
              <label className="text-xs text-gray-300 inline-flex items-center gap-2 px-3">
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
                    className="w-full bg-[#16161b] border border-[#26262d] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 transition-colors"
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
                  className="bg-[#16161b] border border-[#26262d] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 cursor-pointer transition-colors"
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
                    className="w-full bg-[#16161b] border border-[#26262d] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 transition-colors"
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
                  className="bg-[#16161b] border border-[#26262d] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 cursor-pointer transition-colors"
                >
                  <option value="all">All Types</option>
                  {employmentTypes.map(type => (
                    <option key={type} value={type}>{formatLabel(type)}</option>
                  ))}
                </select>

                <div className="lg:col-span-2">
                  <select
                    value={companyQuery || "__all__"}
                    onChange={e => setCompanyQuery(e.target.value === "__all__" ? "" : e.target.value)}
                    className="w-full bg-[#16161b] border border-[#26262d] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-pink-500 transition-colors cursor-pointer"
                  >
                    <option value="__all__">All Companies</option>
                    {companies.map(company => (
                      <option key={company} value={company}>{company}</option>
                    ))}
                  </select>
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
          {activeSection === "resume" ? (
            <ResumeMatchScreen 
              onMatch={() => setResumeMatchEnabled(true)}
              onFileUpload={handleResumeUpload}
            />
          ) : activeSection === "pipeline" ? (
            <>
              <SignedIn>
                <PipelineBoard
                  applications={applications}
                  onMoveStage={(id, stage) => updateApplication(id, { stage })}
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
              {activeSection === "all" && (
                <SignedIn>
                  <MetricsBar metrics={metrics} />
                </SignedIn>
              )}
              {activeSection === "all" && sourceHealth.length > 0 && (
                <SourceHealthBar rows={sourceHealth.slice(0, 8)} />
              )}
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
    </div>
  );
}

/* ---------------- UI COMPONENTS ---------------- */

function Nav({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-2 rounded transition-colors ${
        active ? "bg-[#231824] text-pink-300" : "text-gray-400 hover:bg-[#1b1b20]"
      }`}
    >
      {label}
    </button>
  );
}

function ResumeMatchScreen({ onMatch, onFileUpload }) {
  return (
    <div className="max-w-xl mx-auto text-center bg-[#121216] border border-[#1f1f24] rounded-2xl p-10">
      <h3 className="text-2xl font-bold text-pink-300 mb-2">Match Your Resume</h3>
      <p className="text-gray-400 mb-6">
        Upload your resume (.txt file) and instantly see which roles fit you best.
      </p>

      <input 
        type="file" 
        accept=".pdf,.txt" 
        onChange={onFileUpload}
        className="mb-4 text-gray-300" 
      />
            
      <p className="text-xs text-gray-500 mt-2">
        Tip: Save your resume as .txt or pdf for best results
      </p>
    </div>
  );
}

function MetricsBar({ metrics }) {
  if (!metrics) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {["Applications", "Interviews", "Offers", "Interview Rate"].map(label => (
          <div key={label} className="bg-[#15151a] border border-[#23232a] rounded-2xl p-4">
            <div className="text-xs text-gray-500">{label}</div>
            <div className="mt-2 h-6 w-16 bg-[#23232a] rounded" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <MetricCard label="Applications" value={metrics.totals?.total || 0} />
      <MetricCard label="Interviews" value={metrics.totals?.interview || 0} />
      <MetricCard label="Offers" value={metrics.totals?.offer || 0} />
      <MetricCard label="Interview Rate" value={`${metrics.interviewRate || 0}%`} />
    </div>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="bg-[#15151a] border border-[#23232a] rounded-2xl p-4">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-2xl font-semibold text-white mt-1">{value}</div>
    </div>
  );
}

function SourceHealthBar({ rows }) {
  const statusClasses = (status) => {
    if (status === "Healthy") return "text-emerald-300 bg-emerald-900/20 border-emerald-700/40";
    if (status === "Partial") return "text-amber-300 bg-amber-900/20 border-amber-700/40";
    return "text-rose-300 bg-rose-900/20 border-rose-700/40";
  };

  return (
    <div className="bg-[#15151a] border border-[#23232a] rounded-2xl p-4">
      <div className="text-xs text-gray-500 mb-3">Source Health</div>
      <div className="flex flex-wrap gap-2">
        {rows.map((row) => (
          <span key={row.source} className={`text-xs px-2 py-1 rounded border ${statusClasses(row.status)}`}>
            {row.source}: {row.status}
          </span>
        ))}
      </div>
    </div>
  );
}

function PipelineBoard({ applications, onMoveStage }) {
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

function JobCard({ job, index, saved, applied, onSave, onApply, resumeMatchEnabled, appliedDetails, onUpdateNotes, onToggleDetails, isExpanded }) {
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
      className="bg-[#15151a] border border-[#23232a] rounded-2xl p-5 hover:border-[#2f2f39] hover:-translate-y-[1px] transition-all duration-300 shadow-[0_6px_20px_rgba(0,0,0,0.25)] animate-[fadeInUp_.35s_ease_forwards]"
      style={{ animationDelay: `${Math.min(index, 8) * 40}ms` }}
    >
      <div className="flex gap-5">
        {resumeMatchEnabled && job.matchScore !== undefined && (
          <div className="w-20 h-20 rounded-full border-4 border-pink-400 flex items-center justify-center flex-shrink-0">
            <span className="text-xl font-bold text-pink-300">{job.matchScore}%</span>
          </div>
        )}

        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-11 h-11 rounded-xl bg-[#1e1e25] border border-[#2a2a33] text-pink-300 flex items-center justify-center text-sm font-semibold">
              {initial}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs bg-[#1e1e25] text-gray-300 px-2 py-1 rounded">{job.company}</span>
              {job.source && (
                <span className="text-xs bg-[#1e1e25]/60 text-gray-400 px-2 py-1 rounded">{job.source}</span>
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
            <h3 className="text-lg font-semibold text-white">{job.title}</h3>
            {!applied && (
              <span className="text-xs bg-pink-500/20 text-pink-300 px-2 py-0.5 rounded-full">
                ✨ New
              </span>
            )}
          </div>
          <p className="text-gray-400 text-sm mb-2">{job.location} · {job.employment_type || "Full-time"} · {job.postedDate || job.fetchedAt || "Recently"}</p>
          
          <div className="flex gap-2 flex-wrap">
            {job.employment_type && (
              <span className="inline-block text-xs bg-[#1e1e25] text-gray-400 px-2 py-1 rounded-full">
                {job.employment_type}
              </span>
            )}
            {job.role && (
              <span className="inline-block text-xs bg-[#1e1e25] text-gray-400 px-2 py-1 rounded-full">
                {job.role}
              </span>
            )}
            {job.requirements?.skills && job.requirements.skills.length > 0 && (
              <span className="inline-block text-xs bg-[#1e1e25] text-gray-300 px-2 py-1 rounded-full">
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
            disabled={applied}
            onClick={() => onApply(job.id, job.applyLink)}
            className={`px-4 py-2 rounded font-semibold transition-colors ${
              applied ? "bg-gray-700 text-gray-500 cursor-not-allowed" : "bg-pink-500 text-gray-900 hover:bg-pink-400 shadow-md shadow-pink-900/30"
            }`}
          >
            {applied ? "Applied ✓" : "Apply →"}
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
