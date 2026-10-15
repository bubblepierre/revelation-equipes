import streamlit as st
import time
from google import genai
from google.genai import errors

st.set_page_config(page_title="Révélation des Talents & Rôles d'Équipe", layout="wide")

# Récupération sécurisée de la clé d'API
api_key = st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

MBTI_TYPES = [
    "ISTJ - Logisticien", "ISFJ - Défenseur", "INFJ - Avocat", "INTJ - Architecte",
    "ISTP - Virtuose", "ISFP - Aventurier", "INFP - Médiateur", "INTP - Logicien",
    "ESTP - Entrepreneur", "ESFP - Amuseur", "ENFP - Inspirateur", "ENTP - Innovateur",
    "ESTJ - Directeur", "ESFJ - Consul", "ENFJ - Protagoniste", "ENTJ - Commandant"
]

INTELLIGENCES = [
    "Linguistique (mots, écriture, expression orale)",
    "Logico-mathématique (chiffres, logique, rigueur d'analyse)",
    "Spatiale / Visuelle (formes, schémas, maquettes, design)",
    "Kinesthésique (action, manipulation physique, fabrication)",
    "Interpersonnelle (relations, écoute, empathie, leadership)",
    "Intrapersonnelle (introspection, recul, stratégie personnelle)",
    "Naturaliste (sensibilité aux systèmes, à l'environnement et au vivant)",
    "Musicale / Rythmique (rythme, sensibilité aux ambiances et structures)"
]

VERBES = [
    "Imaginer, dessiner, rêver, inventer (mille idées et créativité)",
    "Fabriquer, assembler, concevoir (fabriquer les idées des autres)",
    "Diriger, manager (rassembler et organiser le travail d'équipe)",
    "Gérer, chiffrer (calculer, régler les problèmes et les flux)",
    "Prévoir, ranger (talent pour structurer et planifier)",
    "Représenter, fédérer, animer (trouver les arguments pour convaincre)",
    "Communiquer, échanger (discuter, animer et présenter)",
    "Contrôler, vérifier (s'assurer du bon fonctionnement et fiabiliser)"
]

st.title("Diagnostic des Talents & Structuration d'Équipe")
st.markdown("Renseignez les profils des membres du groupe pour révéler vos complémentarités et attribuer les responsabilités opérationnelles.")

# Sélection de 1 à 10 membres
nb_membres = st.slider("Nombre de participants dans l'équipe :", min_value=1, max_value=10, value=4)

membres_data = []

# Affichage en 2 colonnes pour faciliter la saisie sur écran ou mobile
colonnes = st.columns(2)

for i in range(nb_membres):
    col = colonnes[i % 2]
    with col:
        st.subheader(f"Membre {i + 1}")
        nom = st.text_input(f"Prénom :", key=f"nom_{i}", placeholder=f"Ex: Participant {i+1}")
        mbti = st.selectbox(f"Profil MBTI :", MBTI_TYPES, key=f"mbti_{i}")
        
        # 2 intelligences dominantes
        intel_1 = st.selectbox(f"Intelligence dominante n°1 :", INTELLIGENCES, key=f"intel1_{i}")
        intel_2 = st.selectbox(f"Intelligence dominante n°2 :", INTELLIGENCES, key=f"intel2_{i}", index=1)
        
        # 2 verbes de talents
        verbe_1 = st.selectbox(f"Verbe de talent n°1 :", VERBES, key=f"verbe1_{i}")
        verbe_2 = st.selectbox(f"Verbe de talent n°2 :", VERBES, key=f"verbe2_{i}", index=1)
        
        valeurs = st.text_input(f"3 à 4 valeurs clés :", key=f"val_{i}", placeholder="Ex: Rigueur, Écoute, Audace")
        
        membres_data.append({
            "prenom": nom if nom else f"Membre {i+1}",
            "mbti": mbti,
            "intel_1": intel_1,
            "intel_2": intel_2,
            "verbe_1": verbe_1,
            "verbe_2": verbe_2,
            "valeurs": valeurs
        })

system_prompt = """
Tu es un consultant expert en dynamique d'équipe, en posture professionnelle et en gouvernance de projet.
Ton rôle est d'analyser la composition d'une équipe ou d'un profil individuel (de 1 à 10 personnes) à partir des données transmises :
- Profil MBTI (16 personnalités)
- 2 Intelligences dominantes de Gardner
- 2 Verbes de talents
- Valeurs déclarées

Ce livrable doit servir aussi bien pour un projet d'innovation, un hackathon, qu'un collectif professionnel (cabinet, entreprise, association). N'invente aucune contrainte thématique non mentionnée.

Respecte scrupuleusement la structure suivante :

### 1. Analyse collective de l'équipe
- **Forces du collectif :** Analyse synthétique des dominantes de l'équipe, des forces opérationnelles et du tempérament global. (Si 1 seule personne, analyse ses atouts majeurs).
- **Points de vigilance & fatigue :** Zones d'angles morts (rôles ou compétences peu représentés) et risques d'épuisement collectif si le travail n'est pas bien réparti.

### 2. Attribution des postes opérationnels
Attribue à chaque membre un poste exécutif officiel adapté au fonctionnement d'une organisation (ex: CEO, CMO, CTO, CDO, CFO, COO, etc.) formulé sous forme d'un binôme strict :
« [Prénom] : [Titre du poste en anglais abrégé et complet] / [Mission principale en français] »
- **Sa mission concrète :** Définis précisément ce qu'il prend en charge dans le projet ou la structure pour assurer le succès collectif, en faisant le lien direct avec son MBTI, ses deux intelligences et ses deux verbes de talents.
- **Ce qui l'épuise :** Les contextes, méthodes de travail ou types de tâches qui le vident de son énergie et qu'il doit limiter ou déléguer.

Ton ton doit être direct, valorisant, professionnel et orienté vers l'action.
"""

if st.button("Révéler les rôles et l'analyse de l'équipe", type="primary"):
    with st.spinner("Analyse des profils en cours..."):
        user_content = f"L'équipe est composée de {nb_membres} personne(s) :\n"
        for m in membres_data:
            user_content += (
                f"- {m['prenom']} | MBTI: {m['mbti']} | "
                f"Intelligences: 1. {m['intel_1']} / 2. {m['intel_2']} | "
                f"Verbes: 1. {m['verbe_1']} / 2. {m['verbe_2']} | "
                f"Valeurs: {m['valeurs']}\n"
            )
        
        # Liste de modèles avec bascule automatique en cas de pic de charge
        modeles_a_tester = ["gemini-flash", "gemini-1.5-flash", "gemini-2.0-flash-lite"]
        reponse_obtenue = False

        for modele in modeles_a_tester:
            try:
                response = client.models.generate_content(
                    model=modele,
                    contents=[system_prompt, user_content]
                )
                st.success("Diagnostic prêt !")
                st.markdown(response.text)
                reponse_obtenue = True
                break
            except Exception:
                time.sleep(1)
                continue

        if not reponse_obtenue:
            st.error("Les serveurs sont temporairement très chargés. Veuillez recliquer sur le bouton dans 10 secondes.")
