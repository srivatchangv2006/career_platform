--
-- PostgreSQL database dump
--

\restrict koZ7d0hwa7uWIexYiprZo1FZXzB8Ol2TIeg1ranuqjPLKMWsxM0oMylYfjA50ny

-- Dumped from database version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)
-- Dumped by pg_dump version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: citext; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;


--
-- Name: EXTENSION citext; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION citext IS 'data type for case-insensitive character strings';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: advice_request_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.advice_request_status AS ENUM (
    'PENDING',
    'ACCEPTED',
    'REJECTED',
    'CANCELLED'
);


ALTER TYPE public.advice_request_status OWNER TO postgres;

--
-- Name: application_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.application_status AS ENUM (
    'SAVED',
    'APPLIED',
    'SCREENING',
    'ASSESSMENT',
    'INTERVIEW',
    'OFFER',
    'REJECTED',
    'WITHDRAWN'
);


ALTER TYPE public.application_status OWNER TO postgres;

--
-- Name: connection_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.connection_status AS ENUM (
    'PENDING',
    'ACCEPTED',
    'REJECTED',
    'BLOCKED'
);


ALTER TYPE public.connection_status OWNER TO postgres;

--
-- Name: job_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.job_status AS ENUM (
    'DRAFT',
    'OPEN',
    'CLOSED',
    'EXPIRED'
);


ALTER TYPE public.job_status OWNER TO postgres;

--
-- Name: notification_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.notification_type AS ENUM (
    'APPLICATION_STATUS',
    'CONNECTION_REQUEST',
    'REFERRAL_RESPONSE',
    'ADVICE_RESPONSE',
    'COMMUNITY_REPLY',
    'COMMENT',
    'AI_PREPARATION',
    'RECRUITER_MESSAGE'
);


ALTER TYPE public.notification_type OWNER TO postgres;

--
-- Name: referral_request_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.referral_request_status AS ENUM (
    'PENDING',
    'ACCEPTED',
    'REJECTED',
    'CANCELLED'
);


ALTER TYPE public.referral_request_status OWNER TO postgres;

--
-- Name: report_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.report_status AS ENUM (
    'OPEN',
    'UNDER_REVIEW',
    'RESOLVED',
    'DISMISSED'
);


ALTER TYPE public.report_status OWNER TO postgres;

--
-- Name: user_role; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_role AS ENUM (
    'CANDIDATE',
    'RECRUITER',
    'PROFESSIONAL',
    'ADMIN'
);


ALTER TYPE public.user_role OWNER TO postgres;

--
-- Name: user_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_status AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'SUSPENDED'
);


ALTER TYPE public.user_status OWNER TO postgres;

--
-- Name: vote_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.vote_type AS ENUM (
    'UP',
    'DOWN'
);


ALTER TYPE public.vote_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: advice_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.advice_requests (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    requester_id uuid NOT NULL,
    advisor_id uuid NOT NULL,
    message text,
    status public.advice_request_status DEFAULT 'PENDING'::public.advice_request_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_advice_requests_different_users CHECK ((requester_id <> advisor_id))
);


ALTER TABLE public.advice_requests OWNER TO postgres;

--
-- Name: agent_feedback; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_feedback (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    interaction_id uuid,
    task_id uuid,
    rating integer,
    feedback text,
    is_helpful boolean,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_agent_feedback_rating CHECK (((rating IS NULL) OR ((rating >= 1) AND (rating <= 5))))
);


ALTER TABLE public.agent_feedback OWNER TO postgres;

--
-- Name: agent_memory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_memory (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    memory_type text NOT NULL,
    memory_key text,
    memory_value jsonb NOT NULL,
    source text,
    confidence_score numeric(5,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_agent_memory_confidence CHECK (((confidence_score IS NULL) OR ((confidence_score >= (0)::numeric) AND (confidence_score <= (100)::numeric))))
);


ALTER TABLE public.agent_memory OWNER TO postgres;

--
-- Name: agent_memory_embeddings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_memory_embeddings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    memory_id uuid NOT NULL,
    embedding public.vector(1536),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.agent_memory_embeddings OWNER TO postgres;

--
-- Name: agent_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_messages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid,
    sender_agent text NOT NULL,
    receiver_agent text NOT NULL,
    message_type text NOT NULL,
    payload jsonb NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    processed_at timestamp with time zone
);


ALTER TABLE public.agent_messages OWNER TO postgres;

--
-- Name: agent_task_steps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_task_steps (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid NOT NULL,
    step_name text NOT NULL,
    step_order integer DEFAULT 0 NOT NULL,
    agent_name text,
    status text DEFAULT 'PENDING'::text NOT NULL,
    input_data jsonb,
    output_data jsonb,
    error_message text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_agent_task_steps_order CHECK ((step_order >= 0))
);


ALTER TABLE public.agent_task_steps OWNER TO postgres;

--
-- Name: agent_tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_tasks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    task_type text NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    input_data jsonb,
    output_data jsonb,
    error_message text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.agent_tasks OWNER TO postgres;

--
-- Name: ai_interactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_interactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    interaction_type text NOT NULL,
    input_text text,
    output_text text,
    model_name text,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ai_interactions OWNER TO postgres;

