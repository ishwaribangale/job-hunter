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
    const keywords = [
      "javascript","react","python","java","node","typescript","sql","aws",
      "docker","kubernetes","frontend","backend","fullstack","devops",
      "machine learning","ai","data science","engineer","developer"
    ];
    const lower = text.toLowerCase();
    return [...new Set(keywords.filter((k) => lower.includes(k)))];
  };

  const calculateMatchScore = (job, keywords) => {
    if (!keywords.length) return 0;
    const text = `${job.title} ${job.company} ${job.role || ""}`.toLowerCase();
    const matches = keywords.filter((k) => text.includes(k));
    return Math.round((matches.length / keywords.length) * 100);
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

      const keywords = extractKeywords(text);
      setResumeText(text);
      setResumeKeywords(keywords);
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

    if (resumeMatchEnabled && resumeKeywords.length) {
      data = data
        .map((j) => ({
          ...j,
          matchScore: calculateMatchScore(j, resumeKeywords),
        }))
        .filter((j) => j.matchScore > 0)
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
                <input type="file" accept=".pdf" onChange={handleResumeUpload} />
              ) : (
                <>
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
                      className="bg-sky-600 px-3 py-1 rounded text-sm"
                    >
                      Apply Match
                    </button>
                    <button
                      onClick={clearResume}
                      className="bg-gray-700 px-3 py-1 rounded text-sm"
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
                className="w-full mb-2 p-2 bg-gray-800 rounded"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />

              <input
                placeholder="Company"
                className="w-full mb-2 p-2 bg-gray-800 rounded"
                value={companyQuery}
                onChange={(e) => setCompanyQuery(e.target.value)}
              />

              <select
                className="w-full mb-2 p-2 bg-gray-800 rounded"
                value={selectedSource}
                onChange={(e) => setSelectedSource(e.target.value)}
              >
                <option value="all">All Sources</option>
                {sources.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>

              <select
                className="w-full mb-2 p-2 bg-gray-800 rounded"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
              >
                <option value="all">All Roles</option>
                {roles.map((r) => (
                  <option key={r}>{r}</option>
                ))}
              </select>

              <select
                className="w-full mb-2 p-2 bg-gray-800 rounded"
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
      <div className="flex-1 p-6 space-y-4">
        <h1 className="text-3xl font-bold text-sky-400">
          Job Intelligence Dashboard
        </h1>

        {filteredJobs.map((job) => (
          <div
            key={job.id}
            className="bg-gray-900 border border-gray-800 p-5 rounded-lg"
          >
            <div className="flex justify-between">
              <div>
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
              </div>

              <div className="text-right">
                {resumeMatchEnabled && job.matchScore > 0 && (
                  <div className="text-sky-400 font-bold">
                    {job.matchScore}% Match
                  </div>
                )}

                <a
                  href={job.applyLink}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-block mt-3 bg-sky-600 px-4 py-2 rounded"
                >
                  Apply →
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
