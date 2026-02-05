import React from "react";

export default function Dashboard() {
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

    // Apply resume matching scores if enabled
    if (resumeMatchEnabled && resumeText) {
      data = data.map(job => ({
        ...job,
        matchScore: calculateMatchScore(job, resumeText)
      }));
    }

    setFilteredJobs(data);
    setCurrentPage(1); // Reset to page 1 when filters change
  }, [jobs, searchQuery, sourceQuery, companyQuery, selectedRole, locationQuery, selectedEmploymentType, resumeMatchEnabled, resumeText]);

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
  const toggleSaveJob = id =>
    setSavedJobs(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);

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

              {/* Source Filter (searchable) */}
              <div>
                <input
                  list="source-options"
                  placeholder="Filter by source..."
                  value={sourceQuery}
                  onChange={e => setSourceQuery(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                />
                <datalist id="source-options">
                  {sources.map(source => (
                    <option key={source} value={source} />
                  ))}
                </datalist>
              </div>

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

              {/* Location Filter (searchable) */}
              <div>
                <input
                  list="location-options"
                  placeholder="Filter by location..."
                  value={locationQuery}
                  onChange={e => setLocationQuery(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
                />
                <datalist id="location-options">
                  {locations.map(location => (
                    <option key={location} value={location} />
                  ))}
                </datalist>
              </div>

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
            <div className="mt-4 flex flex-wrap gap-3 items-center">
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 cursor-pointer transition-colors"
              >
                <option value="score">Sort by: Score</option>
                <option value="date">Sort by: Newest</option>
                <option value="remote">Sort by: Remote First</option>
                {resumeMatchEnabled && <option value="matchScore">Sort by: Match %</option>}
              </select>
              <input
                list="company-options"
                placeholder="Filter by company..."
                value={companyQuery}
                onChange={e => setCompanyQuery(e.target.value)}
                className="bg-gray-900 border border-gray-800 rounded px-4 py-2 text-sm focus:outline-none focus:border-indigo-500 transition-colors w-full md:w-72"
              />
              <datalist id="company-options">
                {companies.map(company => (
                  <option key={company} value={company} />
                ))}
              </datalist>
            </div>

            {/* Company quick chips */}
            <div className="mt-3 flex flex-wrap gap-2">
              {topCompanies.map(name => (
                <button
                  key={name}
                  onClick={() => setCompanyQuery(name)}
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    companyQuery === name
                      ? "bg-indigo-500 text-gray-900 border-indigo-400"
                      : "bg-gray-900 text-gray-300 border-gray-700 hover:border-indigo-500"
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
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Search: "{searchQuery}"
                  </span>
                )}
                {sourceQuery && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Source: {sourceQuery}
                  </span>
                )}
                {companyQuery && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Company: {companyQuery}
                  </span>
                )}
                {selectedRole !== "all" && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Role: {selectedRole}
                  </span>
                )}
                {locationQuery && (
                  <span className="text-xs bg-indigo-900/30 text-indigo-300 px-2 py-1 rounded">
                    Location: {locationQuery}
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
                    setSelectedRole("all");
                    setSelectedEmploymentType("all");
                    setSourceQuery("");
                    setCompanyQuery("");
                    setLocationQuery("");
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
                      setSelectedRole("all");
                      setSelectedEmploymentType("all");
                      setSourceQuery("");
                      setCompanyQuery("");
                      setLocationQuery("");
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

function JobCard({ job, saved, applied, onSave, onApply, resumeMatchEnabled, appliedDetails, onUpdateNotes, onToggleDetails, isExpanded }) {
  const [notes, setNotes] = React.useState(appliedDetails?.notes || "");
  const pill = (() => {
    const loc = (job.location || "").toLowerCase();
    if (loc.includes("remote")) return "Remote";
    if (loc.includes("hybrid")) return "Hybrid";
    if (loc.includes("india")) return "India";
    return "";
  })();
  const initial = (job.company || "?").trim().charAt(0).toUpperCase();
  
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-5 hover:border-gray-700 transition-colors">
      <div className="flex gap-6">
        {resumeMatchEnabled && job.matchScore !== undefined && (
          <div className="w-20 h-20 rounded-full border-4 border-indigo-400 flex items-center justify-center flex-shrink-0">
            <span className="text-xl font-bold text-indigo-400">{job.matchScore}%</span>
          </div>
        )}

        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-full bg-indigo-900/40 border border-indigo-800 text-indigo-300 flex items-center justify-center text-sm font-semibold">
              {initial}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded">{job.company}</span>
              {job.source && (
                <span className="text-xs bg-gray-800/60 text-gray-400 px-2 py-1 rounded">{job.source}</span>
              )}
              {pill && (
                <span className="text-xs bg-emerald-900/30 text-emerald-300 px-2 py-1 rounded">{pill}</span>
              )}
            </div>
          </div>
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
              applied ? "bg-gray-700 text-gray-500 cursor-not-allowed" : "bg-indigo-500 text-gray-900 hover:bg-indigo-400 shadow-md shadow-indigo-900/30"
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
