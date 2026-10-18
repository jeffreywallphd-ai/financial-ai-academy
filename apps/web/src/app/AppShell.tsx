import { Link, NavLink, Outlet, useLocation, useNavigation } from "react-router";

import { Icon } from "../components/Icon";
import { ThemeControl } from "../platform/theme/theme";


export function AppShell() {
  const location = useLocation();
  const navigation = useNavigation();
  const skipLabel = location.pathname.startsWith("/learn/placements/")
    ? "Skip to lesson"
    : location.pathname.startsWith("/help")
      ? "Skip to platform guide"
    : location.pathname.startsWith("/preferences/learning")
      ? "Skip to learning preferences"
    : location.pathname.startsWith("/preferences/display")
      ? "Skip to display and accessibility settings"
    : location.pathname.startsWith("/preferences/assistance")
      ? "Skip to AI help and reminder choices"
    : location.pathname.startsWith("/saved-learning")
      ? "Skip to saved learning"
    : location.pathname.startsWith("/projects")
      ? "Skip to Project content"
      : "Skip to learning content";
  return (
    <>
      <a className="skip-link" href="#main-content">
        {skipLabel}
      </a>
      <header className="app-topbar">
        <Link
          aria-label="Financial AI Academy learning catalog"
          className="brand-link"
          to="/learn"
        >
          <span aria-hidden="true" className="brand-mark">
            <Icon className="faa-icon--lg" name="learn" />
          </span>
          <span>
            <strong>Financial AI Academy</strong>
            <small>Learning before trading</small>
          </span>
        </Link>
        <nav aria-label="Primary" className="app-nav">
          <NavLink to="/learn">Learning library</NavLink>
          <NavLink to="/saved-learning">Saved learning</NavLink>
          <NavLink to="/projects">Projects</NavLink>
          <NavLink to="/preferences/learning">Learning preferences</NavLink>
          <NavLink to="/preferences/display">Display and accessibility</NavLink>
          <NavLink to="/preferences/assistance">AI help and reminders</NavLink>
          <NavLink to="/help">Platform guide</NavLink>
        </nav>
        <ThemeControl />
      </header>
      <main
        aria-busy={navigation.state !== "idle"}
        id="main-content"
        tabIndex={-1}
      >
        <Outlet />
      </main>
      <footer className="app-footer">
        <p>
          Educational content only. The platform does not provide
          personalized investment advice.
        </p>
      </footer>
    </>
  );
}
