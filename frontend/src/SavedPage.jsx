import { useEffect, useState } from "react";
import JobCard from "./JobCard";
import { api } from "./lib";

export default function SavedPage({
  savedIds,
  onToggleSave,
  onOpenJob,
}) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadSavedJobs() {
    setLoading(true);
    setError("");

    try {
      const data = await api("/saved");
      setJobs(data.items || []);
    } catch (err) {
      setError(err.message || "Could not load saved jobs.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSavedJobs();
  }, [savedIds.length]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Saved Jobs
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Jobs you saved for later.
        </p>
      </div>

      {loading && (
        <p className="text-gray-500">
          Loading saved jobs...
        </p>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && !error && jobs.length === 0 && (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white p-8 text-center">
          <h2 className="text-lg font-semibold text-gray-900">
            No saved jobs
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Save jobs you are interested in and they will appear here.
          </p>
        </div>
      )}

      {!loading && !error && jobs.length > 0 && (
        <>
          <p className="mb-4 text-sm text-gray-500">
            {jobs.length} saved jobs
          </p>

          <div className="grid gap-5 md:grid-cols-2">
            {jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                saved={savedIds.includes(job.id)}
                onToggleSave={onToggleSave}
                onOpen={onOpenJob}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}