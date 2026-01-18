function App() {
  const [jobs, setJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    async function load() {
      const res = await fetch(
        "https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json"
      );
      const data = await res.json();
      setJobs(data);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) return <div className="p-6">Loading…</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto font-sans">
      <h1 className="text-2xl font-bold">Job Intelligence Dashboard</h1>
      <p className="text-gray-500 mt-1">{jobs.length} jobs</p>

      <div className="mt-6 space-y-4">
        {jobs.map(job => (
          <div key={job.id} className="border p-4 rounded-lg">
            <h2 className="font-semibold">{job.title}</h2>

            <p className="text-sm text-gray-600">
              {job.company || "Unknown"} • {job.location || "N/A"}
            </p>

            {job.source && (
              <span className="inline-block mt-1 text-xs px-2 py-0.5 bg-gray-100 rounded">
                Source: {job.source}
              </span>
            )}

            <a
              href={job.applyLink}
              target="_blank"
              className="block mt-2 text-blue-600 text-sm"
            >
              Apply →
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
