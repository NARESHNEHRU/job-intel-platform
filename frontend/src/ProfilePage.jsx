import { useEffect, useState } from "react";
import { api } from "./lib";

export default function ProfilePage() {
  const [form, setForm] = useState({
    name: "",
    skills: [],
    experience_years: 0,
    education: "",
    preferred_roles: "",
    preferred_locations: [],
    min_salary_lpa: null,
    work_mode: null,
  });

  const [skillsText, setSkillsText] = useState("");
  const [locationsText, setLocationsText] = useState("");

  const [resume, setResume] = useState(null);
  const [detected, setDetected] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await api("/profile");

        setForm({
          name: data.name || "",
          skills: data.skills || [],
          experience_years: data.experience_years || 0,
          education: data.education || "",
          preferred_roles: data.preferred_roles || "",
          preferred_locations: data.preferred_locations || [],
          min_salary_lpa: data.min_salary_lpa ?? null,
          work_mode: data.work_mode || null,
        });

        setSkillsText((data.skills || []).join(", "));
        setLocationsText(
          (data.preferred_locations || []).join(", ")
        );
      } catch (err) {
        setError(err.message || "Could not load profile.");
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  function updateField(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function saveProfile() {
    setSaving(true);
    setMessage("");
    setError("");

    try {
      const data = await api("/profile", {
        method: "PUT",
        body: JSON.stringify({
          ...form,
          skills: skillsText
            .split(",")
            .map((skill) => skill.trim())
            .filter(Boolean),
          preferred_locations: locationsText
            .split(",")
            .map((location) => location.trim())
            .filter(Boolean),
        }),
      });

      setForm(data);
      setSkillsText((data.skills || []).join(", "));
      setLocationsText(
        (data.preferred_locations || []).join(", ")
      );

      setMessage("Profile saved successfully.");
    } catch (err) {
      setError(err.message || "Could not save profile.");
    } finally {
      setSaving(false);
    }
  }

  async function uploadResume() {
    if (!resume) {
      setError("Please select a PDF, DOCX or TXT resume first.");
      return;
    }

    setUploading(true);
    setMessage("");
    setError("");

    try {
      const body = new FormData();
      body.append("file", resume);

      const response = await fetch(
        "http://127.0.0.1:8000/profile/resume",
        {
          method: "POST",
          body,
        }
      );

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(
          data.detail || `Upload failed: ${response.status}`
        );
      }

      const data = await response.json();

      setDetected(data);

      if (data.skills?.length) {
        const existing = skillsText
          .split(",")
          .map((skill) => skill.trim())
          .filter(Boolean);

        const merged = [...existing];

        for (const skill of data.skills) {
          if (
            !merged.some(
              (item) => item.toLowerCase() === skill.toLowerCase()
            )
          ) {
            merged.push(skill);
          }
        }

        setSkillsText(merged.join(", "));
      }

      if (data.education) {
        updateField("education", data.education);
      }

      setMessage(
        "Resume processed. Review the detected information and save your profile."
      );
    } catch (err) {
      setError(err.message || "Could not process resume.");
    } finally {
      setUploading(false);
    }
  }

  if (loading) {
    return (
      <p className="text-gray-500">
        Loading profile...
      </p>
    );
  }

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          My Profile
        </h1>

        <p className="mt-1 text-sm text-gray-500">
          Add your skills and preferences to improve job
          recommendations.
        </p>
      </div>

      {message && (
        <div className="mb-4 rounded-lg bg-green-50 p-4 text-sm text-green-700">
          {message}
        </div>
      )}

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="space-y-6">
        <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">
            Resume
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Upload a PDF, DOCX or TXT resume to detect skills and
            education.
          </p>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(event) =>
                setResume(event.target.files?.[0] || null)
              }
              className="block w-full rounded-lg border border-gray-300 p-2 text-sm"
            />

            <button
              type="button"
              onClick={uploadResume}
              disabled={uploading}
              className="rounded-lg bg-black px-5 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {uploading ? "Processing..." : "Upload Resume"}
            </button>
          </div>

          {detected && (
            <div className="mt-4 rounded-lg bg-gray-50 p-4">
              <p className="text-sm font-semibold text-gray-800">
                Detected Skills
              </p>

              <p className="mt-1 text-sm text-gray-600">
                {detected.skills?.length
                  ? detected.skills.join(", ")
                  : "No skills detected"}
              </p>

              <p className="mt-3 text-sm font-semibold text-gray-800">
                Detected Education
              </p>

              <p className="mt-1 text-sm text-gray-600">
                {detected.education || "Not detected"}
              </p>
            </div>
          )}
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">
            Profile Information
          </h2>

          <div className="mt-4 space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">
                Name
              </label>

              <input
                value={form.name}
                onChange={(event) =>
                  updateField("name", event.target.value)
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Skills
              </label>

              <input
                value={skillsText}
                onChange={(event) =>
                  setSkillsText(event.target.value)
                }
                placeholder="Python, React, SQL, RAG"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />

              <p className="mt-1 text-xs text-gray-500">
                Separate skills with commas.
              </p>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Experience (years)
              </label>

              <input
                type="number"
                min="0"
                max="40"
                step="0.5"
                value={form.experience_years}
                onChange={(event) =>
                  updateField(
                    "experience_years",
                    Number(event.target.value)
                  )
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Education
              </label>

              <input
                value={form.education}
                onChange={(event) =>
                  updateField("education", event.target.value)
                }
                placeholder="B.Tech IT"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Preferred Roles
              </label>

              <input
                value={form.preferred_roles}
                onChange={(event) =>
                  updateField(
                    "preferred_roles",
                    event.target.value
                  )
                }
                placeholder="AI Engineer, Python Developer"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Preferred Locations
              </label>

              <input
                value={locationsText}
                onChange={(event) =>
                  setLocationsText(event.target.value)
                }
                placeholder="Chennai, Bengaluru"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Minimum Salary (LPA)
              </label>

              <input
                type="number"
                min="0"
                step="0.1"
                value={form.min_salary_lpa ?? ""}
                onChange={(event) =>
                  updateField(
                    "min_salary_lpa",
                    event.target.value === ""
                      ? null
                      : Number(event.target.value)
                  )
                }
                placeholder="5"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium">
                Work Mode
              </label>

              <select
                value={form.work_mode || ""}
                onChange={(event) =>
                  updateField(
                    "work_mode",
                    event.target.value || null
                  )
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              >
                <option value="">Any</option>
                <option value="Remote">Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="Onsite">Onsite</option>
              </select>
            </div>
          </div>

          <button
            type="button"
            onClick={saveProfile}
            disabled={saving}
            className="mt-6 rounded-lg bg-black px-6 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Profile"}
          </button>
        </section>
      </div>
    </div>
  );
}