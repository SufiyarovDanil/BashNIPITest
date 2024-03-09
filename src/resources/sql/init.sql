-- TABLE: well_names

CREATE TABLE IF NOT EXISTS well_names
(
	well_name CHARACTER VARYING(32) NOT NULL,
	CONSTRAINT unique_name UNIQUE (well_name)
);


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

EXECUTE
	'CREATE TABLE well_' || REPLACE(well_uuid::TEXT, '-', '')::CHARACTER VARYING ||
	'(
		pk_id UUID NOT NULL,
		name CHARACTER VARYING(32) NOT NULL,
		head POINT NOT NULL,
		md DOUBLE PRECISION[] NOT NULL,
		x DOUBLE PRECISION[] NOT NULL,
		y DOUBLE PRECISION[] NOT NULL,
		z DOUBLE PRECISION[] NOT NULL
	)';

EXECUTE 'INSERT INTO well_' || REPLACE(well_uuid::TEXT, '-', '')::CHARACTER VARYING ||
		' VALUES ($1, $2, $3, $4, $5, $6, $7)'
USING well_uuid, well_name, well_head, md, x, y, z;

INSERT INTO well_names VALUES (well_name);

RETURN well_uuid;

END;
$$ LANGUAGE plpgsql;


-- Function: delete_well

CREATE OR REPLACE FUNCTION delete_well(well_uuid UUID)
RETURNS BOOLEAN
AS $$
DECLARE
	is_exists BOOLEAN;
	well_name_to_delete TEXT;
	well_table_name TEXT;
BEGIN

well_table_name := 'well_' || REPLACE(well_uuid::TEXT, '-', '');
is_exists := (SELECT EXISTS (
   SELECT FROM information_schema.tables 
   WHERE table_name = well_table_name
));

IF NOT is_exists THEN
	RETURN FALSE;
END IF;

EXECUTE 'SELECT name FROM ' || well_table_name || ' WHERE pk_id = $1'
INTO well_name_to_delete
USING well_uuid;

DELETE FROM well_names WHERE well_name = well_name_to_delete;

EXECUTE 'DROP TABLE ' || well_table_name;

RETURN TRUE;

END;
$$ LANGUAGE plpgsql;
