import { useEffect, useState } from "react";
import "./App.css";

import Detail from "./Detail";
import ForYouPage from "./ForYouPage";
import JobsPage from "./JobsPage";
import ProfilePage from "./ProfilePage";
import SavedPage from "./SavedPage";
import { api } from "./lib";

export default function App() {
  const [page, setPage] = useState("jobs");
  const [savedIds, setSavedIds] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadSavedIds();
  }, []);

  async function loadSavedIds() {
    try {
      const ids = await api("/saved/ids");
      setSavedIds(ids || []);
    } catch (err) {
      setError(err.message || "Could not load saved jobs.");
    }
  }

  async function toggleSave(jobId) {
    setError("");

    const isSaved = savedIds.includes(jobId);

    try {
      if (isSaved) {
        await api(`/saved/${jobId}`, {
          method: "DELETE",
        });

        setSavedIds((current) =>
          current.filter((id) => id !== jobId)
        );
      } else {
        await api(`/saved/${jobId}`, {
          method: "POST",
        });

        setSavedIds((current) => [...current, jobId]);
      }
    } catch (err) {
      setError(err.message || "Could not update saved job.");
    }
  }

  function openJob(job) {
    setSelectedJob(job);
  }

  function closeJob() {
    setSelectedJob(null);
  }

  function renderPage() {
    if (page === "jobs") {
      return (
        <JobsPage
          savedIds={savedIds}
          onToggleSave={toggleSave}
          onOpenJob={openJob}
        />
      );
    }

    if (page === "foryou") {
      return (
        <ForYouPage
          savedIds={savedIds}
          onToggleSave={toggleSave}
          onOpenJob={openJob}
        />
      );
    }

    if (page === "saved") {
      return (
        <SavedPage
          savedIds={savedIds}
          onToggleSave={toggleSave}
          onOpenJob={openJob}
        />
      );
    }

    if (page === "profile") {
      return <ProfilePage />;
    }

    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <button
            type="button"
            onClick={() => setPage("jobs")}
            className="text-xl font-bold text-gray-900"
          >
            AI Job Intelligence
          </button>

          <nav className="flex gap-2">
            <button
              type="button"
              onClick={() => setPage("jobs")}
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                page === "jobs"
                  ? "bg-black text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              Jobs
            </button>

            <button
              type="button"
              onClick={() => setPage("foryou")}
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                page === "foryou"
                  ? "bg-black text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              For You
            </button>

            <button
              type="button"
              onClick={() => setPage("saved")}
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                page === "saved"
                  ? "bg-black text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              Saved
            </button>

            <button
              type="button"
              onClick={() => setPage("profile")}
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                page === "profile"
                  ? "bg-black text-white"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              Profile
            </button>
          </nav>
        </div>
      </header>

      {error && (
        <div className="mx-auto mt-4 max-w-7xl px-6">
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        </div>
      )}

      <main className="mx-auto max-w-7xl px-6 py-8">
        {renderPage()}
      </main>

      {selectedJob && (
        <Detail
          job={selectedJob}
          saved={savedIds.includes(selectedJob.id)}
          onToggleSave={toggleSave}
          onClose={closeJob}
        />
      )}
    </div>
  );
}