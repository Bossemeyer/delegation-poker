import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

# --- Initiale Fragenstruktur ---
delegation_questions = {
    "Strategische Ausrichtung": [
        "Wer entscheidet, ob wir in einen neuen Markt eintreten?",
        "Wer entscheidet, ob wir unser Leistungsportfolio erweitern?"
    ],
    "Meeting & Organisation": [
        "Wer entscheidet, welche Themen auf die Meeting-Agenda kommen?",
        "Wer entscheidet, wer an einem bestimmten Meeting teilnehmen soll?"
    ],
    "Kunden & Markt": [
        "Wer entscheidet, wie wir auf eine Kundenbeschwerde reagieren?",
        "Wer entscheidet, welche Kund:innen wir priorisieren?"
    ],
    "Ressourcen & Personal": [
        "Wer entscheidet, wie Aufgaben im Team verteilt werden?",
        "Wer entscheidet, wer welches Projekt übernimmt?"
    ],
    "Finanzen & Tools": [
        "Wer entscheidet, ob neue Softwaretools angeschafft werden?",
        "Wer entscheidet, wie das Team-Budget aufgeteilt wird?"
    ]
}

# --- Delegation Levels ---
delegation_levels = {
    1: "1. Ich entscheide allein",
    2: "2. Ich entscheide und erkläre dir meine Gründe",
    3: "3. Ich entscheide, hole mir vorher aber deine Meinung ein",
    4: "4. Wir entscheiden gemeinsam",
    5: "5. Du entscheidest, nachdem du meinen Rat gehört hast",
    6: "6. Du entscheidest, informierst mich aber",
    7: "7. Du entscheidest komplett eigenständig"
}

# --- Helper: Reset alles ---
def reset_all_states():
    st.session_state.players = []
    st.session_state.admin = None
    st.session_state.current_question = None
    st.session_state.votes = {}
    st.session_state.round_log = []
    st.session_state.intro_shown = False
    st.session_state.ready_to_start = False
    st.session_state.selected_category = None
    st.session_state.custom_question = None
    st.rerun()

# --- Session State initialisieren ---
if 'intro_shown' not in st.session_state:
    st.session_state.intro_shown = False
if 'players' not in st.session_state:
    st.session_state.players = []
if 'admin' not in st.session_state:
    st.session_state.admin = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'votes' not in st.session_state:
    st.session_state.votes = {}
if 'round_log' not in st.session_state:
    st.session_state.round_log = []
if 'ready_to_start' not in st.session_state:
    st.session_state.ready_to_start = False
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'custom_question' not in st.session_state:
    st.session_state.custom_question = None

# --- Einleitung ---
if not st.session_state.intro_shown:
    st.title("Delegation Poker (Admin gesteuert)")

    st.markdown("""
    ## Was ist Delegation Poker?
    Delegation Poker ist ein spielerisches Tool, mit dem Teams klären, **wie viel Entscheidungsfreiheit** einzelne Teammitglieder:innen bei bestimmten Themen haben.
    Ziel ist es, Transpar