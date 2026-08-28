export const ROLES = Object.freeze({
  CANDIDATE: "CANDIDATE",
  RECRUITER: "RECRUITER",
  ADMIN: "ADMIN",
});

export const PUBLIC_ROLES = Object.freeze([
  ROLES.CANDIDATE,
  ROLES.RECRUITER,
]);

export function isCandidate(role) {
  return role === ROLES.CANDIDATE;
}

export function isRecruiter(role) {
  return role === ROLES.RECRUITER;
}

export function isAdmin(role) {
  return role === ROLES.ADMIN;
}
