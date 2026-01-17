useEffect(() => {
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
      console.error(err);
    }
  };

  loadData();
  const interval = setInterval(loadData, 5 * 60 * 1000);
  return () => clearInterval(interval);
}, []);

