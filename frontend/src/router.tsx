import { createRouter, createRoute, createRootRoute } from "@tanstack/react-router";
import { App } from "./app";

const rootRoute = createRootRoute();

const appRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: App,
});

const routeTree = rootRoute.addChildren([appRoute]);

export const router = createRouter({ routeTree });
