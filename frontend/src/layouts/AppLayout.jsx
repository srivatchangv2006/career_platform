import { Outlet } from "react-router-dom";

import Navbar from "../components/navigation/Navbar";
import Sidebar from "../components/navigation/Sidebar";
import MobileNav from "../components/navigation/MobileNav";

export default function AppLayout() {
  return (
    <div className="app-shell">
      <Navbar />

      <div className="app-body">
        <Sidebar />

        <main className="app-content">
          <Outlet />
        </main>
      </div>

      <MobileNav />
    </div>
  );
}
