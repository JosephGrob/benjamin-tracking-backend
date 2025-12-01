# Backend de suivi GPS pour la navigation de Benjamin Senften  
Architecture FastAPI, hébergement Render, API temps réel

Ce dépôt contient le backend complet permettant de gérer le suivi GPS en temps réel d’un utilisateur (Benjamin) via une API REST. Il a été conçu pour être léger, robuste, facile à déployer, et compatible avec un frontend simple (Leaflet) hébergé sur GitHub Pages.

Ce document constitue une documentation technique détaillée du backend, destinée à un usage professionnel ou de maintenance (développeurs, employeurs, contributeurs).


## 1. Objectifs du backend

Le backend permet les fonctionnalités suivantes :

- Recevoir en direct des positions GPS envoyées depuis un téléphone (via une page web ou un script).
- Stocker un historique des positions sous forme de liste en mémoire (structure Python simple).
- Fournir une API de lecture permettant au frontend d'afficher :
  - la trace complète du trajet,
  - la position actuelle.
- Empêcher les écritures non autorisées via un système de token secret.
- Héberger l’API sur une plateforme cloud accessible publiquement (Render).
- Offrir une documentation interactive automatique (Swagger / ReDoc via FastAPI).

Le modèle choisi devait fonctionner même avec une connectivité intermittente typique d’une navigation maritime.


## 2. Technologies utilisées

### 2.1. Langage

- Python 3.12+

### 2.2. Framework API

- FastAPI  
  Fournit les endpoints REST, la validation automatique via Pydantic, la documentation interactive, et les réponses JSON performantes.

### 2.3. Serveur ASGI

- Uvicorn  
  Utilisé en mode production (via Render) et en mode développement local.

### 2.4. Hébergement backend

- Render (Web Service Standard)  
  Avantages :
  - déploiement automatique à partir d'un dépôt GitHub,
  - maintenance simplifiée,
  - HTTPS automatique,
  - redémarrage automatique si le service tombe.

### 2.5. CORS

Le backend doit accepter les requêtes provenant du frontend GitHub Pages (hébergé sur un autre domaine).  
FastAPI inclut un middleware CORS.

### 2.6. Frontend indépendant

Le backend ne gère pas de pages HTML.  
Il fournit uniquement l’API.

Le frontend Leaflet chargé de l'affichage est hébergé séparément (GitHub Pages).


## 3. Structure du projet
backend-tracking/
│
├── server.py # Code principal du backend FastAPI
├── requirements.txt # Dépendances pour Render ou installation locale
└── README.md # Documentation backend

Fichiers essentiels :

### 3.1. requirements.txt


Les dépendances supplémentaires (pydantic-core, starlette...) sont installées automatiquement.


### 3.2. server.py

Contient :

- le modèle de donnée Position (Pydantic)
- la liste en mémoire `positions`
- les endpoints REST
- la logique métier (limitation du nombre de points, token de sécurité, nettoyage)
- la configuration CORS


## 4. Modèle de données

Un point de trace est représenté par :

```python
class Position(BaseModel):
    lat: float
    lng: float
    time: datetime | None = None
    track_id: str = "live"

## Champs du modèle

- **lat** : latitude en degrés décimaux (obligatoire)
- **lng** : longitude en degrés décimaux (obligatoire)
- **time** : timestamp ISO8601.  
  Si ce champ est vide dans la requête, le backend génère automatiquement un horodatage UTC.
- **track_id** : identifiant du trajet (par défaut `"live"`), utile pour gérer plusieurs traces si nécessaire.

Le choix d’un modèle Pydantic garantit la validation automatique des données en entrée, limite les erreurs, et simplifie la sérialisation JSON.

