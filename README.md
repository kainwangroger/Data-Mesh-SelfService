# Data Mesh — Plateforme Data Self-Service

**Stack :** PostgreSQL (multi-domaine) + dbt + Airflow + Streamlit + MinIO + Custom Governance  
**Contexte :** 500+ employés, 15 domaines métiers | **Niveau :** Avancé

---

## Comprendre le projet

### En langage simple (non-tech)

Imagine une entreprise où chaque équipe (Ventes, Marketing, Finance) possède **ses propres données** comme un département possède son propre classeur. Avant, tout le monde écrivait dans le *même* classeur → chaos.

Le **Data Mesh** c'est :
1. **Chaque domaine possède ses données** — Ventes gère ses ventes, Marketing ses campagnes
2. **Chaque domaine expose des "Data Products"** — des tables bien propres, documentées, avec un SLA
3. **Un portail self-service** pour découvrir et demander l'accès aux données des autres domaines
4. **Des contrats** entre domaines : qui a le droit de lire quoi, à quelle fréquence, avec quelle qualité

> C'est comme un marché : chaque stand (domaine) expose ses produits (data products). Un portail central te dit ce qui est disponible et les règles pour y accéder.

### En langage technique

```
┌─────────────────────────────────────────────────────────────┐
│  Data Mesh Self-Service Portal (Streamlit)                  │
│  Catalogue + Demandes d'accès + Policy Evaluation           │
└─────────────────────────┬───────────────────────────────────┘
                          │ API REST
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Governance API (FastAPI)                                   │
│  · Metadata Registry (data products / contracts / policies) │
│  · Policy-as-Code engine (évaluation d'accès)               │
│  · Audit log                                                │
└─────────────────────────┬───────────────────────────────────┘
                          │ orchestre
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Airflow DAG (quotidien)                                    │
│  · Health check domains                                     │
│  · Validation des contrats                                  │
│  · Détection de schema drift                                │
│  · Rapport de coûts par domaine                             │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Domaine     │  │  Domaine         │  │  Domaine         │
│  SALES       │  │  MARKETING       │  │  FINANCE         │
│              │  │                  │  │                  │
│  input:      │  │  input:          │  │  input:          │
│  · raw_tx    │  │  · campaigns     │  │  · general_ledger│
│  · cust_evts │  │  · camp_results  │  │  · invoices      │
│              │  │                  │  │                  │
│  output:     │  │  output:         │  │  output:         │
│  · sales_tx  │  │  · camp_perf     │  │  · profit_loss   │
│  · cust_360  │  │  · aud_insights  │  │  · cost_dept     │
│  · inv_fore  │  │                  │  │                  │
└──────┬───────┘  └───────┬──────────┘  └────────┬─────────┘
       │                  │                       │
       └──────────────────┼───────────────────────┘
                          │ dbt + PostgreSQL
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PostgreSQL (3 bases isolées)                               │
│  sales_db | marketing_db | finance_db                       │
│  Chacune avec schémas input/ output                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Concepts clés du Data Mesh

| Concept | Définition | Dans ce projet |
|---------|------------|----------------|
| **Domain Ownership** | Chaque équipe possède ses données | 3 bases PostgreSQL isolées (sales, marketing, finance) |
| **Data as a Product** | Les données sont des produits avec SLA | Tables en `output/` versionnées, documentées, avec tags |
| **Self-Service Platform** | Infra qui permet l'autonomie | Portail Streamlit + Governance API |
| **Federated Governance** | Règles globales, exécution locale | Policy-as-Code engine + Data Contracts |

---

## Démarrage rapide

```bash
# 1. Lancer l'infrastructure
docker compose up -d

# 2. Initialiser les domaines et seed les données
python scripts/init_domains.py
python scripts/seed_data.py

# 3. Accéder au portail
open http://localhost:8501

# 4. Voir la governance API
open http://localhost:8100/docs

