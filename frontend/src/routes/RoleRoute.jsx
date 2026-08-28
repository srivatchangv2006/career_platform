import { Navigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { hasRoleAccess } from "../utils/roleAccess";

export default function RoleRoute({
  allowedRoles,
  children,
}) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="page-loading">
        Loading MEDAI...
      </div>
    );
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  if (
    !hasRoleAccess(
      user.role,
      allowedRoles,
    )
  ) {
    return (
      <Navigate
        to="/home"
        replace
      />
    );
  }

  return children;
}
