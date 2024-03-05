-- Database: bnipi_v2

DROP DATABASE IF EXISTS bnipi_v3;

CREATE DATABASE bnipi_v3
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Russian_Russia.1251'
    LC_CTYPE = 'Russian_Russia.1251'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;


-- Table: well

CREATE TABLE IF NOT EXISTS well
(
	pk_id UUID,
	name CHARACTER VARYING(32) NOT NULL,
	head POINT NOT NULL,
	md DOUBLE PRECISION[] NOT NULL,
	x DOUBLE PRECISION[] NOT NULL,
	y DOUBLE PRECISION[] NOT NULL,
	z DOUBLE PRECISION[] NOT NULL,
	CONSTRAINT well_pkey PRIMARY KEY (pk_id),
	CONSTRAINT well_name_key UNIQUE (name, pk_id)
) PARTITION BY LIST (pk_id);


-- Procedure: insert_well

CREATE OR REPLACE FUNCTION insert_well(
	well_name CHARACTER VARYING(32),
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
BEGIN

EXECUTE FORMAT(
	'CREATE TABLE %I PARTITION OF well FOR VALUES IN (%L)',
	'well_' || well_name,
	well_uuid
);

INSERT INTO well (pk_id, name, head, md, x, y, z)
VALUES (well_uuid, well_name, well_head, md, x, y, z);

RETURN well_uuid;

END;
$$ LANGUAGE plpgsql;


-- Function: delete_well

CREATE OR REPLACE FUNCTION delete_well(well_uuid UUID)
RETURNS BOOLEAN
AS $$
DECLARE
	is_exists BOOLEAN;
	well_name VARCHAR(32);
BEGIN

is_exists := (SELECT COUNT(pk_id) FROM well WHERE pk_id = well_uuid) > 0;

IF NOT is_exists THEN
	RETURN FALSE;
END IF;

well_name := (SELECT name FROM well WHERE pk_id = well_uuid);

DELETE FROM well
WHERE pk_id = well_uuid;

EXECUTE FORMAT(
	'DROP TABLE %I;',
	'well_' || well_name
);

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
