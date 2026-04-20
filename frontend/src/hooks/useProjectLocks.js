import { useState, useEffect } from "react";
import axios from "axios";

// Module-level cache so all pages share one fetch per session
let lockCache = null;
let fetchPromise = null;

function fetchLocks() {
  if (fetchPromise) return fetchPromise;
  fetchPromise = axios
    .get("/api/v1/closure/project-locks")
    .then((res) => {
      lockCache = res.data.data || {};
      return lockCache;
    })
    .catch(() => {
      lockCache = {};
      return lockCache;
    });
  return fetchPromise;
}

export function useProjectLocks() {
  const [locks, setLocks] = useState(lockCache || {});
  const [loading, setLoading] = useState(lockCache === null);

  useEffect(() => {
    if (lockCache !== null) return;
    fetchLocks().then((data) => {
      setLocks(data);
      setLoading(false);
    });
  }, []);

  /**
   * Returns lock info for a project.
   * @param {number|string|null} projectId
   * @returns {{ can_edit: boolean, can_delete: boolean, status: string|null, locked: boolean }}
   */
  const getProjectLock = (projectId) => {
    if (!projectId)
      return { can_edit: true, can_delete: true, status: null, locked: false };
    const lock = locks[String(projectId)];
    if (!lock)
      return { can_edit: true, can_delete: true, status: null, locked: false };
    return { ...lock, locked: true };
  };

  return { locks, loading, getProjectLock };
}

/** Call this to bust the cache (e.g. after changing closure status) */
export function invalidateProjectLocks() {
  lockCache = null;
  fetchPromise = null;
}
