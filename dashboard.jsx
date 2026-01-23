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

  // NEW: Resume matching states
  const [resumeText, setResumeText] = React.useState('');
  const [resumeKeywords, setResumeKeywords] = React.useState([]);
  const [resumeMatchEnabled, setResumeMatchEnabled] = React.useState(false);
  const [uploadingResume, setUploadingResume] = React.useState(false);

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

  // NEW: Extract keywords from resume text
  const extractKeywords = (text) => {
    const techKeywords = [
      'javascript', 'python', 'java', 'react', 'node', 'angular', 'vue',
      'typescript', 'sql', 'mongodb', 'aws', 'azure', 'docker', 'kubernetes',
      'frontend', 'backend', 'fullstack', 'devops', 'data science', 'machine learning',
      'ai', 'product manager', 'designer', 'ux', 'ui', 'marketing', 'sales',
      'engineer', 'developer', 'analyst', 'manager', 'lead', 'senior', 'junior',
      'intern', 'django', 'flask', 'spring', 'git', 'agile', 'scrum', 'api',
      'rest', 'graphql', 'html', 'css', 'tailwind', 'bootstrap', 'figma', 'sketch'
    ];

    const lowerText = text.toLowerCase();
    const found = techKeywords.filter(kw => lowerText.includes(kw));
    
    return [...new Set(found)]; // Remove duplicates
  };

  // NEW: Calculate match score between resume and job
  const calculateMatchScore = (job, keywords) => {
    if (!keywords.length) return 0;
    
    const jobText = `${job.title} ${job.company} ${job.role || ''}`.toLowerCase();
    const matches = keywords.filter(kw => jobText.includes(kw));
    
    return Math.round((matches.length / keywords.length) * 100);
  };

  // NEW: Handle resume upload
  const handleResumeUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file');
      return;
    }

    setUploadingResume(true);

    try {
      const fileReader = new FileReader();
      
      fileReader.onload = async function() {
        const typedArray = new Uint8Array(this.result);
        
        // Load PDF
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
        const keywords = extractKeywords(fullText);
        setResumeKeywords(keywords);
        setResumeMatchEnabled(true);
        setUploadingResume(false);
        
        alert(`Resume analyzed! Found ${keywords.length} skills: ${keywords.slice(0, 10).join(', ')}${keywords.length > 10 ? '...' : ''}`);
      };
      
      fileReader.readAsArrayBuffer(file);
    } catch (error) {
      console.error('Error parsing PDF:', error);
      alert('Error reading resume. Please try again.');
      setUploadingResume(false);
    }
  };

  // NEW: Clear resume
  const clearResume = () => {
    setResumeText('');
    setResumeKeywords([]);
    setResumeMatchEnabled(false);
    document.getElementById('resume-input').value = '';
  };

  // Apply filters (MODIFIED to include resume matching)
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

    // NEW: Resume matching filter
    if (resumeMatchEnabled && resumeKeywords.length > 0) {
      filtered = filtered.map(job => ({
        ...job,
        matchScore: calculateMatchScore(job, resumeKeywords)
      })).filter(job => job.matchScore > 0)
        .sort((a, b) => b.matchScore - a.matchScore);
    }

    setFilteredJobs(filtered);
  }, [jobs, searchQuery, selectedSource, selectedRole, selectedLocation, minScore, resumeMatchEnabled, resumeKeywords]);

  // Reset filters (MODIFIED)
  const resetFilters = () => {
    setSearchQuery('');
    setSelectedSource('all');
    setSelectedRole('all');
    setSelectedLocation('all');
    setMinScore(0);
    clearResume();
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
            {resumeMatchEnabled && <span className="text-blue-600 ml-2">• Resume Match Active</span>}
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6 space-y-6">
              
              {/* NEW: Resume Upload Section */}
              <div className="pb-6 border-b">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">📄 Resume Match</h2>
                
                {!resumeMatchEnabled ? (
                  <div>
                    <label className="block">
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-blue-500 transition">
                        <input
                          id="resume-input"
                          type="file"
                          accept=".pdf"
                          onChange={handleResumeUpload}
                          className="hidden"
                          disabled={uploadingResume}
                        />
                        {uploadingResume ? (
                          <div>
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                            <p className="text-sm text-gray-600">Analyzing resume...</p>
                          </div>
                        ) : (
                          <div>
                            <div className="text-4xl mb-2">📤</div>
                            <p className="text-sm text-gray-700 font-medium">Upload Resume (PDF)</p>
                            <p className="text-xs text-gray-500 mt-1">Get personalized job matches</p>
                          </div>
                        )}
                      </div>
                    </label>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <p className="text-sm font-medium text-green-800">✓ Resume Analyzed</p>
                      <p className="text-xs text-green-600 mt-1">{resumeKeywords.length} skills detected</p>
                    </div>
                    
                    <div className="flex flex-wrap gap-1">
                      {resumeKeywords.slice(0, 8).map(kw => (
                        <span key={kw} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                          {kw}
                        </span>
                      ))}
                      {resumeKeywords.length > 8 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                          +{resumeKeywords.length - 8} more
                        </span>
                      )}
                    </div>
                    
                    <button
                      onClick={clearResume}
                      className="w-full px-3 py-2 bg-red-50 text-red-600 text-sm rounded-md hover:bg-red-100 transition"
                    >
                      Clear Resume
                    </button>
                  </div>
                )}
              </div>

              {/* Filters Header */}
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
                <button
                  onClick={resetFilters}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Reset All
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
              <div className="pt-4 border-t">
                <p className="text-sm text-gray-600">
                  {[searchQuery, selectedSource !== 'all', selectedRole !== 'all', selectedLocation !== 'all', minScore > 0, resumeMatchEnabled].filter(Boolean).length} active filters
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
                        <div className="flex items-start gap-3">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                              {job.title}
                            </h3>
                            <p className="text-gray-600 mt-1">
                              {job.company || "Unknown Company"}
                            </p>
                          </div>
                          
                          {/* NEW: Match Score Badge */}
                          {resumeMatchEnabled && job.matchScore > 0 && (
                            <div className="flex-shrink-0">
                              <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                                job.matchScore >= 70 ? 'bg-green-100 text-green-800' :
                                job.matchScore >= 40 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {job.matchScore}% Match
                              </div>
                            </div>
                          )}
                        </div>
                        
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