--
-- Name: application_answers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.application_answers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    application_id uuid NOT NULL,
    question_id uuid NOT NULL,
    answer text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.application_answers OWNER TO postgres;

--
-- Name: application_status_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.application_status_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    application_id uuid NOT NULL,
    status public.application_status NOT NULL,
    changed_by uuid,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.application_status_history OWNER TO postgres;

--
-- Name: applications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.applications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid NOT NULL,
    user_id uuid NOT NULL,
    resume_id uuid,
    status public.application_status DEFAULT 'APPLIED'::public.application_status NOT NULL,
    cover_letter text,
    applied_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.applications OWNER TO postgres;

--
-- Name: career_goals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.career_goals (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    goal_title text NOT NULL,
    target_role text,
    target_industry text,
    target_location text,
    target_company text,
    target_timeline text,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.career_goals OWNER TO postgres;

--
-- Name: career_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.career_recommendations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    goal_id uuid,
    job_id uuid,
    recommendation_type text NOT NULL,
    title text NOT NULL,
    description text,
    priority text,
    metadata jsonb,
    is_completed boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.career_recommendations OWNER TO postgres;

--
-- Name: community_comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.community_comments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    parent_comment_id uuid,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.community_comments OWNER TO postgres;

--
-- Name: community_posts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.community_posts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.community_posts OWNER TO postgres;

--
-- Name: community_votes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.community_votes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    post_id uuid,
    comment_id uuid,
    vote public.vote_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_community_votes_target CHECK ((((post_id IS NOT NULL) AND (comment_id IS NULL)) OR ((post_id IS NULL) AND (comment_id IS NOT NULL))))
);


ALTER TABLE public.community_votes OWNER TO postgres;

--
-- Name: companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.companies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    slug text NOT NULL,
    description text,
    website_url text,
    logo_blob_path text,
    industry text,
    company_size text,
    location text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.companies OWNER TO postgres;

--
-- Name: connections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.connections (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    requester_id uuid NOT NULL,
    receiver_id uuid NOT NULL,
    status public.connection_status DEFAULT 'PENDING'::public.connection_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_connections_different_users CHECK ((requester_id <> receiver_id))
);


ALTER TABLE public.connections OWNER TO postgres;

--
-- Name: education; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.education (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    institution text NOT NULL,
    degree text,
    field_of_study text,
    start_date date,
    end_date date,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_education_dates CHECK (((end_date IS NULL) OR (start_date IS NULL) OR (end_date >= start_date)))
);


ALTER TABLE public.education OWNER TO postgres;

--
-- Name: experience; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experience (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    company_name text NOT NULL,
    job_title text NOT NULL,
    employment_type text,
    location text,
    start_date date,
    end_date date,
    description text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_experience_dates CHECK (((end_date IS NULL) OR (start_date IS NULL) OR (end_date >= start_date)))
);


ALTER TABLE public.experience OWNER TO postgres;

--
-- Name: interview_preparations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interview_preparations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    application_id uuid NOT NULL,
    user_id uuid NOT NULL,
    preparation_type text NOT NULL,
    questions jsonb,
    suggested_answers jsonb,
    strengths jsonb,
    improvement_areas jsonb,
    recommendations jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.interview_preparations OWNER TO postgres;

--
-- Name: interviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interviews (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    application_id uuid NOT NULL,
    interviewer_id uuid,
    interview_type text NOT NULL,
    scheduled_at timestamp with time zone,
    duration_minutes integer,
    meeting_url text,
    location text,
    notes text,
    status text DEFAULT 'SCHEDULED'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_interviews_duration CHECK (((duration_minutes IS NULL) OR (duration_minutes > 0)))
);


ALTER TABLE public.interviews OWNER TO postgres;

--
-- Name: job_matches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_matches (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    job_id uuid NOT NULL,
    match_score numeric(5,2),
    match_reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_job_matches_score CHECK (((match_score IS NULL) OR ((match_score >= (0)::numeric) AND (match_score <= (100)::numeric))))
);


ALTER TABLE public.job_matches OWNER TO postgres;

--
-- Name: job_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_preferences (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    preferred_roles text[],
    preferred_locations text[],
    preferred_employment_types text[],
    preferred_experience_levels text[],
    minimum_salary numeric(12,2),
    preferred_currency character varying(3) DEFAULT 'USD'::character varying,
    remote_preferred boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_job_preferences_salary CHECK (((minimum_salary IS NULL) OR (minimum_salary >= (0)::numeric)))
);


ALTER TABLE public.job_preferences OWNER TO postgres;

--
-- Name: job_recommendation_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_recommendation_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    run_id uuid NOT NULL,
    job_id uuid NOT NULL,
    match_score numeric(5,2),
    recommendation_reason text,
    ranking integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_job_recommendation_items_ranking CHECK (((ranking IS NULL) OR (ranking > 0))),
    CONSTRAINT chk_job_recommendation_items_score CHECK (((match_score IS NULL) OR ((match_score >= (0)::numeric) AND (match_score <= (100)::numeric))))
);


ALTER TABLE public.job_recommendation_items OWNER TO postgres;

--
-- Name: job_recommendation_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_recommendation_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    status text DEFAULT 'PENDING'::text NOT NULL,
    input_context jsonb,
    recommendations jsonb,
    model_name text,
    error_message text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.job_recommendation_runs OWNER TO postgres;

