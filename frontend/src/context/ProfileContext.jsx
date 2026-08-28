import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { getMyProfile } from "../api/profiles.api";
import {
  getMyRecruiterProfile,
} from "../api/recruiterProfiles.api";

import { useAuth } from "../hooks/useAuth";
import ProfileContext from "./ProfileContext.js";

export function ProfileProvider({ children }) {
  const { user } = useAuth();

  const [profile, setProfile] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState(null);

  const [profileExists, setProfileExists] =
    useState(null);

  const loadProfile = useCallback(async () => {
    if (!user) {
      setProfile(null);
      setProfileExists(null);
      setError(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let result;

      if (user.role === "RECRUITER") {
        result =
          await getMyRecruiterProfile();
      } else {
        result = await getMyProfile();
      }

      setProfile(result);
      setProfileExists(true);
    } catch (err) {
      const statusCode =
        err?.response?.status;

      if (statusCode === 404) {
        /*
         * A missing profile is an expected state for
         * a newly registered MEDAI user.
         *
         * It is NOT treated as an application error.
         */
        setProfile(null);
        setProfileExists(false);
        setError(null);
      } else {
        setProfile(null);
        setProfileExists(null);

        setError(
          err?.response?.data?.detail ||
            "Unable to load profile.",
        );
      }
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    // Synchronize profile state with the authenticated user.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProfile();
  }, [loadProfile]);

  const value = useMemo(
    () => ({
      profile,
      profileExists,
      loading,
      error,
      refreshProfile: loadProfile,
    }),
    [
      profile,
      profileExists,
      loading,
      error,
      loadProfile,
    ],
  );

  return (
    <ProfileContext.Provider value={value}>
      {children}
    </ProfileContext.Provider>
  );
}
