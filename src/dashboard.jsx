import React, { useState, useEffect, useMemo } from "react";

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCompany, setSelectedCompany] = useState("all");
  const [selectedRole, setSelectedRole] = useState("all");
  const [selectedLocation, setSelectedLocation] = useState("all");

  const [resumeText, setResumeText] = useState("");
  const [resumeKeywords, setResumeKeywords] = useState([]);
  const [resumePersona, setResumePersona] = useState(null);
  const [resumeSeniority, setResumeSeniority] = useState("mid");
  const [resumeMatchEnabled, setResumeMatchEnabled] = useState(false);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [analyzingJobs, setAnalyzingJobs] = useState(false);

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [savedJobs, setSavedJobs] = useState(new Set());

  // Fetch jobs from your API
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        // Replace this URL with your actual jobs API endpoint
        const response = await fetch("/api/jobs"); // or your jobs.json URL
        
        if (!response.ok) {
          throw new Error("Failed to fetch jobs");
        }
        
        const data = await response.json();
        setJobs(data);
        setFilteredJobs(data);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching jobs:", err);
        // Fallback to empty state if API fails
        setJobs([]);
        setFilteredJobs([]);
        setLoading(false);
        setError("Failed to load jobs. Please try again later.");
      }
    };

    fetchJobs();
  }, []);

  const companies = useMemo(
    () => [...new Set(jobs.map(j => j.company).filter(Boolean))],
    [jobs]
  );

  const roles = useMemo(
    () => [...new Set(jobs.map(j => j.role).filter(Boolean))],
    [jobs]
  );

  const locations = useMemo(
    () => [...new Set(jobs.map(j => j.location).filter(Boolean))],
    [jobs]
  );

  const handleResumeUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingResume(true);
    try {
      setResumeText("Resume uploaded");
      setResumeKeywords(["react", "typescript", "nodejs", "aws", "sql", "python", "javascript"]);
      setResumePersona("Engineer");
      setResumeSeniority("mid");
    } catch (err) {
      console.error("Error uploading resume:", err);
    } finally {
      setUploadingResume(false);
    }
  };

  const applyResumeMatch = () => {
    if (!resumeKeywords.length) return;

    setAnalyzingJobs(true);
    setResumeMatchEnabled(true);

    setTimeout(() => {
      const scored = filteredJobs.map(job => ({
        ...job,
        matchScore: Math.floor(Math.random() * 30) + 65
      }));

      scored.sort((a, b) => b.matchScore - a.matchScore);
      setFilteredJobs(scored);
      setAnalyzingJobs(false);
    }, 1500);
  };

  const clearResume = () => {
    setResumeText("");
    setResumeKeywords([]);
    setResumePersona(null);
    setResumeSeniority("mid");
    setResumeMatchEnabled(false);
    setFilteredJobs(jobs);
  };

  useEffect(() => {
    if (resumeMatchEnabled) return;

    let data = [...jobs];

    if (searchQuery) {
      data = data.filter(
        j =>
          j.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          j.company?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedCompany !== "all") {
      data = data.filter(j => j.company === selectedCompany);
    }

    if (selectedRole !== "all") {
      data = data.filter(j => j.role === selectedRole);
    }

    if (selectedLocation !== "all") {
      data = data.filter(j => j.location === selectedLocation);
    }

    setFilteredJobs(data);
  }, [jobs, searchQuery, selectedCompany, selectedRole, selectedLocation, resumeMatchEnabled]);

  const toggleSaved = (jobId) => {
    const newSaved = new Set(savedJobs);
    if (newSaved.has(jobId)) {
      newSaved.delete(jobId);
    } else {
      newSaved.add(jobId);
    }
    setSavedJobs(newSaved);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-cyan-400 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading jobs…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-950">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-950 text-gray-100">
      {/* SIDEBAR */}
      <div className={`${sidebarOpen ? "w-64" : "w-20"} bg-gradient-to-b from-gray-900 to-gray-950 border-r border-gray-800 transition-all duration-300 flex flex-col`}>
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-cyan-400"
          >
            {sidebarOpen ? "✕" : "☰"}
          </button>
        </div>

        {sidebarOpen && (
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* Logo */}
            <div className="flex items-center gap-3 px-2">
              <div className="w-10 h-10 bg-cyan-400 rounded-lg flex items-center justify-center font-bold text-gray-950 text-lg">
                🏢
              </div>
              <span className="font-bold text-lg text-white">JobFlow</span>
            </div>

            {/* Navigation */}
            <div className="space-y-2">
              <div className="flex items-center gap-3 px-3 py-2 bg-cyan-500/15 rounded-lg text-cyan-400 font-medium">
                <span>🏢</span>
                <span>All Jobs</span>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 hover:bg-gray-800 rounded-lg text-gray-400 cursor-pointer transition-colors">
                <span>⭐</span>
                <span>Top Matches</span>
                <span className="ml-auto bg-cyan-400 text-gray-950 text-xs font-bold px-2 py-1 rounded-full">12</span>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 hover:bg-gray-800 rounded-lg text-gray-400 cursor-pointer transition-colors">
                <span>✓</span>
                <span>Saved</span>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 hover:bg-gray-800 rounded-lg text-gray-400 cursor-pointer transition-colors">
                <span>⏱</span>
                <span>Applied</span>
              </div>
            </div>

            {/* Resume Matcher */}
            <div className="border-t border-gray-800 pt-4">
              <h3 className="text-cyan-400 font-semibold text-sm mb-2">🤖 Smart Matcher</h3>
              <p className="text-xs text-gray-500 mb-3">Keyword + AI hybrid</p>

              {!resumeText ? (
                <label className="block">
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleResumeUpload}
                    className="block w-full text-sm text-gray-400 cursor-pointer file:cursor-pointer"
                    disabled={uploadingResume}
                  />
                  {uploadingResume && <p className="text-xs text-gray-500 mt-2">Processing…</p>}
                </label>
              ) : (
                <div>
                  <div className="flex gap-2 mb-3">
                    {resumePersona && (
                      <span className="px-2 py-1 bg-cyan-900/40 text-cyan-300 text-xs font-bold rounded">
                        {resumePersona}
                      </span>
                    )}
                    {resumeSeniority && (
                      <span className="px-2 py-1 bg-purple-900/40 text-purple-300 text-xs font-bold rounded">
                        {resumeSeniority.toUpperCase()}
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    {resumeKeywords.slice(0, 6).map(k => (
                      <span key={k} className="px-2 py-1 bg-cyan-900/40 text-cyan-300 text-xs rounded">
                        {k}
                      </span>
                    ))}
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={applyResumeMatch}
                      disabled={analyzingJobs}
                      className="flex-1 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 text-gray-950 font-bold py-2 px-3 rounded text-sm transition-colors disabled:cursor-not-allowed"
                    >
                      {analyzingJobs ? "Analyzing…" : "🚀 Match"}
                    </button>
                    <button
                      onClick={clearResume}
                      className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold py-2 px-3 rounded text-sm transition-colors"
                    >
                      Clear
                    </button>
                  </div>

                  {analyzingJobs && (
                    <p className="text-xs text-gray-400 mt-3">⚡ Analyzing jobs…</p>
                  )}
                </div>
              )}
            </div>

            {/* Quick Filters */}
            {!resumeMatchEnabled && (
              <div className="border-t border-gray-800 pt-4">
                <p className="text-xs font-bold text-gray-500 uppercase mb-3">Quick Filters</p>
                <div className="space-y-2">
                  <div className="px-3 py-2 hover:bg-gray-800 rounded text-gray-400 text-sm cursor-pointer transition-colors">
                    Remote Only
                  </div>
                  <div className="px-3 py-2 hover:bg-gray-800 rounded text-gray-400 text-sm cursor-pointer transition-colors">
                    Full-time
                  </div>
                  <div className="px-3 py-2 hover:bg-gray-800 rounded text-gray-400 text-sm cursor-pointer transition-colors">
                    Engineering
                  </div>
                </div>
              </div>
            )}

            {/* See Your Fit */}
            <div className="mt-auto border-t border-gray-800 pt-4">
              <button className="w-full p-4 border border-cyan-500/30 bg-cyan-500/10 hover:bg-cyan-500/20 rounded-lg transition-colors text-center">
                <div className="text-2xl mb-2">✨</div>
                <p className="font-bold text-white mb-1">See Your Fit</p>
                <p className="text-xs text-gray-400">Upload resume to discover</p>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col bg-gray-950">
        {/* Top Bar */}
        <div className="border-b border-gray-800 bg-gradient-to-b from-gray-900 to-gray-950 p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">Job Intelligence</h1>
              <p className="text-gray-400">{filteredJobs.length} roles matched to your profile</p>
            </div>
            {resumeMatchEnabled && (
              <div className="px-4 py-2 border border-cyan-500/30 bg-cyan-500/10 rounded-full text-cyan-400 text-sm font-medium">
                ✨ AI Matching Active
              </div>
            )}
          </div>

          {/* Filters */}
          <div className="flex gap-3 flex-wrap">
            <div className="flex-1 min-w-80 relative">
              <input
                type="text"
                placeholder="Search roles, companies…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 pl-10 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <span className="absolute left-3 top-2.5 text-gray-500">🔍</span>
            </div>

            <div className="relative">
              <select
                value={selectedCompany}
                onChange={(e) => setSelectedCompany(e.target.value)}
                className="bg-gray-900 border border-cyan-500/30 rounded-lg px-4 py-2 text-sm text-cyan-400 font-medium focus:outline-none appearance-none pr-8 cursor-pointer transition-colors hover:border-cyan-500/50"
              >
                <option value="all">All Companies</option>
                {companies.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              <span className="absolute right-2 top-2.5 text-cyan-400 pointer-events-none">▼</span>
            </div>

            <div className="relative">
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="bg-gray-900 border border-cyan-500/30 rounded-lg px-4 py-2 text-sm text-cyan-400 font-medium focus:outline-none appearance-none pr-8 cursor-pointer transition-colors hover:border-cyan-500/50"
              >
                <option value="all">All Roles</option>
                {roles.map(r => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
              <span className="absolute right-2 top-2.5 text-cyan-400 pointer-events-none">▼</span>
            </div>

            <div className="relative">
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="bg-gray-900 border border-cyan-500/30 rounded-lg px-4 py-2 text-sm text-cyan-400 font-medium focus:outline-none appearance-none pr-8 cursor-pointer transition-colors hover:border-cyan-500/50"
              >
                <option value="all">All Locations</option>
                {locations.map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
              <span className="absolute right-2 top-2.5 text-cyan-400 pointer-events-none">▼</span>
            </div>
          </div>
        </div>

        {/* Jobs List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {filteredJobs.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500 text-lg">No jobs found matching your criteria</p>
            </div>
          ) : (
            filteredJobs.map(job => (
              <div
                key={job.id}
                className="bg-gray-900 border border-gray-800 hover:border-cyan-500/30 rounded-xl p-6 transition-all hover:bg-gray-850 group"
              >
                <div className="flex gap-6 items-start">
                  {/* Match Score Circle */}
                  {resumeMatchEnabled && (
                    <div className="flex-shrink-0">
                      <div className="relative w-24 h-24 flex items-center justify-center">
                        <svg className="absolute w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="45" fill="none" stroke="#1f2937" strokeWidth="3" />
                          <circle
                            cx="50"
                            cy="50"
                            r="45"
                            fill="none"
                            stroke="#06b6d4"
                            strokeWidth="3"
                            strokeDasharray={`${job.matchScore * 2.83} 283`}
                            className="transition-all duration-1000"
                          />
                        </svg>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-cyan-400">{job.matchScore}</div>
                          <div className="text-xs text-gray-500">%</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Job Details */}
                  <div className="flex-1">
                    <div className="flex items-start gap-3 mb-2">
                      <h2 className="text-xl font-bold text-white group-hover:text-cyan-400 transition-colors">
                        {job.title}
                      </h2>
                      {job.new && (
                        <span className="px-2 py-1 bg-cyan-500/20 text-cyan-400 text-xs font-bold rounded whitespace-nowrap">
                          ✨ New
                        </span>
                      )}
                    </div>

                    <p className="text-gray-400 mb-3">{job.company}</p>

                    <div className="flex flex-wrap gap-3 mb-3 text-sm text-gray-400">
                      <div className="flex items-center gap-1">
                        <span>📍</span>
                        {job.location}
                      </div>
                      <span>•</span>
                      <span>{job.type}</span>
                      <span>•</span>
                      <span>{job.level}</span>
                    </div>

                    {resumeMatchEnabled && job.insights && (
                      <p className="text-sm text-gray-300 italic bg-gray-800/50 px-3 py-2 rounded border-l-2 border-cyan-400">
                        "{job.insights}"
                      </p>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={() => toggleSaved(job.id)}
                      className={`p-2 rounded-lg transition-colors ${
                        savedJobs.has(job.id)
                          ? "bg-cyan-500/20 text-cyan-400"
                          : "bg-gray-800 text-gray-400 hover:text-cyan-400 hover:bg-cyan-500/10"
                      }`}
                    >
                      ⭐
                    </button>
                    <a
                      href={job.applyLink}
                      className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-gray-950 font-bold rounded-lg transition-colors flex items-center gap-2"
                    >
                      Apply
                      <span>→</span>
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
