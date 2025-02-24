# Import des modules nécessaires
import random
import json
import numpy as np
import streamlit as st
from copy import deepcopy
from statistics import mean, stdev

# Chargement du fichier JSON
with open("members.json", "r") as f:
    members = json.load(f)

# Tri des adhérents par ordre alphabétique
members = {key: members[key] for key in sorted(members)}


# Fonction de génération des équipes
def generate_teams(players):

    # Création d'une copie des joueurs par niveau pour éviter la modification en place
    players_copy = deepcopy(players)

    # Calcul du nombre total de joueurs de la séance
    n_players = len(players_copy)

    # Vérification que le nombre de joueurs est dans l'intervalle [10, 20]
    if n_players not in range(10, 21):
        raise ValueError("Le nombre de joueurs doit être compris entre 10 et 20.")

    # Calcul du nombre d'équipes à créer
    for nb_teams, r in zip([2, 3, 4], [range(10, 13), range(13, 16), range(16, 21)]):
        if n_players in r:
            n_teams = nb_teams

    # Récupération d'une liste contenant les notes des joueurs présents à la séance
    ratings = list(players_copy.values())

    # Nombre d'échantillons d'équipes à générer
    n_samples, samples = 10000, {}
    for i in range(n_samples):

        # On crée une copie de levels pour récupérer la liste initiale à chaque début de boucle
        ratings_copy = deepcopy(ratings)

        # Initialisation des équipes
        teams_sample = {f"Équipe {color}": [] for color in ['A', 'B', 'C', 'D'][:n_teams]}

        # Répartition des joueurs dans les équipes de manière aléatoire
        while ratings_copy:
            for team in teams_sample:
                if ratings_copy:
                    rating = random.choice(ratings_copy)
                    teams_sample[team].append(rating)
                    ratings_copy.remove(rating)

        # Calcul de la note moyenne de chaque équipe
        avg = [mean(team) for team in teams_sample.values()]

        # Enregistrement de chaque échantillon d'équipe avec l'écart-type des moyennes
        samples[f"Échantillon {i}"] = (stdev(avg), teams_sample)

    # Recherche de l'échantillon avec l'écart-type minimum
    best_sample, _ = min(samples.items(), key=lambda x: x[1][0])

    # Utilisation de l'échantillon avec le meilleur écart-type
    teams = samples[best_sample][1]

    # Remplacement des notes par un joueur du niveau correspondant (choix aléatoire si plusieurs joueurs ayant
    # la même note)
    for key, value in teams.items():
        for i, rating in enumerate(value):
            player = random.choice([k for k, v in players_copy.items() if v == rating])
            teams[key][i] = player
            players_copy.pop(player)

    return teams


# Application Streamlit
st.set_page_config(page_title="AFIC - Générateur d'équipes", layout="wide")

col1, col2 = st.columns([0.7, 0.1])
with col1:
    st.write("")
    st.title(":rainbow[Association Futsal Inas Club]")
with col2:
    st.image("logo_association.png", width=100)

tab1, tab2 = st.tabs(["Générateur d'équipes", "Mise à jour des adhérents"])

with tab1:

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.title("⚙️ Générateur d'équipes")
        st.subheader(":green-background[✔️ Sélectionnez les joueurs présents à la séance du jour.]")

    with col2:
        st.write("")
        st.write("")
        st.info(body="***Pour effacer toutes les sélections, rafraichissez la page***", icon="🔄")

    st.write("")

    # Affichage des adhérents sur 4 colonnes
    col1, col2, col3, col4, col5 = st.columns(5, gap='small', vertical_alignment='top')
    columns = np.array_split(list(members.keys()), 5)

    # Constitution de players selon les cases cochées
    players = {}
    for col, i in zip([col1, col2, col3, col4, col5], range(len(columns))):
        with col:
            for member in columns[i]:
                check = st.checkbox(member, value=False)
                if check:
                    players[member] = members[member]

    st.write("")
    st.write(len(players), "joueurs sélectionnés")

    # Appui du bouton "Générer les équipes"
    if st.button("⚙️ Générer les équipes", type='primary'):

        # Génération des équipes
        teams = generate_teams(players=players)
        st.write("")

        # Affichage des équipes formées et des rencontres éventuelles
        col1, col2 = st.columns([0.7, 0.3])

        with col1:
            st.subheader("Équipes formées")
            col1_1, col1_2, col1_3, col1_4 = st.columns(4)

            for col, team, color in zip(
                    [col1_1, col1_2, col1_3, col1_4], teams, ["blue", "green", "orange", "violet"]):

                with col:
                    st.markdown(f":{color}-background[**{team}**]")
                    for player in teams[team]:
                        st.write("-", player)

        with col2:

            if len(teams) == 4:
                l = list(teams.keys())
                random.shuffle(l)
                game1, game2 = l[:2], l[2:]

                st.subheader("Rencontres")
                st.markdown(f"**Match 1** : :grey-background[**{game1[0]}** vs **{game1[1]}**]")
                st.markdown(f"**Match 2** : :red-background[**{game2[0]}** vs **{game2[1]}**]")

