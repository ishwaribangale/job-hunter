import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  const [jobs, setJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [filteredJobs, setFilteredJobs] = React.useState([]);

  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedSource, setSelectedSource] = React.useState("all");
  const [selectedRole, setSelectedRole] = React.useState("all");
  const [selectedLocation, setSelectedLocation] = React.useState("all");
  const [minScore, setMinScore] = React.useState(0);

  const [resumeText, setResumeText] = React.useState("");
  const [resumeKeywords, setResumeKeywords] = React.useState([]);
  const [resumeMatchEnabled, setResumeMatchEnabled] = React.useState(false);
  const [uploadingResume, setUploadingResume] = React.useState(false);

  /* -------------------- SAFE DATA FETCH -------------------- */
  React.useEffect(() => {
    fetch(
      "https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json"
    )
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch jobs");
        return res.json();
      })
      .then((data) => {
        setJobs(Array.isArray(data) ? data : []);
        setFilteredJobs(Array.isArray(data) ? data : []);
      })
      .catch(() => {
        setJobs([]);
        setFilteredJobs([]);
      })
      .finally(() => setLoading(false));
  }, []);

  /* -------------------- FILTER HELPERS -------------------- */
  const sources = React.useMemo(
    () => [...new Set(jobs.map((j) => j?.source).filter(Boolean))].sort(),
    [jobs]
  );

  const roles = React.useMemo(
    () => [...new Set(jobs.map((j) => j?.role).filter(Boolean))].sort(),
    [jobs]
  );

  const locations = React.useMemo(
    () => [...new Set(jobs.map((j) => j?.location).filter(Boolean))].sort(),
    [jobs]
  );

  /* -------------------- RESUME PARSING -------------------- */
  const extractKeywords = (text) => {
    const techKeywords = [
      "javascript","python","java","react","node","angular","vue","typescript",
      "sql","mongodb","aws","azure","docker","kubernetes","frontend","backend",
      "fullstack","devops","data science","machine learning","ai",
      "product manager","designer","ux","ui","marketing","sales",
      "engineer","developer","analyst","manager","lead","senior","junior","intern",
      "django","flask","spring","git","agile","scrum","api","rest","graphql",
      "html","css","tailwind","bootstrap","figma","sketch"
    ];

    const lower = text.toLowerCase();
    return [...new Set(techKeywords.filter((k) => lower.includes(k)))];
  };

  const calculateMatchScore = (job, keywords) => {
    if (!keywords.length) return 0;
    const text = `${job?.title} ${job?.company} ${job?.role}`.toLowerCase();
    const matches = keywords.filter((k) => text.includes(k));
    return Math.round((matches.length / keywords.length) * 100);
  };

  /* -------------------- SAFE RESUME UPLOAD -------------------- */
  const handleResumeUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please upload a PDF file");
      return;
    }

    if (!window?.pdfjsLib) {
      alert("PDF.js failed to load. Resume parsing disabled.");
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
        text += content.items.map((it) => it.str).join(" ") + " ";
      }

      const keywords = extractKeywords(text);

      setResumeText(text);
      setResumeKeywords(keywords);
      setResumeMatchEnabled(true);

      alert(
        `Resume analyzed! Found ${keywords.length} skills: ${keywords
          .slice(0, 10)
          .join(", ")}${keywords.length > 10 ? "..." : ""}`
      );
    } catch (err) {
      console.error(err);
      alert("Error reading resume");
    } finally {
      setUploadingResume(false);
    }
  };

  const clearResume = () => {
    setResumeText("");
    setResumeKeywords([]);
    setResumeMatchEnabled(false);
    const input = document.getElementById("resume-input");
    if (input) input.value = "";
  };

  /* -------------------- FILTER LOGIC -------------------- */
  React.useEffect(() => {
    let data = [...jobs];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      data = data.filter(
        (j) =>
          j?.title?.toLowerCase().includes(q) ||
          j?.company?.toLowerCase().includes(q)
      );
    }

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

  const resetFilters = () => {
    setSearchQuery("");
    setSelectedSource("all");
    setSelectedRole("all");
    setSelectedLocation("all");
    setMinScore(0);
    clearResume();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading jobs...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <h1 className="text-3xl font-bold p-6">Job Intelligence Dashboard</h1>
      <p className="px-6">
        Showing {filteredJobs.length} of {jobs.length} jobs
      </p>

      {filteredJobs.map((job) => (
        <div key={job.id} className="p-4 m-4 bg-white shadow rounded">
          <h3 className="font-semibold">{job.title}</h3>
          <p>{job.company}</p>
          {resumeMatchEnabled && job.matchScore > 0 && (
            <p>{job.matchScore}% Match</p>
          )}
          <a href={job.applyLink} target="_blank" rel="noreferrer">
            Apply
          </a>
        </div>
      ))}
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
