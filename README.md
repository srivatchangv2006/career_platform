# MEDAI Career Platform

MEDAI is a full-stack career platform that brings job discovery, applications, resumes, recruiter hiring workflows, community interaction, referrals, messaging, interviews, and AI-assisted career features into one system.

The platform is built around two primary user experiences — **Candidate** and **Recruiter** — with role-based access controlling the features available to each user.

---

## 📸 Screenshots

### Candidate & Recruiter Platform

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20030316.png" width="900" alt="MEDAI Candidate and Recruiter Platform">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20030520.png" width="900" alt="MEDAI Platform Screenshot 2">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20030608.png" width="900" alt="MEDAI Platform Screenshot 3">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20030652.png" width="900" alt="MEDAI Platform Screenshot 4">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20030746.png" width="900" alt="MEDAI Platform Screenshot 5">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20030834.png" width="900" alt="MEDAI Platform Screenshot 6">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20030922.png" width="900" alt="MEDAI Platform Screenshot 7">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031021.png" width="900" alt="MEDAI Platform Screenshot 8">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031118.png" width="900" alt="MEDAI Platform Screenshot 9">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031141.png" width="900" alt="MEDAI Platform Screenshot 10">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031232.png" width="900" alt="MEDAI Platform Screenshot 11">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031257.png" width="900" alt="MEDAI Platform Screenshot 12">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031506.png" width="900" alt="MEDAI Platform Screenshot 13">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031532.png" width="900" alt="MEDAI Platform Screenshot 14">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031610.png" width="900" alt="MEDAI Platform Screenshot 15">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031636.png" width="900" alt="MEDAI Platform Screenshot 16">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031711.png" width="900" alt="MEDAI Platform Screenshot 17">
</p>

<p align="center">
  <img src="screenshots/Screenshot%202026-08-29%20031753.png" width="900" alt="MEDAI Platform Screenshot 18">
</p>

---

## 1. Technology Stack

### Frontend

- React
- Vite
- React Router
- JavaScript / JSX
- CSS
- Axios-based API client
- Role-aware navigation and protected routes

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Uvicorn

### External Services

- Azure Blob Storage for protected file storage
- Google Gemini for AI-powered features

---

## 2. High-Level Architecture

```text
                          MEDAI PLATFORM

       ┌──────────────────── FRONTEND ────────────────────┐
       │                                                   │
       │ React + Vite                                      │
       │                                                   │
       │ Candidate UI   Recruiter UI   Shared UI          │
       │                                                   │
       └────────────────────────┬──────────────────────────┘
                                │ HTTP / REST
                                ▼
       ┌────────────────────── BACKEND ───────────────────┐
       │                                                   │
       │ FastAPI                                           │
       │                                                   │
       │ Authentication / Roles                            │
       │ Jobs / Applications / Resumes                     │
       │ Community / Referrals / Messages                 │
       │ Interviews / AI Preparation                       │
       │                                                   │
       └──────────────┬──────────────────┬─────────────────┘
                      │                  │
                      ▼                  ▼
                PostgreSQL        Azure Blob Storage
                      │
                      ▼
                 Persistent data
                      │
                      ▼
                 Gemini AI services
```

---

## 3. User Roles

### Candidate

Candidates have access to:

- Jobs
- Applications
- Resume management
- Community
- Referrals
- Messages
- Interviews
- MEDAI interview preparation

### Recruiter

Recruiters have access to:

- Job creation and management
- Applicant management
- Candidate details
- Candidate resumes
- Application status management
- Interview scheduling and management
- Community
- Referrals
- Messages

### Admin

An `ADMIN` role is included in the role/access model and navigation structure.

---

# 4. Jobs

The platform includes a complete job posting and discovery flow for candidates and recruiters.

### Recruiter job functionality

- Create jobs
- View owned jobs
- Edit jobs
- Associate jobs with companies
- Add job metadata
- Add job skills
- Manage job status

### Candidate job functionality

- Browse jobs
- View job details
- See company information
- View job requirements and metadata
- Apply to open jobs

### Job statuses

```text
DRAFT
OPEN
CLOSED
EXPIRED
```

Candidates can apply to jobs when the job is open for applications.

---

# 5. Companies

Companies are represented in the database and associated with jobs.

The company model contains information such as:

- Name
- Slug
- Description
- Website
- Logo storage path
- Industry
- Company size
- Location
- Created / updated timestamps

A set of company records is currently present as development data for the platform.

---

# 6. Skills

Skills are stored separately and can be associated with both jobs and users.

The platform currently contains a seeded collection of skills for development and testing.

Skills are used throughout the platform for:

- Job requirements
- Candidate profiles
- Candidate skill information
- AI interview preparation
- Skill-oriented career analysis

---

# 7. Applications

Candidates can submit applications to jobs and track their application information.

### Candidate functionality

- Apply to a job
- Submit a resume
- Submit a cover letter
- View applications
- View application details
- View related interview information
- View application progress

### Recruiter functionality

Recruiters can:

- View applicants for their jobs
- Open individual applicant details
- Review candidate profiles
- Review candidate skills
- Review screening answers
- Review job information
- Download attached resumes
- Update application status
- Schedule interviews for applicants

