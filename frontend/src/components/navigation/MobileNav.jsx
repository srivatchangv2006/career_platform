import { NavLink } from "react-router-dom";

const items = [
  {
    label: "Home",
    to: "/home",
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
    label: "Profile",
    to: "/profile",
  },
];

export default function MobileNav() {
  return (
    <nav className="mobile-nav">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `mobile-nav-link ${
              isActive
                ? "mobile-nav-link-active"
                : ""
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
