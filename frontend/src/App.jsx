import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Registry from "./pages/Registry";
import RiskClassifier from "./pages/RiskClassifier";
import ValidationTracker from "./pages/ValidationTracker";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <div className="header-brand">
            <h1>GxP-Gov</h1>
            <span className="header-tagline">AI Governance for Regulated Pharma</span>
          </div>
          <nav className="header-nav">
            <NavLink to="/" end className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Registry
            </NavLink>
            <NavLink to="/classify" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Risk Classifier
            </NavLink>
            <NavLink to="/validation" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Validation
            </NavLink>
          </nav>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Registry />} />
            <Route path="/classify" element={<RiskClassifier />} />
            <Route path="/validation" element={<ValidationTracker />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}