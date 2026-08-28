import { useEffect, useRef, useState } from "react";

import { searchUsers } from "../../api/users.api";
import UserSearchResults from "./UserSearchResults";

export default function UserSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const timeoutRef = useRef(null);

  const trimmedQuery = query.trim();

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    if (trimmedQuery.length < 2) {
      return undefined;
    }

    timeoutRef.current = setTimeout(async () => {
      setLoading(true);

      try {
        const response = await searchUsers(
          trimmedQuery,
        );

        setResults(
          Array.isArray(response)
            ? response
            : [],
        );
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [trimmedQuery]);

  function handleChange(event) {
    setQuery(event.target.value);

    if (
      event.target.value.trim().length < 2
    ) {
      setResults([]);
    }
  }

  function clearSearch() {
    setQuery("");
    setResults([]);
  }

  return (
    <div className="user-search">
      <input
        className="navbar-search"
        type="search"
        value={query}
        onChange={handleChange}
        placeholder="Search MEDAI"
        aria-label="Search MEDAI users"
      />

      {trimmedQuery.length >= 2 && (
        <UserSearchResults
          results={results}
          loading={loading}
          query={trimmedQuery}
          onSelect={clearSearch}
        />
      )}
    </div>
  );
}