with tab2:
    st.title("↪️ Mise à jour de la base de données")

    st.warning("⚠️ Pour que vos mises à jour soient bien prises en compte, pensez à rafraichir la page.")

    what_to_do = st.selectbox(
        label="Que souhaitez-vous faire ?",
        options=["Ajout d'un nouvel adhérent", "Modification de la note d'un adhérent", "Suppression d'un adhérent"],
        index=None,
        key="what_to_do",
        placeholder="Choisir une option"
    )

    if what_to_do == "Ajout d'un nouvel adhérent":
        st.write("")
        st.subheader("➕ Ajout d'un nouvel adhérent")

        col1, col2 = st.columns(2)

        with col1:
            new_member = st.text_input(label="Adhérent à ajouter")

        with col2:
            new_member_rating = st.slider("Note du joueur", min_value=1, max_value=99, step=1, value=50)

        # Appui du bouton "Enregistrer"
        if st.button(label="Enregistrer", key="add_player"):

            # Si un nouvel adhérent est renseigné
            if new_member:

                # Si le nouvel adhérent n'existe pas déjà dans la base de données
                if new_member not in members:

                    # Ajout du nouvel adhérent
                    members[new_member] = new_member_rating

                    # Enregistrement de la nouvelle base de données
                    with open("members.json", "w") as f:
                        json.dump(members, f)

                    # Confirmation de la mise à jour
                    with open("members.json", "r") as f:
                        d = json.load(f)

                    if d[new_member]:
                        st.success(f"✅ {new_member} a bien été ajouté à la liste des adhérents de l'association. "
                                   f"Sa note est de {d[new_member]}.")
                    else:
                        st.warning(f"❌ Le joueur {new_member} n'a pas été ajouté à la liste des adhérents.")

                else:
                    st.error(f"❌ {new_member} est déjà présent dans la liste de adhérents.")

            else:
                st.warning("Le champ \"Adhérent à ajouter\" est vide !")

    if what_to_do == "Modification de la note d'un adhérent":
        st.write("")
        st.subheader("🌀 Modification de la note d'un adhérent")

        col1, col2 = st.columns(2)

        with col1:
            option = st.selectbox(
                label="Sélectionner un joueur",
                options=list(members.keys()),
                index=None,
                key="member_to_modify",
                placeholder="Choisir une option"
            )

        if option:
            st.write(f"Vous avez choisi de modifier la note de {option}. Sa note actuelle est :", members[option])

        with col2:
            new_rating = st.slider("Nouvelle note", min_value=1, max_value= 99, step=1, value=50)

        # Appui du bouton "Enregistrer"
        if st.button(label="Enregistrer", key="change_rating"):

            # Si un adhérent est sélectionné
            if option:

                # Mise à jour de sa note
                members[option] = new_rating

                # Enregistrement de la nouvelle donnée
                with open("members.json", "w") as f:
                    json.dump(members, f)

            # Confirmation de la mise à jour
            if not option:
                st.warning("Veuillez sélectionner un adhérent")
            else:
                with open("members.json", "r") as f:
                    d = json.load(f)
                if d[option] == new_rating:
                    st.success(f"✅ La note de {option} a bien été modifiée.")
                else:
                    st.error("❌ La note n'a pas été modifiée.")

    if what_to_do == "Suppression d'un adhérent":
        st.write("")
        st.subheader("❌ Suppression d'un adhérent")

        option = st.selectbox(
            label="Sélectionner un joueur à retirer de la liste des adhérents",
            options=list(members.keys()),
            index=None,
            key="member_to_remove",
            placeholder="Choisir une option"
        )

        if option:
            st.write("Vous êtes sur le point de retirer", option, "de la liste des adhérents de l'association.")

        # Appui du bouton "Confirmer la suppression de l'adhérent"
        if st.button(label="Confirmer la suppression de l'adhérent", key="remove_member"):

            # Si un adhérent est sélectionné
            if option:

                # Suppression de l'adhérent de la base de données
                members.pop(option)

                # Enregistrement de la nouvelle base de données
                with open("members.json", "w") as f:
                    json.dump(members, f)

            # Confirmation de la mise à jour
            if not option:
                st.warning("Veuillez sélectionner un adhérent")
            else:
                with open("members.json", "r") as f:
                    d = json.load(f)
                if option not in d:
                    st.success(f"✅ {option} a bien été retiré de la liste des adhérents.")
                else:
                    st.warning(f"❌ Le joueur {option} n'a pas été retiré de la liste des adhérents.")
