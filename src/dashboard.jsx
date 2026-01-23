import React from "react";

export default function App() {
  const [jobs, setJobs] = React.useState([]);
  const [filteredJobs, setFilteredJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedSource, setSelectedSource] = React.useState("all");
  const [selectedRole, setSelectedRole] = React.useState("all");
  const [selectedLocation, setSelectedLocation] = React.useState("all");
  const [minScore, setMinScore] = React.useState(0);

  const [resumeText, setResumeText] = React.useState("");
  const [resumeKeywords, setResumeKeywords] = React.useState([]);
  const [resumeMatchEnabled, setResumeMatchEnabled] = React.useState(false);
  const [uploadingResume, setUploadingResume] = React.useState(false);

  /* -------------------- FETCH JOBS (SAFE) -------------------- */
  React.useEffect(() => {
    fetch(
      "https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json"
    )
      .then((res) => {
        if (!res.ok) throw new Error("Fetch failed");
        return res.json();
      })
      .then((data) => {
        const list = Array.isArray(data) ? data : [];
        setJobs(list);
        setFilteredJobs(list);
      })
      .catch(() => {
        setJobs([]);
        setFilteredJobs([]);
      })
      .finally(() => setLoading(false));
  }, []);

  /* -------------------- FILTER VALUES -------------------- */
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

  /* -------------------- RESUME HELPERS -------------------- */
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

  /* -------------------- RESUME UPLOAD (GUARDED) -------------------- */
  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || file.type !== "application/pdf") return;

    if (!window.pdfjsLib) {
      alert("PDF.js not loaded");
      return;
    }

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
      setResumeMatchEnabled(true);
    } catch {
      alert("Resume parsing failed");
    } finally {
      setUploadingResume(false);
    }
  };

  const clearResume = () => {
    setResumeText("");
    setResumeKeywords([]);
    setResumeMatchEnabled(false);
  };

  /* -------------------- APPLY FILTERS -------------------- */
  React.useEffect(() => {
    let data = [...jobs];

    if (searchQuery)
      data = data.filter(
        (j) =>
          j.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          j.company?.toLowerCase().includes(searchQuery.toLowerCase())
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
    selectedSource,
    selectedRole,
    selectedLocation,
    minScore,
    resumeMatchEnabled,
    resumeKeywords,
  ]);

  if (loading) {
    return <div className="p-8 text-center">Loading jobs…</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Job Intelligence Dashboard</h1>

      <input
        className="border p-2 mb-4 w-full"
        placeholder="Search jobs…"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      <input type="file" accept=".pdf" onChange={handleResumeUpload} />

      <div className="mt-6 space-y-4">
        {filteredJobs.map((job) => (
          <div key={job.id} className="bg-white p-4 shadow rounded">
            <h3 className="font-semibold">{job.title}</h3>
            <p>{job.company}</p>
            {resumeMatchEnabled && job.matchScore > 0 && (
              <p>{job.matchScore}% match</p>
            )}
            <a
              href={job.applyLink}
              target="_blank"
              rel="noreferrer"
              className="text-blue-600"
            >
              Apply →
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
