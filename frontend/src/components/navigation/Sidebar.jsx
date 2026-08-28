import { NavLink } from "react-router-dom";

import { getNavigationForRole } from "../../constants/navigation";
import { useAuth } from "../../hooks/useAuth";
import { useProfile } from "../../hooks/useProfile";
import { getDisplayHandle } from "../../utils/getDisplayHandle";

import Avatar from "../ui/Avatar";
import Card from "../ui/Card";

export default function Sidebar() {
  const { user } = useAuth();

  const {
    profile,
    loading,
  } = useProfile();

  const menuItems =
    getNavigationForRole(user?.role);

  const displayName =
    profile?.full_name ||
    profile?.designation ||
    user?.email ||
    "MEDAI User";

  const displayHandle =
    getDisplayHandle(user?.email);

  const headline =
    profile?.headline ||
    profile?.designation ||
    "";

  return (
    <aside className="sidebar">
      <Card className="profile-sidebar-card">
        <div className="profile-sidebar-cover" />

        <div className="profile-sidebar-content">
          <Avatar
            name={displayName}
            src={
              profile?.profile_image_blob_path ||
              null
            }
            size="large"
          />

          <h3>
            {loading
              ? "Loading..."
              : displayName}
          </h3>

          <span className="sidebar-handle">
            {displayHandle}
          </span>

          <span className="sidebar-role">
            {user?.role || "USER"}
          </span>

          {headline && (
            <p className="sidebar-headline">
              {headline}
            </p>
          )}

          <NavLink
            to="/profile"
            className="sidebar-profile-link"
          >
            View Profile
          </NavLink>
        </div>
      </Card>

      <Card className="sidebar-menu-card">
        <nav className="sidebar-menu">
          {menuItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </Card>
    </aside>
  );
}