# 5. Airflow
http://localhost:8080 (admin/admin)
```

---

## Guide des composants

### 1. Infrastructure (`docker-compose.yml`)
| Service | Rôle | Port |
|---------|------|------|
| `postgres-domains` | PostgreSQL multi-base (3 domaines) | 5432 |
| `minio` | Data Lake (staging fichiers) | 9002 / 9003 |
| `airflow-webserver` | Orchestrateur gouvernance | 8080 |
| `governance-api` | Metadata registry + Policy Engine | 8100 |
| `portal` | Streamlit self-service | 8501 |

### 2. Domaines & Data Products

**Domaine Sales** (`sales_db`):
| Data Product | Description | SLA |
|---|---|---|
| `sales_transactions` | Transactions quotidiennes par catégorie | Silver |
| `customer_360` | Vue client agrégée (segment, dépenses) | Gold |
| `inventory_forecast` | Prévision demande 14 jours | Bronze |

**Domaine Marketing** (`marketing_db`):
| Data Product | Description |
|---|---|
| `campaign_performance` | ROI par campagne (CTR, ROAS) |
| `audience_insights` | Segments clients (LTV, engagement) |

**Domaine Finance** (`finance_db`):
| Data Product | Description |
|---|---|
| `profit_loss` | Compte de résultat mensuel |
| `cost_by_department` | Coûts par département |

### 3. Governance API (`/platform/governance/`)

FastAPI avec endpoints REST :
- `POST/GET /data-products` — CRUD catalogue de data products
- `POST/GET /data-contracts` — Contrats entre domaines
- `POST/GET /policies` — Règles d'accès
- `POST /evaluate` — Évalue si un acteur peut accéder à une ressource
- `GET /audit-logs` — Traçabilité de tous les événements

### 4. Policy Engine (`policy.py`)
Moteur rule-based avec 4 politiques built-in :
1. **cross_domain_deny** — refus par défaut (sécurité)
2. **sales_finance_read** — Finance peut lire Sales (SLA gold/silver)
3. **marketing_read_all** — Marketing peut tout lire
4. **admin_full_access** — Admin peut tout faire

Les règles supportent : regex sur acteurs, actions, attributs ressource, conditions SLA.

### 5. Portail Self-Service (`/platform/portal/`)
Streamlit avec pages :
- **Accueil** — KPIs + catalogue + répartition par domaine
- **Data Products** — Créer et parcourir le catalogue
- **Data Contracts** — Définir des contrats inter-domaines
- **Policies** — Gérer les règles d'accès
- **Monitoring** — Healthcheck + audit logs + simulation d'accès

### 6. dbt Projects (`/data-products/`)
3 projets dbt indépendants (1 par domaine) avec :
- Profils PostgreSQL isolés
- Sources → staging → data products (modèles output)
- Tests intégrés (not_null, unique)

### 7. Airflow DAG (`governance_dag.py`)
Pipeline quotidien :
1. `check_domain_health` — Vérifie que chaque base répond
2. `validate_data_contracts` — Liste les contrats actifs
3. `detect_schema_drift` — Inspecte les colonnes de chaque table
4. `generate_cost_report` — Coûts par département

---

## Structure du projet

```
.
├── docker-compose.yml              # Infra complète
├── .env.example                    # Variables d'environnement
├── requirements.txt                # Dépendances Python
├── Dockerfile.airflow              # Image Airflow custom
├── Dockerfile.governance           # Image Governance API
├── Dockerfile.portal               # Image Streamlit
│
├── scripts/
│   ├── init-domains.sql            # Init SQL databases + schemas
│   ├── init_domains.py             # Crée les tables input/output
│   └── seed_data.py                # Génère les données de démo
│
├── data-products/
│   ├── profiles.yml                # Connexions dbt aux 3 domaines
│   ├── sales/
│   │   ├── dbt_project.yml
│   │   └── models/
│   │       ├── sources.yml
│   │       ├── input/
│   │       │   ├── stg_raw_transactions.sql
│   │       │   └── stg_customer_events.sql
│   │       └── output/
│   │           ├── sales_transactions.sql
│   │           ├── customer_360.sql
│   │           └── inventory_forecast.sql
│   ├── marketing/
│   │   ├── dbt_project.yml
│   │   └── models/
│   │       ├── sources.yml
│   │       ├── input/
│   │       │   ├── stg_campaigns.sql
│   │       │   └── stg_campaign_results.sql
│   │       └── output/
│   │           ├── campaign_performance.sql
│   │           └── audience_insights.sql
│   └── finance/
│       ├── dbt_project.yml
│       └── models/
│           ├── sources.yml
│           ├── input/
│           │   ├── stg_general_ledger.sql
│           │   └── stg_invoices.sql
│           └── output/
│               ├── profit_loss.sql
│               └── cost_by_department.sql
│
├── platform/
│   ├── portal/
│   │   └── Home.py                 # Streamlit (5 pages)
│   └── governance/
│       ├── main.py                 # FastAPI app
│       ├── models.py               # SQLAlchemy models
│       ├── schemas.py              # Pydantic schemas
│       ├── policy.py               # Policy-as-Code engine
│       └── dags/
│           └── governance_dag.py   # Airflow DAG
├── tests/
└── monitoring/
```

---

## API Governance

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Healthcheck |
| `POST` | `/data-products` | Créer un data product |
| `GET` | `/data-products` | Lister (filtre `?domain=sales`) |
| `GET` | `/data-products/:id` | Détail |
| `POST` | `/data-contracts` | Créer un contrat |
| `GET` | `/data-contracts` | Lister |
| `POST` | `/policies` | Créer une policy |
| `GET` | `/policies` | Lister |
| `POST` | `/evaluate?actor=X&action=Y` | Évaluer un accès |
| `GET` | `/audit-logs` | Logs de traçabilité |

---

## Tests

```bash
# Tester la connexion aux domaines
python -c "
from scripts.init_domains import init_domains
init_domains()
"

# Générer les données de seed
python scripts/seed_data.py

# Lancer la governance API et tester
curl http://localhost:8100/health
curl http://localhost:8100/data-products
```

---

## Aller plus loin

- **Data Sharing** : Ajouter dbt sources cross-domaine (Sales lit Marketing)
- **dbt Contracts** : Ajouter `contract: {enforced: true}` sur les modèles output
- **OpenMetadata** : Remplacer le governance custom par OpenMetadata
- **ML** : Entraîner un modèle de prédiction d'attrition sur le data product `customer_360`
- **Data Quality** : Intégrer Great Expectations aux pipelines dbt
- **CI/CD** : Valider les data contracts en PR avec GitHub Actions
- **Cost Attribution** : Terraform pour provisionner les domaines avec des quotas

---

## Licence

MIT
