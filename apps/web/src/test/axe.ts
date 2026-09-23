import { expect } from "vitest";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

declare module "vitest" {
  interface Matchers<R extends void | Promise<void> = void | Promise<void>> {
    toHaveNoViolations(): R;
  }
}

/** jsdom cannot compute real contrast; token contrast is documented separately. */
const axeOptions = {
  rules: {
    "color-contrast": { enabled: false },
  },
};

export async function expectNoAxeViolations(
  container: HTMLElement,
): Promise<void> {
  const results = await axe(container, axeOptions);
  expect(results).toHaveNoViolations();
}
