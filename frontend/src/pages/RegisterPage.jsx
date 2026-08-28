import {
  useState,
} from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: "",
    role: "CANDIDATE",
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
      await register(form);
      navigate("/login");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create account.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-card">
      <p className="eyebrow">MEDAI</p>

      <h1>Create your account</h1>

      <p className="auth-subtitle">
        Join MEDAI and build your
        professional network.
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

        <label>
          Account type

          <select
            name="role"
            value={form.role}
            onChange={handleChange}
          >
            <option value="CANDIDATE">
              Candidate
            </option>

            <option value="RECRUITER">
              Recruiter
            </option>
          </select>
        </label>

        <button
          type="submit"
          disabled={loading}
          className="primary-button"
        >
          {loading
            ? "Creating..."
            : "Create account"}
        </button>
      </form>

      <p className="auth-footer">
        Already have an account?{" "}
        <Link to="/login">
          Sign in
        </Link>
      </p>
    </div>
  );
}
