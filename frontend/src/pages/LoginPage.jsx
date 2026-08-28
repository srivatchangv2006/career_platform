import {
  useState,
} from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  function handleChange(event) {
    setForm((current) => ({
      ...current,
      [event.target.name]:
        event.target.value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(form);
      navigate("/home");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to log in.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-card">
      <p className="eyebrow">MEDAI</p>

      <h1>Welcome back</h1>

      <p className="auth-subtitle">
        Sign in to continue.
      </p>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="auth-form"
      >
        <label>
          Email

          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>

        <label>
          Password

          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          className="primary-button"
        >
          {loading
            ? "Signing in..."
            : "Sign in"}
        </button>
      </form>

      <p className="auth-footer">
        Don't have an account?{" "}
        <Link to="/register">
          Create one
        </Link>
      </p>
    </div>
  );
}
