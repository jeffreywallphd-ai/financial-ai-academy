import { Link, Outlet, useNavigation } from "react-router";

import { Icon } from "../components/Icon";
import { ThemeControl } from "../platform/theme/theme";


export function AppShell() {
  const navigation = useNavigation();
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to lesson
      </a>
      <header className="app-topbar">
        <Link
          aria-label="Financial AI Academy lesson"
          className="brand-link"
          to="/learn/placements/intro-risk-return-primary"
        >
          <span aria-hidden="true" className="brand-mark">
            <Icon className="faa-icon--lg" name="learn" />
          </span>
          <span>
            <strong>Financial AI Academy</strong>
            <small>Learning before trading</small>
          </span>
        </Link>
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
