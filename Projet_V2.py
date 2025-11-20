import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import csv
import json

## variable globales
DUREE_EMPRUNT_MAXI = 14                     # La duree maximal pour un prêt
MAXI_PRET_ACTIF = 3                         #la limite d'emprunts en cours par lecteur
FORMAT_DE_SAUVEGARDE_DEFAUT = "csv"         #le format de sauvgarde choisi par defaut


# Nettoyer un text en enlevant les espaces avec strip et mettant le tout en manisicule              
def Nettoyer(S: str):
   return (S or "").strip().casefold()


# Choisir le format de sauvegarde qu'on veut travailler dessusentre CSV et JSON                   
def choisir_format_sauvegarde(): 
    format = input("Quelle est la version de sauvegarde que tu souhaite ? csv ou json, (défaut=csv) : ").strip().lower()
    if format not in ("json", "csv"):
        format = FORMAT_DE_SAUVEGARDE_DEFAUT
    #FORMAT_DE_SAUVEGARDE_DEFAUT = format
    print("Le format choisi est ",format)
    return format

# -------------------------------
# Classe Livre                                                                                  
# -------------------------------
class Livre:
    #Compteur des id pour chaque livre  
    Compteur = 1 

    # constructeur par parametres
    def __init__(self, titre, auteur, categorie, exemplaires):
        self.id = Livre.Compteur                                #recoit l'ID actuel du compteur de calsse ;
        Livre.Compteur += 1                                     #incrementation de l'ID
        # Définition des attributs
        self.titre = titre
        self.auteur = auteur
        self.categorie = categorie
        self.exemplaires = max(0, int(exemplaires))             #pour empecher les nombres negatifs
        self.statut = "disponible" if self.exemplaires > 0 else "emprunté"

    #Definition des methodes 
    # mise a jour du statut du livre
    def mettre_a_jour_statut(self):
        self.statut = "disponible" if self.exemplaires > 0 else "emprunté"

    # Affichage des elements principaux d'un livre 
    def afficher(self):
        return f"[{self.id}] {self.titre} ; {self.auteur} ({self.exemplaires} ex.)"
    
    # destructeur de la classe livre
    #def __del__(self):
       # print(f"[{self.id}] {self.titre} ; {self.auteur} ({self.nombre_exemplaires} ex.) est detruit.")
    
# -------------------------------
# Classe Utilisateur + sous-classes                                                              
# -------------------------------
class Utilisateur:
    # constructeur par parametres de la classe Utilisateur
    def __init__(self, identifiant, nom, email):
        #définition des attributs de la classe utilisateur
        self.id = identifiant
        self.nom = nom
        self.email = email
    
    # definition de la methode d'affichage
    def afficher(self):
        return f"{self.id} ; {self.nom}"
    
    # destructeur de la classe
    def __del__(self):
        print(f"Utilisateur detruit: {self.id} ; {self.nom}")

#definition de la classe lecteur herité par la classe Utilisateur                               
class Lecteur(Utilisateur):
    #constructeur par parametre de la classe
    def __init__(self, identifiant, nom, email):
        
        #appel au contructeur parent (utilisateur)
        super().__init__(identifiant, nom, email)
        
        #definition des attributs propre au lecteur
        self.livres_empruntes = set()


#definition de la classe bibliothecaire herité de utilisateur sans rien rajouté de plus         
class Bibliothecaire(Utilisateur):
    pass


# -------------------------------
# Classe Emprunt                                                                                    
# -------------------------------
class Emprunt:
    Compteur = 1
    
    #definition du constructeur par parametre de la classe Emprunt
    def __init__(self, livre_id, lecteur_id):
        self.id = Emprunt.Compteur
        Emprunt.Compteur += 1
        #Définition des attributs de la classe
        self.livre_id = livre_id
        self.lecteur_id = lecteur_id
        self.date_emprunt = datetime.now()
        self.date_retour_prevue = self.date_emprunt + timedelta(days=DUREE_EMPRUNT_MAXI)
        self.date_retour_effective = None
        self.retourne = False


    #Définition des methodes de la classe 
    #méthode pour indiquer le livre comme renduu
    def rendre(self):
        self.date_retour_effective = datetime.now()
        self.retourne = True

    #methode de verification si le livre est en retard 
    def en_retard(self):
        if not self.retourne:
            return datetime.now() > self.date_retour_prevue
        return self.date_retour_effective > self.date_retour_prevue

    #methode pour calculer les jours de retard
    def jours_de_retard(self):
        if not self.retourne:
            return max(0, (datetime.now() - self.date_retour_prevue).days)
        else:
            return max(0, (self.date_retour_effective - self.date_retour_prevue).days)

    #methode d'affichage
    def afficher(self):
        statut = "Retourné" if self.retourne else "En cours"
        return (f"Emprunt {self.id} - Livre {self.livre_id} | {statut}")


