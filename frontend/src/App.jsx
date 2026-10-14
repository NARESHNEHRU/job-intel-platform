
import { useEffect, useState } from "react";
import "./App.css";
import ChatPage from "./ChatPage";
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
  const [aiOpen, setAiOpen] = useState(false);

  useEffect(() => {
    loadSavedIds();
  }, []);

  useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape") {
        setAiOpen(false);
      }
    }

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
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
    setAiOpen(false);
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
    <div className="app-shell min-h-screen">
      <div className="neon-fog" aria-hidden="true" />

      <header className="app-header">
        <div className="app-header-inner">
          <button
            type="button"
            onClick={() => setPage("jobs")}
            className="app-brand"
            aria-label="AI Job Intelligence home"
          >
            <span className="app-brand-icon">
              <span>✦</span>
            </span>

            <span className="app-brand-text">
              <span className="app-brand-title">
                AI Job <span>Intelligence</span>
              </span>

              <span className="app-brand-subtitle">
                Your career, intelligently matched.
              </span>
            </span>
          </button>

          <nav className="app-nav" aria-label="Main navigation">
            <button
              type="button"
              onClick={() => setPage("jobs")}
              className={`app-nav-link ${page === "jobs" ? "active" : ""}`}
              aria-current={page === "jobs" ? "page" : undefined}
            >
              <span className="app-nav-icon">⌕</span>
              <span>Jobs</span>
            </button>

            <button
              type="button"
              onClick={() => setPage("foryou")}
              className={`app-nav-link ${page === "foryou" ? "active" : ""}`}
              aria-current={page === "foryou" ? "page" : undefined}
            >
              <span className="app-nav-icon">✧</span>
              <span>For You</span>
            </button>
            <button
              type="button"
              onClick={() => setPage("saved")}
              className={`app-nav-link ${page === "saved" ? "active" : ""}`}
              aria-current={page === "saved" ? "page" : undefined}
            >
              <span className="app-nav-icon">♡</span>
              <span>Saved</span>
            </button>

            <button
              type="button"
              onClick={() => setPage("profile")}
              className={`app-nav-link ${page === "profile" ? "active" : ""}`}
              aria-current={page === "profile" ? "page" : undefined}
            >
              <span className="app-nav-icon">◎</span>
              <span>Profile</span>
            </button>
          </nav>
        </div>
      </header>

      {error && (
        <div className="mx-auto mt-4 max-w-7xl px-6">
          <div className="rounded-lg border border-red-400/20 bg-red-500/10 p-3 text-sm text-red-200">
            {error}
          </div>
        </div>
      )}

      <main className="mx-auto max-w-7xl px-6 py-8">
        {renderPage()}
      </main>
      {/* Floating Ask AI chat.
          Keep it mounted when closed so the conversation is preserved. */}
      <section
        id="floating-ai-chat"
        className={`ai-chat-panel ${aiOpen ? "is-open" : ""}`}
        aria-label="Ask AI chat"
        aria-hidden={!aiOpen}
        inert={!aiOpen}
      >
        <div className="ai-chat-panel-header">
          <div className="ai-chat-heading">
            <span className="ai-chat-avatar">✳</span>
            <span>
              <strong>Ask AI</strong>
              <small>Job intelligence assistant</small>
            </span>
          </div>

          <button
            type="button"
            className="ai-chat-close"
            onClick={() => setAiOpen(false)}
            aria-label="Close Ask AI"
          >
            ×
          </button>
        </div>

        <div className="ai-chat-panel-body">
          <ChatPage
            onOpen={openJob}
            savedIds={new Set(savedIds)}
            onToggleSave={toggleSave}
            isPopup
          />
        </div>
      </section>

      <button
        type="button"
        className={`ai-floating-button ${aiOpen ? "is-open" : ""}`}
        onClick={() => setAiOpen((open) => !open)}
        aria-label={aiOpen ? "Close Ask AI chat" : "Open Ask AI chat"}
        aria-expanded={aiOpen}
        aria-controls="floating-ai-chat"
      >
        <span className="ai-floating-icon">{aiOpen ? "×" : "✳"}</span>
        <span className="ai-floating-label">
          {aiOpen ? "Close AI" : "Ask AI"}
        </span>
        {!aiOpen && <span className="ai-floating-status" />}
      </button>

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
