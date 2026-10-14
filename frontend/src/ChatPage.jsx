
import { useEffect, useRef, useState } from "react";
import { api } from "./lib";
import JobCard from "./JobCard";

const SUGGESTIONS = [
  "Find Python jobs in Chennai",
  "Show fresher jobs",
  "Find AI jobs above 5 LPA",
  "Which jobs match my profile?",
  "Find jobs requiring Python and RAG",
];

const WELCOME = {
  role: "bot",
  text: "Hi! Ask me about the jobs in the database. I only show real jobs, I never make them up.",
  items: [],
};

export default function ChatPage({
  onOpen,
  savedIds,
  onToggleSave,
  isPopup = false,
}) {
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  useEffect(() => {
    if (isPopup) {
      inputRef.current?.focus({ preventScroll: true });
    }
  }, [isPopup]);

  async function send(text, jobId = null) {
    const msg = text.trim();

    if (!msg || loading) return;

    // Remember the jobs from the last answer so "the first one" works.
    const lastItems =
      [...messages].reverse().find((m) => m.items?.length)?.items || [];

    setMessages((prev) => [...prev, { role: "user", text: msg }]);
    setInput("");
    setLoading(true);

    try {
      const data = await api("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          job_id: jobId,
          last_job_ids: lastItems.map((job) => job.id),
        }),
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: data.reply,
          items: data.items || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Sorry, something went wrong: " + err.message,
          items: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`chat-interface ${isPopup ? "chat-interface-popup" : ""}`}>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`chat-message-row ${
              message.role === "user" ? "is-user" : "is-bot"
            }`}
          >
            <div className="chat-message-content">
              <p
                className={`chat-message-bubble ${
                  message.role === "user" ? "user-bubble" : "bot-bubble"
                }`}
              >
                {message.text}
              </p>

              {message.items?.length > 0 && (
                <div className="chat-job-results">
                  {message.items.map((job) => (
                    <div className="chat-job-result" key={job.id}>
                      <JobCard
                        job={job}
                        onOpen={onOpen}
                        saved={savedIds.has(job.id)}
                        onToggleSave={onToggleSave}
                      />

                      <button
                        type="button"
                        onClick={() =>
                          send(
                            "What skills am I missing for this job?",
                            job.id
                          )
                        }
                        disabled={loading}
                        className="chat-skill-gap-button"
                      >
                        ✧ Skill gaps?
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-thinking" role="status" aria-live="polite">
            <span className="chat-thinking-dots" aria-hidden="true">
              <i />
              <i />
              <i />
            </span>
            <span>Thinking… local AI can take a few seconds.</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="chat-suggestions">
        {SUGGESTIONS.map((suggestion) => (
          <button
            type="button"
            key={suggestion}
            onClick={() => send(suggestion)}
            disabled={loading}
            className="chat-suggestion-chip"
          >
            {suggestion}
          </button>
        ))}
      </div>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          send(input);
        }}
        className="chat-composer"
      >
        <input
          ref={inputRef}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask about jobs…"
          aria-label="Ask a question about jobs"
          autoComplete="off"
          className="chat-composer-input"
        />

        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="chat-send-button"
        >
          {loading ? "…" : "↑"}
        </button>
      </form>

      <p className="chat-privacy-note">
        ✦ Answers are based on jobs in your database.
      </p>
    </div>
  );
}