# -------------------------------
# Classe Bibliotheque                                                                           
# -------------------------------
class Bibliotheque:
    # constructeur par paramtre de la classe
    def __init__(self, nom, adresse):
        #defintion des attributs
        self.nom = nom
        self.adresse = adresse
        self.livres = []
        self.utilisateurs = {}
        self.emprunts = {}
        self.emprunts_par_lecteur = {}

    #Définition des methodes 
    
    #methode qui verifie si l'utilisateur donné est bien le bibliotecaire! 
    def est_bibliothecaire(self, utilisateur):
        return isinstance(utilisateur, Bibliothecaire)

    # --- Gestion des livres --- 

    # methode qui permet de chercher un livre dans la bibliotheque
    def _trouver_livre_par_id(self, livre_id):
        for l in self.livres:
            if l.id == livre_id:
                return l
        return None

    # methode qui sert a rajouter des livres a la bibliotheque
    def ajouter_livre(self, livre, utilisateur):
        
        # verification si l'utilsateur est le bibliothecaire
        if not self.est_bibliothecaire(utilisateur):
            print("Accès refusé car seul le bibliothécaire peut ajouter ou modifier les livres.")
            return False
        
        # voir si le livre existe deja en comparant les titres et l'auteur
        for l in self.livres:
            if (Nettoyer(l.titre), Nettoyer(l.auteur)) == (Nettoyer(livre.titre), Nettoyer(livre.auteur)):
                print("Ce livre existe déjà (même titre + auteur).")
                return False
        # Rajouter le livre à la bibliotheque
        self.livres.append(livre)
        print(f"Livre ajouté : {livre.titre}")
        return True

    # methode pour modifier les livres
    def modifier_livre(self, livre_id, utilisateur, **champs):

        # verifier si l'utilisateur est le bibliothecaire
        if not self.est_bibliothecaire(utilisateur):
            print("Accès refusé car seul le bibliothécaire peut ajouter ou modifier les livres.")
            return False
        
        # chercher le livre dans labibliotheque
        livre = self._trouver_livre_par_id(livre_id)
        if not livre:
            print("Livre introuvable.")
            return False
        
        # la modification du livre selon le champs 
        if 'titre' in champs:
            livre.titre = champs['titre']
        if 'auteur' in champs:
            livre.auteur = champs['auteur']
        if 'categorie' in champs:
            livre.categorie = champs['categorie']
        if 'exemplaires' in champs:
            livre.exemplaires = max(0, int(champs['exemplaires']))
        
        #mise a jour du statut de livre
        livre.mettre_a_jour_statut()
        print("Livre modifié avec succès.")
        return True

    # methode de supprission d'un livre
    def supprimer_livre(self, livre_id, utilisateur):
        # verification si l'utilisateur est le biliothecaire
        if not self.est_bibliothecaire(utilisateur):
            print("Accès refusé.")
            return False
        
        #chercher le livre par id
        livre = self._trouver_livre_par_id(livre_id)
        if not livre:
            print("Livre introuvable.")
            return False
        
        # verifier si il y a un emprunt en cour
        for emprunt in self.emprunts.values():
            if emprunt.livre_id == livre_id and not emprunt.retourne:
                print("Impossible de supprimer un livre emprunté.")
                return False

        # demander la confirmation de la demande de suppression    
        confirmation = Nettoyer(input(f"Confirmer la suppression du livre '{livre.titre}' ? (y/n) : "))
        if confirmation not in {"y", "yes", "oui", "o"}:
            print("Suppression annulée.")
            return False

        #supprimer le livre de la liste de la bibliotheque   
        self.livres.remove(livre)
        print("Le livre '{livre.titre}' est supprimé avec succés.")
        return True
    

    #methode d'affichage des livres
    def afficher_tous_les_livres(self):
        # si la bibliotheque est vide
        if not self.livres:
            print("Pas de livre est disponible.")
            return
        #tri des livres par ordre alphabetique des titres
        for l in sorted(self.livres, key=lambda livre: livre.titre.lower()):
            print(l.afficher())

    #methode de recheche avancée des livres
    def rechercher_livre(self, critere, valeur):

        #nettoyage des textes de criteres
        critere = Nettoyer(critere)
        valeur = Nettoyer(valeur)

        #liste de stockage des resultat trouvé
        resultats = []

        #parcourir les livres existants de la bibliotheque en le nettoyant
        for l in self.livres:
            titre = Nettoyer(l.titre)
            auteur = Nettoyer(l.auteur)
            categorie = Nettoyer(l.categorie)
            dispo = Nettoyer(l.statut)

        # comparaison selon le critere écrit
            if critere == "titre" and valeur in titre:
                resultats.append(l)
            elif critere == "auteur" and valeur in auteur:
                resultats.append(l)
            elif critere == "categorie" and valeur in categorie:
                resultats.append(l)
            elif critere == "disponibilite" and valeur == dispo:
                resultats.append(l)
        # cas de resultat vide        
        if not resultats:
            print("Aucun résultat est troouvé")
            return
        
        #Affichage du resultat
        for r in resultats:
            print(r.afficher())

    # --- Utilisateurs --- 

    # methode pour trouver un utilisateur par son email
    def trouver_utilisateur_par_email(self, email):
        for utilisateur in self.utilisateurs.values():
            if utilisateur.email.lower() == email.lower():
                return utilisateur
        return None
    
    #methode pour ajouter un utilisateur
    def ajouter_utilisateur(self, utilisateur):
        #verification de l'existance de l'ID
        if utilisateur.id in self.utilisateurs:
            print("ID déjà utilisé pour un autre utilisateur.")
            return False
        
        #verification de l'existance de l'email
        if self.trouver_utilisateur_par_email(utilisateur.email):
            print("Email déjà utilisé pour un autre utilisateur.")
            return False
        
        #methode pour ajouter l'utilisateur au dictionnaire des utilisateurs 
        self.utilisateurs[utilisateur.id] = utilisateur
        print(f"Utilisateur {utilisateur.nom} ajouté.")
        return True

    #methode d'affichage
    def afficher_utilisateurs(self):
        # cas d'aucun utilisateur est enrigistré
        if not self.utilisateurs:
            print("Pas d'utilisateur dans la bibliotheque enrigistré.")
            return
        #parcourir les utilisateurs enrigistré
        for utilisateur in self.utilisateurs.values():
            #affichage
            print(utilisateur.afficher())



    # --- Emprunts --- 

    #methode d'emprunt pour un livre
    def emprunter_livre(self, livre_id, lecteur_id):
        # recupere l'id de l'utilisateur
        lecteur = self.utilisateurs.get(lecteur_id)

        #verifier que c'est un lecteur pas le bibliothecaire
        if not isinstance(lecteur, Lecteur):
            print("Utilisateur non valide; il faut que ça soit un lecteur.")
            return False
        
        # cherche le livre par son id
        livre = self._trouver_livre_par_id(livre_id)
        if not livre:
            print("Livre introuvable.")
            return False
        
        # verifier le nombre d'exemplaire disponible
        if livre.exemplaires <= 0:
            print("Aucun exemplaire disponible.")
            return False
        
        # vérifie si le lecteur a déjà emprunté ce livre
        if livre_id in lecteur.livres_empruntes:
            print("Ce lecteur a déjà emprunté ce livre.")
            return False
        

        # Limite d'emprunts actifs
        nb_actifs = 0
        for id_emprunt in self.emprunts_par_lecteur.get(lecteur_id, set()):
            emprunt_enregistre = self.emprunts.get(id_emprunt)
            if emprunt_enregistre and not emprunt_enregistre.est_retourne:
                nb_actifs += 1    

        if nb_actifs >= MAXI_PRET_ACTIF:
            print(f"Limite atteinte : {MAXI_PRET_ACTIF} emprunt(s) actif(s).")
            return False         
        
        
        # crée un nouvel emprunt
        emprunt = Emprunt(livre_id, lecteur_id)
        # enregistre l'emprunt dans le dictionnaire des emprunts
        self.emprunts[emprunt.id] = emprunt


        #ajoute l'emprunt à la liste de ce lecteur (si elle n'existe pas, on la crée)
        if lecteur_id not in self.emprunts_par_lecteur:
            self.emprunts_par_lecteur[lecteur_id] = set()
        self.emprunts_par_lecteur[lecteur_id].add(emprunt.id)

        # mémorise côté lecteur qu'il a ce livre
        lecteur.livres_empruntes.add(livre_id)


        # décrémente le stock du livre et met à jour le statut
        livre.exemplaires -= 1
        livre.mettre_a_jour_statut()

        print(f"Un emprunt à été créé : {emprunt.id}")
        return True
    

    #methode pour rendre un libre
    def rendre_livre(self, emprunt_id):
        #recupere l'id de l'emprubt
        emprunt = self.emprunts.get(emprunt_id)
        if not emprunt:
            print("Emprunt introuvable.")
            return False
        
        #verifie si le livre est rendu
        if emprunt.retourne:
            print("Le livre est déjà retourné.")
            return False

        # marquer que le luvre est rendu
        emprunt.rendre()

        #cherche le livre et le lecteur concerné par cet emprunt
        livre = self._trouver_livre_par_id(emprunt.livre_id)
        lecteur = self.utilisateurs.get(emprunt.lecteur_id)

        #changer le statut et le nb d'exemplaire du livre car il est rendu 
        if livre:
            livre.exemplaires += 1
            livre.mettre_a_jour_statut()

        #enlever le livre de la liste d'empriunt du lecteeur
        if isinstance(lecteur, Lecteur):
            lecteur.livres_empruntes.discard(emprunt.livre_id)


        print("Livre rendu avec succès.")

        #verification s'il ya du retard
        if emprunt.en_retard():
            print(f"⚠ Retard de {emprunt.jours_de_retard()} jour(s).")
        return True
    

    #methode qui liste les emprunts existants
    def lister_emprunts_en_cours(self):
        en_cours = [e for e in self.emprunts.values() if not e.retourne]
        if not en_cours:
            print("Aucun emprunt en cours.")
            return
        for e in en_cours:
            print(e.afficher())

    def lister_emprunts_par_lecteur(self, lecteur_id):

        #recupere l'ensemble des ids de tous les emprunts fait par un seul lecteur
        identifiants = self.emprunts_par_lecteur.get(lecteur_id, set())
        if not identifiants:
            print("Aucun emprunt pour ce lecteur.")

            return
        #parcourir  les identifiants pour afficher les emprunts pour un lecteur
        for id_emprunt in identifiants:
            emrprunt = self.emprunts.get(id_emprunt)
            if emrprunt:
                print(emrprunt.afficher())

    # --- Statistiques Console--- 
        # méthode pour afficher les statistiques de ma bibliotheque
    def statistiques(self):
        # compte le nombre livres
        total_livres = len(self.livres)

        # compte le nombre de lecteurs (objets de type Lecteur)
        total_lecteurs = 0
        for utilisateur in self.utilisateurs.values():
            if isinstance(utilisateur, Lecteur):
                total_lecteurs += 1

        # compte le nombre de bibliothécaires
        total_biblios = 0
        for utilisateur in self.utilisateurs.values():
            if isinstance(utilisateur, Bibliothecaire):
                total_biblios += 1

        # compte le nombre d'emprunts encore actifs (non retournés)
        emprunts_actifs = 0
        for emprunt in self.emprunts.values():
            if not emprunt.est_retourne:
                emprunts_actifs += 1

        # compte le nombre d'emprunts en retard
        emprunts_retard = 0
        for emprunt in self.emprunts.values():
            if not emprunt.est_retourne and emprunt.en_retard():
                emprunts_retard += 1

        # affiche les statistiques globales
        print(f"=== Statistiques de la bibliothèque : {self.nom} ===")
        print(f"Livres : {total_livres}")
        print(f"Lecteurs : {total_lecteurs}")
        print(f"Bibliothécaires : {total_biblios}")
        print(f"Emprunts actifs : {emprunts_actifs}")
        print(f"Emprunts en retard : {emprunts_retard}")




