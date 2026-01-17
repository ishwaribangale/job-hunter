function App() {
  const [jobs, setJobs] = React.useState([]);

  React.useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch(
          "https://raw.githubusercontent.com/YOUR-USERNAME/job-hunter/main/data/jobs.json"
        );
        const githubJobs = await response.json();

        const manualJobs =
          JSON.parse(localStorage.getItem("manualJobs")) || [];

        setJobs([...manualJobs, ...githubJobs]);
      } catch (err) {
        console.error("Error loading jobs:", err);
      }
    };

    loadData();
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 font-sans">
      <h1 className="text-2xl font-bold">
        Job Intelligence Dashboard
      </h1>

      <p className="text-gray-500 mt-2">
        {jobs.length} jobs found
      </p>

      <div className="mt-6 space-y-4">
        {jobs.map((job, index) => (
          <div
            key={index}
            className="border rounded-lg p-4 shadow-sm"
          >
            <h2 className="font-semibold">
              {job.title || "Untitled Role"}
            </h2>
            <p className="text-sm text-gray-600">
              {job.company || "Unknown Company"}
            </p>
            {job.link && (
              <a
                href={job.link}
                target="_blank"
                className="text-blue-600 text-sm"
              >
                View Job
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* 🔥 THIS PART IS MANDATORY */
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
