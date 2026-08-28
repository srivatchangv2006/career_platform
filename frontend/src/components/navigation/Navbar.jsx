import { Link, NavLink } from "react-router-dom";

import { getNavigationForRole } from "../../constants/navigation";
import { useAuth } from "../../hooks/useAuth";
import { useProfile } from "../../hooks/useProfile";
import { getDisplayHandle } from "../../utils/getDisplayHandle";
import UserSearch from "../../features/search/UserSearch";
import Avatar from "../ui/Avatar";

export default function Navbar() {
  const { user, logout } = useAuth();

  const {
    profile,
    loading: profileLoading,
  } = useProfile();

  const navigationItems =
    getNavigationForRole(user?.role);

  const displayHandle =
    getDisplayHandle(user?.email);

  const displayName =
    profile?.full_name ||
    profile?.designation ||
    user?.email ||
    "MEDAI User";

  const avatarName =
    profile?.full_name ||
    user?.email ||
    "MEDAI User";

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="navbar-left">
          <Link
            to="/home"
            className="medai-logo"
          >
            MEDAI
          </Link>

          <div className="navbar-search-wrapper">
            <UserSearch />
          </div>
        </div>

        <nav className="navbar-nav">
          {navigationItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `navbar-link ${
                  isActive
                    ? "navbar-link-active"
                    : ""
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="navbar-right">
          <Link
            to="/profile"
            className="navbar-profile"
          >
            <Avatar
              name={avatarName}
              size="small"
            />

            <div className="navbar-profile-text">
              <span className="navbar-profile-name">
                {profileLoading
                  ? "Loading..."
                  : displayName}
              </span>

              <span className="navbar-profile-handle">
                {displayHandle}
              </span>
            </div>
          </Link>

          <button
            type="button"
            className="logout-button"
            onClick={logout}
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
