-- This script was generated by the Schema Diff utility in pgAdmin 4
-- For the circular dependencies, the order in which Schema Diff writes the objects is not very sophisticated
-- and may require manual changes to the script to ensure changes are applied in the correct order.
-- Please report an issue for any failure with the reproduction steps.

CREATE TABLE IF NOT EXISTS public.request
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    body jsonb NOT NULL,
    path text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT request_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.request
    OWNER to postgres;

GRANT ALL ON TABLE public.request TO anon;

GRANT ALL ON TABLE public.request TO authenticated;

GRANT ALL ON TABLE public.request TO postgres;

GRANT ALL ON TABLE public.request TO service_role;

CREATE TABLE IF NOT EXISTS public.response
(
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    body jsonb NOT NULL,
    request uuid NOT NULL,
    CONSTRAINT response_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.response
    OWNER to postgres;

GRANT ALL ON TABLE public.response TO anon;

GRANT ALL ON TABLE public.response TO authenticated;

GRANT ALL ON TABLE public.response TO postgres;

GRANT ALL ON TABLE public.response TO service_role;

