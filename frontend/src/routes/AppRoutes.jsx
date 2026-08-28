import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import JobsEntryPage from "../pages/JobsEntryPage";
import JobDetailsPage from "../pages/JobDetailsPage";
import { ROLE_ACCESS } from "../utils/roleAccess";
import PublicProfile from "../features/profile/public/PublicProfile";
import AuthLayout from "../layouts/AuthLayout";
import AppLayout from "../layouts/AppLayout";

import HomePage from "../pages/HomePage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import ProfileEntryPage from "../pages/ProfileEntryPage";
import NetworkPage from "../features/networking/NetworkPage";
import CommunityPage from "../pages/shared/CommunityPage";
import ReferralsPage from "../pages/shared/ReferralsPage";
import MessagesPage from "../pages/shared/MessagesPage";

import ApplicationsPage from "../pages/candidate/ApplicationsPage";
import InterviewsPage from "../pages/candidate/InterviewsPage";
import InterviewDetailsPage from "../pages/candidate/InterviewDetailsPage";
import CandidateDashboardPage from "../pages/candidate/CandidateDashboardPage";

import RecruiterDashboardPage from "../pages/recruiter/RecruiterDashboardPage";
import ApplicantsPage from "../pages/recruiter/ApplicantsPage";
import ApplicantDetailsPage from "../pages/recruiter/ApplicantDetailsPage";
import ApplicationDetailsPage from "../pages/candidate/ApplicationDetailsPage";
import ProtectedRoute from "./ProtectedRoute";
import RoleRoute from "./RoleRoute";


function RoleProtectedPage({
  allowedRoles,
  children,
}) {
  return (
    <RoleRoute allowedRoles={allowedRoles}>
      {children}
    </RoleRoute>
  );
}


export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ==================================================
            PUBLIC / AUTH ROUTES
            ================================================== */}

        <Route element={<AuthLayout />}>

          <Route
            path="/login"
            element={<LoginPage />}
          />

          <Route
            path="/register"
            element={<RegisterPage />}
          />

        </Route>


        {/* ==================================================
            AUTHENTICATED APPLICATION
            ================================================== */}

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >

          {/* ==================================================
              SHARED ROUTES
              ================================================== */}

          <Route
            path="/home"
            element={
              <RoleProtectedPage
                allowedRoles={ROLE_ACCESS.HOME}
              >
                <HomePage />
              </RoleProtectedPage>
            }
          />

          <Route
            path="/network"
            element={
              <RoleProtectedPage
                allowedRoles={ROLE_ACCESS.NETWORK}
              >
                <NetworkPage />
              </RoleProtectedPage>
            }
          />

          <Route
            path="/jobs"
            element={
              <RoleProtectedPage
                allowedRoles={ROLE_ACCESS.JOBS}
              >
                <JobsEntryPage />
              </RoleProtectedPage>
            }
          />
          <Route
            path="/jobs/:jobId"
            element={<JobDetailsPage />}
          />

          <Route
            path="/community"
            element={
              <RoleProtectedPage
                allowedRoles={ROLE_ACCESS.COMMUNITY}
              >
                <CommunityPage />
              </RoleProtectedPage>
            }
          />

          <Route
            path="/referrals"
            element={
              <RoleProtectedPage
                allowedRoles={ROLE_ACCESS.REFERRALS}
              >
                <ReferralsPage />
              </RoleProtectedPage>
            }
          />

          <Route
            path="/messages"
            element={
              <RoleProtectedPage
                allowedRoles={ROLE_ACCESS.MESSAGES}
              >
                <MessagesPage />
              </RoleProtectedPage>
            }
          />


          {/* ==================================================
              PROFILE
              ================================================== */}

          <Route
            path="/profile"
            element={<ProfileEntryPage />}
          />
                    
          <Route
            path="/profile/:userId"
            element={<PublicProfile />}
          />

          {/* ==================================================
              CANDIDATE-ONLY ROUTES
              ================================================== */}

          <Route
            path="/candidate"
            element={
              <RoleProtectedPage
                allowedRoles={[
                  "CANDIDATE",
                ]}
              >
                <CandidateDashboardPage />
              </RoleProtectedPage>
            }
          />


          <Route
            path="/interviews"
            element={
              <RoleProtectedPage
                allowedRoles={[
                  "CANDIDATE",
                ]}
              >
                <InterviewsPage />
              </RoleProtectedPage>
            }
          />

          <Route
            path="/interviews/:interviewId"
            element={
              <RoleProtectedPage
                allowedRoles={[
                  "CANDIDATE",
                ]}
              >
                <InterviewDetailsPage />
              </RoleProtectedPage>
            }
          />

          <Route
            path="/applications"
            element={
              <RoleProtectedPage
                allowedRoles={
                  ROLE_ACCESS.APPLICATIONS
                }
              >
                <ApplicationsPage />
              </RoleProtectedPage>
            }
          />
          <Route
            path="/applications/:applicationId"
            element={
              <RoleProtectedPage
                allowedRoles={["CANDIDATE"]}
              >
                <ApplicationDetailsPage />
              </RoleProtectedPage>
            }
          />


          {/* ==================================================
              RECRUITER-ONLY ROUTES
              ================================================== */}

          <Route
            path="/recruiter"
            element={
              <RoleProtectedPage
                allowedRoles={
                  ROLE_ACCESS.RECRUITER
                }
              >
                <RecruiterDashboardPage />
              </RoleProtectedPage>
            }
          />


          <Route
            path="/recruiter/applicants/:applicationId"
            element={
              <RoleProtectedPage
                allowedRoles={
                  ROLE_ACCESS.RECRUITER
                }
              >
                <ApplicantDetailsPage />
              </RoleProtectedPage>
            }
          />

          <Route
            path="/recruiter/applicants"
            element={
              <RoleProtectedPage
                allowedRoles={
                  ROLE_ACCESS.RECRUITER
                }
              >
                <ApplicantsPage />
              </RoleProtectedPage>
            }
          />


          {/* ==================================================
              DEFAULT AUTHENTICATED ROUTE
              ================================================== */}

          <Route
            path="/"
            element={
              <Navigate
                to="/home"
                replace
              />
            }
          />

        </Route>


        {/* ==================================================
            UNKNOWN ROUTES
            ================================================== */}

        <Route
          path="*"
          element={
            <Navigate
              to="/home"
              replace
            />
          }
        />

      </Routes>
    </BrowserRouter>
  );
}
