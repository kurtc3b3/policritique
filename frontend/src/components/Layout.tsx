import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

const links = [
  { to: "/", label: "Overview", end: true },
  { to: "/elections", label: "Elections" },
  { to: "/members", label: "MPs" },
  { to: "/parties", label: "Parties" },
  { to: "/constituencies", label: "Constituencies" },
  { to: "/manifestos", label: "Manifestos" },
];

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <h1>policritique</h1>
          <p>UK political open data</p>
        </div>
        <nav className="nav-list">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div>{user?.email}</div>
          <button type="button" className="btn btn-ghost" onClick={logout} style={{ marginTop: "0.75rem" }}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
