import { type FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await register(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create account</h1>
        <p>Register to query election results, MPs, and manifestos.</p>
        {error && <div className="error-banner">{error}</div>}
        <form className="form-stack" onSubmit={handleSubmit}>
          <label>
            Email
            <input
              className="input"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              className="input"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />
          </label>
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? "Creating account…" : "Register"}
          </button>
        </form>
        <p style={{ marginTop: "1.25rem" }}>
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
