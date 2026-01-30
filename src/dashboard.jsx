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

  const [savedJobs, setSavedJobs] = React.useState([]);
  const [appliedJobs, setAppliedJobs] = React.useState([]);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const [appliedJobsDetails, setAppliedJobsDetails] = React.useState({});
  const [expandedJob, setExpandedJob] = React.useState(null);
  const [currentPage, setCurrentPage] = React.useState(1);
  const [itemsPerPage] = React.useState(20);
  const [sortBy, setSortBy] = React.useState("score");
  const [resumeText, setResumeText] = React.useState("");
  const [resumeKeywords, setResumeKeywords] = React.useState([]);

  /* ---------------- FETCH JOBS ---------------- */
  React.useEffect(() => {
    fetch("https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json")
      .then(res => res.json())
      .then(data => {
        setJobs(data);
        setFilteredJobs(data);
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
        setSearchQuery("");
        setSelectedSource("all");
        setSelectedRole("all");
        setSelectedLocation("all");
        setSelectedEmploymentType("all");
        setFilteredJobs(jobs.filter(j => j.location?.toLowerCase().includes("remote")));
      }
    },
    {
      label: "Full-time",
      action: () => {
        setSearchQuery("");
        setSelectedSource("all");
        setSelectedRole("all");
        setSelectedLocation("all");
        setSelectedEmploymentType("all");
        setFilteredJobs(jobs.filter(j => j.employment_type === "Full-time"));
      }
    },
    {
      label: "Engineering",
      action: () => {
        setSearchQuery("");
        setSelectedSource("all");
        setSelectedRole("all");
        setSelectedLocation("all");
        setSelectedEmploymentType("all");
        setFilteredJobs(jobs.filter(j => j.role === "Engineering"));
      }
    },
    {
      label: "Reset Filters",
      action: () => {
        setSearchQuery("");
        setSelectedSource("all");
        setSelectedRole("all");
        setSelectedLocation("all");
        setSelectedEmploymentType("all");
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

    if (selectedSource !== "all") {
      data = data.filter(j => j.source === selectedSource);
    }

    if (selectedRole !== "all") {
      data = data.filter(j => j.role === selectedRole);
    }

    if (selectedLocation !== "all") {
      data = data.filter(j => j.location === selectedLocation);
    }

    if (selectedEmploymentType !== "all") {
      data = data.filter(j => j.employment_type === selectedEmploymentType);
    }

    // Apply resume matching scores if enabled
    if (resumeMatchEnabled && resumeKeywords.length > 0) {
      data = data.map(job => ({
        ...job,
        matchScore: calculateMatchScore(job, resumeKeywords)
      }));
    }

    setFilteredJobs(data);
    setCurrentPage(1); // Reset to page 1 when filters change
  }, [jobs, searchQuery, selectedSource, selectedRole, selectedLocation, selectedEmploymentType, resumeMatchEnabled, resumeKeywords]);

  /* ---------------- SECTION FILTER ---------------- */
  const displayJobs = React.useMemo(() => {
    if (activeSection === "saved") return filteredJobs.filter(j => savedJobs.includes(j.id));
    if (activeSection === "applied") return filteredJobs.filter(j => appliedJobs.includes(j.id));
    if (activeSection === "top") return filteredJobs.filter(j => j.matchScore >= 75);
    return filteredJobs;
  }, [filteredJobs, activeSection, savedJobs, appliedJobs]);

  /* ---------------- SORT JOBS ---------------- */
  const sortedJobs = React.useMemo(() => {
    const data = [...displayJobs];
    
    switch(sortBy) {
      case "matchScore":
        return data.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
      case "date":
        return data.sort((a, b) => new Date(b.postedDate || b.fetchedAt) - new Date(a.postedDate || a.fetchedAt));
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
  const toggleSaveJob = id =>
    setSavedJobs(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);

  const calculateMatchScore = (job, userKeywords) => {
    if (!job.requirements?.keywords || job.requirements.keywords.length === 0) {
      return 0;
    }
    
    const jobKeywords = job.requirements.keywords.map(k => k.toLowerCase());
    const userKwLower = userKeywords.map(k => k.toLowerCase());
    
    const matches = jobKeywords.filter(jk => 
      userKwLower.some(uk => uk.includes(jk) || jk.includes(uk))
    );
    
    const score = Math.round((matches.length / jobKeywords.length) * 100);
    return Math.min(score, 100);
  };

  const markJobAsApplied = (id, applyLink) => {
    // Open the job link
    if (applyLink) {
      window.open(applyLink, '_blank', 'noopener,noreferrer');
    }
    
    // Mark as applied with details
    setAppliedJobs(prev => prev.includes(id) ? prev : [...prev, id]);
    
    // Store application details
    const job = jobs.find(j => j.id === id);
    setAppliedJobsDetails(prev => ({
      ...prev,
      [id]: {
        appliedDate: new Date().toISOString(),
        notes: "",
        job: job
      }
    }));
  };

  const handleResumeUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      setResumeText(text);
      
      // Extract keywords (simple approach - extract capitalized words and tech terms)
      const words = text.match(/\b[A-Z][a-z]+\b|\b[A-Z]{2,}\b/g) || [];
      const techTerms = text.match(/\b(python|javascript|react|java|aws|docker|kubernetes|sql|mongodb|node|typescript|vue|angular)\b/gi) || [];
      
      const allKeywords = [...new Set([...words, ...techTerms])];
      setResumeKeywords(allKeywords);
      setResumeMatchEnabled(true);
      setActiveSection("all"); // Show all jobs with match scores
    };
    reader.readAsText(file);
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
              ? "Match your resume against open roles"
              : `${displayJobs.length} opportunities`}
          </p>
        </header>

        {/* FILTERS BAR */}
        {activeSection !== "resume" && (
          <div className="p-6 bg-[#0f172a] border-b border-gray-800">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
              {/* Search */}
              <div className="lg:col-span-2">
                <input
                  type="text"
                  placeholder="Search jobs by title or company..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              {/* Source Filter */}
              <select
                value={selectedSource}
                onChange={e => setSelectedSource(e.target.value)}
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 cursor-pointer transition-colors"
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
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 cursor-pointer transition-colors"
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
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 cursor-pointer transition-colors"
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
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 cursor-pointer transition-colors"
              >
                <option value="all">All Types</option>
                {employmentTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            {/* Second Row - Sort */}
            <div className="mt-4">
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 cursor-pointer transition-colors"
              >
                <option value="score">Sort by: Score</option>
                <option value="date">Sort by: Date</option>
                {resumeMatchEnabled && <option value="matchScore">Sort by: Match %</option>}
              </select>
            </div>

            {/* Active Filters Display */}
            {(searchQuery || selectedSource !== "all" || selectedRole !== "all" || selectedLocation !== "all" || selectedEmploymentType !== "all") && (
              <div className="mt-4 flex flex-wrap gap-2 items-center">
                <span className="text-xs text-gray-500">Active filters:</span>
                {searchQuery && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Search: "{searchQuery}"
                  </span>
                )}
                {selectedSource !== "all" && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Source: {selectedSource}
                  </span>
                )}
                {selectedRole !== "all" && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Role: {selectedRole}
                  </span>
                )}
                {selectedLocation !== "all" && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Location: {selectedLocation}
                  </span>
                )}
                {selectedEmploymentType !== "all" && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Type: {selectedEmploymentType}
                  </span>
                )}
                <button
                  onClick={() => {
                    setSearchQuery("");
                    setSelectedSource("all");
                    setSelectedRole("all");
                    setSelectedLocation("all");
                    setSelectedEmploymentType("all");
                  }}
                  className="text-xs text-indigo-400 hover:text-indigo-300 underline"
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
          ) : (
            <div className="space-y-4">
              {displayJobs.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg mb-2">No jobs found matching your filters</p>
                  <button
                    onClick={() => {
                      setSearchQuery("");
                      setSelectedSource("all");
                      setSelectedRole("all");
                      setSelectedLocation("all");
                      setSelectedEmploymentType("all");
                    }}
                    className="text-indigo-400 hover:text-indigo-300 underline"
                  >
                    Clear all filters
                  </button>
                </div>
              ) : (
                <>
                  {paginatedJobs.map(job => (
                    <JobCard
                      key={job.id}
                      job={job}
                      saved={savedJobs.includes(job.id)}
                      applied={appliedJobs.includes(job.id)}
                      appliedDetails={appliedJobsDetails[job.id]}
                      isExpanded={expandedJob === job.id}
                      onSave={toggleSaveJob}
                      onApply={markJobAsApplied}
                      onUpdateNotes={(id, notes) => {
                        setAppliedJobsDetails(prev => ({
                          ...prev,
                          [id]: { ...prev[id], notes }
                        }));
                      }}
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
        active ? "bg-indigo-900/30 text-indigo-400" : "text-gray-400 hover:bg-gray-800"
      }`}
    >
      {label}
    </button>
  );
}

function ResumeMatchScreen({ onMatch, onFileUpload }) {
  return (
    <div className="max-w-xl mx-auto text-center bg-gray-900 border border-gray-800 rounded-xl p-10">
      <h3 className="text-2xl font-bold text-indigo-400 mb-2">Match Your Resume</h3>
      <p className="text-gray-400 mb-6">
        Upload your resume (.txt file) and instantly see which roles fit you best.
      </p>

      <input 
        type="file" 
        accept=".txt" 
        onChange={onFileUpload}
        className="mb-4 text-gray-300" 
      />
      
      <p className="text-xs text-gray-500 mt-2">
        Tip: Save your resume as .txt for best results
      </p>
    </div>
  );
}

function JobCard({ job, saved, applied, onSave, onApply, resumeMatchEnabled, appliedDetails, onUpdateNotes, onToggleDetails, isExpanded }) {
  const [notes, setNotes] = React.useState(appliedDetails?.notes || "");
  
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-5 hover:border-gray-700 transition-colors">
      <div className="flex gap-6">
        {resumeMatchEnabled && job.matchScore !== undefined && (
          <div className="w-20 h-20 rounded-full border-4 border-indigo-400 flex items-center justify-center flex-shrink-0">
            <span className="text-xl font-bold text-indigo-400">{job.matchScore}%</span>
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
          
          <div className="flex gap-2 flex-wrap">
            {job.employment_type && (
              <span className="inline-block text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded">
                {job.employment_type}
              </span>
            )}
            {job.role && (
              <span className="inline-block text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded">
                {job.role}
              </span>
            )}
            {job.requirements?.skills && job.requirements.skills.length > 0 && (
              <span className="inline-block text-xs bg-blue-900/30 text-blue-300 px-2 py-1 rounded">
                {job.requirements.skills.slice(0, 3).join(", ")}
              </span>
            )}
          </div>
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
              applied ? "bg-gray-700 text-gray-500 cursor-not-allowed" : "bg-indigo-500 text-gray-900 hover:bg-indigo-400"
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
              {new Date(appliedDetails.appliedDate).toLocaleDateString('en-US', { 
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
              onBlur={() => onUpdateNotes(job.id, notes)}
              placeholder="Add notes about your application..."
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-indigo-500 resize-none"
              rows={3}
            />
          </div>
        </div>
      )}
    </div>
  );
}