--
-- Name: job_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_reports (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid NOT NULL,
    reported_by uuid NOT NULL,
    reason text NOT NULL,
    description text,
    status public.report_status DEFAULT 'OPEN'::public.report_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.job_reports OWNER TO postgres;

--
-- Name: job_screening_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_screening_questions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id uuid NOT NULL,
    question text NOT NULL,
    question_type text DEFAULT 'TEXT'::text NOT NULL,
    is_required boolean DEFAULT true NOT NULL,
    display_order integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_job_screening_questions_order CHECK ((display_order >= 0))
);


ALTER TABLE public.job_screening_questions OWNER TO postgres;

--
-- Name: job_skills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.job_skills (
    job_id uuid NOT NULL,
    skill_id uuid NOT NULL,
    is_required boolean DEFAULT true NOT NULL,
    proficiency_level text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.job_skills OWNER TO postgres;

--
-- Name: jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_id uuid NOT NULL,
    posted_by uuid NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    location text,
    employment_type text,
    experience_level text,
    salary_min numeric(12,2),
    salary_max numeric(12,2),
    currency character varying(3) DEFAULT 'USD'::character varying,
    status public.job_status DEFAULT 'DRAFT'::public.job_status NOT NULL,
    application_deadline date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_jobs_salary CHECK (((salary_min IS NULL) OR (salary_max IS NULL) OR (salary_max >= salary_min)))
);


ALTER TABLE public.jobs OWNER TO postgres;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    type public.notification_type NOT NULL,
    title text NOT NULL,
    message text NOT NULL,
    reference_id uuid,
    is_read boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: profile_views; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.profile_views (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    viewer_id uuid,
    viewed_user_id uuid NOT NULL,
    viewed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_profile_views_different_users CHECK (((viewer_id IS NULL) OR (viewer_id <> viewed_user_id)))
);


ALTER TABLE public.profile_views OWNER TO postgres;

--
-- Name: profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.profiles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    full_name text NOT NULL,
    headline text,
    bio text,
    location text,
    profile_image_blob_path text,
    years_of_experience numeric(4,1),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_profiles_experience CHECK (((years_of_experience IS NULL) OR (years_of_experience >= (0)::numeric)))
);


ALTER TABLE public.profiles OWNER TO postgres;

--
-- Name: recruiter_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recruiter_profiles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    company_id uuid NOT NULL,
    designation text,
    bio text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.recruiter_profiles OWNER TO postgres;

--
-- Name: referrals; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.referral_opportunities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    posted_by uuid NOT NULL,
    job_id uuid NOT NULL,
    message text,
    max_referrals integer,
    status text DEFAULT 'OPEN'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT referral_opportunities_pkey PRIMARY KEY (id),
    CONSTRAINT fk_referral_opportunities_posted_by
        FOREIGN KEY (posted_by)
        REFERENCES public.users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_referral_opportunities_job
        FOREIGN KEY (job_id)
        REFERENCES public.jobs(id)
        ON DELETE CASCADE,
    CONSTRAINT chk_referral_opportunities_max_referrals
        CHECK (
            max_referrals IS NULL
            OR max_referrals > 0
        ),
    CONSTRAINT chk_referral_opportunities_status
        CHECK (
            status IN ('OPEN', 'CLOSED')
        )
);

CREATE TABLE public.referrals (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    opportunity_id uuid NOT NULL,
    requester_id uuid NOT NULL,
    resume_id uuid,
    message text,
    status public.referral_request_status DEFAULT 'PENDING'::public.referral_request_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT referrals_pkey PRIMARY KEY (id),
    CONSTRAINT fk_referrals_opportunity
        FOREIGN KEY (opportunity_id)
        REFERENCES public.referral_opportunities(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_referrals_requester
        FOREIGN KEY (requester_id)
        REFERENCES public.users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_referrals_resume
        FOREIGN KEY (resume_id)
        REFERENCES public.resumes(id)
        ON DELETE SET NULL
);


ALTER TABLE public.referrals OWNER TO postgres;

--
-- Name: resume_analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resume_analysis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    resume_id uuid NOT NULL,
    user_id uuid NOT NULL,
    summary text,
    strengths jsonb,
    weaknesses jsonb,
    extracted_skills jsonb,
    experience_summary jsonb,
    education_summary jsonb,
    recommendations jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.resume_analysis OWNER TO postgres;

--
-- Name: resumes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resumes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    file_name text NOT NULL,
    blob_container text NOT NULL,
    blob_path text NOT NULL,
    content_type text DEFAULT 'application/pdf'::text NOT NULL,
    file_size_bytes bigint,
    is_primary boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_resumes_file_size CHECK (((file_size_bytes IS NULL) OR (file_size_bytes >= 0)))
);


ALTER TABLE public.resumes OWNER TO postgres;

