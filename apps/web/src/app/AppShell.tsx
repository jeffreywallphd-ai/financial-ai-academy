import {
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Link,
  Outlet,
  useLocation,
  useNavigation,
} from "react-router";

import { Icon } from "../components/Icon";
import type { IconName } from "../components/Icon";
import { ThemeControl } from "../platform/theme/theme";


const LESSON_PATH =
  "/learn/placements/intro-risk-return-primary";
const DRAWER_MEDIA_QUERY = "(max-width: 63.99rem)";

interface PlannedNavigationItem {
  label: string;
  icon: IconName;
}

const plannedNavigation: PlannedNavigationItem[] = [
  { label: "Dashboard", icon: "home" },
  { label: "Practice", icon: "practice" },
  { label: "Labs", icon: "labs" },
  { label: "Projects", icon: "projects" },
  { label: "Progress", icon: "progress" },
  { label: "Workspace", icon: "workspace" },
];

const plannedUtilityNavigation: PlannedNavigationItem[] = [
  { label: "Settings", icon: "settings" },
  { label: "Help", icon: "help" },
];

function PlannedNavigation({
  items,
}: {
  items: PlannedNavigationItem[];
}) {
  return items.map((item) => (
    <span
      aria-disabled="true"
      className="primary-nav-item primary-nav-item--unavailable"
      key={item.label}
      title={item.label + " — planned"}
    >
      <Icon name={item.icon} />
      <span className="nav-item-label">{item.label}</span>
      <span aria-hidden="true" className="nav-item-status">
        Planned
      </span>
      <span className="visually-hidden">Not available yet</span>
    </span>
  ));
}

export function AppShell() {
  const navigation = useNavigation();
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerViewport, setDrawerViewport] = useState(() =>
    window.matchMedia(DRAWER_MEDIA_QUERY).matches,
  );
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const isLessonRoute = location.pathname.startsWith(
    "/learn/placements/",
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia(DRAWER_MEDIA_QUERY);
    const updateViewport = (event: MediaQueryListEvent) => {
      setDrawerViewport(event.matches);
      if (!event.matches) {
        setDrawerOpen(false);
      }
    };
    setDrawerViewport(mediaQuery.matches);
    mediaQuery.addEventListener("change", updateViewport);
    return () =>
      mediaQuery.removeEventListener("change", updateViewport);
  }, []);

  useEffect(() => {
    document.body.toggleAttribute(
      "data-navigation-open",
      drawerViewport && drawerOpen,
    );
    if (drawerViewport && drawerOpen) {
      closeButtonRef.current?.focus();
    }
    return () =>
      document.body.removeAttribute("data-navigation-open");
  }, [drawerOpen, drawerViewport]);

  useEffect(() => {
    if (!drawerOpen) {
      return;
    }
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDrawerOpen(false);
        menuButtonRef.current?.focus();
      }
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [drawerOpen]);

  const closeDrawer = (restoreFocus = false) => {
    setDrawerOpen(false);
    if (restoreFocus) {
      menuButtonRef.current?.focus();
    }
  };

  return (
    <div
      className="app-shell"
      data-navigation-open={drawerOpen}
    >
      <a className="skip-link" href="#main-content">
        Skip to lesson
      </a>
      {drawerViewport && drawerOpen ? (
        <button
          aria-label="Close navigation"
          className="navigation-overlay"
          onClick={() => closeDrawer(true)}
          type="button"
        />
      ) : null}
      <aside
        aria-hidden={drawerViewport && !drawerOpen ? "true" : undefined}
        className="app-sidebar"
        inert={drawerViewport && !drawerOpen ? true : undefined}
      >
        <div className="sidebar-brand-row">
          <Link
            aria-label="Financial AI Academy lesson"
            className="brand-link"
            onClick={() => closeDrawer()}
            to={LESSON_PATH}
          >
            <span aria-hidden="true" className="brand-mark">
              <Icon className="faa-icon--lg" name="learn" />
            </span>
            <span className="brand-copy">
              <strong>Financial AI</strong>
              <small>Academy</small>
            </span>
          </Link>
          <button
            aria-label="Close navigation menu"
            className="faa-icon-button sidebar-close-button"
            onClick={() => closeDrawer(true)}
            ref={closeButtonRef}
            title="Close navigation"
            type="button"
          >
            <Icon name="close" />
          </button>
        </div>
        <nav
          aria-label="Primary navigation"
          className="primary-navigation"
          id="primary-navigation"
        >
          <p className="nav-section-label">Learning</p>
          <Link
            aria-current={isLessonRoute ? "page" : undefined}
            className={
              "primary-nav-item" +
              (isLessonRoute ? " primary-nav-item--active" : "")
            }
            onClick={() => closeDrawer()}
            to={LESSON_PATH}
          >
            <Icon
              className={isLessonRoute ? "faa-icon--active" : ""}
              name="learn"
            />
            <span className="nav-item-label">Learn</span>
          </Link>
          <PlannedNavigation items={plannedNavigation} />
          <div className="primary-navigation-utility">
            <PlannedNavigation items={plannedUtilityNavigation} />
          </div>
        </nav>
      </aside>
      <div className="app-shell-content">
        <header className="app-topbar">
          <div className="topbar-location">
            <button
              aria-controls="primary-navigation"
              aria-expanded={drawerOpen}
              aria-label="Open navigation menu"
              className="faa-icon-button navigation-menu-button"
              onClick={() => setDrawerOpen(true)}
              ref={menuButtonRef}
              title="Open navigation"
              type="button"
            >
              <Icon name="menu" />
            </button>
            <span aria-hidden="true" className="topbar-location-icon">
              <Icon name="learn" />
            </span>
            <span>
              <strong>Learn</strong>
              <small>Lesson workspace</small>
            </span>
          </div>
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
      </div>
    </div>
  );
}
