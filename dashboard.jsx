const loadJobsFromGitHub = async () => {
  const response = await fetch(
    "https://raw.githubusercontent.com/YOUR-USERNAME/job-hunter/main/data/jobs.json"
  );
  const jobs = await response.json();
  setJobs(jobs);
};
