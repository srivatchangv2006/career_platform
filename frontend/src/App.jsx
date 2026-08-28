import { AuthProvider } from "./context/AuthContext.jsx";
import { ProfileProvider } from "./context/ProfileContext.jsx";
import AppRoutes from "./routes/AppRoutes";

export default function App() {
  return (
    <AuthProvider>
      <ProfileProvider>
        <AppRoutes />
      </ProfileProvider>
    </AuthProvider>
  );
}
