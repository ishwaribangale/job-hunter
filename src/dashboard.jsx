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

/* ---------------- AI-POWERED MATCHING ---------------- */
const analyzeJobWithAI = async (job, resumeSummary) => {
  try {
    console.log("Analyzing job:", job.title); // Debug log
    
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
      const errorText = await response.text();
      console.error("API Error:", response.status, errorText);
      throw new Error(`API returned ${response.status}`);
    }

    const data = await response.json();
    console.log("API Response:", data); // Debug log
    
    const text = data.content?.find(c => c.type === "text")?.text || "{}";
    
    // Clean the text - remove markdown code blocks if present
    const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    const result = JSON.parse(cleanText);
    
    return {
      score: Math.min(100, Math.max(0, result.score || 50)),
      reason: result.reason || "AI match analysis",
      insights: result.insights || ""
    };
  } catch (error) {
    console.error("AI matching failed for job:", job.title, error);
    return {
      score: 50,
      reason: "Unable to analyze",
      insights: "AI analysis unavailable"
    };
  }
};
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

      const data = await response.json();
      const text = data.content.find(c => c.type === "text")?.text || "{}";
      const result = JSON.parse(text.trim());
      
      return {
        score: Math.min(100, Math.max(0, result.score)),
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

  /* ---------------- APPLY AI RESUME MATCH ---------------- */
const applyResumeMatch = async () => {
  if (!resumeKeywords.length) return;
  
  setAnalyzingJobs(true);
  setResumeMatchEnabled(true);

  const resumeSummary = {
    persona: resumePersona,
    seniority: resumeSeniority,
    keywords: resumeKeywords
  };

  // Analyze jobs in batches to avoid rate limits
  const batchSize = 3; // Changed from 5 to 3
  const jobsToAnalyze = [...filteredJobs];
  const analyzedJobs = [];

  for (let i = 0; i < jobsToAnalyze.length; i += batchSize) {
    const batch = jobsToAnalyze.slice(i, i + batchSize);
    
    console.log(`Analyzing batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(jobsToAnalyze.length/batchSize)}`);
    
    const results = await Promise.all(
      batch.map(job => analyzeJobWithAI(job, resumeSummary))
    );
    
    batch.forEach((job, idx) => {
      analyzedJobs.push({
        ...job,
        matchScore: results[idx].score,
        reason: results[idx].reason,
        insights: results[idx].insights
      });
    });

    // Update UI progressively
    setFilteredJobs([...analyzedJobs, ...jobsToAnalyze.slice(i + batchSize)]);
    
    // Add delay between batches to avoid rate limits
    if (i + batchSize < jobsToAnalyze.length) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  // Sort by score
  analyzedJobs.sort((a, b) => b.matchScore - a.matchScore);
  setFilteredJobs(analyzedJobs);
  setAnalyzingJobs(false);
};

    // Analyze jobs in batches to avoid rate limits
    const batchSize = 5;
    const jobsToAnalyze = [...filteredJobs];
    const analyzedJobs = [];

    for (let i = 0; i < jobsToAnalyze.length; i += batchSize) {
      const batch = jobsToAnalyze.slice(i, i + batchSize);
      const results = await Promise.all(
        batch.map(job => analyzeJobWithAI(job, resumeSummary))
      );
      
      batch.forEach((job, idx) => {
        analyzedJobs.push({
          ...job,
          matchScore: results[idx].score,
          reason: results[idx].reason,
          insights: results[idx].insights
        });
      });

      // Update UI progressively
      setFilteredJobs([...analyzedJobs, ...jobsToAnalyze.slice(i + batchSize)]);
    }

    // Sort by score
    analyzedJobs.sort((a, b) => b.matchScore - a.matchScore);
    setFilteredJobs(analyzedJobs);
    setAnalyzingJobs(false);
  };

  const clearResume = () => {
    setResumeText("");
    setResumeKeywords([]);
    setResumePersona(null);
    setResumeSeniority("mid");
    setResumeMatchEnabled(false);
    setFilteredJobs(jobs); // Reset to original
  };

  /* ---------------- APPLY FILTERS ---------------- */
  React.useEffect(() => {
    if (resumeMatchEnabled) return; // Don't filter when AI matching is active

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
              <h3 className="font-semibold text-sky-400 mb-2">🤖 AI Resume Matcher</h3>

              {!resumeText ? (
                <div>
                  <input 
                    type="file" 
                    accept=".pdf" 
                    onChange={handleResumeUpload}
                    className="text-sm text-gray-400"
                    disabled={uploadingResume}
                  />
                  {uploadingResume && (
                    <div className="text-xs text-gray-500 mt-2">Processing PDF...</div>
                  )}
                </div>
              ) : (
                <>
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
                    {resumeKeywords.slice(0, 8).map((k) => (
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
                      disabled={analyzingJobs}
                      className="bg-sky-600 px-3 py-1 rounded text-sm hover:bg-sky-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {analyzingJobs ? "Analyzing..." : "🚀 AI Match"}
                    </button>
                    <button
                      onClick={clearResume}
                      className="bg-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-600"
                    >
                      Clear
                    </button>
                  </div>

                  {analyzingJobs && (
                    <div className="mt-3 text-xs text-gray-400">
                      AI is analyzing each job against your resume...
                    </div>
                  )}
                </>
              )}
            </div>

            {/* FILTERS */}
            {!resumeMatchEnabled && (
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
            )}
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
              {analyzingJobs ? "Analyzing..." : `${filteredJobs.length} jobs analyzed`}
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

                  {/* AI Insights */}
                  {resumeMatchEnabled && job.insights && (
                    <div className="mt-3 text-sm text-gray-300 italic">
                      "{job.insights}"
                    </div>
                  )}
                </div>

                {/* Match Display */}
                <div className="text-right ml-4 flex flex-col items-end">
                  {resumeMatchEnabled && job.matchScore !== undefined && (
                    <div className="mb-1">
                      <div className={`font-bold text-2xl ${
                        job.matchScore >= 75 ? 'text-green-400' :
                        job.matchScore >= 60 ? 'text-sky-400' :
                        job.matchScore >= 45 ? 'text-yellow-400' :
                        'text-orange-400'
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