# -------------------------------
# Fonctions de menu 
# -------------------------------

#fonction qui insite l'utilisateur a choisir un nombre                                                      
def demander_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Veuillez entrer un nombre.")

#fonction qui inititialise la bibliotheque grace aux classes et leurs constructeurs                             
def initialiser_bibliotheque():
    b = Bibliotheque("Bibliothèque Beb bhar", "Rue de Marseille")
    admin = Bibliothecaire(1, "Firas Saibi", "Firassaibi@biblio.com")
    lecteur1 = Lecteur(2, "Abdelkirm benmokhtar", "ABenmokhtar@email.com")
    lecteur2 = Lecteur(3, "Elyes Benjilali", "EBenjilalie@email.com")
    lecteur3 = Lecteur(4, "Faysel Baourir", "Fbaourir@email.com")
    b.ajouter_utilisateur(admin)
    b.ajouter_utilisateur(lecteur1)
    b.ajouter_utilisateur(lecteur2)
    b.ajouter_utilisateur(lecteur3)
    b.ajouter_livre(Livre("Les Reves perdus de Leyla", "Mohamed Harmel", "Roman", 5), admin)
    b.ajouter_livre(Livre("Les sculpteur de masques", " Mohamed Harmel", "Fantasy", 3), admin)
    b.ajouter_livre(Livre("El_moquadimah", " Abdel Rahmen ibn Khaldoun", "Historique", 13), admin)
    b.ajouter_livre(Livre("Le joueur d'echec", " Le joueur d'echec", "Fantasy", 10), admin)
    b.ajouter_livre(Livre("Les Rois de sable", "Naguib Mahfouz", "Roman", 5), admin)
    b.ajouter_livre(Livre("Le Siècle des deux printemps", "Azzedine Choukri", "Roman", 3), admin)
    b.ajouter_livre(Livre("Le Sommeil du mimosa", "Hassouna Mosbahi", "Roman", 4), admin)
    b.ajouter_livre(Livre("Les Larmes de l’âme", "Abdelwahab Meddeb", "Historique", 12), admin)
    b.ajouter_livre(Livre("Phantasia", "Abdelwahab Meddeb", "Roman", 8), admin)
    b.ajouter_livre(Livre("Ma vérité", "Hatem Ben Arfa", "Sport", 3), admin)
    b.ajouter_livre(Livre("La Rage de vaincre", "Habib Galhia", "Sport", 5), admin)
    b.ajouter_livre(Livre("Mon rêve olympique", "Oussama Mellouli", "Sport", 4), admin)
    b.ajouter_livre(Livre("Un destin de champion", "Anis Boussaïdi", "Sport", 8), admin)
    b.ajouter_livre(Livre("Le football, ma passion", "Ali Kaabi", "Sport", 11), admin)
    b.ajouter_livre(Livre("L'homme qui se croyait libre", "Abdelwahab Bouhdiba", "Psychologie", 10), admin)
    b.ajouter_livre(Livre("La personnalité tunisienne", "Taoufik Ben Brik", "Psychologie", 2), admin)
    b.ajouter_livre(Livre("L'amour et la sexualité au Maghreb", "Abdelwahab Bouhdiba", "Psychologie", 4), admin)
    b.ajouter_livre(Livre("Le moi, l'autre et le nous", "Fethi Benslama", "Psychologie", 8), admin)
    b.ajouter_livre(Livre("La psychanalyse à l'épreuve de l'islam", "Fethi Benslama", "Psychologie", 7), admin)


    return b


