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

  const [resumeText, setResumeText] = React.useState("");
  const [resumeKeywords, setResumeKeywords] = React.useState([]);
  const [resumePersona, setResumePersona] = React.useState(null);
  const [resumeSeniority, setResumeSeniority] = React.useState("mid");
  const [resumeMatchEnabled, setResumeMatchEnabled] = React.useState(false);
  const [uploadingResume, setUploadingResume] = React.useState(false);
  const [analyzingJobs, setAnalyzingJobs] = React.useState(false);

  const [activeSection, setActiveSection] = React.useState("all-jobs");
  const [savedJobs, setSavedJobs] = React.useState([]);
  const [appliedJobs, setAppliedJobs] = React.useState([]);

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

  /* Quick Filter Options */
  const quickFilters = [
    { label: "Remote Only", key: "remote", filter: (j) => j.location?.toLowerCase().includes("remote") },
    { label: "Full-time", key: "fulltime", filter: (j) => j.employment_type === "Full-time" || j.title?.toLowerCase().includes("full-time") },
    { label: "Engineering", key: "engineering", filter: (j) => j.role === "Engineering" || j.title?.toLowerCase().includes("engineer") }
  ];

  /* Top Matches Count */
  const topMatchesCount = React.useMemo(() => {
    return filteredJobs.filter(j => j.matchScore >= 75).length;
  }, [filteredJobs]);

  /* ---------------- RESUME HELPERS ---------------- */
  const extractKeywords = (text) => {
    const lower = text.toLowerCase();

    const PERSONAS = {
      pm: ["product manager", "product management", "roadmap", "stakeholder", "user stories", "requirements", "prds", "backlog", "prioritization", "go-to-market", "g2m", "metrics", "kpis", "experiments", "a/b testing", "customer discovery", "product strategy", "growth", "analytics", "sql", "jira", "confluence", "figma"],
      engineer: ["javascript", "react", "node", "typescript", "python", "java", "sql", "docker", "kubernetes", "aws", "backend", "frontend", "fullstack", "api", "microservices", "system design", "devops", "software engineer", "developer"],
      data: ["data analysis", "machine learning", "ai", "statistics", "pandas", "numpy", "sql", "etl", "dashboard", "modeling", "data scientist", "analyst"]
    };

    const SENIORITY_KEYWORDS = {
      junior: ["junior", "entry", "associate", "jr", "graduate", "intern"],
      mid: ["mid", "intermediate", "ii", "2"],
      senior: ["senior", "sr", "lead", "staff", "principal", "architect", "director"]
    };

    const personaScores = Object.entries(PERSONAS).map(([role, words]) => {
      const score = words.filter((w) => lower.includes(w)).length;
      return { role, score };
    });

    personaScores.sort((a, b) => b.score - a.score);
    const detectedPersona = personaScores[0]?.role || "engineer";

    const extracted = PERSONAS[detectedPersona]
      .filter((kw) => lower.includes(kw))
      .slice(0, 15);

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

  /* ---------------- KEYWORD-BASED MATCHING (Fast) ---------------- */
  const calculateKeywordMatch = (job, resumeData) => {
    let score = 50;
    
    const jobReqs = job.requirements || {};
    const jobSkills = jobReqs.skills || [];
    
    if (jobSkills.length > 0) {
      const matchedSkills = jobSkills.filter(skill => 
        resumeData.keywords.some(kw => kw.toLowerCase().includes(skill.toLowerCase()))
      );
      score += (matchedSkills.length / jobSkills.length) * 40;
    }
    
    const titleLower = job.title.toLowerCase();
    
    if (resumeData.persona === 'pm' && titleLower.includes('product')) score += 20;
    else if (resumeData.persona === 'engineer' && (titleLower.includes('engineer') || titleLower.includes('developer'))) score += 20;
    else if (resumeData.persona === 'data' && titleLower.includes('data')) score += 20;
    else if (resumeData.keywords.some(kw => titleLower.includes(kw.toLowerCase()))) score += 10;
    
    if (resumeData.seniority === 'senior' && (titleLower.includes('senior') || titleLower.includes('lead'))) score += 10;
    else if (resumeData.seniority === 'junior' && (titleLower.includes('junior') || titleLower.includes('entry'))) score += 10;
    else if (resumeData.seniority === 'mid') score += 5;
    
    return Math.min(100, Math.max(0, Math.round(score)));
  };

  /* ---------------- AI-POWERED MATCHING (for top jobs only) ---------------- */
  const analyzeJobWithAI = async (job, resumeSummary) => {
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [{
            role: "user",
            content: `You are a job matching expert. Analyze this job against the candidate's resume.

RESUME SUMMARY:
- Persona: ${resumeSummary.persona}
- Seniority: ${resumeSummary.seniority}
- Key Skills: ${resumeSummary.keywords.join(", ")}

JOB DETAILS:
- Title: ${job.title}
- Company: ${job.company}
- Role Category: ${job.role || "Not specified"}
- Location: ${job.location}

Respond ONLY with a JSON object (no markdown, no backticks):
{
  "score": <number 0-100>,
  "reason": "<5-7 word explanation>",
  "insights": "<1 sentence about why this match works or doesn't>"
}

Consider:
1. Does the job title align with their persona and seniority?
2. For PM roles: look for product area fit (AI, Safety, Growth, Tools, etc)
3. For similar seniority levels, differentiate based on role specificity
4. Company reputation and role scope matter
5. Give varied scores - don't rate everything the same!`
          }]
        })
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const data = await response.json();
      const text = data.content?.find(c => c.type === "text")?.text || "{}";
      const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      const result = JSON.parse(cleanText);
      
      return {
        score: Math.min(100, Math.max(0, result.score || 50)),
        reason: result.reason || "AI match analysis",
        insights: result.insights || ""
      };
    } catch (error) {
      console.error("AI matching failed:", error);
      return {
        score: 50,
        reason: "Unable to analyze",
        insights: "AI analysis unavailable"
      };
    }
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

  /* ---------------- HYBRID MATCHING: Keyword + AI ---------------- */
  const applyResumeMatch = async () => {
    if (!resumeKeywords.length) return;
    
    setAnalyzingJobs(true);
    setResumeMatchEnabled(true);

    const resumeSummary = {
      persona: resumePersona,
      seniority: resumeSeniority,
      keywords: resumeKeywords
    };

    const keywordScored = filteredJobs.map(job => ({
      ...job,
      matchScore: calculateKeywordMatch(job, resumeSummary),
      reason: "Keyword match",
      insights: "Based on resume keywords and job requirements"
    }));

    keywordScored.sort((a, b) => b.matchScore - a.matchScore);
    setFilteredJobs(keywordScored);

    const TOP_JOBS_TO_ANALYZE = 20;
    const topJobs = keywordScored.slice(0, TOP_JOBS_TO_ANALYZE);
    const restJobs = keywordScored.slice(TOP_JOBS_TO_ANALYZE);

    const aiAnalyzed = [];
    
    for (let i = 0; i < topJobs.length; i++) {
      const job = topJobs[i];
      const aiResult = await analyzeJobWithAI(job, resumeSummary);
      
      aiAnalyzed.push({
        ...job,
        matchScore: aiResult.score,
        reason: aiResult.reason,
        insights: aiResult.insights
      });

      setFilteredJobs([...aiAnalyzed, ...topJobs.slice(i + 1), ...restJobs]);
      
      if (i < topJobs.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    const finalJobs = [...aiAnalyzed, ...restJobs];
    finalJobs.sort((a, b) => b.matchScore - a.matchScore);
    
    setFilteredJobs(finalJobs);
    setAnalyzingJobs(false);
  };

  const clearResume = () => {
    setResumeText("");
    setResumeKeywords([]);
    setResumePersona(null);
    setResumeSeniority("mid");
    setResumeMatchEnabled(false);
    setFilteredJobs(jobs);
  };

  /* Save/Apply Job */
  const toggleSaveJob = (jobId) => {
    setSavedJobs(prev => 
      prev.includes(jobId) ? prev.filter(id => id !== jobId) : [...prev, jobId]
    );
  };

  const markJobAsApplied = (jobId) => {
    setAppliedJobs(prev => 
      prev.includes(jobId) ? prev : [...prev, jobId]
    );
  };

  /* Get Display Jobs Based on Section */
  const getDisplayJobs = () => {
    switch(activeSection) {
      case "top-matches":
        return filteredJobs.filter(j => j.matchScore >= 75);
      case "saved":
        return filteredJobs.filter(j => savedJobs.includes(j.id));
      case "applied":
        return filteredJobs.filter(j => appliedJobs.includes(j.id));
      default:
        return filteredJobs;
    }
  };

  const displayJobs = getDisplayJobs();

  /* Get Score Color */
  const getScoreColor = (score) => {
    if (score >= 75) return "text-green-400 border-green-400";
    if (score >= 60) return "text-cyan-400 border-cyan-400";
    if (score >= 45) return "text-yellow-400 border-yellow-400";
    return "text-orange-400 border-orange-400";
  };

  /* Apply Filters */
  React.useEffect(() => {
    if (resumeMatchEnabled) return;

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

    setFilteredJobs(data);
  }, [
    jobs,
    searchQuery,
    companyQuery,
    selectedSource,
    selectedRole,
    selectedLocation,
    resumeMatchEnabled
  ]);

  if (loading) {
    return <div className="p-10 text-center text-gray-500">Loading jobs…</div>;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      {/* SIDEBAR */}
      <div className="w-64 bg-gray-900 border-r border-gray-800 overflow-y-auto">
        {/* Logo */}
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-cyan-400 flex items-center justify-center text-gray-900 font-bold">
              📦
            </div>
            <h1 className="text-xl font-bold">JobFlow</h1>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          <button
            onClick={() => setActiveSection("all-jobs")}
            className={`w-full text-left px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              activeSection === "all-jobs"
                ? "bg-cyan-900/30 text-cyan-400"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            📦 All Jobs
          </button>

          <button
            onClick={() => setActiveSection("top-matches")}
            className={`w-full text-left px-4 py-2 rounded-lg flex items-center gap-2 justify-between transition-colors ${
              activeSection === "top-matches"
                ? "bg-cyan-900/30 text-cyan-400"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            <span>📈 Top Matches</span>
            {topMatchesCount > 0 && (
              <span className="bg-cyan-400 text-gray-900 text-xs font-bold px-2 py-1 rounded-full">
                {topMatchesCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveSection("saved")}
            className={`w-full text-left px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              activeSection === "saved"
                ? "bg-cyan-900/30 text-cyan-400"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            🔖 Saved
          </button>

          <button
            onClick={() => setActiveSection("applied")}
            className={`w-full text-left px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              activeSection === "applied"
                ? "bg-cyan-900/30 text-cyan-400"
                : "text-gray-400 hover:text-gray-300"
            }`}
          >
            ⏱️ Applied
          </button>
        </nav>

        {/* Quick Filters */}
        {activeSection === "all-jobs" && (
          <div className="p-4 border-t border-gray-800">
            <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">Quick Filters</h3>
            <div className="space-y-2">
              {quickFilters.map((qf) => (
                <button
                  key={qf.key}
                  onClick={() => {
                    const filtered = jobs.filter(qf.filter);
                    setFilteredJobs(filtered);
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
                >
                  {qf.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Resume Matcher */}
        <div className="p-4 border-t border-gray-800">
          <div className="bg-cyan-900/20 border border-cyan-900/40 rounded-lg p-4">
            <h3 className="font-semibold text-cyan-400 mb-2 flex items-center gap-2">
              ✨ See Your Fit
            </h3>
            <p className="text-xs text-gray-400 mb-3">Upload your resume to discover roles</p>

            {!resumeText ? (
              <div>
                <label className="block">
                  <input 
                    type="file" 
                    accept=".pdf" 
                    onChange={handleResumeUpload}
                    className="text-xs text-gray-400 cursor-pointer"
                    disabled={uploadingResume}
                  />
                </label>
                {uploadingResume && (
                  <div className="text-xs text-gray-500 mt-2">⏳ Processing PDF...</div>
                )}
              </div>
            ) : (
              <>
                <div className="flex flex-wrap gap-2 mb-3">
                  {resumePersona && (
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-cyan-800/40 text-cyan-300">
                      {resumePersona.toUpperCase()}
                    </span>
                  )}
                  {resumeSeniority && (
                    <span className="px-2 py-1 text-xs font-semibold rounded bg-purple-800/40 text-purple-300">
                      {resumeSeniority.toUpperCase()}
                    </span>
                  )}
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={applyResumeMatch}
                    disabled={analyzingJobs}
                    className="flex-1 bg-cyan-600 px-3 py-1 rounded text-xs font-semibold hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {analyzingJobs ? "Analyzing..." : "🚀 Match"}
                  </button>
                  <button
                    onClick={clearResume}
                    className="flex-1 bg-gray-700 px-3 py-1 rounded text-xs hover:bg-gray-600 transition-colors"
                  >
                    Clear
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-900 border-b border-gray-800 px-6 py-4">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-cyan-400">Job Intelligence</h1>
              <p className="text-gray-400 text-sm mt-1">
                {resumeMatchEnabled 
                  ? `${displayJobs.length} roles matched to your profile` 
                  : `${displayJobs.length} opportunities available`}
              </p>
            </div>
            {resumeMatchEnabled && (
              <div className="px-3 py-1 bg-cyan-900/30 border border-cyan-900/50 rounded-lg text-cyan-400 text-sm flex items-center gap-2">
                ✨ AI Matching Active
              </div>
            )}
          </div>

          {/* Search & Filters */}
          {!resumeMatchEnabled && (
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <input
                  placeholder="Search roles, companies..."
                  className="w-full px-4 py-2 bg-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 text-gray-100 placeholder-gray-500"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <span className="absolute right-3 top-2.5 text-gray-500">🔍</span>
              </div>

              <select
                className="px-4 py-2 bg-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 text-gray-100"
                value={selectedSource}
                onChange={(e) => setSelectedSource(e.target.value)}
              >
                <option value="all">All Companies</option>
                {sources.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>

              <select
                className="px-4 py-2 bg-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 text-gray-100"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
              >
                <option value="all">All Roles</option>
                {roles.map((r) => (
                  <option key={r}>{r}</option>
                ))}
              </select>

              <select
                className="px-4 py-2 bg-gray-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 text-gray-100"
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
              >
                <option value="all">All Locations</option>
                {locations.map((l) => (
                  <option key={l}>{l}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Jobs List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {displayJobs.length === 0 ? (
            <div className="text-center text-gray-500 py-10">
              <p className="text-lg">No jobs found</p>
              <p className="text-sm mt-1">Try adjusting your filters or uploading your resume</p>
            </div>
          ) : (
            displayJobs.map((job) => (
              <div
                key={job.id}
                className="bg-gray-900 border border-gray-800 rounded-lg p-5 hover:border-gray-700 transition-colors hover:bg-gray-800/50"
              >
                <div className="flex gap-4">
                  {/* Match Score Circle */}
                  {resumeMatchEnabled && job.matchScore !== undefined && (
                    <div className={`flex-shrink-0 w-24 h-24 rounded-full border-4 ${getScoreColor(job.matchScore)} flex items-center justify-center`}>
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${getScoreColor(job.matchScore)}`}>
                          {job.matchScore}
                        </div>
                        <div className="text-xs text-gray-400">match</div>
                      </div>
                    </div>
                  )}

                  {/* Job Content */}
                  <div className="flex-1">
                    <div className="flex items-start gap-2 mb-2">
                      <h2 className="text-lg font-semibold">{job.title}</h2>
                      {!appliedJobs.includes(job.id) && (
                        <span className="px-2 py-0.5 text-xs font-semibold bg-cyan-900/40 text-cyan-300 rounded">
                          ✨ New
                        </span>
                      )}
                    </div>

                    <p className="text-gray-400 text-sm mb-3 flex items-center gap-2">
                      <span>🏢 {job.company}</span>
                      <span>📍 {job.location}</span>
                    </p>

                    <div className="flex flex-wrap gap-2 mb-3">
                      {job.role && (
                        <span className="text-xs px-2.5 py-1 bg-gray-800 rounded text-gray-300">
                          {job.role}
                        </span>
                      )}
                      {job.employment_type && (
                        <span className="text-xs px-2.5 py-1 bg-gray-800 rounded text-gray-300">
                          {job.employment_type}
                        </span>
                      )}
                      {job.source && (
                        <span className="text-xs px-2.5 py-1 bg-gray-800 rounded text-gray-300">
                          {job.source}
                        </span>
                      )}
                    </div>

                    {/* AI Insights */}
                    {resumeMatchEnabled && job.insights && (
                      <p className="text-sm text-gray-300 italic">
                        💡 {job.insights}
                      </p>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex-shrink-0 flex gap-2">
                    <button
                      onClick={() => toggleSaveJob(job.id)}
                      className={`p-2 rounded transition-colors ${
                        savedJobs.includes(job.id)
                          ? "bg-yellow-900/40 text-yellow-400"
                          : "bg-gray-800 text-gray-400 hover:text-gray-300"
                      }`}
                      title="Save job"
                    >
                      🔖
                    </button>

                    <a
                      href={job.applyLink}
                      target="_blank"
                      rel="noreferrer"
                      onClick={() => markJobAsApplied(job.id)}
                      className="px-4 py-2 bg-cyan-500 text-gray-900 font-semibold rounded-lg hover:bg-cyan-400 transition-colors flex items-center gap-2"
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
    </div>
  );
}
