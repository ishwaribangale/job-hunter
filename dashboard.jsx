function App() {
  const [jobs, setJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch(
          "https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json"
        );

        const githubJobs = await response.json();

        const manualJobs =
          JSON.parse(localStorage.getItem("manualJobs")) || [];

        setJobs([...manualJobs, ...githubJobs]);
      } catch (err) {
        console.error("Error loading jobs:", err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    return () => {};
  }, []);

  if (loading) {
    return <div className="p-6">Loading jobs…</div>;
  }

  return (
    <div className="p-6 font-sans max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold">
        Job Intelligence Dashboard
      </h1>

      <p className="text-gray-500 mt-2">
        {jobs.length} jobs found
      </p>

      <div className="mt-6 space-y-4">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="border rounded-lg p-4 shadow-sm"
          >
            <h2 className="font-semibold">
              {job.title || "Untitled Role"}
            </h2>

            <p className="text-sm text-gray-600">
              {job.company || "Unknown Company"}
              {" • "}
              {job.location || "Location not specified"}
            </p>

            {job.matchScore !== undefined && (
              <p className="text-xs text-gray-400 mt-1">
                Match Score: {job.matchScore}
              </p>
            )}

            {job.applyLink && (
              <a
                href={job.applyLink}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 text-sm mt-2 inline-block"
              >
                Apply →
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* 🔥 MANDATORY RENDER */
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
