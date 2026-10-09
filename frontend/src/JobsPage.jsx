import { useEffect, useState } from "react";
import JobCard from "./JobCard";
import { api } from "./lib";

export default function JobsPage({
  savedIds,
  onToggleSave,
  onOpenJob,
}) {
  const [jobs, setJobs] = useState([]);
  const [locations, setLocations] = useState([]);
  const [skills, setSkills] = useState([]);

  const [q, setQ] = useState("");
  const [location, setLocation] = useState("");
  const [skill, setSkill] = useState("");
  const [fresher, setFresher] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadFilters() {
      try {
        const data = await api("/meta/filters");
        setLocations(data.locations || []);
        setSkills(data.skills || []);
      } catch (err) {
        setError(err.message || "Could not load filters.");
      }
    }

    loadFilters();
  }, []);

  async function searchJobs() {
    setLoading(true);
    setError("");

    try {
      let data;

      if (q.trim()) {
        const params = new URLSearchParams();
        params.set("q", q.trim());

        if (location) {
          params.set("location", location);
        }

        if (skill) {
          params.append("skills", skill);
        }

        if (fresher) {
          params.set("fresher", "true");
        }

        params.set("limit", "50");

        data = await api(`/search?${params.toString()}`);
        setJobs(data.items || []);
      } else {
        const params = new URLSearchParams();

        if (location) {
          params.set("location", location);
        }

        if (skill) {
          params.append("skills", skill);
        }

        if (fresher) {
          params.set("fresher", "true");
        }

        params.set("limit", "50");

        data = await api(`/jobs?${params.toString()}`);
        setJobs(data.items || []);
      }
    } catch (err) {
      setError(err.message || "Could not load jobs.");
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }

  function clearSearch() {
    setQ("");
    setLocation("");
    setSkill("");
    setFresher(false);
  }

  useEffect(() => {
    searchJobs();
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Find Jobs
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Search and filter jobs collected from your job sources.
        </p>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <input
            type="text"
            value={q}
            onChange={(event) => setQ(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                searchJobs();
              }
            }}
            placeholder="Search jobs..."
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-black"
          />

          <select
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All locations</option>

            {locations.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>

          <select
            value={skill}
            onChange={(event) => setSkill(event.target.value)}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">All skills</option>

            {skills.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>

          <label className="flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-2 text-sm">
            <input
              type="checkbox"
              checked={fresher}
              onChange={(event) => setFresher(event.target.checked)}
            />

            Fresher / Entry Level
          </label>
        </div>

        <div className="mt-4 flex gap-2">
          <button
            type="button"
            onClick={searchJobs}
            className="rounded-lg bg-black px-5 py-2 text-sm font-medium text-white hover:bg-gray-800"
          >
            Search
          </button>

          <button
            type="button"
            onClick={() => {
              clearSearch();
              setTimeout(searchJobs, 0);
            }}
            className="rounded-lg border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Clear
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-5 rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="mt-6">
        {loading ? (
          <p className="text-gray-500">Loading jobs...</p>
        ) : jobs.length === 0 ? (
          <div className="rounded-xl border border-dashed border-gray-300 p-10 text-center">
            <p className="font-medium text-gray-700">
              No jobs found
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Try changing your search or filters.
            </p>
          </div>
        ) : (
          <>
            <p className="mb-4 text-sm text-gray-500">
              {jobs.length} jobs found
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
    </div>
  );
}