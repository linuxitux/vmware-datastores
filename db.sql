
drop table datastore_space;
--drop sequence datastore_space_id_seq;

-- datastore_space
-- Tabla para almacenar estadísticas de uso de datastores en formato JSON
CREATE TABLE datastore_space (
  id integer NOT NULL,
  fecha timestamp NOT NULL,
  jdata jsonb NOT NULL
);
CREATE SEQUENCE datastore_space_id_seq;
ALTER SEQUENCE datastore_space_id_seq OWNED BY datastore_space.id;
ALTER TABLE datastore_space ALTER id SET DEFAULT nextval('datastore_space_id_seq');

-- datastore_space_fecha_idx
-- Indice para la columna 'fecha' de la tabla 'datastore_space'
CREATE INDEX datastore_space_fecha_idx ON datastore_space (fecha);

-- datastore_usage
-- Tabla para almacenar estadísticas de uso de datastores por vm en formato JSON
CREATE TABLE datastore_usage (
  id integer NOT NULL,
  fecha timestamp NOT NULL,
  jdata jsonb NOT NULL
);
CREATE SEQUENCE datastore_usage_id_seq;
ALTER SEQUENCE datastore_usage_id_seq OWNED BY datastore_usage.id;
ALTER TABLE datastore_usage ALTER id SET DEFAULT nextval('datastore_usage_id_seq');

-- datastore_space_fecha_idx
-- Indice para la columna 'fecha' de la tabla 'datastore_space'
CREATE INDEX datastore_usage_fecha_idx ON datastore_usage (fecha);
