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

CREATE TABLE public.agent_memory_embeddings (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    memory_id uuid NOT NULL,
    embedding public.vector(1536),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

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

CREATE TABLE public.application_answers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    application_id uuid NOT NULL,
    question_id uuid NOT NULL,
    answer text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.application_status_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    application_id uuid NOT NULL,
    status public.application_status NOT NULL,
    changed_by uuid,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

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

CREATE TABLE public.community_comments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    post_id uuid NOT NULL,
    user_id uuid NOT NULL,
    parent_comment_id uuid,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.community_posts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.community_votes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    post_id uuid,
    comment_id uuid,
    vote public.vote_type NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_community_votes_target CHECK ((((post_id IS NOT NULL) AND (comment_id IS NULL)) OR ((post_id IS NULL) AND (comment_id IS NOT NULL))))
);

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

CREATE TABLE public.connections (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    requester_id uuid NOT NULL,
    receiver_id uuid NOT NULL,
    status public.connection_status DEFAULT 'PENDING'::public.connection_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_connections_different_users CHECK ((requester_id <> receiver_id))
);

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

CREATE TABLE public.job_matches (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    job_id uuid NOT NULL,
    match_score numeric(5,2),
    match_reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_job_matches_score CHECK (((match_score IS NULL) OR ((match_score >= (0)::numeric) AND (match_score <= (100)::numeric))))
);

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

CREATE TABLE public.job_skills (
    job_id uuid NOT NULL,
    skill_id uuid NOT NULL,
    is_required boolean DEFAULT true NOT NULL,
    proficiency_level text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

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

CREATE TABLE public.profile_views (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    viewer_id uuid,
    viewed_user_id uuid NOT NULL,
    viewed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_profile_views_different_users CHECK (((viewer_id IS NULL) OR (viewer_id <> viewed_user_id)))
);

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

CREATE TABLE public.recruiter_profiles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    company_id uuid NOT NULL,
    designation text,
    bio text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.referrals (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    requester_id uuid NOT NULL,
    referrer_id uuid NOT NULL,
    job_id uuid NOT NULL,
    message text,
    status public.referral_request_status DEFAULT 'PENDING'::public.referral_request_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_referrals_different_users CHECK ((requester_id <> referrer_id))
);

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

CREATE TABLE public.saved_jobs (
    user_id uuid NOT NULL,
    job_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

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

CREATE TABLE public.skills (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    slug text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.user_activity (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    user_id uuid NOT NULL,
    activity_type text NOT NULL,
    reference_id uuid,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE public.user_follows (
    follower_id uuid NOT NULL,
    following_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_user_follows_different_users CHECK ((follower_id <> following_id))
);

CREATE TABLE public.user_skills (
    user_id uuid NOT NULL,
    skill_id uuid NOT NULL,
    proficiency text,
    years_experience numeric(4,1),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_user_skills_experience CHECK (((years_experience IS NULL) OR (years_experience >= (0)::numeric)))
);

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email public.citext NOT NULL,
    password_hash text NOT NULL,
    role public.user_role DEFAULT 'CANDIDATE'::public.user_role NOT NULL,
    status public.user_status DEFAULT 'ACTIVE'::public.user_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

