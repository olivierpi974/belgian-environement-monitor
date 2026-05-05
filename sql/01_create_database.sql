SELECT 'CREATE DATABASE belgian_environnement_data'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'belgian_environnement_data')\gexec
