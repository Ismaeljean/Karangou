# 🎬 KARANGOU STUDIOS

Plateforme de **vidéo à la demande (VOD)** et de **financement participatif** dédiée au développement du **cinéma africain**.

---

# 📖 Présentation

**Karangou Studios** est une entreprise de production audiovisuelle basée au **Togo**, spécialisée dans la production de films, séries et contenus culturels.

Sous son ancienne dénomination **Rebel Reaction Prod.**, la structure a produit le film :

**"Innocent malgré tout"**
Réalisé par **Kouamé Mathurin Samuel CODJOVI**

Ce film a été sélectionné en compétition officielle dans plusieurs festivals internationaux :

* FESPACO
* Écrans Noirs
* Charity Films

Fort de cette expérience, Karangou Studios souhaite proposer une **solution innovante pour soutenir la production cinématographique africaine**.

La plateforme **Karangou Studios** combine :

* **diffusion de films africains**
* **financement participatif de nouveaux projets**

L'objectif est de créer un **écosystème numérique permettant aux créateurs africains de financer leurs œuvres directement auprès du public**.

---

# 🎯 Concept de la plateforme

Le modèle de Karangou Studios repose sur un principe simple :

1️⃣ Un créateur (réalisateur, producteur, auteur…) publie **une réalisation déjà produite**.
2️⃣ Cette réalisation est associée à **un projet de film futur**.
3️⃣ Les spectateurs peuvent **regarder gratuitement le film existant**.
4️⃣ Les utilisateurs peuvent ensuite **contribuer financièrement au financement du nouveau projet**.

Ainsi, chaque film diffusé sur la plateforme devient **un levier pour financer une nouvelle production**.

---

# 🧩 Fonctionnalités principales

## 🎥 Visionnage de films

La plateforme permet aux utilisateurs de :

* regarder des films africains en ligne
* découvrir de nouveaux réalisateurs
* consulter les informations d’un film
* ajouter un film aux favoris
* commenter et noter un film

Fonctionnalités :

* lecteur vidéo intégré
* fiche détaillée du film
* système d’évaluation
* système de commentaires
* catégorisation des films (genre, réalisateur, etc.)

---

## 💰 Financement participatif

Chaque film peut être associé à **un projet de production futur**.

Les utilisateurs peuvent :

* découvrir les projets en cours de financement
* consulter les objectifs financiers
* suivre la progression du financement
* contribuer financièrement

Fonctionnalités :

* page dédiée aux projets
* barre de progression du financement
* historique des contributions
* possibilité de coproduction

---

## 👤 Gestion des utilisateurs

Les utilisateurs de la plateforme peuvent :

* créer un compte
* publier une réalisation
* proposer un projet de film
* financer un projet
* participer aux discussions

Types d’utilisateurs :

* **Auteur**
* **Acteur**
* **Producteur**
* **Spectateur / Fan**

Chaque utilisateur possède :

* un profil
* un historique de contributions
* une liste de films publiés
* une liste de projets proposés

---

## 💬 Interaction communautaire

Karangou Studios encourage l’échange entre passionnés de cinéma.

Fonctionnalités communautaires :

* commentaires sur les films
* système de notation
* forum de discussion
* recommandations entre utilisateurs
* notifications d’activité

---

# 🗄️ Modèle de données

La plateforme repose sur plusieurs entités principales.

## Utilisateur

Représente un membre inscrit sur la plateforme.

Informations principales :

* nom d’utilisateur
* email
* rôle
* biographie
* photo de profil
* date d’inscription

---

## Réalisation

Une **réalisation** correspond à un film **déjà produit et disponible en visionnage**.

Une réalisation contient :

* titre
* description
* vidéo
* affiche
* genre
* durée
* auteur
* date de sortie

Chaque réalisation peut servir **une seule fois** à financer un projet.

---

## Projet

Un **projet** représente un film **qui n’a pas encore été réalisé** faute de financement.

Informations :

* titre
* synopsis
* pré-affiche
* budget objectif
* montant collecté
* auteur
* réalisation associée

Chaque projet est obligatoirement **rattaché à une réalisation existante**.

---

## Contribution

Une contribution correspond à un **financement effectué par un utilisateur**.

Informations :

* utilisateur
* projet
* montant
* date de contribution
* moyen de paiement

---

## Commentaire

Permet aux utilisateurs de donner leur avis sur un film.

---

## Évaluation

Permet aux utilisateurs de **noter un film**.

---

# 📏 Règles de gestion

Le fonctionnement de la plateforme repose sur plusieurs règles importantes.

### 1️⃣ Publication

Un utilisateur doit être **inscrit** pour :

* publier une réalisation
* proposer un projet
* contribuer à un financement

---

### 2️⃣ Relation Réalisation → Projet

Une **réalisation peut être utilisée une seule fois** pour financer un projet.

```
1 Réalisation → 1 Projet maximum
```

---

### 3️⃣ Obligation de rattachement

Un **projet doit obligatoirement être associé à une réalisation existante**.

Cela garantit que :

* les spectateurs peuvent voir un exemple du travail du créateur
* la confiance des contributeurs est renforcée

---

### 4️⃣ Financement d’un projet

Un projet est considéré comme **financé** lorsque :

```
montant_collecte ≥ budget_objectif
```

---

### 5️⃣ Participation des utilisateurs

Un utilisateur peut :

* commenter plusieurs films
* noter plusieurs films
* financer plusieurs projets

---

# 🏗️ Architecture technique

Le projet est développé avec **Django (Python)**.

Organisation du projet :

```
karangou/

utilisateurs/
realisations/
projets/
financement/
communaute/

templates/
static/

manage.py
```

Applications principales :

* **utilisateurs** → gestion des comptes
* **realisations** → gestion des films
* **projets** → gestion des projets de production
* **financement** → gestion des contributions
* **communaute** → commentaires et forum

---

# 🎨 Interface utilisateur

Le frontend est basé sur :

* **HTML**
* **Bootstrap 5**
* **JavaScript**

Objectifs du design :

* interface moderne
* expérience utilisateur intuitive
* navigation simple
* design cinématographique
* compatibilité mobile

---

# 📱 Responsive Design

Le site est optimisé pour :

* ordinateurs
* tablettes
* smartphones

---

# 🔐 Sécurité

La plateforme prévoit :

* authentification sécurisée
* protection des données personnelles
* sécurisation des transactions financières
* gestion des permissions utilisateurs

---

# ⚡ Performances

Objectifs techniques :

* chargement rapide des pages
* optimisation des médias
* gestion efficace du trafic

---

# 🚀 Installation du projet

Créer un environnement virtuel :

```
python -m venv env
```

Activer l’environnement :

```
source env/bin/activate
```

Installer les dépendances :

```
pip install -r requirements.txt
```

Appliquer les migrations :

```
python manage.py migrate
```

Lancer le serveur :

```
python manage.py runserver
```

Accéder au site :

```
http://127.0.0.1:8000
```

---

# 🌍 Vision

Karangou Studios ambitionne de devenir une **plateforme majeure de financement du cinéma africain**, en donnant aux créateurs les moyens de produire leurs œuvres tout en restant fidèles à leurs identités culturelles.

L’objectif est de **réduire la dépendance aux circuits de financement traditionnels** et de permettre au public de devenir **acteur du développement du cinéma africain**.

---

# 👨‍💻 Auteur

Projet développé dans le cadre de la plateforme **Karangou Studios**.
