export default function Input({
  label,
  error,
  className = "",
  ...props
}) {
  return (
    <label className="ui-input-wrapper">
      {label && (
        <span className="ui-input-label">
          {label}
        </span>
      )}

      <input
        {...props}
        className={`ui-input ${className}`.trim()}
      />

      {error && (
        <span className="ui-input-error">
          {error}
        </span>
      )}
    </label>
  );
}
