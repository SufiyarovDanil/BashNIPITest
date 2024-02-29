-- Database: bnipi_v2

DROP DATABASE IF EXISTS bnipi_v2;

CREATE DATABASE bnipi_v2
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Russian_Russia.1251'
    LC_CTYPE = 'Russian_Russia.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;


-- Table: public.well

DROP TABLE IF EXISTS public.well;

CREATE TABLE IF NOT EXISTS public.well
(
    pk_id uuid NOT NULL,
    name character varying(64) COLLATE pg_catalog."default" NOT NULL,
    head point NOT NULL,
    CONSTRAINT well_pkey PRIMARY KEY (pk_id),
    CONSTRAINT well_name_key UNIQUE (name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.well
    OWNER to postgres;


-- Table: public.trajectory

DROP TABLE IF EXISTS public.trajectory;

CREATE TABLE IF NOT EXISTS public.trajectory
(
    pk_id bigint NOT NULL DEFAULT nextval('trajectory_pk_id_seq'::regclass),
    md double precision NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    z double precision NOT NULL,
    fk_well_id uuid NOT NULL,
    CONSTRAINT trajectory_pkey PRIMARY KEY (pk_id),
    CONSTRAINT trajectory_fk_well_id_fkey FOREIGN KEY (fk_well_id)
        REFERENCES public.well (pk_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.trajectory
    OWNER to postgres;
