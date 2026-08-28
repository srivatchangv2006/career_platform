import { Navigate } from "react-router-dom";

import { ROLES } from "../constants/roles";
import { useAuth } from "../hooks/useAuth";

import CandidateProfile from "../features/profile/candidate/CandidateProfile";
import RecruiterProfile from "../features/profile/recruiter/RecruiterProfile";

export default function ProfileEntryPage() {
  const { user } = useAuth();

  if (user?.role === ROLES.CANDIDATE) {
    return <CandidateProfile />;
  }

  if (user?.role === ROLES.RECRUITER) {
    return <RecruiterProfile />;
  }

  return <Navigate to="/home" replace />;
}
