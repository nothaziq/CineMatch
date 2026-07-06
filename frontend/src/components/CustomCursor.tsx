import { useEffect, useRef, useState } from "react";

const HOVER_TARGET_SELECTOR =
  'a, button, input, textarea, select, [role="button"], [tabindex]:not([tabindex="-1"])';

/**
 * A custom cursor: a small precise dot (tracks the pointer 1:1) plus a
 * softer "spotlight" ring that trails behind with gentle easing — a nod to
 * the marquee-light motif used elsewhere (.light-leak). Scales up and warms
 * in opacity over interactive elements.
 *
 * Intentionally does nothing on touch devices (no `pointer: fine`) or when
 * the user has requested reduced motion — a following cursor is exactly the
 * kind of ambient animation that preference is meant to suppress.
 */
export function CustomCursor() {
  const [enabled, setEnabled] = useState(false);
  const dotRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);

  // Ring position lags the real pointer via simple lerp easing, read/written
  // in a single rAF loop rather than on every mousemove event.
  const pointer = useRef({ x: 0, y: 0 });
  const ring = useRef({ x: 0, y: 0 });
  const rafId = useRef<number | null>(null);

  useEffect(() => {
    const finePointer = window.matchMedia("(pointer: fine)").matches;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!finePointer || reducedMotion) return;

    setEnabled(true);
    document.documentElement.classList.add("custom-cursor-active");

    const handleMove = (e: MouseEvent) => {
      pointer.current.x = e.clientX;
      pointer.current.y = e.clientY;
      if (dotRef.current) {
        dotRef.current.style.transform = `translate3d(${e.clientX}px, ${e.clientY}px, 0)`;
      }
    };

    const handleOver = (e: MouseEvent) => {
      const target = (e.target as Element)?.closest?.(HOVER_TARGET_SELECTOR);
      ringRef.current?.classList.toggle("custom-cursor-ring--active", !!target);
    };

    const handleLeaveWindow = () => {
      dotRef.current?.classList.add("custom-cursor-dot--hidden");
      ringRef.current?.classList.add("custom-cursor-ring--hidden");
    };
    const handleEnterWindow = () => {
      dotRef.current?.classList.remove("custom-cursor-dot--hidden");
      ringRef.current?.classList.remove("custom-cursor-ring--hidden");
    };

    const tick = () => {
      // Ease the ring toward the real pointer position rather than snapping.
      ring.current.x += (pointer.current.x - ring.current.x) * 0.18;
      ring.current.y += (pointer.current.y - ring.current.y) * 0.18;
      if (ringRef.current) {
        ringRef.current.style.transform = `translate3d(${ring.current.x}px, ${ring.current.y}px, 0)`;
      }
      rafId.current = requestAnimationFrame(tick);
    };

    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseover", handleOver);
    document.addEventListener("mouseleave", handleLeaveWindow);
    document.addEventListener("mouseenter", handleEnterWindow);
    rafId.current = requestAnimationFrame(tick);

    return () => {
      document.documentElement.classList.remove("custom-cursor-active");
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseover", handleOver);
      document.removeEventListener("mouseleave", handleLeaveWindow);
      document.removeEventListener("mouseenter", handleEnterWindow);
      if (rafId.current) cancelAnimationFrame(rafId.current);
    };
  }, []);

  if (!enabled) return null;

  return (
    <div aria-hidden="true">
      <div ref={ringRef} className="custom-cursor-ring" />
      <div ref={dotRef} className="custom-cursor-dot" />
    </div>
  );
}