### Application pipeline

```text
APPLIED
   ↓
SCREENING
   ↓
ASSESSMENT
   ↓
INTERVIEW
   ↓
OFFER
```

`REJECTED` is supported as an application outcome from applicable stages.

---

# 8. Resume Management

Resume management is implemented with protected storage support.

### Candidate resume functionality

- Upload resume
- Rename resume
- Set primary resume
- Delete resume
- Maintain multiple resumes

### Recruiter resume functionality

Recruiters can securely download the resume associated with an applicant.

Resume files are stored using Azure Blob Storage and are accessed through authenticated backend endpoints rather than exposing storage locations directly in the frontend.

---

# 9. Recruiter Applicant Management

Recruiters have a dedicated applicant workflow for reviewing candidates.

An applicant detail view includes:

- Candidate identity
- Candidate email
- Candidate headline
- Candidate profile information
- Location
- Experience
- Candidate skills
- Screening answers
- Job applied for
- Company
- Application status
- Resume information
- Resume download
- Interview scheduling

Application status can be updated directly from the applicant detail view.

---

# 10. Community

The platform includes a social community feed for users.

### Community feed

Posts contain:

- Author information
- Author role / profile context
- Post content
- Images where attached
- Voting
- Comments
- Replies

### Create Post

Post creation is handled through a dedicated modal opened from the Community feed.

```text
Community Feed
      │
      ▼
Create Post
      │
      ▼
Post Modal
 ├── Content
 ├── Image
 └── Publish
```

### Images

Community images are uploaded and displayed using an image layout that preserves the uploaded image rather than forcing an aggressive crop.

### Comments and replies

Community discussions support threaded replies. Replies are visually indented so the parent-child relationship is clear.

---

# 11. Referrals

The referral system allows users to offer referrals and request referrals.

## Referral opportunities

A referral opportunity can be based on either:

```text
Platform Job
```

or:

```text
Other Opportunity
```

### Platform Job

The user selects an open MEDAI job from the job list.

### Other Opportunity

Users can create a referral for an opportunity that is not represented by a MEDAI job listing by entering information such as:

- Company
- Opportunity title
- Referral message
- Maximum referrals

## Referral requests

The request flow is:

```text
User offers referral
        ↓
Candidate requests referral
        ↓
Referrer receives request
        ↓
Referrer reviews request
        ↓
Accept / Reject
```

A referral request can include an attached resume.

The referrer can securely view the attached resume through an authenticated endpoint. Resume access is tied to the referral opportunity owner and the requesting candidate's resume record.

---

# 12. Messages

Messages are implemented as a one-to-one conversation system.

The Messages page is a **single-page messaging workspace**.

```text
┌────────────────────┬──────────────────────────────────┐
│ Conversations      │ Selected conversation             │
│                    │                                  │
│ Person              │ Message history                 │
│ Last message       │                                  │
│                    │                                  │
│ Person              │                                  │
│ Last message       │                                  │
│                    ├──────────────────────────────────┤
│                    │ Message input             Send    │
└────────────────────┴──────────────────────────────────┘
```

### Conversation functionality

- View previous conversations
- View conversation history
- Select a conversation
- Send messages
- Edit own messages
- Delete own messages
- Mark conversations as read
- Track unread counts
- Show latest message preview
- Keep recent conversations ordered by activity
- Start a conversation from a user's profile

Conversation entries can use the other user's:

- Display name
- Email
- Role
- Headline
- Company
- Avatar where available
- Last message
- Unread count

The messaging backend enforces conversation participation and ownership rules for protected operations such as reading, sending, editing, and deleting messages.

---

# 13. Interviews

Interview scheduling and candidate interview access are implemented across recruiter and candidate workflows.

## Recruiter interview scheduling

Recruiters can schedule an interview against an applicant.

Interview details include:

- Interview type
- Date and time
- Duration
- Meeting URL
- Location
- Notes
- Status

Supported interview statuses include:

```text
SCHEDULED
CONFIRMED
COMPLETED
CANCELLED
RESCHEDULED
```

Recruiter interview APIs support creating, viewing, updating, and deleting interviews, with ownership checks based on the recruiter's job/application scope.

## Candidate My Interviews

Candidates can view their scheduled interviews from:

```text
My Interviews
```

Each interview can show:

- Interview type
- Status
- Date and time
- Duration
- Location
- Recruiter-provided notes
- Meeting link
- Interview detail page
- MEDAI preparation action

## Interview details

The candidate interview detail page brings together:

- Job title
- Company
- Interview status
- Date and time
- Duration
- Location
- Meeting link
- Notes
- MEDAI interview preparation

---

# 14. MEDAI Interview Preparation

The platform includes an AI-powered interview preparation workflow.

The preparation service builds context from the interview, application, job, candidate skills, and stored career context before generating preparation content through Gemini.

The preparation output includes:

- Likely interview questions
- Suggested answer guidance
- Candidate strengths
- Improvement areas
- Practical recommendations

The candidate can generate or regenerate preparation directly from the interview experience.

### AI usage-limit handling

