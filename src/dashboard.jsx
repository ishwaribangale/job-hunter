import React from "react";

export default function Dashboard() {
  const [jobs, setJobs] = React.useState([]);
  const [filteredJobs, setFilteredJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedSource, setSelectedSource] = React.useState("all");
  const [selectedRole, setSelectedRole] = React.useState("all");
  const [selectedLocation, setSelectedLocation] = React.useState("all");
  const [selectedEmploymentType, setSelectedEmploymentType] = React.useState("all");

  const [activeSection, setActiveSection] = React.useState("all");
  const [resumeMatchEnabled, setResumeMatchEnabled] = React.useState(false);
  const [resumeFile, setResumeFile] = React.useState(null);

  const [savedJobs, setSavedJobs] = React.useState([]);
  const [appliedJobs, setAppliedJobs] = React.useState([]);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  /* ---------------- FETCH JOBS ---------------- */
  React.useEffect(() => {
    fetch("https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json")
      .then(res => res.json())
      .then(data => {
        // Add match scores for demo purposes
        const jobsWithScores = data.map(job => ({
          ...job,
          matchScore: Math.floor(Math.random() * 40) + 60 // Random score 60-100
        }));
        setJobs(jobsWithScores);
        setFilteredJobs(jobsWithScores);
      })
      .finally(() => setLoading(false));
  }, []);

  /* ---------------- FILTER VALUES ---------------- */
  const sources = [...new Set(jobs.map(j => j?.source).filter(Boolean))];
  const roles = [...new Set(jobs.map(j => j?.role).filter(Boolean))];
  const locations = [...new Set(jobs.map(j => j?.location).filter(Boolean))];
  const employmentTypes = [...new Set(jobs.map(j => j?.employment_type).filter(Boolean))];

  /* ---------------- QUICK FILTERS ---------------- */
  const quickFilters = [
    {
      label: "Remote Only",
      action: () => {
        setSelectedLocation("all");
        setSelectedRole("all");
        setSelectedSource("all");
        setSelectedEmploymentType("all");
        setFilteredJobs(jobs.filter(j => j.location?.toLowerCase().includes("remote")));
      }
    },
    {
      label: "Full-time",
      action: () => {
        setSelectedLocation("all");
        setSelectedRole("all");
        setSelectedSource("all");
        setSelectedEmploymentType("all");
        setFilteredJobs(jobs.filter(j => j.employment_type === "Full-time"));
      }
    },
    {
      label: "Engineering",
      action: () => {
        setSelectedLocation("all");
        setSelectedRole("all");
        setSelectedSource("all");
        setSelectedEmploymentType("all");
        setFilteredJobs(jobs.filter(j => j.role === "Engineering"));
      }
    },
    {
      label: "Reset Filters",
      action: () => {
        setSearchQuery("");
        setSelectedLocation("all");
        setSelectedRole("all");
        setSelectedSource("all");
        setSelectedEmploymentType("all");
        setFilteredJobs(jobs);
      }
    }
  ];

  /* ---------------- FILTER LOGIC ---------------- */
  React.useEffect(() => {
    let data = [...jobs];

    if (searchQuery) {
      data = data.filter(j =>
        j.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        j.company?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        j.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedSource !== "all") data = data.filter(j => j.source === selectedSource);
    if (selectedRole !== "all") data = data.filter(j => j.role === selectedRole);
    if (selectedLocation !== "all") data = data.filter(j => j.location === selectedLocation);
    if (selectedEmploymentType !== "all") data = data.filter(j => j.employment_type === selectedEmploymentType);

    setFilteredJobs(data);
  }, [jobs, searchQuery, selectedSource, selectedRole, selectedLocation, selectedEmploymentType]);

  /* ---------------- SECTION FILTER ---------------- */
  const displayJobs = React.useMemo(() => {
    let data = filteredJobs;
    
    if (activeSection === "saved") {
      data = data.filter(j => savedJobs.includes(j.id));
    } else if (activeSection === "applied") {
      data = data.filter(j => appliedJobs.includes(j.id));
    } else if (activeSection === "top") {
      data = data.filter(j => j.matchScore >= 75);
    } else if (activeSection === "resume" && resumeMatchEnabled) {
      // Sort by match score when resume matching is enabled
      data = [...data].sort((a, b) => b.matchScore - a.matchScore);
    }
    
    return data;
  }, [filteredJobs, activeSection, savedJobs, appliedJobs, resumeMatchEnabled]);

  /* ---------------- ACTIONS ---------------- */
  const toggleSaveJob = id =>
    setSavedJobs(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);

  const markJobAsApplied = (id, applyLink) => {
    // Open the job link in a new tab
    if (applyLink) {
      window.open(applyLink, '_blank', 'noopener,noreferrer');
    }
    // Mark as applied
    setAppliedJobs(prev => prev.includes(id) ? prev : [...prev, id]);
  };

  const handleResumeMatch = () => {
    if (resumeFile) {
      setResumeMatchEnabled(true);
      // Simulate resume processing - in real app, you'd process the PDF here
      const sortedJobs = [...jobs].sort((a, b) => b.matchScore - a.matchScore);
      setFilteredJobs(sortedJobs);
    }
  };

  const handleResumeFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setResumeFile(file);
    }
  };

  const clearResume = () => {
    setResumeFile(null);
    setResumeMatchEnabled(false);
    setFilteredJobs(jobs);
  };

  if (loading) {
    return <div className="p-10 text-center text-gray-500">Loading jobs…</div>;
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-100 flex">
      {/* SIDEBAR */}
      <aside className={`${sidebarOpen ? "w-72" : "w-16"} bg-[#0f172a] border-r border-gray-800 transition-all`}>
        <div className="p-4 flex justify-between items-center">
          {sidebarOpen && <h1 className="text-xl font-bold text-indigo-400">JobFlow</h1>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-indigo-400">
            {sidebarOpen ? "✕" : "☰"}
          </button>
        </div>

        {sidebarOpen && (
          <div className="px-4 space-y-6">
            {/* NAV */}
            <nav className="space-y-2">
              <Nav label="All Jobs" active={activeSection === "all"} onClick={() => setActiveSection("all")} />
              <Nav label="Top Matches" active={activeSection === "top"} onClick={() => setActiveSection("top")} />
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
                    className="w-full text-left px-3 py-2 rounded bg-gray-800/50 hover:bg-gray-800 text-sm transition-colors"
                  >
                    {q.label}
                  </button>
                ))}
              </div>
            </div>

            {/* RESUME MATCHER CARD */}
            <div className="bg-indigo-900/20 border border-indigo-900/40 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-indigo-300 mb-1">Resume Matcher</h4>
              <p className="text-xs text-gray-400 mb-3">
                Upload your resume to find best-fit roles
              </p>
              <button
                onClick={() => setActiveSection("resume")}
                className="w-full bg-indigo-500 text-gray-900 py-1.5 rounded text-sm font-semibold hover:bg-indigo-400 transition-colors"
              >
                See Your Fit →
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* MAIN */}
      <main className="flex-1 flex flex-col">
        {/* HEADER */}
        <header className="p-6 border-b border-gray-800 bg-[#0f172a]">
          <h2 className="text-3xl font-bold text-indigo-400">
            {activeSection === "resume" ? "Resume Matches" : "Job Intelligence"}
          </h2>
          <p className="text-gray-400 mt-1">
            {activeSection === "resume"
              ? resumeMatchEnabled 
                ? `${displayJobs.length} matched opportunities` 
                : "Match your resume against open roles"
              : `${displayJobs.length} opportunities`}
          </p>
        </header>

        {/* FILTERS BAR */}
        {activeSection !== "resume" && (
          <div className="p-6 bg-[#0f172a] border-b border-gray-800">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {/* Search */}
              <div className="lg:col-span-2">
                <input
                  type="text"
                  placeholder="Search jobs by title or company..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Source Filter */}
              <select
                value={selectedSource}
                onChange={e => setSelectedSource(e.target.value)}
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="all">All Sources</option>
                {sources.map(source => (
                  <option key={source} value={source}>{source}</option>
                ))}
              </select>

              {/* Role Filter */}
              <select
                value={selectedRole}
                onChange={e => setSelectedRole(e.target.value)}
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="all">All Roles</option>
                {roles.map(role => (
                  <option key={role} value={role}>{role}</option>
                ))}
              </select>

              {/* Location Filter */}
              <select
                value={selectedLocation}
                onChange={e => setSelectedLocation(e.target.value)}
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="all">All Locations</option>
                {locations.map(location => (
                  <option key={location} value={location}>{location}</option>
                ))}
              </select>

              {/* Employment Type Filter */}
              <select
                value={selectedEmploymentType}
                onChange={e => setSelectedEmploymentType(e.target.value)}
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="all">All Types</option>
                {employmentTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* CONTENT */}
        <section className="flex-1 overflow-y-auto p-6">
          {activeSection === "resume" && !resumeMatchEnabled ? (
            <ResumeMatchScreen 
              onMatch={handleResumeMatch} 
              onFileChange={handleResumeFileChange}
              onClear={clearResume}
              resumeFile={resumeFile}
            />
          ) : (
            <div className="space-y-4">
              {displayJobs.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">No jobs found matching your filters</p>
                  <button
                    onClick={() => {
                      setSearchQuery("");
                      setSelectedLocation("all");
                      setSelectedRole("all");
                      setSelectedSource("all");
                      setSelectedEmploymentType("all");
                    }}
                    className="mt-4 text-indigo-400 hover:text-indigo-300"
                  >
                    Clear all filters
                  </button>
                </div>
              ) : (
                displayJobs.map(job => (
                  <JobCard
                    key={job.id}
                    job={job}
                    saved={savedJobs.includes(job.id)}
                    applied={appliedJobs.includes(job.id)}
                    onSave={toggleSaveJob}
                    onApply={markJobAsApplied}
                    resumeMatchEnabled={resumeMatchEnabled && activeSection === "resume"}
                  />
                ))
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
        active ? "bg-indigo-900/30 text-indigo-400" : "text-gray-400 hover:bg-gray-800"
      }`}
    >
      {label}
    </button>
  );
}

function ResumeMatchScreen({ onMatch, onFileChange, onClear, resumeFile }) {
  return (
    <div className="max-w-xl mx-auto text-center bg-gray-900 border border-gray-800 rounded-xl p-10">
      <h3 className="text-2xl font-bold text-indigo-400 mb-2">Match Your Resume</h3>
      <p className="text-gray-400 mb-6">
        Upload your resume and instantly see which roles fit you best.
      </p>

      <div className="mb-4">
        <label className="block mb-2 text-sm text-gray-400">
          {resumeFile ? `Selected: ${resumeFile.name}` : "Choose a PDF file"}
        </label>
        <input 
          type="file" 
          accept=".pdf"
          onChange={onFileChange}
          className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-indigo-500 file:text-gray-900 hover:file:bg-indigo-400 file:cursor-pointer cursor-pointer"
        />
      </div>
      
      <div className="flex gap-3 justify-center">
        <button
          onClick={onMatch}
          disabled={!resumeFile}
          className={`px-6 py-2 rounded font-semibold transition-colors ${
            resumeFile 
              ? "bg-indigo-500 text-gray-900 hover:bg-indigo-400 cursor-pointer" 
              : "bg-gray-700 text-gray-500 cursor-not-allowed"
          }`}
        >
          Match Resume
        </button>
        <button 
          onClick={onClear}
          className="bg-gray-700 px-6 py-2 rounded hover:bg-gray-600 transition-colors"
        >
          Clear
        </button>
      </div>
    </div>
  );
}

function JobCard({ job, saved, applied, onSave, onApply, resumeMatchEnabled }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-5 flex gap-6 hover:border-gray-700 transition-colors">
      {resumeMatchEnabled && job.matchScore !== undefined && (
        <div className="flex-shrink-0">
          <div className="w-20 h-20 rounded-full border-4 border-indigo-400 flex items-center justify-center">
            <span className="text-xl font-bold text-indigo-400">{job.matchScore}</span>
          </div>
          <p className="text-xs text-center text-gray-500 mt-1">Match</p>
        </div>
      )}

      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="text-xl font-semibold">{job.title}</h3>
          {!applied && (
            <span className="text-xs bg-indigo-900/40 text-indigo-300 px-2 py-0.5 rounded">
              ✨ New
            </span>
          )}
        </div>
        <p className="text-gray-400 text-sm mb-2">{job.company} · {job.location}</p>
        
        {job.employment_type && (
          <span className="inline-block text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded mr-2">
            {job.employment_type}
          </span>
        )}
        {job.role && (
          <span className="inline-block text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded">
            {job.role}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-2 flex-shrink-0">
        <button
          onClick={() => onSave(job.id)}
          className={`px-3 py-2 rounded transition-colors ${
            saved ? "bg-yellow-900/40 text-yellow-400" : "bg-gray-800 text-gray-400 hover:bg-gray-700"
          }`}
          title={saved ? "Unsave job" : "Save job"}
        >
          🔖
        </button>
        <button
          disabled={applied}
          onClick={() => onApply(job.id, job.applyLink)}
          className={`px-4 py-2 rounded font-semibold transition-colors ${
            applied 
              ? "bg-gray-700 text-gray-500 cursor-not-allowed" 
              : "bg-indigo-500 text-gray-900 hover:bg-indigo-400"
          }`}
        >
          {applied ? "Applied" : "Apply →"}
        </button>
      </div>
    </div>
  );
}
