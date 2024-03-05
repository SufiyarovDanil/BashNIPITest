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

CREATE TABLE IF NOT EXISTS well
(
	pk_id UUID NOT NULL,
    name CHARACTER VARYING(32) NOT NULL,
    head POINT NOT NULL,
	trajectory_table_name CHARACTER VARYING(45) NOT NULL,
    CONSTRAINT well_pkey PRIMARY KEY (pk_id),
    CONSTRAINT well_name_key UNIQUE (name)
)


CREATE OR REPLACE FUNCTION insert_well(
	well_name CHARACTER VARYING,
	well_head POINT,
	md DOUBLE PRECISION[],
	x DOUBLE PRECISION[],
	y DOUBLE PRECISION[],
	z DOUBLE PRECISION[]
)
RETURNS UUID
AS $$
DECLARE
	well_uuid UUID := gen_random_uuid();
	trajectory_table_name TEXT := 'trajectory' || well_name;
BEGIN

INSERT INTO well (pk_id, name, head, trajectory_table_name)
VALUES (well_uuid, well_name, well_head, trajectory_table_name);

EXECUTE FORMAT(
	'CREATE TABLE %I
	(
    	md double precision NOT NULL,
    	x double precision NOT NULL,
    	y double precision NOT NULL,
    	z double precision NOT NULL
	)',
	trajectory_table_name
);

EXECUTE FORMAT(
	'INSERT INTO %I (md, x, y, z)
	SELECT * FROM UNNEST(
	%L::DOUBLE PRECISION[],
	%L::DOUBLE PRECISION[],
	%L::DOUBLE PRECISION[],
	%L::DOUBLE PRECISION[]
	)
	AS zzz("MD", "X", "Y", "Z")',
	trajectory_table_name,
	md, x, y, z);

RETURN well_uuid;

END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_well_with_trajectory(well_id uuid)
RETURNS TABLE(
	"name" CHARACTER VARYING(32),
	"head" POINT,
	"MD" DOUBLE PRECISION[],
	"X" DOUBLE PRECISION[],
	"Y" DOUBLE PRECISION[],
	"Z" DOUBLE PRECISION[]
)
AS $$
DECLARE
	traj_table_name CHARACTER VARYING;
BEGIN

traj_table_name := (SELECT trajectory_table_name FROM well WHERE pk_id = well_id);

RETURN QUERY
	EXECUTE FORMAT(
	'
	SELECT well.name, well.head, md, x, y, z
	FROM well, (
		SELECT ARRAY_AGG(md) as md, ARRAY_AGG(x) as x, ARRAY_AGG(y) as y, ARRAY_AGG(z) as z 
		FROM %I
	)
	WHERE pk_id = %L
	',
	traj_table_name,
	well_id
	);
END;
$$ LANGUAGE plpgsql;
