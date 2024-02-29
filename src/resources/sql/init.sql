CREATE TYPE point3D AS
(
	x DOUBLE PRECISION,
	y DOUBLE PRECISION,
	z DOUBLE PRECISION
);

-- Table: public.well

-- DROP TABLE IF EXISTS public.well;

CREATE TABLE IF NOT EXISTS public.well
(
    pk_id uuid NOT NULL,
    name character varying(64) COLLATE pg_catalog."default" NOT NULL,
    head point NOT NULL,
    measured_depth double precision[] NOT NULL,
    trajectory point3d[] NOT NULL,
    CONSTRAINT well_pkey PRIMARY KEY (pk_id),
    CONSTRAINT well_name_key UNIQUE (name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.well
    OWNER to postgres;