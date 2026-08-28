import { Outlet } from "react-router-dom";

export default function AuthLayout() {
  return (
    <div className="auth-layout">
      <div className="auth-brand">
        MEDAI
      </div>

      <Outlet />
    </div>
  );
}
