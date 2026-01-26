import React from "react";

export default function Dashboard() {
  const [jobs, setJobs] = React.useState([]);
  const [filteredJobs, setFilteredJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  const [searchQuery, setSearchQuery] = React.useState("");
  const [selectedSource, setSelectedSource] = React.useState("all");
  const [selectedRole, setSelectedRole] = React.useState("all");
  const [selectedLocation, setSelectedLocation] = React.useState("all");

  const [resumeMatchEnabled, setResumeMatchEnabled] = React.useState(false);

  const [activeSection, setActiveSection] = React.useState("all");
  const [savedJobs, setSavedJobs] = React.useState([]);
  const [appliedJobs, setAppliedJobs] = React.useState([]);
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  /* ---------------- FETCH JOBS ---------------- */
  React.useEffect(() => {
    fetch(
      "https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json"
    )
      .then(res => res.json())
      .then(data => {
        setJobs(data);
        setFilteredJobs(data);
      })
      .finally(() => setLoading(false));
  }, []);

  /* ---------------- FILTER VALUES ---------------- */
  const sources = React.useMemo(
    () => [...new Set(jobs.map(j => j?.source).filter(Boolean))],
    [jobs]
  );
  const roles = React.useMemo(
    () => [...new Set(jobs.map(j => j?.role).filter(Boolean))],
    [jobs]
  );
  const locations = React.useMemo(
    () => [...new Set(jobs.map(j => j?.location).filter(Boolean))],
    [jobs]
  );

  /* ---------------- FILTER LOGIC ---------------- */
  React.useEffect(() => {
    if (resumeMatchEnabled) return;

    let data = [...jobs];

    if (searchQuery) {
      data = data.filter(
        j =>
          j.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          j.company?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedSource !== "all")
      data = data.filter(j => j.source === selectedSource);

    if (selectedRole !== "all")
      data = data.filter(j => j.role === selectedRole);

    if (selectedLocation !== "all")
      data = data.filter(j => j.location === selectedLocation);

    setFilteredJobs(data);
  }, [
    jobs,
    searchQuery,
    selectedSource,
    selectedRole,
    selectedLocation,
    resumeMatchEnabled
  ]);

  /* ---------------- SECTION FILTER ---------------- */
  const displayJobs = React.useMemo(() => {
    switch (activeSection) {
      case "top":
        return filteredJobs.filter(j => j.matchScore >= 75);
      case "saved":
        return filteredJobs.filter(j => savedJobs.includes(j.id));
      case "applied":
        return filteredJobs.filter(j => appliedJobs.includes(j.id));
      default:
        return filteredJobs;
    }
  }, [filteredJobs, activeSection, savedJobs, appliedJobs]);

  /* ---------------- ACTIONS ---------------- */
  const toggleSaveJob = id => {
    setSavedJobs(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const markJobAsApplied = id => {
    setAppliedJobs(prev => (prev.includes(id) ? prev : [...prev, id]));
  };

  /* ---------------- SCORE STYLES ---------------- */
  const scoreStyle = score => {
    if (score >= 75) return "border-green-500 text-green-400";
    if (score >= 60) return "border-cyan-400 text-cyan-400";
    if (score >= 45) return "border-yellow-400 text-yellow-400";
    return "border-orange-400 text-orange-400";
  };

  if (loading) {
    return <div className="p-10 text-center text-gray-500">Loading jobs…</div>;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      {/* SIDEBAR */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-16"
        } bg-gray-900 border-r border-gray-800 transition-all`}
      >
        <div className="p-4 flex items-center justify-between">
          {sidebarOpen && <h1 className="text-xl font-bold text-cyan-400">JobFlow</h1>}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-cyan-400"
          >
            {sidebarOpen ? "✕" : "☰"}
          </button>
        </div>

        {sidebarOpen && (
          <nav className="px-4 space-y-2">
            <SidebarButton label="All Jobs" active={activeSection === "all"} onClick={() => setActiveSection("all")} />
            <SidebarButton label="Top Matches" active={activeSection === "top"} onClick={() => setActiveSection("top")} />
            <SidebarButton label="Saved" active={activeSection === "saved"} onClick={() => setActiveSection("saved")} />
            <SidebarButton label="Applied" active={activeSection === "applied"} onClick={() => setActiveSection("applied")} />
          </nav>
        )}
      </aside>

      {/* MAIN */}
      <main className="flex-1 flex flex-col">
        {/* HEADER */}
        <header className="p-6 border-b border-gray-800 bg-gray-900">
          <h2 className="text-3xl font-bold text-cyan-400">Job Intelligence</h2>
          <p className="text-gray-400 mt-1">
            {resumeMatchEnabled
              ? `${displayJobs.length} roles matched`
              : `${displayJobs.length} opportunities available`}
          </p>

          <div className="flex gap-2 mt-4">
            <input
              placeholder="Search roles or companies…"
              className="flex-1 px-4 py-2 bg-gray-800 rounded-lg"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />

            <select className="bg-gray-800 px-3 py-2 rounded" value={selectedSource} onChange={e => setSelectedSource(e.target.value)}>
              <option value="all">All Companies</option>
              {sources.map(s => <option key={s}>{s}</option>)}
            </select>

            <select className="bg-gray-800 px-3 py-2 rounded" value={selectedRole} onChange={e => setSelectedRole(e.target.value)}>
              <option value="all">All Roles</option>
              {roles.map(r => <option key={r}>{r}</option>)}
            </select>

            <select className="bg-gray-800 px-3 py-2 rounded" value={selectedLocation} onChange={e => setSelectedLocation(e.target.value)}>
              <option value="all">All Locations</option>
              {locations.map(l => <option key={l}>{l}</option>)}
            </select>
          </div>
        </header>

        {/* JOB LIST */}
        <section className="p-6 space-y-4 overflow-y-auto">
          {displayJobs.map(job => (
            <div
              key={job.id}
              className="bg-gray-900 border border-gray-800 rounded-lg p-5 flex gap-6"
            >
              {/* MATCH RING */}
              {resumeMatchEnabled && job.matchScore !== undefined && (
                <div
                  className={`w-20 h-20 rounded-full border-4 flex items-center justify-center ${scoreStyle(
                    job.matchScore
                  )}`}
                >
                  <span className="text-xl font-bold">{job.matchScore}</span>
                </div>
              )}

              {/* CONTENT */}
              <div className="flex-1">
                <h3 className="text-xl font-semibold">{job.title}</h3>
                <p className="text-gray-400 text-sm">
                  {job.company} · {job.location}
                </p>

                <div className="flex gap-2 mt-2">
                  {job.role && <Tag>{job.role}</Tag>}
                  {job.employment_type && <Tag>{job.employment_type}</Tag>}
                  {job.source && <Tag>{job.source}</Tag>}
                </div>

                {resumeMatchEnabled && job.insights && (
                  <p className="mt-3 text-sm italic text-gray-300">
                    💡 {job.insights}
                  </p>
                )}
              </div>

              {/* ACTIONS */}
              <div className="flex flex-col gap-2">
                <button
                  onClick={() => toggleSaveJob(job.id)}
                  className={`px-3 py-2 rounded ${
                    savedJobs.includes(job.id)
                      ? "bg-yellow-900/40 text-yellow-400"
                      : "bg-gray-800 text-gray-400"
                  }`}
                >
                  🔖
                </button>

                <a
                  href={job.applyLink}
                  target="_blank"
                  rel="noreferrer"
                  onClick={() => markJobAsApplied(job.id)}
                  className="px-4 py-2 bg-cyan-500 text-gray-900 font-semibold rounded"
                >
                  Apply →
                </a>
              </div>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}

/* ---------------- SMALL COMPONENTS ---------------- */

function SidebarButton({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-2 rounded ${
        active
          ? "bg-cyan-900/30 text-cyan-400"
          : "text-gray-400 hover:bg-gray-800"
      }`}
    >
      {label}
    </button>
  );
}

function Tag({ children }) {
  return (
    <span className="text-xs px-2 py-1 bg-gray-800 rounded text-gray-300">
      {children}
    </span>
  );
}
