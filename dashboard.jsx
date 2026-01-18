function App() {
  const [jobs, setJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetch(
      "https://raw.githubusercontent.com/ishwaribangale/job-hunter/main/data/jobs.json"
    )
      .then((res) => res.json())
      .then((data) => setJobs(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6">Loading jobs…</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold">Job Intelligence Dashboard</h1>
      <p className="text-gray-500 mt-1">{jobs.length} jobs found</p>

      <div className="mt-6 space-y-4">
        {jobs.map((job) => (
          <div key={job.id} className="border p-4 rounded-lg">
            <h2 className="font-semibold">{job.title}</h2>

            <p className="text-sm text-gray-600">
              {job.company || "Unknown"} • {job.location || "—"}
            </p>

            <span className="inline-block mt-2 text-xs bg-gray-100 px-2 py-1 rounded">
              Source: {job.source}
            </span>

            <div>
              <a
                href={job.applyLink}
                target="_blank"
                className="text-blue-600 text-sm mt-2 inline-block"
              >
                Apply →
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
