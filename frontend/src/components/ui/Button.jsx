export default function Button({
  children,
  variant = "primary",
  type = "button",
  disabled = false,
  onClick,
  className = "",
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`ui-button ui-button-${variant} ${className}`.trim()}
    >
      {children}
    </button>
  );
}
