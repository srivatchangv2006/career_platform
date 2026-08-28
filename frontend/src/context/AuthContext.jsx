import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getCurrentUser,
  loginUser,
  registerUser,
} from "../api/auth.api";

import AuthContext from "./AuthContext.js";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadCurrentUser = useCallback(async () => {
    const token = localStorage.getItem(
      "medai_access_token",
    );

    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch {
      localStorage.removeItem(
        "medai_access_token",
      );
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Authentication bootstrap: synchronize the
    // persisted token with React application state.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadCurrentUser();
  }, [loadCurrentUser]);

  const login = useCallback(
    async (credentials) => {
      const result = await loginUser(credentials);

      localStorage.setItem(
        "medai_access_token",
        result.access_token,
      );

      await loadCurrentUser();

      return result;
    },
    [loadCurrentUser],
  );

  const register = useCallback(
    async (payload) => {
      return registerUser(payload);
    },
    [],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(
      "medai_access_token",
    );

    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
    }),
    [
      user,
      loading,
      login,
      register,
      logout,
    ],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

