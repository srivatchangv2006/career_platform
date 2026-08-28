import { ROLES } from "./roles";

const commonNavigation = [
  {
    label: "Home",
    to: "/home",
  },
  {
    label: "Network",
    to: "/network",
  },
  {
    label: "Jobs",
    to: "/jobs",
  },
  {
    label: "Community",
    to: "/community",
  },
  {
    label: "Messages",
    to: "/messages",
  },
  {
    label: "Referrals",
    to: "/referrals",
  },
];

const candidateNavigation = [
  ...commonNavigation.slice(0, 2),

  {
    label: "Jobs",
    to: "/jobs",
  },

  {
    label: "Applications",
    to: "/applications",
  },

  {
    label: "My Interviews",
    to: "/interviews",
  },

  {
    label: "Community",
    to: "/community",
  },

  {
    label: "Referrals",
    to: "/referrals",
  },

  {
    label: "Messages",
    to: "/messages",
  },
];

const recruiterNavigation = [
  ...commonNavigation.slice(0, 2),

  {
    label: "Jobs",
    to: "/jobs",
  },

  {
    label: "Applicants",
    to: "/recruiter/applicants",
  },

  {
    label: "Community",
    to: "/community",
  },

  {
    label: "Referrals",
    to: "/referrals",
  },

  {
    label: "Messages",
    to: "/messages",
  },
];

const adminNavigation = [
  {
    label: "Dashboard",
    to: "/admin",
  },
  {
    label: "Users",
    to: "/admin/users",
  },
  {
    label: "Jobs",
    to: "/admin/jobs",
  },
  {
    label: "Community",
    to: "/admin/community",
  },
  {
    label: "Reports",
    to: "/admin/reports",
  },
];

export function getNavigationForRole(role) {
  switch (role) {
    case ROLES.CANDIDATE:
      return candidateNavigation;

    case ROLES.RECRUITER:
      return recruiterNavigation;

    case ROLES.ADMIN:
      return adminNavigation;

    default:
      return commonNavigation;
  }
}
