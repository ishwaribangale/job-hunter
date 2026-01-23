
function App() {
  const [jobs, setJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [filteredJobs, setFilteredJobs] = React.useState([]);
  
  // Filter states
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedSource, setSelectedSource] = React.useState('all');
  const [selectedRole, setSelectedRole] = React.useState('all');
  const [selectedLocation, setSelectedLocation] = React.useState('all');
  const [minScore, setMinScore] = React.useState(0);

  // Load jobs
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

  // Get unique values for filters
  const sources = React.useMemo(() => {
    const uniqueSources = [...new Set(jobs.map(j => j.source))].filter(Boolean);
    return uniqueSources.sort();
  }, [jobs]);

  const roles = React.useMemo(() => {
    const uniqueRoles = [...new Set(jobs.map(j => j.role))].filter(Boolean);
    return uniqueRoles.sort();
  }, [jobs]);

  const locations = React.useMemo(() => {
    const uniqueLocations = [...new Set(jobs.map(j => j.location))].filter(Boolean);
    return uniqueLocations.sort();
  }, [jobs]);

  // Apply filters
  React.useEffect(() => {
    let filtered = jobs;

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(job => 
        job.title?.toLowerCase().includes(query) ||
        job.company?.toLowerCase().includes(query)
      );
    }

    // Source filter
    if (selectedSource !== 'all') {
      filtered = filtered.filter(job => job.source === selectedSource);
    }

    // Role filter
    if (selectedRole !== 'all') {
      filtered = filtered.filter(job => job.role === selectedRole);
    }

    // Location filter
    if (selectedLocation !== 'all') {
      filtered = filtered.filter(job => job.location === selectedLocation);
    }

    // Score filter
    if (minScore > 0) {
      filtered = filtered.filter(job => (job.score || 0) >= minScore);
    }

    setFilteredJobs(filtered);
  }, [jobs, searchQuery, selectedSource, selectedRole, selectedLocation, minScore]);

  // Reset filters
  const resetFilters = () => {
    setSearchQuery('');
    setSelectedSource('all');
    setSelectedRole('all');
    setSelectedLocation('all');
    setMinScore(0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading jobs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Job Intelligence Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Showing {filteredJobs.length} of {jobs.length} jobs
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
                <button
                  onClick={resetFilters}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Reset
                </button>
              </div>

              <div className="space-y-4">
                {/* Search */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Search
                  </label>
                  <input
                    type="text"
                    placeholder="Job title or company..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Source Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Source
                  </label>
                  <select
                    value={selectedSource}
                    onChange={(e) => setSelectedSource(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Sources ({jobs.length})</option>
                    {sources.map(source => (
                      <option key={source} value={source}>
                        {source} ({jobs.filter(j => j.source === source).length})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Role Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role
                  </label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Roles</option>
                    {roles.map(role => (
                      <option key={role} value={role}>
                        {role} ({jobs.filter(j => j.role === role).length})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Location Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <select
                    value={selectedLocation}
                    onChange={(e) => setSelectedLocation(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Locations</option>
                    {locations.map(location => (
                      <option key={location} value={location}>
                        {location} ({jobs.filter(j => j.location === location).length})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Score Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Min Score: {minScore}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={minScore}
                    onChange={(e) => setMinScore(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0</span>
                    <span>100</span>
                  </div>
                </div>
              </div>

              {/* Active Filters Count */}
              <div className="mt-6 pt-4 border-t">
                <p className="text-sm text-gray-600">
                  {[searchQuery, selectedSource !== 'all', selectedRole !== 'all', selectedLocation !== 'all', minScore > 0].filter(Boolean).length} active filters
                </p>
              </div>
            </div>
          </div>

          {/* Jobs List */}
          <div className="lg:col-span-3">
            {filteredJobs.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <p className="text-gray-500 text-lg">No jobs found matching your filters</p>
                <button
                  onClick={resetFilters}
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Reset Filters
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredJobs.map((job) => (
                  <div key={job.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                          {job.title}
                        </h3>
                        <p className="text-gray-600 mt-1">
                          {job.company || "Unknown Company"}
                        </p>
                        
                        <div className="flex flex-wrap gap-2 mt-3">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            📍 {job.location || "Remote"}
                          </span>
                          {job.role && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              💼 {job.role}
                            </span>
                          )}
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            🏢 {job.source}
                          </span>
                          {job.score > 0 && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                              ⭐ Score: {job.score}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <a
                        href={job.applyLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-4 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 whitespace-nowrap"
                      >
                        Apply →
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);

