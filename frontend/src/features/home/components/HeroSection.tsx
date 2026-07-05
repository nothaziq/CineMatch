import { motion } from "framer-motion";

export function HeroSection() {
  return (
    <section className="relative flex min-h-[70vh] items-end overflow-hidden border-b border-[var(--color-panel-border)]">
      {/* Ambient glow — quiet, not competing with the signature card hover moment */}
      <div
        aria-hidden
        className="absolute -top-1/3 right-0 h-[140%] w-1/2 rounded-full opacity-20 blur-3xl"
        style={{
          background:
            "radial-gradient(circle, var(--color-marquee) 0%, transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="absolute -bottom-1/3 left-0 h-[120%] w-1/2 rounded-full opacity-15 blur-3xl"
        style={{
          background: "radial-gradient(circle, var(--color-signal) 0%, transparent 70%)",
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 max-w-2xl px-6 pb-16 md:px-10"
      >
        <p className="mb-3 font-[var(--font-mono)] text-xs uppercase tracking-[0.2em] text-[var(--color-marquee)]">
          Every film, one thread at a time
        </p>
        <h1 className="font-[var(--font-display)] text-5xl font-semibold leading-[1.05] text-[var(--color-bone)] md:text-6xl">
          Find what to watch,
          <br />
          by what you already love.
        </h1>
        <p className="mt-5 max-w-md text-[var(--color-bone-dim)]">
          CineMatch reads the DNA of the films you pick — genre, cast, director,
          theme — and traces a line to what you'll want next.
        </p>
      </motion.div>
    </section>
  );
}
