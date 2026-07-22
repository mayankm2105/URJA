export function AmbientOrbs({ variant = "hero" }: { variant?: "hero" | "subtle" }) {
  if (variant === "subtle") {
    return (
      <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
        <div
          className="orb"
          style={{
            width: 600,
            height: 600,
            top: -200,
            right: -100,
            background: "radial-gradient(circle, #5b5fed 0%, transparent 70%)",
            opacity: 0.15,
          }}
        />
      </div>
    );
  }
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      <div
        className="orb"
        style={{
          width: 720,
          height: 720,
          top: -160,
          left: "20%",
          background: "radial-gradient(circle, #5b5fed 0%, transparent 70%)",
        }}
      />
      <div
        className="orb"
        style={{
          width: 640,
          height: 640,
          top: 40,
          right: "10%",
          background: "radial-gradient(circle, #3e8ef7 0%, transparent 70%)",
          animationDelay: "-12s",
        }}
      />
      <div
        className="orb"
        style={{
          width: 480,
          height: 480,
          bottom: -100,
          left: "35%",
          background: "radial-gradient(circle, #7b7fff 0%, transparent 70%)",
          animationDelay: "-22s",
          opacity: 0.25,
        }}
      />
    </div>
  );
}
