export function getDisplayHandle(email) {
  if (!email || typeof email !== "string") {
    return "@user";
  }

  const localPart = email
    .split("@")[0]
    ?.trim();

  if (!localPart) {
    return "@user";
  }

  return `@${localPart}`;
}


export function getDisplayName(email) {
  if (!email || typeof email !== "string") {
    return "MEDAI User";
  }

  const localPart = email
    .split("@")[0]
    ?.trim();

  return localPart || "MEDAI User";
}
