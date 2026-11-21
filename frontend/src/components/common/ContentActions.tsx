import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

export default function ContentActions({ label, className, children }: {
  label: string;
  className: string;
  children: (choose: (action: () => void) => void) => ReactNode;
}) {
  const menu = useRef<HTMLDetailsElement>(null);
  const trigger = useRef<HTMLElement>(null);

  useEffect(() => {
    function dismissOutside(event: PointerEvent) {
      if (event.target instanceof Node && menu.current && !menu.current.contains(event.target)) {
        menu.current.open = false;
      }
    }
    document.addEventListener('pointerdown', dismissOutside);
    return () => document.removeEventListener('pointerdown', dismissOutside);
  }, []);

  return <details ref={menu} className={`post-owner-menu ${className}`} onBlur={event => {
    if (!event.currentTarget.contains(event.relatedTarget)) event.currentTarget.open = false;
  }} onKeyDown={event => {
    if (event.key === 'Escape' && event.currentTarget.open) {
      event.currentTarget.open = false;
      trigger.current?.focus();
    }
  }}>
    <summary ref={trigger} aria-label={label}>⋯</summary>
    <div className="post-owner-options">
      {children(action => {
        if (menu.current) menu.current.open = false;
        trigger.current?.focus();
        action();
      })}
    </div>
  </details>;
}
