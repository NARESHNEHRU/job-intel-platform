import { useEffect, useState } from "react";
import JobCard from "./JobCard";
import { api } from "./lib";

export default function ForYouPage({
  savedIds,
  onToggleSave,
  onOpenJob,
}) {
  const [jobs, setJobs] = useState([]);
  const [hasProfile, setHasProfile] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadRecommendations() {
    setLoading(true);
    setError("");

    try {
      const data = await api("/recommendations?limit=20");

      setHasProfile(data.has_profile);
      setJobs(data.items || []);
    } catch (err) {
      setError(
        err.message || "Could not load recommendations."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRecommendations();
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          For You
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Jobs ranked based on your profile, skills, experience,
          location and preferences.
        </p>
      </div>

      {loading && (
        <p className="text-gray-500">
          Finding the best jobs for you...
        </p>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && !error && !hasProfile && (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white p-8 text-center">
          <h2 className="text-lg font-semibold text-gray-900">
            Set up your profile first
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Add your skills or preferred roles to get personalized
            job recommendations.
          </p>
        </div>
      )}

      {!loading && !error && hasProfile && jobs.length === 0 && (
        <div className="rounded-xl border border-dashed border-gray-300 bg-white p-8 text-center">
          <h2 className="text-lg font-semibold text-gray-900">
            No recommendations yet
          </h2>

          <p className="mt-2 text-sm text-gray-500">
            Try adding more skills or preferences to your profile.
          </p>
        </div>
      )}

      {!loading && !error && hasProfile && jobs.length > 0 && (
        <>
          <p className="mb-4 text-sm text-gray-500">
            {jobs.length} recommended jobs
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