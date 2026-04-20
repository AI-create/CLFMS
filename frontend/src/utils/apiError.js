/**
 * Extract a readable string from an Axios error.
 * Handles Pydantic v2 detail arrays ({type, loc, msg, ...}) and plain strings.
 */
export function apiError(err, fallback = "An error occurred") {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (Array.isArray(detail)) {
    return detail.map((e) => e.msg || JSON.stringify(e)).join("; ");
  }
  if (typeof detail === "object") return JSON.stringify(detail);
  return String(detail) || fallback;
}
