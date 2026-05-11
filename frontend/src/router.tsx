import { createRouter, createRoute, createRootRoute } from "@tanstack/react-router";
import { App } from "./app";
import { IdeShell } from "./components/ide/ide-shell";

const rootRoute = createRootRoute();

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: App,
});

const ideRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/ide",
  component: IdeShell,
});

const routeTree = rootRoute.addChildren([loginRoute, ideRoute]);

export const router = createRouter({ routeTree });
