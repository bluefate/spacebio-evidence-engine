import type { AnchorHTMLAttributes, ReactNode } from "react";

type NewTabLinkProps = AnchorHTMLAttributes<HTMLAnchorElement> & {
  href: string;
  children: ReactNode;
};

/** External link that announces a new tab and uses a safe rel set. */
export function NewTabLink({ href, children, className, ...rest }: NewTabLinkProps) {
  return (
    <a
      {...rest}
      href={href}
      className={className}
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
      <span className="visuallyHidden"> (opens in a new tab)</span>
    </a>
  );
}
