"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col items-center justify-center p-4">
        <h2 className="text-xl font-bold mb-4">Something went wrong!</h2>
        <button
          onClick={() => reset()}
          className="rounded bg-black px-4 py-2 text-white dark:bg-white dark:text-black"
        >
          Try again
        </button>
      </body>
    </html>
  );
}
