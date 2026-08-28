import { Navigate } from "react-router-dom";

import { ROLES } from "../constants/roles";
import { useAuth } from "../hooks/useAuth";

import CandidateJobs from "../features/jobs/candidate/CandidateJobs";
import RecruiterJobs from "../features/jobs/recruiter/RecruiterJobs";

export default function JobsEntryPage() {
  const { user } = useAuth();

  if (user?.role === ROLES.CANDIDATE) {
    return <CandidateJobs />;
  }

  if (user?.role === ROLES.RECRUITER) {
    return <RecruiterJobs />;
  }

  return <Navigate to="/home" replace />;
}
