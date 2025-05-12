# 📋 Microsoft Fabric – Interview Prep Cheat Sheet

## ✅ PART 1 — Questions techniques sur Fabric

### 1. **As-tu pu utiliser Microsoft Fabric directement ?**

> Non, mon tenant était trop récent et Microsoft bloque les essais Fabric sur les nouveaux comptes. J’ai contacté le support, et comme solution, j’ai simulé les briques principales de Fabric avec Python (pandas, SQLite, Streamlit) pour prouver ma compréhension de l’architecture et des étapes.

---

### 2. **Comment fonctionne Microsoft Fabric dans sa globalité ?**

> Microsoft Fabric est une plateforme unifiée de données dans Microsoft 365. Elle centralise le stockage, la transformation, l’analyse, et la visualisation des données via des composants intégrés comme OneLake, Lakehouse, Notebooks, Dataflows Gen2, Power BI et Semantic Models.

---

### 3. **Qu’est-ce qu’un Lakehouse dans Fabric ?**

> C’est un entre-deux entre un Data Lake et un Data Warehouse. Les fichiers (Parquet ou Delta) sont stockés dans OneLake mais accessibles comme des tables relationnelles, ce qui permet à la fois flexibilité et performances analytiques.

---

### 4. **Qu’est-ce qu’un modèle sémantique ?**

> C’est la couche métier entre les données brutes et les rapports Power BI. Il comprend les relations entre les tables, les mesures, les hiérarchies, les filtres. Il standardise la manière d’analyser les données, quel que soit l’utilisateur.

---

### 5. **Qu’as-tu simulé dans ton projet Python pour remplacer Fabric ?**

| Élément Fabric     | Simulé avec                 |
| ------------------ | --------------------------- |
| OneLake            | Fichiers CSV locaux         |
| Lakehouse          | SQLite DB (`fabric_sim.db`) |
| Dataflows Gen2     | pandas (`model.py`)         |
| Notebooks          | Jupyter & scripts Python    |
| Semantic Model     | Fonctions métiers Python    |
| Power BI Dashboard | Streamlit app interactive   |

---

### 6. **Que ferais-tu si tu avais accès à Fabric ?**

> J’aurais importé les fichiers dans OneLake, modélisé les données dans un Lakehouse, transformé via Notebooks ou Dataflows Gen2, puis connecté tout cela à Power BI avec un Semantic Model pour créer un rapport visuel.

---

## ✅ PART 2 — Définitions clés de Microsoft Fabric

### 🔹 **Data Lake**

> Un Data Lake est un stockage centralisé conçu pour contenir de grandes quantités de données brutes, structurées ou non structurées, dans leur format natif. Il permet une ingestion rapide et une flexibilité pour l’analyse ou la transformation ultérieure.

### 🔹 **OneLake**

> Le Data Lake unifié de Microsoft. Il centralise le stockage de tous les fichiers utilisés par Fabric (Parquet, Delta…) et permet un accès partagé entre les outils.

### 🔹 **Lakehouse**

> Architecture hybride : fichiers de type Data Lake avec structure de type entrepôt. Supporte les tables Delta, relations, et requêtes SQL.

### 🔹 **Dataflows Gen2**

> Outil d’ETL visuel low-code pour transformer les données en étapes (nettoyage, mapping, enrichissement) avant de les charger dans un Lakehouse ou un dataset Power BI.

### 🔹 **Notebooks (Spark)**

> Environnement interactif basé sur PySpark ou SQL. Permet d’explorer, transformer, ou modéliser les données avec du code.

### 🔹 **Semantic Model**

> Anciennement Dataset. C’est la couche logique de modélisation de données pour Power BI : tables, relations, mesures DAX, hierarchies, filtres…

### 🔹 **Power BI Report**

> Tableau de bord interactif basé sur un Semantic Model. Visuels, slicers, KPIs, partagé dans les workspaces Fabric.

### 🔹 **Warehouse**

> Entrepôt relationnel SQL optimisé pour l’analyse structurée. Plus rigide que le Lakehouse, mais performant pour les grandes bases tabulaires.

### 🔹 **Pipelines**

> Orchestration de flux de données, équivalent d’Azure Data Factory dans Fabric. Permet d’automatiser ingestion → transformation → stockage.

### 🔹 **Workspace Fabric**

> Espace collaboratif de projet. Regroupe tous les objets Fabric (Lakehouse, Dataflow, modèles, rapports, notebooks…).

---

## ✅ PART 3 — Étapes recommandées pour présenter ton projet

1. **Introduction (1 min)**

> "J’ai développé une simulation complète d’un pipeline Fabric en Python, suite à l’impossibilité d’accéder à la version d’essai officielle."

2. **Structure du projet (1–2 min)**

> * Input : fichiers CSV RH (absences, contrats, salaires)
> * Lakehouse simulé : SQLite DB
> * Dataflows Gen2 : traitement `pandas` dans `model.py`
> * Semantic model : fonctions de calculs métier (absence rate, effectifs, salaire moyen)
> * Dashboard : app Streamlit interactive qui simule Power BI

3. **Focus fonctionnel (2 min)**

> * Taux d’absence (corrigé pour les incohérences >100%)
> * Salaires : net, brut, brut 108, écart H/F, distribution
> * Visualisation par entreprise

4. **Points forts**

> * Autonomie / adaptation à l’indisponibilité de Fabric
> * Nettoyage intelligent des données (virgules, strings)
> * Modèle sémantique simulé dans Python

5. **Limites / perspectives**

> * Pas de lien direct entre la table des salaires et les contrats (pas de `person_id`)
> * Enrichissement possible avec filtres temporels, exports, ou Streamlit Cloud

---

## ✅ Phrase d'accroche pour démarrer l'entretien

> "Pour répondre au use case RH qui m’a été confié, j’ai simulé l’ensemble du pipeline Microsoft Fabric avec des outils Python. Cela m’a permis d’appliquer les étapes Fabric (ingestion, transformation, modélisation, visualisation) tout en gardant une logique claire, modulaire, et adaptée aux contraintes techniques du moment."