# fonction qui charge les fichiers csv avec pandas                                                          
def charger_csv_pandas(f_livres="livres.csv", f_utilisateurs="utilisateurs.csv", f_emprunts="emprunts.csv"):
    
    #charge les fichiers csv en DataFrame
    df_livres = pd.read_csv(f_livres)
    df_users = pd.read_csv(f_utilisateurs)
    df_emprunts = pd.read_csv(f_emprunts)

    # verifier les colonnes
    for col in ["id","titre","auteur","categorie","exemplaires","statut"]:
        if col not in df_livres.columns:
            print(f"Colonne manquante dans livres.csv: {col}")

    for col in ["id","nom","email","type"]:
        if col not in df_users.columns:
            print(f"Colonne manquante dans utilisateurs.csv: {col}")

    for col in ["id","livre_id","lecteur_id","retourne"]:
        if col not in df_emprunts.columns:
            print(f"Colonne manquante dans emprunts.csv: {col}")

    # conversion en bool du resultat retourné
        if "est_retourne" in df_emprunts.columns:
            df_emprunts["est_retourne"] = df_emprunts["est_retourne"].astype(str).str.lower().isin(
            ["true", "1", "vrai", "yes", "y", "oui"]
        )

    return df_livres, df_users, df_emprunts


#la fonction qui genere les les graphiques  et calcul les stats version pandas                               
def stats_et_graphs(df_livres, df_users, df_emprunts, dossier_sortie="MesGraphiques"):

    # --- 1) Nombre total de livres par catégorie (barres) ---
    #nombre de livres dans chaque catégorie
    livres_par_cat = df_livres["categorie"].value_counts().sort_values(ascending=False)


    print("\n=== Livres par catégorie ===")
    print(livres_par_cat)

    # je trace un graphique en barres
    plt.figure()
    livres_par_cat.plot(kind="bar")  # simple et clair
    plt.title("Nombre de livres par catégorie")
    plt.xlabel("Catégorie")
    plt.ylabel("Nombre de livres")
    plt.tight_layout()
    plt.savefig(Path(dossier_sortie) / "livres_par_categorie.png")
    plt.close()


    # Nombre de livres empruntés (barres simple: empruntés vs non-empruntés)
    # nb d'emprunts qui sont EN COURS
    emprunts_en_cours = (~df_emprunts["retourne"]).sum()

    # total de livres 
    total_livres = len(df_livres)

    # livres "non empruntés" 
    non_empruntes = max(0, total_livres - int(emprunts_en_cours))

    print("\n=== Emprunts ===")
    print(f"Livres empruntés (en cours) : {emprunts_en_cours}")
    print(f"Livres non empruntés       : {non_empruntes}")

    #mini bar chart
    plt.figure()
    pd.Series(
        {"Empruntés": emprunts_en_cours, "Non empruntés": non_empruntes}
    ).plot(kind="bar")
    plt.title("Livres empruntés (en cours) vs non empruntés")
    plt.ylabel("Nombre")
    plt.tight_layout()
    plt.savefig(Path(dossier_sortie) / "empruntes_vs_non_empruntes.png")
    plt.close()

    # Nombre d’utilisateurs par type (camembert)
    # nombre des lecteur et Bibliothecaire
    users_par_type = df_users["type"].value_counts()

    print("\n=== Utilisateurs par type ===")
    print(users_par_type)

    # camembert
    plt.figure()
    users_par_type.plot(kind="pie", autopct="%1.0f%%", ylabel="")  #  afficher en %
    plt.title("Répartition des utilisateurs")
    plt.tight_layout()
    plt.savefig(Path(dossier_sortie) / "utilisateurs_par_type.png")
    plt.close()

    print(f"\nGraphiques enregistrés dans: {Path(dossier_sortie).resolivree()}")
    print(" - livres_par_categorie.png")
    print(" - empruntes_vs_non_empruntes.png")
    print(" - utilisateurs_par_type.png")

