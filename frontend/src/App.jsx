import { useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Scanner from "./pages/Scanner";
import History from "./pages/History";
import About from "./pages/About";
import { Icon, Logo } from "./components/Common";

const NAV = [
  { to: "/", label: "Overview", icon: "dashboard" },
  { to: "/scan", label: "Check", icon: "scan" },
  { to: "/history", label: "History", icon: "history" },
  { to: "/about", label: "How it works", icon: "info" },
];

export default function App() {
  const [open, setOpen] = useState(false);
  return (
    <div className="shell">
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <Logo />
        <nav>
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.to === "/"} onClick={() => setOpen(false)}>
              <Icon name={n.icon} />{n.label}
            </NavLink>
          ))}
        </nav>
        <p className="side-note">Rule-based checks. Not a guarantee of safety.</p>
      </aside>
      {open && <div className="scrim" onClick={() => setOpen(false)} />}
      <div className="main">
        <div className="topbar">
          <button className="icon-btn" onClick={() => setOpen(true)} aria-label="Open menu"><Icon name="menu" /></button>
          <Logo />
        </div>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scan" element={<Scanner />} />
            <Route path="/history" element={<History />} />
            <Route path="/about" element={<About />} />
            <Route path="*" element={<p className="alert error">Page not found.</p>} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
