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


-- Table: well

CREATE TABLE IF NOT EXISTS public.well
(
    pk_id UUID NOT NULL,
    name CHARACTER VARYING(64) NOT NULL,
    head POINT NOT NULL,
    CONSTRAINT well_pkey PRIMARY KEY (pk_id),
    CONSTRAINT well_name_key UNIQUE (name)
)


-- Table: trajectory

CREATE TABLE IF NOT EXISTS trajectory
(
	fk_well_id UUID,
	md DOUBLE PRECISION NOT NULL,
	x DOUBLE PRECISION NOT NULL,
	y DOUBLE PRECISION NOT NULL,
	z DOUBLE PRECISION NOT NULL,
	CONSTRAINT fk_well_id
		FOREIGN KEY (fk_well_id)
        REFERENCES well (pk_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
) PARTITION BY LIST (fk_well_id);



-- Procedure: insert_well

CREATE OR REPLACE FUNCTION insert_well(
	well_name CHARACTER VARYING(64),
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
	trajectory_table_name TEXT := 'trajectory_' || well_name;
	l_sql TEXT;
BEGIN

INSERT INTO well (pk_id, name, head)
VALUES (well_uuid, well_name, well_head);

l_sql := format(
	'CREATE TABLE %I PARTITION OF trajectory FOR VALUES IN (%L)',
	trajectory_table_name,
	well_uuid
);
EXECUTE l_sql;

INSERT INTO trajectory (fk_well_id, md, x, y, z)
SELECT well_uuid, zzz.*
FROM UNNEST(md, x, y, z) as zzz(md, x, y, z);

RETURN well_uuid;

END;
$$ LANGUAGE plpgsql;


-- Function: delete_well

CREATE OR REPLACE FUNCTION delete_well(well_uuid UUID)
RETURNS BOOLEAN
AS $$
DECLARE
	is_exists BOOLEAN;
	well_name VARCHAR(64);
	l_sql TEXT;
BEGIN

is_exists := (SELECT COUNT(pk_id) FROM well WHERE pk_id = well_uuid) > 0;

IF NOT is_exists THEN
	RETURN FALSE;
END IF;

well_name := (SELECT name FROM well WHERE pk_id = well_uuid);

DELETE FROM well
WHERE pk_id = well_uuid;

l_sql := format(
	'DROP TABLE %I;',
	'trajectory_' || well_name
);

EXECUTE l_sql;

RETURN TRUE;

END;
$$ LANGUAGE plpgsql;


-- Function: get_well_with_trajectory

CREATE OR REPLACE FUNCTION get_well_with_trajectory(well_id UUID)
RETURNS TABLE(
	"name" CHARACTER VARYING(64),
	"head" POINT,
	"MD" DOUBLE PRECISION[],
	"X" DOUBLE PRECISION[],
	"Y" DOUBLE PRECISION[],
	"Z" DOUBLE PRECISION[]
)
AS $$

SELECT name, head, "MD", "X", "Y", "Z"
FROM well, (
	SELECT ARRAY_AGG(md) as "MD", ARRAY_AGG(x) as "X", ARRAY_AGG(y) as "Y", ARRAY_AGG(z) as "Z"
	   FROM trajectory
	   WHERE fk_well_id = well_id
)
WHERE pk_id = well_id
$$ LANGUAGE SQL;


-- Function: get_well

CREATE OR REPLACE FUNCTION get_well(well_id UUID)
RETURNS TABLE (
	"name" CHARACTER VARYING(64),
	"head" POINT
)
AS $$

SELECT name, head
FROM well
WHERE pk_id = well_id

$$ LANGUAGE SQL;


-- Prepare: get_well

PREPARE get_well(UUID) AS
	SELECT name, head
	FROM well
	WHERE pk_id = $1


-- Prepare: get_well_with_trajectory

PREPARE get_well_with_trajectory(UUID) AS
	SELECT name, head, "MD", "X", "Y", "Z"
	FROM well, (
		SELECT ARRAY_AGG(md) as "MD", ARRAY_AGG(x) as "X", ARRAY_AGG(y) as "Y", ARRAY_AGG(z) as "Z"
	   	FROM trajectory
	   	WHERE fk_well_id = $1
	)
	WHERE pk_id = $1
