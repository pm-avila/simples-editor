import { createRouter, createRoute, createRootRoute } from "@tanstack/react-router";
import { IdeShell } from "./components/ide/ide-shell";

const rootRoute = createRootRoute();

const ideRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: IdeShell,
});

const routeTree = rootRoute.addChildren([ideRoute]);

export const router = createRouter({ routeTree });