The candidate interview experience handles AI usage-limit conditions including HTTP `429`, quota-related responses, rate-limit responses, and resource-exhausted errors.

When preparation cannot be generated because of an AI usage limit, the interview itself remains available and the user receives a clear message explaining that MEDAI preparation is temporarily unavailable.

---

# 15. AI / Agent Services

The backend contains a collection of AI-oriented services that support the broader MEDAI experience.

Current service areas include:

- Resume analysis
- Skill-gap analysis
- Job recommendations
- Interview preparation
- AI interaction logging
- Agent memory
- Agent tasks
- Agent task steps
- Agent feedback
- Agent messages
- Career recommendations

The platform stores AI-related interaction and preparation data so generated outputs can be associated with the relevant user and career workflow.

---

# 16. Authentication and Role-Based Access

The application uses role-based access throughout the frontend and backend.

Roles include:

```text
CANDIDATE
RECRUITER
ADMIN
```

Frontend navigation and routes are role-aware, while backend endpoints enforce authentication, role requirements, and resource ownership.

Examples include:

- Recruiters can manage only interviews belonging to applications for jobs they own.
- Recruiters can access applicant resumes only through protected endpoints.
- Candidates can access only their own applications and interviews.
- Message operations are restricted to conversation participants.
- Referral resume access is restricted to the owner of the relevant referral opportunity.

---

# 17. Backend Structure

```text
backend/
├── main.py
├── models/
├── schemas/
├── routers/
├── services/
├── dependencies/
└── venv/
```

### Directory roles

| Directory | Purpose |
|---|---|
| `models/` | SQLAlchemy database models |
| `schemas/` | Pydantic request and response models |
| `routers/` | FastAPI API routes |
| `services/` | Business logic, storage, AI, and reusable services |
| `dependencies/` | Authentication, roles, and database dependencies |

---

# 18. Frontend Structure

```text
frontend/
└── src/
    ├── api/
    ├── components/
    ├── constants/
    ├── features/
    ├── hooks/
    ├── layouts/
    ├── pages/
    │   ├── candidate/
    │   ├── recruiter/
    │   └── shared/
    ├── routes/
    └── utils/
```

The frontend is organized so feature APIs, reusable UI components, role-specific pages, shared pages, and routing remain separated.

---

# 19. Important API Areas

The backend contains feature-specific routers for areas such as:

```text
/jobs
/applications
/resumes
/skills
/community-posts
/community-comments
/connections
/referral-opportunities
/referral-requests
/messages
/interviews
/recruiter/interviews
/recruiter/applications
/recruiter
```

Interview preparation uses:

```text
/interviews/{interview_id}/prepare
/interviews/{interview_id}/preparation
```

---

# 20. Local Development

## Backend

```bash
cd ~/career_platform/backend
source venv/bin/activate
uvicorn main:app --reload
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend

```bash
cd ~/career_platform/frontend
npm install
npm run dev
```

The Vite development application normally runs at:

```text
http://localhost:5173
```

---

# 21. Quality Checks

### Frontend

```bash
cd ~/career_platform/frontend
npm run lint
npm run build
```

### Backend syntax check

```bash
cd ~/career_platform/backend
python -m py_compile path/to/file.py
```

API changes can be tested through the FastAPI Swagger interface at `/docs`.

---

# 22. Environment Configuration

Local environment files contain credentials and service configuration and are kept outside version control.

Typical configuration includes:

- PostgreSQL connection information
- Azure Blob Storage configuration
- Gemini API key
- Frontend API configuration

The repository ignores local environment files such as:

```text
backend/.env
frontend/.env
frontend/.env.*
```

---

# 23. GitHub Repository

The project is maintained in GitHub on the `main` branch.

Typical development checkpoint workflow:

```bash
git status
git diff --stat
npm run lint
npm run build
git add .
git commit -m "Describe the change"
git push origin main
```

Git checkpoints are used before larger feature changes so working versions of the platform are preserved.

---

# 24. Current Repository Feature Summary

The current repository contains the following implemented platform areas:

```text
Authentication / role-based access
        │
        ├── Jobs
        ├── Applications
        ├── Resumes
        ├── Recruiter applicant management
        ├── Community
        ├── Referrals
        ├── Messages
        ├── Interviews
        └── MEDAI AI services
```

### Candidate experience

```text
Candidate
  ├── Home / dashboard
  ├── Profile
  ├── Network
  ├── Jobs
  ├── Applications
  ├── Resumes
  ├── Community
  ├── Referrals
  ├── Messages
  ├── My Interviews
  └── MEDAI interview preparation
```

### Recruiter experience

```text
Recruiter
  ├── Home / dashboard
  ├── Profile
  ├── Network
  ├── Jobs
  ├── Applicants
  ├── Candidate details
  ├── Candidate resumes
  ├── Interview scheduling
  ├── Community
  ├── Referrals
  └── Messages
```

---

# 25. Project Development Principle

MEDAI is structured as a connected career platform. Major modules share user, job, application, resume, referral, messaging, interview, and AI context through protected backend services and role-aware frontend workflows.

The repository is organized so that feature-specific functionality remains separated while still being connected through common authentication, database, storage, and AI infrastructure.

