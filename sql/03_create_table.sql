CREATE TABLE IF NOT EXISTS silver.f1_emission
(reportingYear INT,
eprtr_sectorcode SMALLINT,
eprtr_sectorname VARCHAR(100),
facilityinspireid VARCHAR(100),
facilityName VARCHAR(100),
city VARCHAR (50),
Longitude NUMERIC(15,6),
Latitude NUMERIC(15,6),
emitted_co2_kg NUMERIC(15,4));


CREATE TABLE IF NOT EXISTS monitoring.silver_monitoring
(table_name VARCHAR(50),
nb_rows_out INT,
nb_null_in SMALLINT,
nb_null_out SMALLINT,
nb_col_out SMALLINT, 
duration_sec NUMERIC (6,2),
date_transform TIMESTAMP);

CREATE TABLE IF NOT EXISTS silver.f5_energy
(reportingyear INT,
lcpinspireid VARCHAR(100),
installationpartname VARCHAR(100),
city_of_facility VARCHAR(50),
longitude NUMERIC(15,6),
latitude NUMERIC(15,6),
biomass DOUBLE PRECISION, 
coal DOUBLE PRECISION,
lignite DOUBLE PRECISION,
liquidfuels DOUBLE PRECISION,
naturalgas DOUBLE PRECISION,
othergases DOUBLE PRECISION,
othersolidfuels DOUBLE PRECISION,
peat DOUBLE PRECISION,
PRIMARY KEY (lcpinspireid, reportingyear)
);