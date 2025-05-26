import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

# --- Logo im Kopfbereich, linksbündig ---
logo_path = "Y-SiTE Logo.png"
try:
    st.image(logo_path, width=120)
except Exception:
    st.warning("Logo nicht gefunden. Bitte Datei 'Y-SiTE Logo.png' im Script-Ordner ablegen.")

# --- Fragenstruktur (je Kategorie 5 Fragen) ---
delegation_questions = {
    "Strategische Ausrichtung": [
        "Wer entscheidet, ob wir in einen neuen Markt eintreten?",
        "Wer entscheidet, ob wir unser Leistungsportfolio erweitern?",
        "Wer entscheidet, welche Vision oder Leitbild das Unternehmen verfolgt?",
        "Wer entscheidet, ob Kooperationen mit externen Partner:innen eingegangen werden?",
        "Wer entscheidet, wann und wie neue Geschäftsmodelle getestet werden?"
    ],
    "Meeting & Organisation": [
        "Wer entscheidet, welche Themen auf die Meeting-Agenda kommen?",
        "Wer entscheidet, wer an einem bestimmten Meeting teilnehmen soll?",
        "Wer entscheidet, wie oft und in welchem Rhythmus Teammeetings stattfinden?",
        "Wer entscheidet, ob ein Meeting vor Ort oder remote durchgeführt wird?",
        "Wer entscheidet, welche Tools für die interne Zusammenarbeit genutzt werden?"
    ],
    "Kunden & Markt": [
        "Wer entscheidet, wie wir auf eine Kundenbeschwerde reagieren?",
        "Wer entscheidet, welche Kund:innen wir priorisieren?",
        "Wer entscheidet, welche Angebote oder Aktionen für Kund:innen entwickelt werden?",
        "Wer entscheidet, wie Feedback von Kund:innen ausgewertet und genutzt wird?",
        "Wer entscheidet, wie wir mit besonders herausfordernden Kund:innen umgehen?"
    ],
    "Ressourcen & Personal": [
        "Wer entscheidet, wie Aufgaben im Team verteilt werden?",
        "Wer entscheidet, wer welches Projekt übernimmt?",
        "Wer entscheidet, wie die Urlaubsplanung im Team abläuft?",
        "Wer entscheidet, wer an Weiterbildungen oder Schulungen teilnimmt?",
        "Wer entscheidet, wie neue Kolleg:innen ins Team integriert werden?"
    ],
    "Finanzen & Tools": [
        "Wer entscheidet, ob neue Softwaretools angeschafft werden?",
        "Wer entscheidet, wie das Team-Budget aufgeteilt wird?",
        "Wer entscheidet, ob größere Investitionen (z. B. Hardware, Ausstattung) getätigt werden?",
        "Wer entscheidet, wie Reisekosten oder Spesen im Team genehmigt werden?",
        "Wer entscheidet, welche finanziellen Ressourcen für Team-Events oder Incentives eingesetzt werden?"
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

def reset_all_states(confirm=False):
    if not confirm:
        st.session_state.show_reset_dialog = True
        return
    st.session_state.players = []
    st.session_state.players_lower = set()
    st.session_state.admin = None
    st.session_state.current_question = None
    st.session_state.votes = {}
    st.session_state.round_log = []
    st.session_state.intro_shown = False
    st.session_state.ready_to_start = False
    st.session_state.selected_category = None
    st.session_state.custom_question = None
    st.session_state.phase = 'setup'
    st.session_state.question_history = set()
    st.session_state.show_reset_dialog = False
    st.session_state.show_protocol = False
    st.rerun()

# --- Session-Init ---
for key, default in [
    ('intro_shown', False),
    ('players', []),
    ('players_lower', set()),
    ('admin', None),
    ('current_question', None),
    ('votes', {}),
    ('round_log', []),
    ('ready_to_start', False),
    ('selected_category', None),
    ('custom_question', None),
    ('phase', 'setup'),
    ('question_history', set()),
    ('show_reset_dialog', False),
    ('show_protocol', False)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Einleitung ---
if st.session_state.phase == 'setup':
    st.title("Delegation Poker")

    st.markdown(
        """
        ### Was ist Delegation Poker?
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

        - Alle Spieler:innen wählen ihre Einschätzung im Chat von Teams (Stufe 1–7) 

        - Wenn alle ihren Eintrag vorgenommen haben, wird das Ergebnis in den Chat gesendet.

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

    with st.form(key="name_form", clear_on_submit=True):
        name = st.text_input("Name eingeben:", value="")
        submitted = st.form_submit_button("Hinzufügen")
        if submitted:
            name_clean = name.strip()
            name_lower = name_clean.lower()
            if name_clean == "":
                st.warning("Bitte einen Namen eingeben.")
            elif name_lower in st.session_state.players_lower:
                st.warning("Name bereits vergeben! Bitte anderen Namen wählen.")
            else:
                st.session_state.players.append(name_clean)
                st.session_state.players_lower.add(name_lower)
                if not st.session_state.admin:
                    st.session_state.admin = name_clean
                st.success(f"{name_clean} hinzugefügt.")

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

# --- Abstimmungsphase mit "Nächste Frage" und "Neue Kategorie" ---
elif st.session_state.phase == 'voting':
    def get_next_question():
        if st.session_state.selected_category == "Eigene Frage":
            return st.session_state.custom_question
        else:
            all_qs = [q for q in delegation_questions[st.session_state.selected_category]
                      if (st.session_state.selected_category, q) not in st.session_state.question_history]
            return random.choice(all_qs) if all_qs else None

    # Frage initialisieren oder nächste Frage ziehen
    if not st.session_state.current_question:
        question = get_next_question()
        if question is None:
            st.info("Alle Fragen dieser Kategorie wurden schon gestellt. Wähle eine andere Kategorie oder stelle eine eigene Frage.")
            if st.button("Zurück zur Kategorie-Auswahl"):
                st.session_state.phase = 'category'
                st.session_state.current_question = None
                st.rerun()
            st.stop()
        st.session_state.current_question = (st.session_state.selected_category, question)
        st.session_state.votes = {}

    category, question = st.session_state.current_question
    st.subheader(f"Kategorie: {category}")
    st.markdown(f"### *{question}*")

    # Buttons für nächste Frage & neue Kategorie, solange keine Stimmen abgegeben wurden
    if not st.session_state.votes and st.session_state.selected_category != "Eigene Frage":
        colA, colB = st.columns(2)
        all_qs = [q for q in delegation_questions[st.session_state.selected_category]
                  if (st.session_state.selected_category, q) not in st.session_state.question_history and q != question]
        with colA:
            if all_qs and st.button("Nächste Frage"):
                new_question = random.choice(all_qs)
                st.session_state.current_question = (st.session_state.selected_category, new_question)
                st.rerun()
        with colB:
            if st.button("Neue Kategorie"):
                st.session_state.current_question = None
                st.session_state.phase = 'category'
                st.rerun()

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
    stdev = (sum((x - avg) ** 2 for x in votes) / len(votes)) ** 0.5 if len(votes) > 1 else 0.0
    consensus = len(set(votes)) == 1

    st.write("### Ergebnisse")
    for player, vote in st.session_state.votes.items():
        st.write(f"{player}: Stufe {vote} ({delegation_levels[vote]})")
    st.write(f"Durchschnittliche Stufe: **{avg:.2f}**")
    st.write(f"Standardabweichung: **{stdev:.2f}**")
    st.write(f"Konsens erreicht? **{'Ja' if consensus else 'Nein'}**")

    # Visualisierung
    fig, ax = plt.subplots()
    players = list(st.session_state.votes.keys())
    scores = list(st.session_state.votes.values())
    ax.bar(players, scores)
    ax.set_xlabel('Spieler:innen')
    ax.set_ylabel('Gewählte Delegationsstufe')
    ax.set_ylim(0, 8)
    ax.set_title('Delegationsstufen pro Spieler:in')
    plt.xticks(rotation=30, ha='right')
    st.pyplot(fig)

    # Frage als benutzt markieren
    if (category, question) not in st.session_state.question_history:
        st.session_state.question_history.add((category, question))

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

# --- Immer sichtbare Buttons und Reset-Dialog ---
if st.session_state.show_reset_dialog:
    st.warning("Willst du das Spiel wirklich komplett zurücksetzen? Das kann nicht rückgängig gemacht werden.")
    col1, col2 = st.columns(2)
    if col1.button("Ja, alles zurücksetzen"):
        reset_all_states(confirm=True)
    if col2.button("Abbrechen"):
        st.session_state.show_reset_dialog = False
        st.rerun()
else:
    if st.button("Neustart"):
        reset_all_states(confirm=False)

# --- Download Ergebnisse ---
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

# --- Protokoll / Übersicht aller geklärten Delegationspunkte ---
if st.session_state.round_log:
    if 'show_protocol' not in st.session_state:
        st.session_state['show_protocol'] = False

    # Button zum Protokoll ein- und ausblenden
    if not st.session_state['show_protocol']:
        if st.button("Spiel beenden & Protokoll anzeigen"):
            st.session_state['show_protocol'] = True
            st.rerun()
    else:
        st.markdown("## Protokoll aller geklärten Delegationspunkte")
        for i, r in enumerate(st.session_state.round_log, 1):
            st.markdown(f"""
            **{i}. {r['category']}**  
            *{r['question']}*

            - Durchschnittliche Stufe: **{r['average']:.2f}**
            - Standardabweichung: **{r['stdev']:.2f}**
            - Konsens: **{'Ja' if r['consensus'] else 'Nein'}**
            - Stimmen: {", ".join(f"{k}: {v}" for k, v in r['votes'].items())}
            ---
            """)
        if st.button("Protokoll ausblenden"):
            st.session_state['show_protocol'] = False
            st.rerun()

# --- Branding und Footer ---
st.markdown("---")

st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; color: #888; margin-top: 10px;'>
        <b>Powered by Y-SiTE - Lars Bossemeyer
    </div>
    """,
    unsafe_allow_html=True
)