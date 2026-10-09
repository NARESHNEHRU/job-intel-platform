const API = "http://127.0.0.1:8000";

export async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  return response.json();
}

export function salaryLabel(job) {
  if (job.salary_text) {
    return job.salary_text;
  }

  const min = job.salary_min_inr;
  const max = job.salary_max_inr;

  if (min && max) {
    return `₹${(min / 100000).toFixed(1)}–₹${(max / 100000).toFixed(1)} LPA`;
  }

  if (max) {
    return `Up to ₹${(max / 100000).toFixed(1)} LPA`;
  }

  if (min) {
    return `From ₹${(min / 100000).toFixed(1)} LPA`;
  }

  return "Salary not mentioned";
}

export function expLabel(job) {
  const min = job.experience_min_years;
  const max = job.experience_max_years;

  if (min === null && max === null) {
    return "Experience not mentioned";
  }

  if (min !== null && max !== null) {
    if (min === max) {
      return `${min} years`;
    }

    return `${min}–${max} years`;
  }

  if (min !== null) {
    return `${min}+ years`;
  }

  return `Up to ${max} years`;
}
