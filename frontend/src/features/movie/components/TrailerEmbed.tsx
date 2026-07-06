import { useState } from "react";
import { Play } from "lucide-react";

interface TrailerEmbedProps {
  trailerUrl: string | null;
  title: string;
  backdropUrl?: string | null;
}

/**
 * Click-to-load trailer embed. We don't render the YouTube iframe until the
 * user asks for it — avoids paying for an extra iframe/network request on
 * every movie detail page load when most visitors never watch the trailer,
 * and avoids autoplaying video unexpectedly.
 */
export function TrailerEmbed({ trailerUrl, title, backdropUrl }: TrailerEmbedProps) {
  const [playing, setPlaying] = useState(false);

  if (!trailerUrl) {
    return null;
  }

  return (
    <section className="px-6 py-8 md:px-10">
      <h2 className="mb-4 font-[var(--font-display)] text-2xl font-semibold text-[var(--color-bone)]">
        Trailer
      </h2>

      <div className="glass relative aspect-video w-full max-w-3xl overflow-hidden rounded-xl">
        {playing ? (
          <iframe
            className="h-full w-full"
            src={`${trailerUrl}?autoplay=1`}
            title={`${title} trailer`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        ) : (
          <button
            type="button"
            onClick={() => setPlaying(true)}
            aria-label={`Play trailer for ${title}`}
            className="group relative flex h-full w-full items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-marquee)]"
          >
            {backdropUrl ? (
              <img
                src={backdropUrl}
                alt=""
                aria-hidden
                className="absolute inset-0 h-full w-full object-cover opacity-60 transition-opacity group-hover:opacity-75"
              />
            ) : (
              <div className="absolute inset-0 bg-[var(--color-panel)]" />
            )}
            <span className="relative flex h-16 w-16 items-center justify-center rounded-full bg-[var(--color-marquee)] text-[var(--color-ink)] shadow-lg transition-transform group-hover:scale-110">
              <Play size={28} fill="currentColor" strokeWidth={0} />
            </span>
          </button>
        )}
      </div>
    </section>
  );
}
