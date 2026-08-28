export default function Avatar({
  name = "MEDAI User",
  src = null,
  size = "medium",
}) {
  const initial =
    name?.trim()?.charAt(0)?.toUpperCase() || "M";

  return (
    <div
      className={`ui-avatar ui-avatar-${size}`}
      aria-label={name}
    >
      {src ? (
        <img
          src={src}
          alt={name}
          className="ui-avatar-image"
        />
      ) : (
        <span>{initial}</span>
      )}
    </div>
  );
}
