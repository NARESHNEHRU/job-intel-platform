import { salaryLabel, expLabel } from "./lib";

export default function JobCard({
  job,
  saved,
  onToggleSave,
  onOpen,
}) {
  const match = job.match;

  return (
    <div
      className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div
          className="flex-1 cursor-pointer"
          onClick={() => onOpen(job)}
        >
          <h3 className="text-lg font-semibold text-gray-900">
            {job.job_title || "Untitled role"}
          </h3>

          <p className="mt-1 text-sm font-medium text-gray-600">
            {job.company || "Company not mentioned"}
          </p>
        </div>

        <button
          type="button"
          onClick={() => onToggleSave(job.id)}
          className="text-2xl leading-none"
          title={saved ? "Remove from saved jobs" : "Save job"}
        >
          {saved ? "★" : "☆"}
        </button>
      </div>

      <div className="mt-4 space-y-2 text-sm text-gray-600">
        <p>
          📍{" "}
          {job.locations?.length
            ? job.locations.join(", ")
            : "Location not mentioned"}
        </p>

        <p>💼 {expLabel(job)}</p>

        <p>💰 {salaryLabel(job)}</p>

        {job.work_mode && <p>🏢 {job.work_mode}</p>}
      </div>

      {job.skills?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {job.skills.slice(0, 6).map((skill) => (
            <span
              key={skill}
              className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700"
            >
              {skill}
            </span>
          ))}
        </div>
      )}

      {match && (
        <div className="mt-4 rounded-lg bg-gray-50 p-3">
          <p className="font-semibold text-gray-800">
            Match: {match.score}%
          </p>

          {match.reasons?.length > 0 && (
            <p className="mt-1 text-sm text-gray-600">
              {match.reasons[0]}
            </p>
          )}
        </div>
      )}

      <button
        type="button"
        onClick={() => onOpen(job)}
        className="mt-5 w-full rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
      >
        View Details
      </button>
    </div>
  );
}
