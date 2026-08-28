import { ROLES } from "../constants/roles";

export const ROLE_ACCESS = Object.freeze({
  HOME: [
    ROLES.CANDIDATE,
    ROLES.RECRUITER,
    ROLES.ADMIN,
  ],

  PROFILE: [
    ROLES.CANDIDATE,
    ROLES.RECRUITER,
    ROLES.ADMIN,
  ],

  NETWORK: [
    ROLES.CANDIDATE,
    ROLES.RECRUITER,
  ],

  JOBS: [
    ROLES.CANDIDATE,
    ROLES.RECRUITER,
  ],

  APPLICATIONS: [
    ROLES.CANDIDATE,
  ],

  RECRUITER: [
    ROLES.RECRUITER,
  ],

  COMMUNITY: [
    ROLES.CANDIDATE,
    ROLES.RECRUITER,
  ],

  REFERRALS: [
    ROLES.CANDIDATE,
    ROLES.RECRUITER,
  ],

  MESSAGES: [
    ROLES.CANDIDATE,
    ROLES.RECRUITER,
  ],

  ADMIN: [
    ROLES.ADMIN,
  ],
});

export function hasRoleAccess(
  role,
  allowedRoles,
) {
  return allowedRoles.includes(role);
}
