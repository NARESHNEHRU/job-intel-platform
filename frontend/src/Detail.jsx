import { useEffect, useState } from "react";
import { api, salaryLabel, expLabel } from "./lib";

export default function Detail({ job, onClose, saved, onToggleSave }) {
  const [details, setDetails] = useState(job);
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDetails() {
      setLoading(true);
      setError("");

      try {
        const [jobData, matchData] = await Promise.all([
          api(`/jobs/${job.id}`),
          api(`/jobs/${job.id}/match`),
        ]);

        if (!active) return;

        setDetails(jobData);
        setMatch(matchData.has_profile ? matchData : null);
      } catch (err) {
        if (active) {
          setError(err.message || "Could not load job details.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDetails();

    return () => {
      active = false;
    };
  }, [job.id]);

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40">
      <div className="h-full w-full max-w-2xl overflow-y-auto bg-white p-6 shadow-xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {details.job_title || "Untitled role"}
            </h2>

            <p className="mt-1 text-gray-600">
              {details.company || "Company not mentioned"}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-3 py-2 text-xl text-gray-500 hover:bg-gray-100"
          >
            ×
          </button>
        </div>

        <button
          type="button"
          onClick={() => onToggleSave(details.id)}
          className="mt-5 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-gray-50"
        >
          {saved ? "★ Saved" : "☆ Save Job"}
        </button>

        {loading && (
          <p className="mt-6 text-gray-500">
            Loading job details...
          </p>
        )}

        {error && (
          <div className="mt-6 rounded-lg bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && (
          <div className="mt-6 space-y-6">
            <section>
              <h3 className="text-lg font-semibold text-gray-900">
                Job Information
              </h3>

              <div className="mt-3 space-y-2 text-sm text-gray-600">
                <p>
                  <strong>Location:</strong>{" "}
                  {details.locations?.length
                    ? details.locations.join(", ")
                    : "Not mentioned"}
                </p>

                <p>
                  <strong>Experience:</strong> {expLabel(details)}
                </p>

                <p>
                  <strong>Salary:</strong> {salaryLabel(details)}
                </p>

                {details.work_mode && (
                  <p>
                    <strong>Work mode:</strong> {details.work_mode}
                  </p>
                )}

                {details.employment_type && (
                  <p>
                    <strong>Employment:</strong> {details.employment_type}
                  </p>
                )}

                {details.education && (
                  <p>
                    <strong>Education:</strong>{" "}
                    {Array.isArray(details.education)
                      ? details.education.join(", ")
                      : details.education}
                  </p>
                )}
              </div>
            </section>

            {details.skills?.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-gray-900">
                  Required Skills
                </h3>

                <div className="mt-3 flex flex-wrap gap-2">
                  {details.skills.map((skill) => (
                    <span
                      key={skill}
                      className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {match && (
              <section className="rounded-xl bg-gray-50 p-5">
                <h3 className="text-lg font-semibold text-gray-900">
                  Why It Matches
                </h3>

                <p className="mt-2 text-2xl font-bold">
                  {match.score}%
                </p>

                {match.reasons?.length > 0 && (
                  <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-gray-600">
                    {match.reasons.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                )}
              </section>
            )}

            {match?.matched_skills?.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-gray-900">
                  Your Matching Skills
                </h3>

                <div className="mt-3 flex flex-wrap gap-2">
                  {match.matched_skills.map((skill) => (
                    <span
                      key={skill}
                      className="rounded-full bg-green-100 px-3 py-1 text-sm text-green-800"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {match?.missing_skills?.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-gray-900">
                  Skill Gaps
                </h3>

                <div className="mt-3 flex flex-wrap gap-2">
                  {match.missing_skills.map((skill) => (
                    <span
                      key={skill}
                      className="rounded-full bg-orange-100 px-3 py-1 text-sm text-orange-800"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {details.application_url && (
              <section>
                <a
                  href={details.application_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-block rounded-lg bg-black px-5 py-3 text-sm font-medium text-white hover:bg-gray-800"
                >
                  Apply Now
                </a>
              </section>
            )}

            {details.original_text && (
              <section>
                <h3 className="text-lg font-semibold text-gray-900">
                  Original Message
                </h3>

                <pre className="mt-3 whitespace-pre-wrap rounded-lg bg-gray-100 p-4 text-sm text-gray-700">
                  {details.original_text}
                </pre>
              </section>
            )}

            {details.warnings?.length > 0 && (
              <section>
                <h3 className="text-lg font-semibold text-gray-900">
                  Data Warnings
                </h3>

                <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-gray-600">
                  {details.warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}