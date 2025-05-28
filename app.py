import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

# --- Custom Button Styles & Logo-Zentrierung via CSS ---
st.markdown("""
<style>
/* Standard-Button: grün auf Hover und Aktiv */
div.stButton > button:not(.neu-start-btn):hover,
div.stButton > button:not(.neu-start-btn):focus,
div.stButton > button:not(.neu-start-btn):active {
    background-color: #1ec94c !important;
    color: white !important;
    border-color: #1ec94c !important;
}
/* Neu-Start-Button: rot auch auf Hover/Aktiv */
.neu-start-btn {
    background-color: #fa5252 !important;
    color: white !important;
    border-color: #fa5252 !important;
}
.neu-start-btn:hover,
.neu-start-btn:focus,
.neu-start-btn:active {
    background-color: #c92a2a !important;
    border-color: #c92a2a !important;
    color: white !important;
}
/* Logo zentrieren */
.logo-center {
    display: flex;
    justify-content: center;
    margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# --- Logo zentriert und groß ---
logo_path = "Y-SiTE Logo.png"
st.markdown('<div class="logo-center">', unsafe_allow_html=True)
try:
    st.image(logo_path, use_container_width=True)
except Exception:
    st.warning("Logo nicht gefunden. Bitte Datei 'Y-SiTE Logo.png' im Script-Ordner ablegen.")
st.markdown('</div>', unsafe_allow_html=True)

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
    1: "1. Verkünden   - Ich entscheide allein",
    2: "2. Verkaufen   - Ich entscheide und erkläre dir meine Gründe",
    3: "3. Befragen    - Ich entscheide, hole mir vorher aber deine Meinung ein",
    4: "4. Einigen     - Wir entscheiden gemeinsam",
    5: "5. Beraten     - Du entscheidest, nachdem du meinen Rat gehört hast",
    6: "6. Erkundigen  - Du entscheidest, informierst mich aber",
    7: "7. Delegieren  - Du entscheidest komplett eigenständig"
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

# --- Neu-Start-Button (ganz rechts, aber NICHT auf der Startseite) ---
if st.session_state.phase != 'setup':
    cols = st.columns([8, 1])  # Button ganz rechts oben
    with cols[1]:
        # Der "Neu-Start"-Button bekommt die eigene CSS-Klasse über unsafe_allow_html (per JS nachträglich)
        st.markdown("""
        <script>
        Array.from(document.querySelectorAll('button')).forEach(btn => {
            if (btn.innerText.trim() === "Neu-Start") {
                btn.classList.add('neu-start-btn');
            }
        });
        </script>
        """, unsafe_allow_html=True)
        if st.button("Neu-Start", key="neu_start_button"):
            reset_all_states(confirm=False)

# --- Reset-Dialog (bleibt überall erreichbar, wenn nötig) ---
if st.session_state.show_reset_dialog:
    st.warning("Willst du das Spiel wirklich komplett zurücksetzen? Das kann nicht rückgängig gemacht werden.")
    col1, col2 = st.columns([1, 1])
    if col1.button("Ja, alles zurücksetzen"):
        reset_all_states(confirm=True)
    if col2.button("Abbrechen"):
        st.session_state.show_reset_dialog = False
        st.rerun()

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
          1. **Verkünden**  - Ich entscheide allein  
          2. **Verkaufen**  - Ich entscheide und erkläre dir meine Gründe  
          3. **Befragen**.  - Ich entscheide, hole mir vorher aber deine Meinung ein  
          4. **Einigen**.   - Wir entscheiden gemeinsam  
          5. **Beraten**    - Du entscheidest, nachdem du meinen Rat gehört hast  
          6. **Erkundigen** - Du entscheidest, informierst mich aber  
          7. **Delegieren** - Du entscheidest komplett eigenständig


        - In jeder Runde wird eine Frage gestellt, z.B.:  
        „Wer entscheidet, ob neue Softwaretools angeschafft werden?“

        - Alle Spieler:innen wählen verdeckt ihre Einschätzung (Stufe 1–7) und schreiben sie in den Chat von Teams.

        - Wenn alle ihre Einschätzung vorgenommen haben, werden die Einträge im Chat gesendet angezeigt und gemeinsam besprochen.

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

    st.write("### Ergebnisse")
    for player, vote in st.session_state.votes.items():
        st.write(f"{player}: {vote} ({delegation_levels[vote]})")

    # Visualisierung bleibt optional
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
        'votes': st.session_state.votes.copy()
    })

    if st.button("Frage wiederholen"):
        st.session_state.votes = {}
        st.session_state.phase = 'voting'
        st.rerun()

    if st.button("Nächste Runde"):
        st.session_state.current_question = None
        st.session_state.votes = {}
        if category == "Eigene Frage":
            st.session_state.phase = 'category'
        else:
            st.session_state.phase = 'voting'
        st.rerun()

# --- Download Ergebnisse (finale Version pro Frage) ---
if st.session_state.round_log:
    final_questions = {}
    for r in st.session_state.round_log:
        key = (r['category'], r['question'])
        final_questions[key] = r  # Immer der letzte Stand überschreibt vorherige

    df = pd.DataFrame([
        {
            'Kategorie': r['category'],
            'Frage': r['question'],
            'Votes': ", ".join(f"{k}: {v} ({delegation_levels[v]})" for k, v in r['votes'].items())
        }
        for r in final_questions.values()
    ])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Ergebnisse (CSV)", data=csv, file_name='delegation_poker_results.csv', mime='text/csv')

# --- Protokoll / Übersicht aller geklärten Delegationspunkte (ohne Dopplungen, nur letzter Stand) ---
if st.session_state.round_log:
    final_questions = {}
    for r in st.session_state.round_log:
        key = (r['category'], r['question'])
        final_questions[key] = r  # Immer der letzte Stand überschreibt vorherige

    if 'show_protocol' not in st.session_state:
        st.session_state['show_protocol'] = False

    if not st.session_state['show_protocol']:
        if st.button("Spiel beenden & Protokoll anzeigen"):
            st.session_state['show_protocol'] = True
            st.rerun()
    else:
        st.markdown("## Protokoll aller geklärten Delegationspunkte (finale Version pro Frage)")
        for i, ((category, question), r) in enumerate(final_questions.items(), 1):
            st.markdown(f"""
            **{i}. {category}**  
            *{question}*

            - Stimmen:
            """)
            for player, vote in r['votes'].items():
                st.markdown(
                    f"  - {player}: {vote} ({delegation_levels[vote]})"
                )
            st.markdown("---")
        if st.button("Protokoll ausblenden"):
            st.session_state['show_protocol'] = False
            st.rerun()

# --- Branding und Footer ---
st.markdown("---")

st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; color: #888; margin-top: 10px;'>
        <b>Powered very relaxed with wine & ChatGpt 4.1 Vibe-Coding - Y-SiTE - Lars Bossemeyer
    </div>
    """,
    unsafe_allow_html=True
)