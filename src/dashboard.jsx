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

  const [activeSection, setActiveSection] = React.useState("all-jobs");
  const [savedJobs, setSavedJobs] = React.useState([]);
  const [appliedJobs, setAppliedJobs] = React.useState([]);
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
        "product manager","roadmap","stakeholder","user stories",
        "prioritization","metrics","kpis","sql","jira","figma"
      ],
      engineer: [
        "javascript","react","node","typescript","python","java",
        "go","docker","kubernetes","aws","api","graphql"
      ],
      data: [
        "data","analytics","machine learning","sql","python",
        "pandas","numpy","tableau"
      ]
    };

    const SENIORITY_KEYWORDS = {
      junior: ["junior","entry","intern"],
      mid: ["mid","ii"],
      senior: ["senior","lead","staff","principal"]
    };

    const personaScores = Object.entries(PERSONAS).map(([role, words]) => ({
      role,
      score: words.filter(w => lower.includes(w)).length
    }));

    personaScores.sort((a,b) => b.score - a.score);

    const persona = personaScores[0]?.role || "engineer";

    const keywords = PERSONAS[persona].filter(k => lower.includes(k)).slice(0,15);

    const seniority =
      SENIORITY_KEYWORDS.senior.some(k => lower.includes(k)) ? "senior" :
      SENIORITY_KEYWORDS.junior.some(k => lower.includes(k)) ? "junior" :
      "mid";

    return {
      persona,
      seniority,
      keywords: [...new Set(keywords)]
    };
  };

  /* ---------------- MATCHING LOGIC ---------------- */
  const calculateKeywordMatch = (job, resume) => {
    let score = 0;
    const reqs = job.requirements || {};
    const skills = reqs.skills || [];
    const experience = reqs.experience_years || 0;
    const title = job.title.toLowerCase();

    // Title + persona
    if (resume.persona === "pm" && title.includes("product")) score += 20;
    if (resume.persona === "engineer" && (title.includes("engineer") || title.includes("developer"))) score += 20;
    if (resume.persona === "data" && title.includes("data")) score += 20;

    // Seniority
    if (resume.seniority === "senior" && title.includes("senior")) score += 10;
    if (resume.seniority === "junior" && title.includes("junior")) score += 10;
    if (resume.seniority === "mid" && !title.includes("senior")) score += 5;

    // Skills
    let matchedSkills = [];
    if (skills.length) {
      matchedSkills = skills.filter(s =>
        resume.keywords.some(k =>
          k.includes(s.toLowerCase()) ||
          s.toLowerCase().includes(k)
        )
      );
      score += (matchedSkills.length / skills.length) * 40;
    }

    // Experience
    if (experience) {
      if (resume.seniority === "senior" && experience >= 5) score += 15;
      else if (resume.seniority === "mid" && experience <= 6) score += 10;
      else if (resume.seniority === "junior" && experience <= 3) score += 10;
      else score -= 10;
    }

    const finalScore = Math.min(100, Math.max(0, Math.round(score)));

    const insights =
      finalScore >= 75
        ? "Strong match for your profile"
        : finalScore >= 60
        ? "Good match, worth a look"
        : finalScore >= 45
        ? "Moderate match"
        : "Low match for your profile";

    return { score: finalScore, matchedSkills, insights };
  };

  /* ---------------- RESUME UPLOAD ---------------- */
  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !window.pdfjsLib) return;

    setUploadingResume(true);
    try {
      const buffer = await file.arrayBuffer();
      const pdf = await window.pdfjsLib.getDocument({ data: buffer }).promise;
      let text = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map(i => i.str).join(" ");
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

  /* ---------------- APPLY MATCH ---------------- */
  const applyResumeMatch = () => {
    const resume = {
      persona: resumePersona,
      seniority: resumeSeniority,
      keywords: resumeKeywords
    };

    const scored = jobs.map(j => {
      const r = calculateKeywordMatch(j, resume);
      return { ...j, matchScore: r.score, matchedSkills: r.matchedSkills, insights: r.insights };
    });

    scored.sort((a,b) => b.matchScore - a.matchScore);
    setFilteredJobs(scored);
    setResumeMatchEnabled(true);
  };

  const clearResume = () => {
    setResumeText("");
    setResumeKeywords([]);
    setResumePersona(null);
    setResumeSeniority("mid");
    setResumeMatchEnabled(false);
    setFilteredJobs(jobs);
  };

  /* ---------------- JOB ACTIONS ---------------- */
  const toggleSaveJob = (id) =>
    setSavedJobs(p => p.includes(id) ? p.filter(x => x !== id) : [...p, id]);

  const markJobAsApplied = (id) =>
    setAppliedJobs(p => p.includes(id) ? p : [...p, id]);

  /* ---------------- FILTERING ---------------- */
  React.useEffect(() => {
    if (resumeMatchEnabled) return;

    let data = [...jobs];
    if (searchQuery)
      data = data.filter(j =>
        j.title.toLowerCase().includes(searchQuery.toLowerCase())
      );
    if (companyQuery)
      data = data.filter(j =>
        j.company.toLowerCase().includes(companyQuery.toLowerCase())
      );
    if (selectedSource !== "all") data = data.filter(j => j.source === selectedSource);
    if (selectedRole !== "all") data = data.filter(j => j.role === selectedRole);
    if (selectedLocation !== "all") data = data.filter(j => j.location === selectedLocation);

    setFilteredJobs(data);
  }, [jobs, searchQuery, companyQuery, selectedSource, selectedRole, selectedLocation, resumeMatchEnabled]);

  if (loading) {
    return <div className="p-10 text-center text-gray-500">Loading jobs…</div>;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
      <h1 className="text-3xl font-bold text-cyan-400 mb-4">Job Hunter</h1>

      <div className="flex gap-2 mb-4">
        <input
          placeholder="Search role…"
          className="px-3 py-2 bg-gray-800 rounded"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
        <input
          placeholder="Company…"
          className="px-3 py-2 bg-gray-800 rounded"
          value={companyQuery}
          onChange={e => setCompanyQuery(e.target.value)}
        />
      </div>

      <input type="file" accept=".pdf" onChange={handleResumeUpload} />
      {resumeText && (
        <div className="flex gap-2 mt-2">
          <button onClick={applyResumeMatch} className="bg-cyan-600 px-3 py-1 rounded">
            Match Jobs
          </button>
          <button onClick={clearResume} className="bg-gray-700 px-3 py-1 rounded">
            Clear
          </button>
        </div>
      )}

      <div className="mt-6 space-y-4">
        {filteredJobs.map(job => (
          <div key={job.id} className="border border-gray-800 p-4 rounded">
            <h2 className="text-lg font-semibold">{job.title}</h2>
            <p className="text-gray-400">{job.company}</p>

            {resumeMatchEnabled && (
              <>
                <p className="text-cyan-400 mt-1">{job.matchScore}% match</p>
                <p className="text-sm italic">{job.insights}</p>
                <div className="flex gap-2 mt-2">
                  {job.matchedSkills?.map(s => (
                    <span key={s} className="text-xs bg-green-900/30 px-2 py-0.5 rounded">{s}</span>
                  ))}
                </div>
              </>
            )}

            <div className="flex gap-2 mt-3">
              <button onClick={() => toggleSaveJob(job.id)}>🔖</button>
              <a href={job.applyLink} target="_blank" rel="noreferrer" onClick={() => markJobAsApplied(job.id)}>
                Apply →
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
