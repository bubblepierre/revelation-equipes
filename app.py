import streamlit as st
from google import genai
from google.genai import errors

# Configuration de la page
st.set_page_config(page_title="Strat'Team", layout="wide")

# Connexion à l'API Google (récupération de la clé depuis Streamlit Secrets)
api_key = st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Données des menus déroulants
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

st.title("Strat'Team : Découvrez vos Talents & Structurez votre Équipe")
st.markdown("Renseignez les profils de votre équipe pour révéler vos complémentarités et attribuer les responsabilités du projet.")

# Curseur de 1 à 10 membres
nb_membres = st.slider("Nombre de participants dans l'équipe :", min_value=1, max_value=10, value=4)

membres_data = []
colonnes = st.columns(2)

# Génération des fiches de saisie
for i in range(nb_membres):
    col = colonnes[i % 2]
    with col:
        st.subheader(f"Membre {i + 1}")
        nom = st.text_input(f"Prénom :", key=f"nom_{i}", placeholder=f"Ex: Participant {i+1}")
        mbti = st.selectbox(f"Profil MBTI :", MBTI_TYPES, key=f"mbti_{i}")
        intel_1 = st.selectbox(f"Intelligence dominante n°1 :", INTELLIGENCES, key=f"intel1_{i}")
        intel_2 = st.selectbox(f"Intelligence dominante n°2 :", INTELLIGENCES, key=f"intel2_{i}", index=1)
        verbe_1 = st.selectbox(f"Verbe de talent n°1 :", VERBES, key=f"verbe1_{i}")
        verbe_2 = st.selectbox(f"Verbe de talent n°2 :", VERBES, key=f"verbe2_{i}", index=1)
        valeurs = st.text_input(f"3 à 4 valeurs clés :", key=f"val_{i}", placeholder="Ex: Rigueur, Écologie, Écoute")
        
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
Tu es un expert en dynamique d'équipe et gouvernance de projet.
Analyse l'équipe (1 à 10 personnes) selon le MBTI, les 2 Intelligences de Gardner, les 2 Verbes de talents et les Valeurs.

Structure ta réponse EXACTEMENT ainsi :

### 1. Cartographie de l'équipe
- **Les Forces :** Décris la dynamique collective, l'énergie dominante et la créativité du groupe.
- **Points de Vigilance :** Ce qui manque à l'équipe et ce qui risque de les bloquer (les angles morts).

### 2. Attribution des Postes & Missions
Attribue à CHAQUE membre un rôle exécutif officiel (CEO, CMO, CTO, CDO, CFO, COO...) sous cette forme stricte :
**[Prénom] : [Titre du poste] / [Mission]**
- **Ta mission concrète :** Explique son rôle opérationnel direct en justifiant par ses talents (MBTI, intelligences, verbes).
- **Attention à la fatigue :** Indique les tâches ou contextes qui vont l'épuiser (sa zone de frustration) et qu'il/elle doit éviter.

Sois ultra-professionnel, percutant et valorisant. N'invente pas de contraintes thématiques.
"""

if st.button("Révéler les rôles de l'équipe", type="primary"):
    with st.spinner("L'IA analyse vos talents..."):
        user_content = f"L'équipe est composée de {nb_membres} personne(s) :\n"
        for m in membres_data:
            user_content += (
                f"- {m['prenom']} | MBTI: {m['mbti']} | "
                f"Intelligences: 1. {m['intel_1']} / 2. {m['intel_2']} | "
                f"Verbes: 1. {m['verbe_1']} / 2. {m['verbe_2']} | "
                f"Valeurs: {m['valeurs']}\n"
            )
        
        try:
            # Appel direct au modèle de production exigé par l'API
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=[system_prompt, user_content]
            )
            st.success("Diagnostic d'équipe prêt !")
            st.markdown(response.text)
        except errors.APIError as e:
            st.error(f"Une erreur technique est survenue : {e}")