--
-- Name: saved_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.saved_jobs (
    user_id uuid NOT NULL,
    job_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.saved_jobs OWNER TO postgres;

--
-- Name: skill_gap_analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.skill_gap_analysis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    job_id uuid NOT NULL,
    matched_skills jsonb,
    missing_skills jsonb,
    recommendations jsonb,
    overall_match_score numeric(5,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_skill_gap_analysis_score CHECK (((overall_match_score IS NULL) OR ((overall_match_score >= (0)::numeric) AND (overall_match_score <= (100)::numeric))))
);


ALTER TABLE public.skill_gap_analysis OWNER TO postgres;

--
-- Name: skills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.skills (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    slug text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.skills OWNER TO postgres;

--
-- Name: user_activity; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_activity (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    activity_type text NOT NULL,
    reference_id uuid,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_activity OWNER TO postgres;

--
-- Name: user_follows; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_follows (
    follower_id uuid NOT NULL,
    following_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_user_follows_different_users CHECK ((follower_id <> following_id))
);


ALTER TABLE public.user_follows OWNER TO postgres;

--
-- Name: user_skills; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_skills (
    user_id uuid NOT NULL,
    skill_id uuid NOT NULL,
    proficiency text,
    years_experience numeric(4,1),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_user_skills_experience CHECK (((years_experience IS NULL) OR (years_experience >= (0)::numeric)))
);


ALTER TABLE public.user_skills OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email public.citext NOT NULL,
    password_hash text NOT NULL,
    role public.user_role DEFAULT 'CANDIDATE'::public.user_role NOT NULL,
    status public.user_status DEFAULT 'ACTIVE'::public.user_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: advice_requests advice_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.advice_requests
    ADD CONSTRAINT advice_requests_pkey PRIMARY KEY (id);


--
-- Name: agent_feedback agent_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_feedback
    ADD CONSTRAINT agent_feedback_pkey PRIMARY KEY (id);


--
-- Name: agent_memory_embeddings agent_memory_embeddings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_memory_embeddings
    ADD CONSTRAINT agent_memory_embeddings_pkey PRIMARY KEY (id);


--
-- Name: agent_memory agent_memory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_memory
    ADD CONSTRAINT agent_memory_pkey PRIMARY KEY (id);


--
-- Name: agent_messages agent_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_messages
    ADD CONSTRAINT agent_messages_pkey PRIMARY KEY (id);


--
-- Name: agent_task_steps agent_task_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_task_steps
    ADD CONSTRAINT agent_task_steps_pkey PRIMARY KEY (id);


--
-- Name: agent_tasks agent_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_tasks
    ADD CONSTRAINT agent_tasks_pkey PRIMARY KEY (id);


--
-- Name: ai_interactions ai_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_interactions
    ADD CONSTRAINT ai_interactions_pkey PRIMARY KEY (id);


--
-- Name: application_answers application_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_answers
    ADD CONSTRAINT application_answers_pkey PRIMARY KEY (id);


--
-- Name: application_status_history application_status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_status_history
    ADD CONSTRAINT application_status_history_pkey PRIMARY KEY (id);


--
-- Name: applications applications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_pkey PRIMARY KEY (id);


--
-- Name: career_goals career_goals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.career_goals
    ADD CONSTRAINT career_goals_pkey PRIMARY KEY (id);


--
-- Name: career_recommendations career_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.career_recommendations
    ADD CONSTRAINT career_recommendations_pkey PRIMARY KEY (id);


--
-- Name: community_comments community_comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_comments
    ADD CONSTRAINT community_comments_pkey PRIMARY KEY (id);


--
-- Name: community_posts community_posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_posts
    ADD CONSTRAINT community_posts_pkey PRIMARY KEY (id);


--
-- Name: community_votes community_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_votes
    ADD CONSTRAINT community_votes_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: companies companies_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_slug_key UNIQUE (slug);


--
-- Name: connections connections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.connections
    ADD CONSTRAINT connections_pkey PRIMARY KEY (id);


--
-- Name: education education_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.education
    ADD CONSTRAINT education_pkey PRIMARY KEY (id);


--
-- Name: experience experience_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experience
    ADD CONSTRAINT experience_pkey PRIMARY KEY (id);


--
-- Name: interview_preparations interview_preparations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_preparations
    ADD CONSTRAINT interview_preparations_pkey PRIMARY KEY (id);


--
-- Name: interviews interviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_pkey PRIMARY KEY (id);


--
-- Name: job_matches job_matches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_matches
    ADD CONSTRAINT job_matches_pkey PRIMARY KEY (id);


--
-- Name: job_preferences job_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_preferences
    ADD CONSTRAINT job_preferences_pkey PRIMARY KEY (id);


--
-- Name: job_preferences job_preferences_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_preferences
    ADD CONSTRAINT job_preferences_user_id_key UNIQUE (user_id);


--
-- Name: job_recommendation_items job_recommendation_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_recommendation_items
    ADD CONSTRAINT job_recommendation_items_pkey PRIMARY KEY (id);


--
-- Name: job_recommendation_runs job_recommendation_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_recommendation_runs
    ADD CONSTRAINT job_recommendation_runs_pkey PRIMARY KEY (id);


--
-- Name: job_reports job_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_reports
    ADD CONSTRAINT job_reports_pkey PRIMARY KEY (id);


--
-- Name: job_screening_questions job_screening_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_screening_questions
    ADD CONSTRAINT job_screening_questions_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: job_skills pk_job_skills; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_skills
    ADD CONSTRAINT pk_job_skills PRIMARY KEY (job_id, skill_id);


--
-- Name: saved_jobs pk_saved_jobs; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT pk_saved_jobs PRIMARY KEY (user_id, job_id);


--
-- Name: user_follows pk_user_follows; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_follows
    ADD CONSTRAINT pk_user_follows PRIMARY KEY (follower_id, following_id);


--
-- Name: user_skills pk_user_skills; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT pk_user_skills PRIMARY KEY (user_id, skill_id);


--
-- Name: profile_views profile_views_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profile_views
    ADD CONSTRAINT profile_views_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_key UNIQUE (user_id);


--
-- Name: recruiter_profiles recruiter_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recruiter_profiles
    ADD CONSTRAINT recruiter_profiles_pkey PRIMARY KEY (id);


--
-- Name: recruiter_profiles recruiter_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recruiter_profiles
    ADD CONSTRAINT recruiter_profiles_user_id_key UNIQUE (user_id);


--
-- Name: referrals referrals_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referrals
    ADD CONSTRAINT referrals_pkey PRIMARY KEY (id);


--
-- Name: resume_analysis resume_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resume_analysis
    ADD CONSTRAINT resume_analysis_pkey PRIMARY KEY (id);


--
-- Name: resumes resumes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resumes
    ADD CONSTRAINT resumes_pkey PRIMARY KEY (id);


--
-- Name: skill_gap_analysis skill_gap_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skill_gap_analysis
    ADD CONSTRAINT skill_gap_analysis_pkey PRIMARY KEY (id);


--
-- Name: skills skills_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_name_key UNIQUE (name);


--
-- Name: skills skills_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_pkey PRIMARY KEY (id);


--
-- Name: skills skills_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_slug_key UNIQUE (slug);


--
-- Name: application_answers uq_application_answers_application_question; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_answers
    ADD CONSTRAINT uq_application_answers_application_question UNIQUE (application_id, question_id);


--
-- Name: applications uq_applications_job_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT uq_applications_job_user UNIQUE (job_id, user_id);


--
-- Name: community_votes uq_community_votes_comment_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_votes
    ADD CONSTRAINT uq_community_votes_comment_user UNIQUE (user_id, comment_id);


--
-- Name: community_votes uq_community_votes_post_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_votes
    ADD CONSTRAINT uq_community_votes_post_user UNIQUE (user_id, post_id);


--
-- Name: connections uq_connections_request; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.connections
    ADD CONSTRAINT uq_connections_request UNIQUE (requester_id, receiver_id);


--
-- Name: job_matches uq_job_matches_user_job; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_matches
    ADD CONSTRAINT uq_job_matches_user_job UNIQUE (user_id, job_id);


--
-- Name: job_recommendation_items uq_job_recommendation_items_run_job; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_recommendation_items
    ADD CONSTRAINT uq_job_recommendation_items_run_job UNIQUE (run_id, job_id);


--
-- Name: skill_gap_analysis uq_skill_gap_analysis_user_job; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skill_gap_analysis
    ADD CONSTRAINT uq_skill_gap_analysis_user_job UNIQUE (user_id, job_id);


--
-- Name: user_activity user_activity_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_activity
    ADD CONSTRAINT user_activity_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_advice_requests_advisor_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_advice_requests_advisor_status ON public.advice_requests USING btree (advisor_id, status);


--
-- Name: idx_advice_requests_requester_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_advice_requests_requester_status ON public.advice_requests USING btree (requester_id, status);


--
-- Name: idx_agent_feedback_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_feedback_user ON public.agent_feedback USING btree (user_id, created_at DESC);


--
-- Name: idx_agent_memory_embeddings_memory; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_memory_embeddings_memory ON public.agent_memory_embeddings USING btree (memory_id);


--
-- Name: idx_agent_memory_user_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_memory_user_created ON public.agent_memory USING btree (user_id, created_at DESC);


--
-- Name: idx_agent_messages_task_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_messages_task_created ON public.agent_messages USING btree (task_id, created_at);


--
-- Name: idx_agent_task_steps_task; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_task_steps_task ON public.agent_task_steps USING btree (task_id);


--
-- Name: idx_agent_tasks_user_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_agent_tasks_user_status ON public.agent_tasks USING btree (user_id, status);


--
-- Name: idx_ai_interactions_user_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ai_interactions_user_created ON public.ai_interactions USING btree (user_id, created_at DESC);


--
-- Name: idx_application_answers_application_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_application_answers_application_id ON public.application_answers USING btree (application_id);


--
-- Name: idx_application_answers_question_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_application_answers_question_id ON public.application_answers USING btree (question_id);


--
-- Name: idx_application_status_history_application; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_application_status_history_application ON public.application_status_history USING btree (application_id, created_at DESC);


--
-- Name: idx_applications_applied_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_applications_applied_at ON public.applications USING btree (applied_at DESC);


--
-- Name: idx_applications_job_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_applications_job_id ON public.applications USING btree (job_id);


--
-- Name: idx_applications_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_applications_status ON public.applications USING btree (status);


--
-- Name: idx_applications_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_applications_user_id ON public.applications USING btree (user_id);


--
-- Name: idx_career_goals_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_career_goals_user ON public.career_goals USING btree (user_id);


--
-- Name: idx_career_recommendations_job; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_career_recommendations_job ON public.career_recommendations USING btree (job_id);


--
-- Name: idx_career_recommendations_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_career_recommendations_user ON public.career_recommendations USING btree (user_id, created_at DESC);


--
-- Name: idx_community_comments_post_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_community_comments_post_created ON public.community_comments USING btree (post_id, created_at);


--
-- Name: idx_community_comments_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_community_comments_user ON public.community_comments USING btree (user_id);


--
-- Name: idx_community_posts_user_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_community_posts_user_created ON public.community_posts USING btree (user_id, created_at DESC);


--
-- Name: idx_community_votes_comment; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_community_votes_comment ON public.community_votes USING btree (comment_id);


--
-- Name: idx_community_votes_post; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_community_votes_post ON public.community_votes USING btree (post_id);


--
-- Name: idx_connections_receiver_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_connections_receiver_status ON public.connections USING btree (receiver_id, status);


--
-- Name: idx_connections_requester_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_connections_requester_status ON public.connections USING btree (requester_id, status);


--
-- Name: idx_education_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_education_user_id ON public.education USING btree (user_id);


--
-- Name: idx_experience_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_experience_user_id ON public.experience USING btree (user_id);


--
-- Name: idx_interviews_application; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_interviews_application ON public.interviews USING btree (application_id);


--
-- Name: idx_interviews_scheduled_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_interviews_scheduled_at ON public.interviews USING btree (scheduled_at);


--
-- Name: idx_job_matches_job_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_matches_job_id ON public.job_matches USING btree (job_id);


--
-- Name: idx_job_matches_user_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_matches_user_score ON public.job_matches USING btree (user_id, match_score DESC);


--
-- Name: idx_job_preferences_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_preferences_user_id ON public.job_preferences USING btree (user_id);


--
-- Name: idx_job_recommendation_items_job; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_recommendation_items_job ON public.job_recommendation_items USING btree (job_id);


--
-- Name: idx_job_recommendation_items_run; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_recommendation_items_run ON public.job_recommendation_items USING btree (run_id);


--
-- Name: idx_job_recommendation_runs_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_recommendation_runs_status ON public.job_recommendation_runs USING btree (status);


--
-- Name: idx_job_recommendation_runs_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_recommendation_runs_user ON public.job_recommendation_runs USING btree (user_id, created_at DESC);


--
-- Name: idx_job_screening_questions_job_order; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_screening_questions_job_order ON public.job_screening_questions USING btree (job_id, display_order);


--
-- Name: idx_job_skills_skill_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_job_skills_skill_id ON public.job_skills USING btree (skill_id);


--
-- Name: idx_jobs_application_deadline; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_jobs_application_deadline ON public.jobs USING btree (application_deadline);


--
-- Name: idx_jobs_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_jobs_company_id ON public.jobs USING btree (company_id);


--
-- Name: idx_jobs_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_jobs_location ON public.jobs USING btree (location);


--
-- Name: idx_jobs_posted_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_jobs_posted_by ON public.jobs USING btree (posted_by);


--
-- Name: idx_jobs_status_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_jobs_status_created_at ON public.jobs USING btree (status, created_at DESC);


--
-- Name: idx_notifications_user_unread; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_user_unread ON public.notifications USING btree (user_id, is_read, created_at DESC);


--
-- Name: idx_profile_views_viewed_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_profile_views_viewed_user ON public.profile_views USING btree (viewed_user_id, viewed_at DESC);


--
-- Name: idx_profiles_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_profiles_user_id ON public.profiles USING btree (user_id);


--
-- Name: idx_recruiter_profiles_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recruiter_profiles_company_id ON public.recruiter_profiles USING btree (company_id);


--
-- Referral indexes
--

CREATE INDEX idx_referral_opportunities_job
    ON public.referral_opportunities USING btree (job_id);


CREATE INDEX idx_referral_opportunities_posted_by
    ON public.referral_opportunities USING btree (posted_by);


CREATE INDEX idx_referral_opportunities_status
    ON public.referral_opportunities USING btree (status);


CREATE INDEX idx_referrals_opportunity
    ON public.referrals USING btree (opportunity_id);


CREATE INDEX idx_referrals_requester
    ON public.referrals USING btree (requester_id);


CREATE INDEX idx_referrals_status
    ON public.referrals USING btree (status);


CREATE INDEX idx_referrals_resume
    ON public.referrals USING btree (resume_id);


--
-- Name: idx_resume_analysis_resume; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_resume_analysis_resume ON public.resume_analysis USING btree (resume_id);


--
-- Name: idx_resume_analysis_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_resume_analysis_user ON public.resume_analysis USING btree (user_id, created_at DESC);


--
-- Name: idx_resumes_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_resumes_user_id ON public.resumes USING btree (user_id);


--
-- Name: idx_resumes_user_primary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_resumes_user_primary ON public.resumes USING btree (user_id, is_primary);


--
-- Name: idx_saved_jobs_job_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_saved_jobs_job_id ON public.saved_jobs USING btree (job_id);


--
-- Name: idx_skill_gap_analysis_job; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_skill_gap_analysis_job ON public.skill_gap_analysis USING btree (job_id);


--
-- Name: idx_skill_gap_analysis_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_skill_gap_analysis_user ON public.skill_gap_analysis USING btree (user_id, created_at DESC);


--
-- Name: idx_user_activity_user_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_activity_user_created ON public.user_activity USING btree (user_id, created_at DESC);


--
-- Name: idx_user_follows_following; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_follows_following ON public.user_follows USING btree (following_id);


--
-- Name: idx_user_skills_skill_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_skills_skill_id ON public.user_skills USING btree (skill_id);


--
-- Name: idx_users_role_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_role_status ON public.users USING btree (role, status);


--
-- Name: advice_requests fk_advice_requests_advisor; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.advice_requests
    ADD CONSTRAINT fk_advice_requests_advisor FOREIGN KEY (advisor_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: advice_requests fk_advice_requests_requester; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.advice_requests
    ADD CONSTRAINT fk_advice_requests_requester FOREIGN KEY (requester_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: agent_feedback fk_agent_feedback_interaction; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_feedback
    ADD CONSTRAINT fk_agent_feedback_interaction FOREIGN KEY (interaction_id) REFERENCES public.ai_interactions(id) ON DELETE SET NULL;


--
-- Name: agent_feedback fk_agent_feedback_task; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_feedback
    ADD CONSTRAINT fk_agent_feedback_task FOREIGN KEY (task_id) REFERENCES public.agent_tasks(id) ON DELETE SET NULL;


--
-- Name: agent_feedback fk_agent_feedback_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_feedback
    ADD CONSTRAINT fk_agent_feedback_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: agent_memory_embeddings fk_agent_memory_embeddings_memory; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_memory_embeddings
    ADD CONSTRAINT fk_agent_memory_embeddings_memory FOREIGN KEY (memory_id) REFERENCES public.agent_memory(id) ON DELETE CASCADE;


--
-- Name: agent_memory fk_agent_memory_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_memory
    ADD CONSTRAINT fk_agent_memory_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: agent_messages fk_agent_messages_task; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_messages
    ADD CONSTRAINT fk_agent_messages_task FOREIGN KEY (task_id) REFERENCES public.agent_tasks(id) ON DELETE CASCADE;


--
-- Name: agent_task_steps fk_agent_task_steps_task; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_task_steps
    ADD CONSTRAINT fk_agent_task_steps_task FOREIGN KEY (task_id) REFERENCES public.agent_tasks(id) ON DELETE CASCADE;


--
-- Name: agent_tasks fk_agent_tasks_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_tasks
    ADD CONSTRAINT fk_agent_tasks_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: ai_interactions fk_ai_interactions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_interactions
    ADD CONSTRAINT fk_ai_interactions_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: application_answers fk_application_answers_application; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_answers
    ADD CONSTRAINT fk_application_answers_application FOREIGN KEY (application_id) REFERENCES public.applications(id) ON DELETE CASCADE;


--
-- Name: application_answers fk_application_answers_question; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_answers
    ADD CONSTRAINT fk_application_answers_question FOREIGN KEY (question_id) REFERENCES public.job_screening_questions(id) ON DELETE CASCADE;


--
-- Name: application_status_history fk_application_status_history_application; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_status_history
    ADD CONSTRAINT fk_application_status_history_application FOREIGN KEY (application_id) REFERENCES public.applications(id) ON DELETE CASCADE;


--
-- Name: application_status_history fk_application_status_history_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_status_history
    ADD CONSTRAINT fk_application_status_history_user FOREIGN KEY (changed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: applications fk_applications_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT fk_applications_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: applications fk_applications_resume; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT fk_applications_resume FOREIGN KEY (resume_id) REFERENCES public.resumes(id) ON DELETE SET NULL;


--
-- Name: applications fk_applications_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT fk_applications_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: career_goals fk_career_goals_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.career_goals
    ADD CONSTRAINT fk_career_goals_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: career_recommendations fk_career_recommendations_goal; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.career_recommendations
    ADD CONSTRAINT fk_career_recommendations_goal FOREIGN KEY (goal_id) REFERENCES public.career_goals(id) ON DELETE SET NULL;


--
-- Name: career_recommendations fk_career_recommendations_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.career_recommendations
    ADD CONSTRAINT fk_career_recommendations_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE SET NULL;


--
-- Name: career_recommendations fk_career_recommendations_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.career_recommendations
    ADD CONSTRAINT fk_career_recommendations_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: community_comments fk_community_comments_parent; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_comments
    ADD CONSTRAINT fk_community_comments_parent FOREIGN KEY (parent_comment_id) REFERENCES public.community_comments(id) ON DELETE CASCADE;


--
-- Name: community_comments fk_community_comments_post; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_comments
    ADD CONSTRAINT fk_community_comments_post FOREIGN KEY (post_id) REFERENCES public.community_posts(id) ON DELETE CASCADE;


--
-- Name: community_comments fk_community_comments_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_comments
    ADD CONSTRAINT fk_community_comments_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: community_posts fk_community_posts_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_posts
    ADD CONSTRAINT fk_community_posts_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: community_votes fk_community_votes_comment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_votes
    ADD CONSTRAINT fk_community_votes_comment FOREIGN KEY (comment_id) REFERENCES public.community_comments(id) ON DELETE CASCADE;


--
-- Name: community_votes fk_community_votes_post; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_votes
    ADD CONSTRAINT fk_community_votes_post FOREIGN KEY (post_id) REFERENCES public.community_posts(id) ON DELETE CASCADE;


--
-- Name: community_votes fk_community_votes_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.community_votes
    ADD CONSTRAINT fk_community_votes_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: connections fk_connections_receiver; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.connections
    ADD CONSTRAINT fk_connections_receiver FOREIGN KEY (receiver_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: connections fk_connections_requester; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.connections
    ADD CONSTRAINT fk_connections_requester FOREIGN KEY (requester_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: education fk_education_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.education
    ADD CONSTRAINT fk_education_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: experience fk_experience_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experience
    ADD CONSTRAINT fk_experience_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: interview_preparations fk_interview_preparations_application; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_preparations
    ADD CONSTRAINT fk_interview_preparations_application FOREIGN KEY (application_id) REFERENCES public.applications(id) ON DELETE CASCADE;


--
-- Name: interview_preparations fk_interview_preparations_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_preparations
    ADD CONSTRAINT fk_interview_preparations_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: interviews fk_interviews_application; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT fk_interviews_application FOREIGN KEY (application_id) REFERENCES public.applications(id) ON DELETE CASCADE;


--
-- Name: interviews fk_interviews_interviewer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT fk_interviews_interviewer FOREIGN KEY (interviewer_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: job_matches fk_job_matches_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_matches
    ADD CONSTRAINT fk_job_matches_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: job_matches fk_job_matches_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_matches
    ADD CONSTRAINT fk_job_matches_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: job_preferences fk_job_preferences_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_preferences
    ADD CONSTRAINT fk_job_preferences_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: job_recommendation_items fk_job_recommendation_items_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_recommendation_items
    ADD CONSTRAINT fk_job_recommendation_items_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: job_recommendation_items fk_job_recommendation_items_run; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_recommendation_items
    ADD CONSTRAINT fk_job_recommendation_items_run FOREIGN KEY (run_id) REFERENCES public.job_recommendation_runs(id) ON DELETE CASCADE;


--
-- Name: job_recommendation_runs fk_job_recommendation_runs_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_recommendation_runs
    ADD CONSTRAINT fk_job_recommendation_runs_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: job_reports fk_job_reports_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_reports
    ADD CONSTRAINT fk_job_reports_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: job_reports fk_job_reports_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_reports
    ADD CONSTRAINT fk_job_reports_user FOREIGN KEY (reported_by) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: job_screening_questions fk_job_screening_questions_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_screening_questions
    ADD CONSTRAINT fk_job_screening_questions_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: job_skills fk_job_skills_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_skills
    ADD CONSTRAINT fk_job_skills_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: job_skills fk_job_skills_skill; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.job_skills
    ADD CONSTRAINT fk_job_skills_skill FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: jobs fk_jobs_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT fk_jobs_company FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: jobs fk_jobs_posted_by; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT fk_jobs_posted_by FOREIGN KEY (posted_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: notifications fk_notifications_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: profile_views fk_profile_views_viewed_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profile_views
    ADD CONSTRAINT fk_profile_views_viewed_user FOREIGN KEY (viewed_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: profile_views fk_profile_views_viewer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profile_views
    ADD CONSTRAINT fk_profile_views_viewer FOREIGN KEY (viewer_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: profiles fk_profiles_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: recruiter_profiles fk_recruiter_profiles_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recruiter_profiles
    ADD CONSTRAINT fk_recruiter_profiles_company FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: recruiter_profiles fk_recruiter_profiles_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recruiter_profiles
    ADD CONSTRAINT fk_recruiter_profiles_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: referrals fk_referrals_requester; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referrals
    ADD CONSTRAINT fk_referrals_requester FOREIGN KEY (requester_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: resume_analysis fk_resume_analysis_resume; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resume_analysis
    ADD CONSTRAINT fk_resume_analysis_resume FOREIGN KEY (resume_id) REFERENCES public.resumes(id) ON DELETE CASCADE;


--
-- Name: resume_analysis fk_resume_analysis_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resume_analysis
    ADD CONSTRAINT fk_resume_analysis_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: resumes fk_resumes_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resumes
    ADD CONSTRAINT fk_resumes_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: saved_jobs fk_saved_jobs_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT fk_saved_jobs_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: saved_jobs fk_saved_jobs_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.saved_jobs
    ADD CONSTRAINT fk_saved_jobs_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: skill_gap_analysis fk_skill_gap_analysis_job; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skill_gap_analysis
    ADD CONSTRAINT fk_skill_gap_analysis_job FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: skill_gap_analysis fk_skill_gap_analysis_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skill_gap_analysis
    ADD CONSTRAINT fk_skill_gap_analysis_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_activity fk_user_activity_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_activity
    ADD CONSTRAINT fk_user_activity_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_follows fk_user_follows_follower; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_follows
    ADD CONSTRAINT fk_user_follows_follower FOREIGN KEY (follower_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_follows fk_user_follows_following; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_follows
    ADD CONSTRAINT fk_user_follows_following FOREIGN KEY (following_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_skills fk_user_skills_skill; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT fk_user_skills_skill FOREIGN KEY (skill_id) REFERENCES public.skills(id) ON DELETE CASCADE;


--
-- Name: user_skills fk_user_skills_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT fk_user_skills_user FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict koZ7d0hwa7uWIexYiprZo1FZXzB8Ol2TIeg1ranuqjPLKMWsxM0oMylYfjA50ny

