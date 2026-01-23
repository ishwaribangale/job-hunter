import React from "react";

export default function App() {
  const [jobs, setJobs] = React.useState([]);
  const [filteredJobs, setFilteredJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  const [searchQuery, setSearchQuery] = React.useState("");
  const [companyQuery, setCompanyQuery] = React.useState("");
  const [selectedSource, setSelectedSource] = React.useState("all");
  const [selectedRole, setSelectedRole] = React.useState("all");
  const [selectedLocation, setSelectedLocation] = React.useState("all");
  const [minScore, setMinScore] = React.useState(0);

  const [resumeText, setResumeText] = React.useState("");
  const [resumeKeywords, setResumeKeywords] = React.useState([]);
  const [resumePersona, setResumePersona] = React.useState(null);
  const [resumeSeniority, setResumeSeniority] = React.useState("mid");
  const [resumeMatchEnabled, setResumeMatchEnabled] = React.useState(false);
  const [uploadingResume, setUploadingResume] = React.useState(false);

  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  /* ---------------- FETCH JOBS ---------------- */
  React.useEffect(() => {
    fetch(
      "https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json"
    )
      .then((res) => res.json())
      .then((data) => {
        setJobs(data);
        setFilteredJobs(data);
      })
      .finally(() => setLoading(false));
  }, []);

  /* ---------------- FILTER VALUES ---------------- */
  const sources = React.useMemo(
    () => [...new Set(jobs.map((j) => j?.source).filter(Boolean))],
    [jobs]
  );
  const roles = React.useMemo(
    () => [...new Set(jobs.map((j) => j?.role).filter(Boolean))],
    [jobs]
  );
  const locations = React.useMemo(
    () => [...new Set(jobs.map((j) => j?.location).filter(Boolean))],
    [jobs]
  );

  /* ---------------- RESUME HELPERS ---------------- */
  const extractKeywords = (text) => {
    const lower = text.toLowerCase();

    const PERSONAS = {
      pm: [
        "product manager",
        "product management",
        "roadmap",
        "stakeholder",
        "user stories",
        "requirements",
        "prds",
        "backlog",
        "prioritization",
        "go-to-market",
        "g2m",
        "metrics",
        "kpis",
        "experiments",
        "a/b testing",
        "customer discovery",
        "product strategy",
        "growth",
        "analytics",
        "sql",
        "jira",
        "confluence",
        "figma"
      ],
      engineer: [
        "javascript",
        "react",
        "node",
        "typescript",
        "python",
        "java",
        "sql",
        "docker",
        "kubernetes",
        "aws",
        "backend",
        "frontend",
        "fullstack",
        "api",
        "microservices",
        "system design",
        "devops",
        "software engineer",
        "developer"
      ],
      data: [
        "data analysis",
        "machine learning",
        "ai",
        "statistics",
        "pandas",
        "numpy",
        "sql",
        "etl",
        "dashboard",
        "modeling",
        "data scientist",
        "analyst"
      ]
    };

    const SENIORITY_KEYWORDS = {
      junior: ["junior", "entry", "associate", "jr", "graduate", "intern"],
      mid: ["mid", "intermediate", "ii", "2"],
      senior: ["senior", "sr", "lead", "staff", "principal", "architect", "director"]
    };

    // 1️⃣ Detect persona by signal strength
    const personaScores = Object.entries(PERSONAS).map(([role, words]) => {
      const score = words.filter((w) => lower.includes(w)).length;
      return { role, score };
    });

    personaScores.sort((a, b) => b.score - a.score);
    const detectedPersona = personaScores[0]?.role || "engineer";

    // 2️⃣ Extract only persona-relevant keywords
    const extracted = PERSONAS[detectedPersona]
      .filter((kw) => lower.includes(kw))
      .slice(0, 15);

    // 3️⃣ Detect seniority
    const seniority = SENIORITY_KEYWORDS.senior.some(s => lower.includes(s))
      ? "senior"
      : SENIORITY_KEYWORDS.junior.some(s => lower.includes(s))
      ? "junior"
      : "mid";

    return {
      persona: detectedPersona,
      keywords: [...new Set(extracted)],
      seniority
    };
  };

  // ✅ NEW: Signal-based matching algorithm
  const calculateMatchScore = (job, keywords, persona, resumeSeniority) => {
    const jobText = `${job.title} ${job.role || ""}`.toLowerCase();
    
    // 1️⃣ PERSONA FIT (0-40 points) - Is this even the right type of role?
    let personaScore = 0;
    let personaFit = "unrelated";
    const PERSONA_SIGNALS = {
      pm: ["product", "manager", "pm", "management"],
      engineer: ["engineer", "developer", "software", "frontend", "backend", "fullstack", "swe"],
      data: ["data", "analyst", "analytics", "scientist", "ml", "machine learning"]
    };
    
    const signals = PERSONA_SIGNALS[persona] || [];
    const hasStrongSignal = signals.some(s => jobText.includes(s));
    
    if (hasStrongSignal) {
      personaScore = 40;
      personaFit = "strong";
    } else {
      const hasAnySignal = Object.values(PERSONA_SIGNALS)
        .flat()
        .some(s => jobText.includes(s));
      if (hasAnySignal) {
        personaScore = 15;
        personaFit = "adjacent";
      }
    }
    
    // 2️⃣ SKILL MATCHES (0-40 points) - Do your skills appear?
    const matchedKeywords = keywords.filter(k => jobText.includes(k));
    const skillScore = Math.min(matchedKeywords.length * 8, 40);
    const skillLevel = skillScore >= 32 ? "strong" : skillScore >= 16 ? "good" : skillScore > 0 ? "some" : "none";
    
    // 3️⃣ SENIORITY ALIGNMENT (0-20 points) - Does level match?
    let seniorityScore = 10;
    let seniorityFit = "neutral";
    const SENIORITY_KEYWORDS = {
      junior: ["junior", "entry", "associate", "jr", "graduate", "intern"],
      mid: ["mid", "intermediate", "ii", "2"],
      senior: ["senior", "sr", "lead", "staff", "principal", "architect"]
    };
    
    const jobSeniority = SENIORITY_KEYWORDS.senior.some(s => jobText.includes(s))
      ? "senior"
      : SENIORITY_KEYWORDS.junior.some(s => jobText.includes(s))
      ? "junior"
      : "mid";
    
    if (resumeSeniority === jobSeniority) {
      seniorityScore = 20;
      seniorityFit = "perfect";
    } else if (
      (resumeSeniority === "mid" && jobSeniority !== "junior") ||
      (resumeSeniority === "senior" && jobSeniority === "mid")
    ) {
      seniorityScore = 10;
      seniorityFit = "stretch";
    } else {
      seniorityScore = 0;
      seniorityFit = "mismatch";
    }
    
    // Generate human-readable reason
    const generateReason = () => {
      const parts = [];
      
      if (personaFit === "strong") parts.push("Right role");
      else if (personaFit === "adjacent") parts.push("Adjacent role");
      
      if (skillLevel === "strong") parts.push("strong skills match");
      else if (skillLevel === "good") parts.push("good skills match");
      else if (skillLevel === "some") parts.push("some skills match");
      
      if (seniorityFit === "perfect") parts.push("perfect level");
      else if (seniorityFit === "stretch") parts.push("stretch level");
      
      return parts.join(", ") || "Possible fit";
    };
    
    const totalScore = personaScore + skillScore + seniorityScore;
    
    return {
      score: Math.round(totalScore),
      reason: generateReason(),
      breakdown: {
        persona: personaScore,
        skills: skillScore,
        seniority: seniorityScore,
        matchedKeywords
      }
    };
  };

  /* ---------------- RESUME UPLOAD ---------------- */
  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || file.type !== "application/pdf") return;
    if (!window.pdfjsLib) return alert("PDF.js not loaded");

    setUploadingResume(true);
    try {
      const buffer = await file.arrayBuffer();
      const pdf = await window.pdfjsLib.getDocument({ data: buffer }).promise;
      let text = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map((i) => i.str).join(" ");
      }

      const result = extractKeywords(text);
      setResumeText(text);
      setResumeKeywords(result.keywords);
      setResumePersona(result.persona);
      setResumeSeniority(result.seniority);
    } finally {
      setUploadingResume(false);
    }
  };

  /* ---------------- APPLY RESUME MATCH ---------------- */
  const applyResumeMatch = () => {
    if (!resumeKeywords.length) return;
    setResumeMatchEnabled(true);
  };

  const clearResume = () => {
    setResumeText("");
    setResumeKeywords([]);
    setResumePersona(null);
    setResumeSeniority("mid");
    setResumeMatchEnabled(false);
  };

  /* ---------------- APPLY FILTERS ---------------- */
  React.useEffect(() => {
    let data = [...jobs];

    if (searchQuery)
      data = data.filter(
        (j) =>
          j.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          j.company?.toLowerCase().includes(searchQuery.toLowerCase())
      );

    if (companyQuery)
      data = data.filter((j) =>
        j.company?.toLowerCase().includes(companyQuery.toLowerCase())
      );

    if (selectedSource !== "all")
      data = data.filter((j) => j.source === selectedSource);

    if (selectedRole !== "all")
      data = data.filter((j) => j.role === selectedRole);

    if (selectedLocation !== "all")
      data = data.filter((j) => j.location === selectedLocation);

    if (minScore > 0)
      data = data.filter((j) => (j.score || 0) >= minScore);

    // ✅ NEW: Improved matching with reason
    if (resumeMatchEnabled && resumeKeywords.length) {
      data = data
        .map((j) => {
          const result = calculateMatchScore(j, resumeKeywords, resumePersona, resumeSeniority);
          return {
            ...j,
            matchScore: result.score,
            reason: result.reason,
            matchBreakdown: result.breakdown
          };
        })
        .filter((j) => j.matchScore >= 30) // Only show reasonable matches
        .sort((a, b) => b.matchScore - a.matchScore);
    }

    setFilteredJobs(data);
  }, [
    jobs,
    searchQuery,
    companyQuery,
    selectedSource,
    selectedRole,
    selectedLocation,
    minScore,
    resumeMatchEnabled,
    resumeKeywords,
    resumePersona,
    resumeSeniority
  ]);

  if (loading) {
    return <div className="p-10 text-center text-gray-500">Loading jobs…</div>;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      {/* SIDEBAR */}
      <div
        className={`${
          sidebarOpen ? "w-80" : "w-16"
        } bg-gray-900 border-r border-gray-800 transition-all`}
      >
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-4 text-sky-400"
        >
          ☰
        </button>

        {sidebarOpen && (
          <div className="p-4 space-y-8">
            {/* RESUME MATCHER */}
            <div>
              <h3 className="font-semibold text-sky-400 mb-2">Resume Matcher</h3>

              {!resumeText ? (
                <div>
                  <input 
                    type="file" 
                    accept=".pdf" 
                    onChange={handleResumeUpload}
                    className="text-sm text-gray-400"
                  />
                  {uploadingResume && (
                    <div className="text-xs text-gray-500 mt-2">Processing...</div>
                  )}
                </div>
              ) : (
                <>
                  {/* ✅ NEW: Show both persona and seniority */}
                  <div className="flex gap-2 mb-2">
                    {resumePersona && (
                      <div className="inline-block px-2 py-1 text-xs font-semibold rounded bg-sky-800/40 text-sky-300">
                        {resumePersona.toUpperCase()}
                      </div>
                    )}
                    {resumeSeniority && (
                      <div className="inline-block px-2 py-1 text-xs font-semibold rounded bg-purple-800/40 text-purple-300">
                        {resumeSeniority.toUpperCase()}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 mt-2">
                    {resumeKeywords.map((k) => (
                      <span
                        key={k}
                        className="px-2 py-1 bg-sky-900/40 text-sky-300 text-xs rounded"
                      >
                        {k}
                      </span>
                    ))}
                  </div>

                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={applyResumeMatch}
                      className="bg-sky-600 px-3 py-1 rounded text-sm hover:bg-sky-700"
                    >
                      Apply Match
                    </button>
                    <button
                      onClick={clearResume}
                      className="bg-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-600"
                    >
                      Clear
                    </button>
                  </div>
                </>
              )}
            </div>

            {/* FILTERS */}
            <div>
              <h3 className="font-semibold text-sky-400 mb-2">Filters</h3>

              <input
                placeholder="Search title or company"
                className="w-full mb-2 p-2 bg-gray-800 rounded text-sm"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />

              <input
                placeholder="Company"
                className="w-full mb-2 p-2 bg-gray-800 rounded text-sm"
                value={companyQuery}
                onChange={(e) => setCompanyQuery(e.target.value)}
              />

              <select
                className="w-full mb-2 p-2 bg-gray-800 rounded text-sm"
                value={selectedSource}
                onChange={(e) => setSelectedSource(e.target.value)}
              >
                <option value="all">All Sources</option>
                {sources.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>

              <select
                className="w-full mb-2 p-2 bg-gray-800 rounded text-sm"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
              >
                <option value="all">All Roles</option>
                {roles.map((r) => (
                  <option key={r}>{r}</option>
                ))}
              </select>

              <select
                className="w-full mb-2 p-2 bg-gray-800 rounded text-sm"
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
              >
                <option value="all">All Locations</option>
                {locations.map((l) => (
                  <option key={l}>{l}</option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 p-6 space-y-4 overflow-y-auto">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-sky-400">
            Job Intelligence Dashboard
          </h1>
          {resumeMatchEnabled && (
            <div className="text-sm text-gray-400">
              Showing {filteredJobs.length} matches (≥30%)
            </div>
          )}
        </div>

        {filteredJobs.length === 0 ? (
          <div className="text-center text-gray-500 py-10">
            No jobs found matching your criteria
          </div>
        ) : (
          filteredJobs.map((job) => (
            <div
              key={job.id}
              className="bg-gray-900 border border-gray-800 p-5 rounded-lg hover:border-gray-700 transition-colors"
            >
              <div className="flex justify-between">
                <div className="flex-1">
                  <h2 className="font-semibold text-lg">{job.title}</h2>
                  <p className="text-gray-400">{job.company}</p>

                  <div className="flex flex-wrap gap-2 mt-2 text-xs">
                    <span className="bg-gray-800 px-2 py-1 rounded">
                      {job.location}
                    </span>
                    {job.role && (
                      <span className="bg-gray-800 px-2 py-1 rounded">
                        {job.role}
                      </span>
                    )}
                    <span className="bg-gray-800 px-2 py-1 rounded">
                      {job.source}
                    </span>
                  </div>

                  {/* ✅ NEW: Show matched keywords */}
                  {resumeMatchEnabled && job.matchBreakdown?.matchedKeywords?.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {job.matchBreakdown.matchedKeywords.slice(0, 5).map((kw) => (
                        <span
                          key={kw}
                          className="px-2 py-0.5 bg-green-900/30 text-green-400 text-xs rounded border border-green-800/50"
                        >
                          {kw}
                        </span>
                      ))}
                      {job.matchBreakdown.matchedKeywords.length > 5 && (
                        <span className="text-xs text-gray-500 self-center">
                          +{job.matchBreakdown.matchedKeywords.length - 5} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* ✅ NEW: Enhanced match display with reason */}
                <div className="text-right ml-4 flex flex-col items-end">
                  {resumeMatchEnabled && job.matchScore > 0 && (
                    <div className="mb-1">
                      <div className={`font-bold text-2xl ${
                        job.matchScore >= 70 ? 'text-green-400' :
                        job.matchScore >= 50 ? 'text-sky-400' :
                        'text-yellow-400'
                      }`}>
                        {job.matchScore}%
                      </div>
                      <div className="text-xs text-gray-300 mt-1 max-w-[180px] text-right">
                        {job.reason || "Match found"}
                      </div>
                    </div>
                  )}

                  <a
                    href={job.applyLink}
                    target="_blank"
                    rel="noreferrer"
                    className="bg-sky-600 px-4 py-2 rounded hover:bg-sky-700 transition-colors text-sm"
                  >
                    Apply →
                  </a>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
