-- ============================================================================
-- SkillBridge Supabase Database Schema & Row Level Security (RLS) Policies
-- Run this script in the Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)
-- ============================================================================

-- 1. PROFILES TABLE
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    target_group TEXT DEFAULT 'Fresher Only',
    skills_input TEXT DEFAULT '',
    hours_per_day INTEGER DEFAULT 2,
    days_per_week INTEGER DEFAULT 5,
    start_date TEXT,
    has_analyzed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS for profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can delete own profile" ON public.profiles;
CREATE POLICY "Users can delete own profile"
    ON public.profiles FOR DELETE
    USING (auth.uid() = id);


-- 2. USER GAP ANALYSES TABLE (Stored Analysis Results)
CREATE TABLE IF NOT EXISTS public.user_gap_analyses (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    skills_input TEXT NOT NULL,
    group_name TEXT NOT NULL,
    coverage_percentage REAL NOT NULL,
    matched_count INTEGER NOT NULL,
    total_top INTEGER NOT NULL,
    matched_skills JSONB DEFAULT '[]'::jsonb,
    missing_skills JSONB DEFAULT '[]'::jsonb,
    not_in_dataset JSONB DEFAULT '[]'::jsonb,
    main_roadmap JSONB DEFAULT '[]'::jsonb,
    optional_roadmap JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT user_gap_analyses_user_id_key UNIQUE (user_id)
);

-- Enable RLS for user_gap_analyses
ALTER TABLE public.user_gap_analyses ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own gap analysis" ON public.user_gap_analyses;
CREATE POLICY "Users can view own gap analysis"
    ON public.user_gap_analyses FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own gap analysis" ON public.user_gap_analyses;
CREATE POLICY "Users can insert own gap analysis"
    ON public.user_gap_analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own gap analysis" ON public.user_gap_analyses;
CREATE POLICY "Users can update own gap analysis"
    ON public.user_gap_analyses FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own gap analysis" ON public.user_gap_analyses;
CREATE POLICY "Users can delete own gap analysis"
    ON public.user_gap_analyses FOR DELETE
    USING (auth.uid() = user_id);


-- 3. STUDY SCHEDULES TABLE (Metadata)
CREATE TABLE IF NOT EXISTS public.study_schedules (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    total_weeks INTEGER NOT NULL,
    hours_per_day REAL NOT NULL,
    days_per_week INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT study_schedules_user_id_key UNIQUE (user_id)
);

-- Enable RLS for study_schedules
ALTER TABLE public.study_schedules ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own schedule" ON public.study_schedules;
CREATE POLICY "Users can view own schedule"
    ON public.study_schedules FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own schedule" ON public.study_schedules;
CREATE POLICY "Users can insert own schedule"
    ON public.study_schedules FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own schedule" ON public.study_schedules;
CREATE POLICY "Users can update own schedule"
    ON public.study_schedules FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own schedule" ON public.study_schedules;
CREATE POLICY "Users can delete own schedule"
    ON public.study_schedules FOR DELETE
    USING (auth.uid() = user_id);


-- 4. STUDY TASKS TABLE (Individual tasks with completion tracking)
CREATE TABLE IF NOT EXISTS public.study_tasks (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    task_id TEXT NOT NULL,
    week_num INTEGER NOT NULL,
    week_label TEXT NOT NULL,
    date_str TEXT NOT NULL,
    day_index INTEGER NOT NULL,
    task_order INTEGER NOT NULL,
    skill TEXT NOT NULL,
    hours REAL NOT NULL,
    display_text TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT study_tasks_user_task_unique UNIQUE (user_id, task_id)
);

-- Enable RLS for study_tasks
ALTER TABLE public.study_tasks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own tasks" ON public.study_tasks;
CREATE POLICY "Users can view own tasks"
    ON public.study_tasks FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own tasks" ON public.study_tasks;
CREATE POLICY "Users can insert own tasks"
    ON public.study_tasks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own tasks" ON public.study_tasks;
CREATE POLICY "Users can update own tasks"
    ON public.study_tasks FOR UPDATE
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own tasks" ON public.study_tasks;
CREATE POLICY "Users can delete own tasks"
    ON public.study_tasks FOR DELETE
    USING (auth.uid() = user_id);


-- 5. CHAT HISTORY TABLE (Per-user study assistant conversations)
CREATE TABLE IF NOT EXISTS public.chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS for chat_history
ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own chat" ON public.chat_history;
CREATE POLICY "Users can view own chat"
    ON public.chat_history FOR SELECT
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own chat" ON public.chat_history;
CREATE POLICY "Users can insert own chat"
    ON public.chat_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own chat" ON public.chat_history;
CREATE POLICY "Users can delete own chat"
    ON public.chat_history FOR DELETE
    USING (auth.uid() = user_id);


-- 6. AUTOMATIC PROFILE CREATION TRIGGER ON SIGNUP
-- Automatically creates a matching public.profiles row when a new user signs up in auth.users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email)
    VALUES (new.id, new.email)
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

