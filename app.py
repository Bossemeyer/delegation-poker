import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

# --- Fragenstruktur ---
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

# --- Delegationsstufen ---
delegation_levels = {
    1: "1. Ich entscheide allein",
    2: "2. Ich entscheide und erkläre dir meine Gründe",
    3: "3. Ich entscheide, hole mir vorher aber deine Meinung ein",
    4: "4. Wir entscheiden gemeinsam",
    5: "5. Du entscheidest, nachdem du meinen Rat gehört hast",
    6: "6. Du entscheidest, informierst mich aber",
    7: "7. Du entscheidest komplett eigenständig"
}

# --- Reset-Funktion ---
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
    st.session_state.phase = 'setup'
    st.rerun()

# --- Session-Init ---
for key, default in [
    ('intro_shown', False),
    ('players', []),
    ('admin', None),
    ('current_question', None),
    ('votes', {}),
    ('round_log', []),
    ('ready_to_start', False),
    ('selected_category', None),
    ('custom_question', None),
    ('phase', 'setup')  # NEU: Phasensteuerung
]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Einleitung ---
if st.session_state.phase == 'setup':
    st.title("Delegation Poker (Admin gesteuert)")

    st.markdown(
        """
        ## Was ist Delegation Poker?
        Delegation Poker ist ein spielerisches Tool, mit dem Teams klären, **wie viel Entscheidungsfreiheit** einzelne Teammitglieder:innen bei bestimmten Themen haben.
        Ziel ist es, Transparenz zu schaffen: Wer entscheidet was? Und auf welcher Delegationsebene?

        ### Wie funktioniert es?
        - Es gibt 7 Delegationsebenen:
          1. Ich entscheide allein  
          2. Ich entscheide und erkläre dir meine Gründe  
          3. Ich entscheide, hole mir vorher aber deine Meinung ein  
          4. Wir entscheiden gemeinsam  
          5. Du entscheidest, nachdem du meinen Rat gehört hast  
          6. Du entscheidest, informierst mich aber  
          7. Du entscheidest komplett eigenständig

        - In jeder Runde wird eine Frage gestellt, z. B.:  
        „Wer entscheidet, ob neue Softwaretools angeschafft werden?“

        - Alle Spieler:innen wählen verdeckt ihre Einschätzung (Stufe 1–7).

        - Danach werden die Ergebnisse sichtbar gemacht und gemeinsam besprochen.

        ### Ziel
        Am Ende habt ihr ein besseres Verständnis davon, wie Verantwortung und Entscheidungen im Team verteilt sind – und wo ihr vielleicht etwas anpassen wollt.
        """
    )

    if st.button("Loslegen"):
        st.session_state.phase = 'login'
        st.rerun()

# --- Spieler:innen-Login ---
elif st.session_state.phase == 'login':
    st.header("Spieler:innen anmelden")
    name = st.text_input("Name eingeben:")
    if st.button("Hinzufügen"):
        if name and name not in st.session_state.players:
            st.session_state.players.append(name)
            if not st.session_state.admin:
                st.session_state.admin = name
    st.write("Angemeldete Spieler:innen:", ", ".join(st.session_state.players))
    if st.session_state.admin:
        st.write(f"**Admin:** {st.session_state.admin}")
    if st.button("Zur Kategorie-Auswahl", disabled=(len(st.session_state.players) < 1)):
        st.session_state.phase = 'category'
        st.rerun()

# --- Kategorie- und Fragenauswahl ---
elif st.session_state.phase == 'category':
    st.header("Kategorie auswählen")
    categories = list(delegation_questions.keys()) + ["Eigene Frage eingeben"]
    category_choice = st.selectbox("Wähle eine Kategorie:", categories)

    if category_choice == "Eigene Frage eingeben":
        custom_question = st.text_input("Formuliere deine eigene Frage:")
        if st.button("Bestätigen (eigene Frage)") and custom_question:
            st.session_state.selected_category = "Eigene Frage"
            st.session_state.custom_question = custom_question
            st.session_state.phase = 'voting'
            st.rerun()
    else:
        if st.button("Bestätigen (Kategorie)"):
            st.session_state.selected_category = category_choice
            st.session_state.phase = 'voting'
            st.rerun()

# --- Abstimmungsphase ---
elif st.session_state.phase == 'voting':
    if not st.session_state.current_question:
        if st.session_state.selected_category == "Eigene Frage":
            question = st.session_state.custom_question
        else:
            question = random.choice(delegation_questions[st.session_state.selected_category])
        st.session_state.current_question = (st.session_state.selected_category, question)
        st.session_state.votes = {}

    category, question = st.session_state.current_question
    st.subheader(f"Kategorie: {category}")
    st.markdown(f"### *{question}*")

    for player in st.session_state.players:
        if player not in st.session_state.votes:
            options = list(delegation_levels.values())
            vote_label = st.selectbox(f"{player}, wähle deine Stufe:", options, key=f"vote_{player}")
            vote_number = int(vote_label.split('.')[0])
            if st.button(f"Bestätigen ({player})", key=f"confirm_{player}"):
                st.session_state.votes[player] = vote_number
                st.rerun()

    if len(st.session_state.votes) == len(st.session_state.players):
        st.success("Alle Stimmen abgegeben! Ergebnisse freigeben?")
        if st.button("Aufdecken"):
            st.session_state.phase = 'results'
            st.rerun()

# --- Ergebnisphase ---
elif st.session_state.phase == 'results':
    category, question = st.session_state.current_question
    votes = list(st.session_state.votes.values())
    avg = sum(votes) / len(votes)
    stdev = (sum((x - avg) ** 2 for x in votes) / len(votes)) ** 0.5
    consensus = len(set(votes)) == 1

    st.write("### Ergebnisse")
    for player, vote in st.session_state.votes.items():
        st.write(f"{player}: Stufe {vote} ({delegation_levels[vote]})")
    st.write(f"Durchschnittliche Stufe: **{avg:.2f}**")
    st.write(f"Standardabweichung: **{stdev:.2f}**")
    st.write(f"Konsens erreicht? **{'Ja' if consensus else 'Nein'}**")

    fig, ax = plt.subplots()
    players = list(st.session_state.votes.keys())
    scores = list(st.session_state.votes.values())

    ax.bar(players, scores)
    ax.set_xlabel('Spieler:innen')
    ax.set_ylabel('Gewählte Delegationsstufe')
    ax.set_ylim(0, 8)
    ax.set_title('Delegationsstufen pro Spieler:in')
    st.pyplot(fig)

    st.session_state.round_log.append({
        'category': category,
        'question': question,
        'votes': st.session_state.votes.copy(),
        'average': avg,
        'stdev': stdev,
        'consensus': consensus
    })

    if st.button("Frage wiederholen"):
        st.session_state.votes = {}
        st.session_state.phase = 'voting'
        st.rerun()

    if st.button("Nächste Runde"):
        st.session_state.current_question = None
        st.session_state.votes = {}
        st.session_state.phase = 'voting'
        st.rerun()

# --- Immer sichtbare Buttons ---
if st.button("Neustart"):
    reset_all_states()

if st.session_state.round_log:
    df = pd.DataFrame([
        {
            'Kategorie': r['category'],
            'Frage': r['question'],
            'Durchschnitt': r['average'],
            'Standardabweichung': r['stdev'],
            'Konsens': r['consensus'],
            'Votes': ", ".join(f"{k}: {v}" for k, v in r['votes'].items())
        }
        for r in st.session_state.round_log
    ])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Ergebnisse (CSV)", data=csv, file_name='delegation_poker_results.csv', mime='text/csv')