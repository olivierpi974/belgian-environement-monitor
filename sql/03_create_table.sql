CREATE TABLE IF NOT EXISTS silver.f1_emission
(reportingYear INT,
eprtr_sectorcode SMALLINT,
eprtr_sectorname VARCHAR(100),
facilityinspireid VARCHAR(100),
facilityName VARCHAR(100),
city VARCHAR (50),
Longitude NUMERIC(15,6),
Latitude NUMERIC(15,6),
pollutant VARCHAR(100),
emitted_pollutant_kg NUMERIC(15,4));


CREATE TABLE IF NOT EXISTS monitoring.silver_monitoring
(table_name VARCHAR(50),
nb_rows_out INT,
nb_null_in INT,
nb_null_out INT,
nb_col_out INT, 
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

CREATE TABLE IF NOT EXISTS silver.f6_installation
(reportingyear INT,
parent_facilityinspireid VARCHAR(120),
installationinspireid VARCHAR(120),
city_of_facility VARCHAR(50),
longitude NUMERIC(15,6),
latitude NUMERIC(15,6),
PRIMARY KEY(installationinspireid,reportingyear));

CREATE TABLE IF NOT EXISTS silver.bridge_lcp_installation
(lcpinspireid VARCHAR(120), 
installationinspireid VARCHAR(120), 
parent_facilityinspireid VARCHAR(120),
lcp_name VARCHAR(255),
installation_name VARCHAR(255),
lcp_city VARCHAR(100),
installation_city VARCHAR(100),
lcp_longitude DOUBLE PRECISION,
lcp_latitude DOUBLE PRECISION,
installation_longitude DOUBLE PRECISION,
installation_latitude DOUBLE PRECISION,
distance_km DOUBLE PRECISION, 
name_similarity DOUBLE PRECISION,
same_city_flag BOOLEAN,
id_guess_match BOOLEAN,
same_city_search_used BOOLEAN,
candidate_rank INT,
match_score DOUBLE PRECISION,
top1_minus_top2 DOUBLE PRECISION,
confidence_level VARCHAR(10), 
manual_review_required BOOLEAN,
PRIMARY KEY (lcpinspireid)
);


CREATE TABLE IF NOT EXISTS gold.dim_year 
(
    year SMALLINT PRIMARY KEY,
    decade SMALLINT,
);

CREATE TABLE IF NOT EXISTS  gold.dim_pollutant
(pollutant_id SMALLINT,
pollutant VARCHAR(150), 
PRIMARY KEY (pollutant_id))

CREATE TABLE IF NOT EXISTS gold.dim_sector
(
    eprtr_sectorcode INT PRIMARY KEY, 
    eprtr_sectorname VARCHAR(150), 
    
)

CREATE TABLE IF NOT EXISTS gold.dim_site
(
    site_id SMALLINT PRIMARY KEY, 
    facilityinspireid TEXT, 
    facilityName VARCHAR(150), 
    city VARCHAR(120), 
    longitude DOUBLE PRECISION, 
    latitude DOUBLE PRECISION, 

)

CREATE TABLE IF NOT EXISTS gold.fact_emissions_air
( year SMALLINT REFERENCES gold.dim_year (year), 
fk_eprtr_sectorcode INT REFERENCES gold.dim_sector (eprtr_sectorcode), 
fk_site_id SMALLINT REFERENCES gold.dim_site (site_id),
fk_pollutant_id SMALLINT REFERENCES gold.dim_pollutant (pollutant_id),
emitted_pollutant_kg DOUBLE PRECISION, 
PRIMARY KEY (year, fk_site_id, fk_pollutant_id)
)