#fonction pour lancer le chargement des csv et calculer les stats et et les graphiques                        
def run_rapport_pandas(
    f_livres="livres.csv",
    f_utilisateurs="utilisateurs.csv",
    f_emprunts="emprunts.csv",
    dossier_sortie="MesGraphiques"):

    # crée le dossier de sortie s'il n'existe pas
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)

    # charge les données depuis les fichiers CSV
    df_livres, df_utilisateurs, df_emprunts = charger_csv_pandas(
        f_livres, f_utilisateurs, f_emprunts
    )

    # lance le calcul des stats et la création des graphes
    stats_et_graphs(df_livres, df_utilisateurs, df_emprunts, dossier_sortie)

    print("Rapport généré dans le dossier :", dossier_sortie)

# fonction qui exporte les données de la bibliothèque vers des fichiers CSV                                     
def exporter_csv_depuis_biblio(biblio,
                               f_livres="livres.csv",
                               f_utilisateurs="utilisateurs.csv",
                               f_emprunts="emprunts.csv"):

    # --- 1) LIVRES ---
    with open(f_livres, "w", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.writer(fichier)
        ecrivain.writerow(["id", "titre", "auteur", "categorie", "exemplaires", "statut"])
        
        # parcour la liste des livres
        for livre in getattr(biblio, "livres", []):
            ecrivain.writerow([getattr(livre, "id", ""),
                        getattr(livre, "titre", ""),
                        getattr(livre, "auteur", ""),
                        getattr(livre, "categorie", ""),
                        getattr(livre, "exemplaires", 0),
                        getattr(livre, "statut", "")])

    # --- 2) UTILISATEURS ---
    with open(f_utilisateurs, "w", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.writer(fichier)
        ecrivain.writerow(["id", "nom", "email", "type"])  # type = Lecteur / Bibliothecaire
        
        # parcourt le dictionnaire des utilisateurs
        for utilisateur in getattr(biblio, "utilisateurs", {}).values():

            # déterminer le type d utilisateur
            if isinstance(utilisateur, Lecteur):
                type_utilisateur = "Lecteur"
            elif isinstance(utilisateur, Bibliothecaire):
                type_utilisateur = "Bibliothecaire"
            else:
                type_utilisateur = utilisateur.__class__.__name__
            ecrivain.writerow([getattr(utilisateur, "id", ""),
                        getattr(utilisateur, "nom", ""),
                        getattr(utilisateur, "email", ""),
                        type_utilisateur])

    # --- 3) EMPRUNTS ---
    with open(f_emprunts, "w", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.writer(fichier)
        ecrivain.writerow(["id", "livre_id", "lecteur_id", "retourne",
                    "date_emprunt", "date_retour_prevue", "date_retour_effective"])

        # parcourt les emprunts
        # parcourt le dictionnaire des emprunts
        for emprunt in getattr(biblio, "emprunts", {}).values():
            ecrivain.writerow([
                getattr(emprunt, "id", ""),
                getattr(emprunt, "id_livre", ""),
                getattr(emprunt, "id_lecteur", ""),
                getattr(emprunt, "est_retourne", False)
            ])

    print(" Export CSV terminé avec succès.")
    print(f" - {f_livres}")
    print(f" - {f_utilisateurs}")
    print(f" - {f_emprunts}")


##  Sauvegarde chargement JSON                                                                                  
def sauvegarder_json(biblio, dossier="data_json"):
    p = Path(dossier); p.mkdir(parents=True, exist_ok=True)

    # livres.json
    livres = []
    for livre in getattr(biblio, "livres", []):
        livres.append({
            "id": livre.id,
            "titre": livre.titre,
            "auteur": livre.auteur,
            "categorie": livre.categorie,
            "exemplaires": int(livre.exemplaires),
            "statut": livre.statut
        })
    (p / "livres.json").write_text(json.dumps(livres, ensure_ascii=False, indent=2), encoding="utf-8")

    # utilisateurs.json
    users = []
    for u in getattr(biblio, "utilisateurs", {}).values():
        t = "Lecteur" if isinstance(u, Lecteur) else ("Bibliothecaire" if isinstance(u, Bibliothecaire) else u.__class__.__name__)
        users.append({
            "id": u.id,
            "nom": u.nom,
            "email": u.email,
            "type": t
        })
    (p / "utilisateurs.json").write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")

    # emprunts.json
    emps = []
    for e in getattr(biblio, "emprunts", {}).values():
        emps.append({
            "id": e.id,
            "livre_id": e.livre_id,
            "lecteur_id": e.lecteur_id,
            "retourne": bool(e.retourne),
            "date_emprunt": e.date_emprunt.isoformat() if e.date_emprunt else None,
            "date_retour_prevue": e.date_retour_prevue.isoformat() if e.date_retour_prevue else None,
            "date_retour_effective": e.date_retour_effective.isoformat() if e.date_retour_effective else None
        })
    (p / "emprunts.json").write_text(json.dumps(emps, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"JSON sauvegardés dans {p.resolve()}")

# chargement du json                                                                                                
def charger_json(biblio, dossier="data_json"):
    p = Path(dossier)
    if not p.exists():
        print("Dossier JSON introuvable.")
        return

    # reset
    biblio.livres = []
    biblio.utilisateurs = {}
    biblio.emprunts = {}
    biblio.emprunts_par_lecteur = {}

    # --- LIVRES ---
    pf = p / "livres.json"
    max_id_livre = 0
    if pf.exists():
        data_livres = json.loads(pf.read_text(encoding="utf-8"))
        for r in data_livres:
            titre = r.get("titre", "")
            auteur = r.get("auteur", "")
            categorie = r.get("categorie", "")
            nb = int(r.get("exemplaires", 0))
            livre = Livre(titre, auteur, categorie, nb)
            livre.id = int(r.get("id", livre.id))
            max_id_livre = max(max_id_livre, livre.id)
            livre.mettre_a_jour_statut()
            biblio.livres.append(livre)
    else:
        print("Fichier livres.json manquant.")

    # --- UTILISATEURS ---
    pu = p / "utilisateurs.json"
    if pu.exists():
        data_users = json.loads(pu.read_text(encoding="utf-8"))
        for r in data_users:
            uid = int(r.get("id"))
            nom = r.get("nom", "")
            email = r.get("email", "")
            typ = (r.get("type", "") or "").strip().lower()
            if typ == "lecteur":
                user = Lecteur(uid, nom, email)
            else:
                user = Bibliothecaire(uid, nom, email)
            biblio.utilisateurs[uid] = user
    else:
        print("Fichier utilisateurs.json manquant.")

    # --- EMPRUNTS ---
    pe = p / "emprunts.json"
    max_id_emprunt = 0
    if pe.exists():
        data_emps = json.loads(pe.read_text(encoding="utf-8"))
        for r in data_emps:
            e = Emprunt(int(r.get("livre_id")), int(r.get("lecteur_id")))
            e.id = int(r.get("id", e.id))
            max_id_emprunt = max(max_id_emprunt, e.id)

            # dates
            try:
                de = r.get("date_emprunt")
                e.date_emprunt = datetime.fromisoformat(de) if de else datetime.now()
            except:
                pass
            try:
                drp = r.get("date_retour_prevue")
                e.date_retour_prevue = datetime.fromisoformat(drp) if drp else e.date_emprunt + timedelta(days=DUREE_EMPRUNT_MAXI)
            except:
                pass
            try:
                dre = r.get("date_retour_effective")
                e.date_retour_effective = datetime.fromisoformat(dre) if dre else None
            except:
                pass

            e.retourne = bool(r.get("retourne", False))

            # Enregistre
            biblio.emprunts[e.id] = e
            biblio.emprunts_par_lecteur.setdefault(e.lecteur_id, set()).add(e.id)

            # Marquer côté lecteur
            lecteur = biblio.utilisateurs.get(e.lecteur_id)
            if isinstance(lecteur, Lecteur) and not e.retourne:
                lecteur.livres_empruntes.add(e.livre_id)
    else:
        print("Fichier emprunts.json manquant.")

    # --- Remettre les compteurs pour éviter collisions d'ID ---
    try:
        Livre.Compteur = max_id_livre + 1
    except:
        pass
    try:
        Emprunt.Compteur = max_id_emprunt + 1
    except:
        pass

    print(f"Données JSON chargées depuis {p.resolve()}")



#Sauvegarde des données de la bibliothèque                                                                              
def sauver_donnees(biblio):
    if FORMAT_DE_SAUVEGARDE_DEFAUT:
        #exporte les données de la bibliothèque dans un fichier CSV.
        exporter_csv_depuis_biblio(biblio)
    else:
        sauvegarder_json(biblio)
#Charge les données de la bibliothèque (CSV lu directement, JSON reconstruit en objets)                                   
def charger_donnees(biblio):
    if FORMAT_DE_SAUVEGARDE_DEFAUT:
       print(" Mode CSV : rien à reconstruire en objets (pandas lit directement les CSV).")
    else:
        charger_json(biblio)


# -------------------------------
# Application principale                                                                                 
# -------------------------------
def MenuApp():

    choisir_format_sauvegarde()
    # creation dun bibliotheque vide
    biblio = initialiser_bibliotheque()

    #charger depuis le disque (JSON si choisi)
    try:
        charger_donnees(biblio)
    except Exception as e:
        print("Pas de données à charger pour l’instant.", e)

    print("Bienvenue dans la gestion de la bibliothèque !")

    # boucle principale du menu
    while True:
        print("\n1. Livres\n2. Utilisateurs\n3. Emprunts\n4. Sauvegarder&Charger\n5. Recherches\n6. Statistiques\n7. Graph\n8. Quitter")
        choix = input("Votre choix : ")
        
        if choix == "1":
            print("\n1. Voir tous les livres\n2. Ajouter\n3. Modifier\n4. Supprimer\n5. Retour")
            c = input("Choix : ")
            # Voir tous les livres
            if c == "1":
                biblio.afficher_tous_les_livres()

            # Ajouter un livre
            elif c == "2":
                id_admin = demander_int("ID bibliothécaire : ")
                admin = biblio.utilisateurs.get(id_admin)
                if not biblio.est_bibliothecaire(admin):
                    print("Accès refusé.")
                else:
                    titre = input("Titre : "); auteur = input("Auteur : "); cat = input("Catégorie : ")
                    nb = demander_int("Exemplaires : ")
                    biblio.ajouter_livre(Livre(titre, auteur, cat, nb), admin)

            # Modifier un livre       
            elif c == "3":
                id_admin = demander_int("ID bibliothécaire : ")
                admin = biblio.utilisateurs.get(id_admin)
                if not biblio.est_bibliothecaire(admin):
                    print("Accès refusé.")
                else:
                    id_livre = demander_int("ID livre : ")
                    nv_titre = input("Nouveau titre (laisser vide) : ")
                    champs = {}
                    if nv_titre: champs["titre"] = nv_titre
                    biblio.modifier_livre(id_livre, admin, **champs)

             # Supprimer un livre       
            elif c == "4":
                id_admin = demander_int("ID bibliothécaire : ")
                admin = biblio.utilisateurs.get(id_admin)
                if not biblio.est_bibliothecaire(admin):
                    print("Accès refusé.")
                else:
                    id_livre = demander_int("ID livre : ")
                    biblio.supprimer_livre(id_livre, admin)

         #GESTION DES UTILISATEURS 
        elif choix == "2":
        
            print("\n1. Ajouter utilisateur\n2. Voir utilisateurs\n3. Retour")
            c = input("Choix : ")

            # Ajouter un utilisateur
            if c == "1":
                idu = demander_int("ID : "); nom = input("Nom : "); email = input("Email : ")
                typ = input("Type (lecteur/bibliothecaire) : ").lower()
                if typ == "lecteur":
                    biblio.ajouter_utilisateur(Lecteur(idu, nom, email))
                elif typ == "bibliothecaire":
                    biblio.ajouter_utilisateur(Bibliothecaire(idu, nom, email))

        # Voir la liste des utilisateurs                    
            elif c == "2":
                biblio.afficher_utilisateurs()

        #GESTION DES EMPRUNTS
        elif choix == "3":
            # >>> ton code actuel des emprunts (inchangé)
            print("\n1. Emprunter\n2. Rendre\n3. Voir emprunts en cours\n4. Par lecteur\n5. Retour")
            c = input("Choix : ")

            # Emprunter un livre
            if c == "1":
                idl = demander_int("ID lecteur : ")
                idlivre = demander_int("ID livre : ")
                biblio.emprunter_livre(idlivre, idl)

                # Rendre un livre
            elif c == "2":
                biblio.lister_emprunts_en_cours()
                idemprunt = demander_int("ID emprunt : ")
                biblio.rendre_livre(idemprunt)

            # Voir tous les emprunts en cours
            elif c == "3":
                biblio.lister_emprunts_en_cours()

            # Voir les emprunts d’un lecteur précis
            elif c == "4":
                idl = demander_int("ID lecteur : ")
                biblio.lister_emprunts_par_lecteur(idl)

        #SAUVEGARDE / CHARGEMENT
        elif choix == "4":
            print("\n1. Sauvegarder maintenant\n2. Charger depuis disque\n3. Export CSV (pour pandas)\n4. Retour")
            c = input("Choix : ")
            # Sauvegarder
            if c == "1":
                sauver_donnees(biblio)
            # Charger
            elif c == "2":
                charger_donnees(biblio)
            ## Exporter en CSV
            elif c == "3":
                exporter_csv_depuis_biblio(biblio)

        #RECHERCHES
        elif choix == "5":
            crit = input("Critère (titre/auteur/categorie/disponibilite) : ")
            val = input("Valeur : ")
            biblio.rechercher_livre(crit, val)

        #STATISTIQUES console
        elif choix == "6":
            biblio.statistiques()

        #GRAPHIQUES
        elif choix == "7":
            print("\n=== GRAPH / STATISTIQUES VISUELLES ===")
            try:
                exporter_csv_depuis_biblio(biblio)
                run_rapport_pandas()
                print("Graphiques générés dans le dossier 'MesGraphiques/'.")
                print(" - livres_par_categorie.png")
                print(" - empruntes_vs_non_empruntes.png")
                print(" - utilisateurs_par_type.png")
            except Exception as e:
                print(" Impossible de générer les graphiques :", e)


        #QUITTER
        elif choix == "8":
            print("Mercii pour la visite !")
            break

        else:
            print("Choix invalide.")



if __name__ == "__main__":
    MenuApp()


    
