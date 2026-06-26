-- ══════════════════════════════════════════
-- Initialisation des domaines Data Mesh
-- Exécuté automatiquement au premier démarrage de PostgreSQL
-- ══════════════════════════════════════════

-- 1. Domaines isolés (1 base par domaine)
CREATE DATABASE sales_db;
CREATE DATABASE marketing_db;
CREATE DATABASE finance_db;

-- 2. Schémas Input/Output pour chaque domaine
\c sales_db
CREATE SCHEMA input;
CREATE SCHEMA output;
GRANT ALL ON SCHEMA input TO admin;
GRANT ALL ON SCHEMA output TO admin;

\c marketing_db
CREATE SCHEMA input;
CREATE SCHEMA output;
GRANT ALL ON SCHEMA input TO admin;
GRANT ALL ON SCHEMA output TO admin;

\c finance_db
CREATE SCHEMA input;
CREATE SCHEMA output;
GRANT ALL ON SCHEMA input TO admin;
GRANT ALL ON SCHEMA output TO admin;

-- 3. Metadata database for governance
\c datamesh
CREATE SCHEMA governance;
GRANT ALL ON SCHEMA governance TO admin;
