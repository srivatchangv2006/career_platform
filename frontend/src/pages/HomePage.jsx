import { Navigate } from "react-router-dom";

import { ROLES } from "../constants/roles";
import { useAuth } from "../hooks/useAuth";

import CandidateDashboard from "../features/home/candidate/CandidateDashboard";
import RecruiterDashboard from "../features/home/recruiter/RecruiterDashboard";

export default function HomePage() {
  const { user } = useAuth();

  if (user?.role === ROLES.CANDIDATE) {
    return <CandidateDashboard />;
  }

  if (user?.role === ROLES.RECRUITER) {
    return <RecruiterDashboard />;
  }

  return <Navigate to="/login" replace />;
}
