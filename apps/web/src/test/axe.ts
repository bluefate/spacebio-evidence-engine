import { expect } from "vitest";
import { axe, toHaveNoViolations } from "jest-axe";

expect.extend(toHaveNoViolations);

/** jsdom cannot compute real contrast; token contrast is documented separately. */
const axeOptions = {
  rules: {
    "color-contrast": { enabled: false },
  },
};

export async function expectNoAxeViolations(container: HTMLElement): Promise<void> {
  const results = await axe(container, axeOptions);
  expect(results).toHaveNoViolations();
}
