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

# Session State initialisieren
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

# --- Einleitung ---
if not st.session_state.intro_shown:
    st.title("Delegation Poker (Admin gesteuert)")

    st.markdown("""
    ## 🃏 Delegation Poker – Was ist das?
    Delegation Poker ist ein spielerisches Tool, mit dem Teams klären, **wie viel Entscheidungsfreiheit** einzelne Teammitglieder:innen bei bestimmten Themen haben.
    Ziel ist es, Transparenz zu schaffen: Wer entscheidet was? Und auf welcher Delegationsebene?

    ### 🔑 Wie funktioniert es?
    - Es gibt **7 Delegationsebenen**:
      1️⃣ Ich entscheide allein.  
      2️⃣ Ich entscheide und erkläre dir meine Gründe.  
      3️⃣ Ich entscheide, hole mir vorher aber deine Meinung ein.  
      4️⃣ Wir entscheiden gemeinsam.  
      5️⃣ Du entscheidest, nachdem du meinen Rat gehört hast.  
      6️⃣ Du entscheidest, informierst mich aber.  
      7️⃣ Du entscheidest komplett eigenständig.

    - In jeder Runde wird eine Frage gestellt, z. B.:  
    **„Wer entscheidet, ob neue Softwaretools angeschafft werden?“**

    - Alle Spieler:innen wählen **verdeckt** ihre Einschätzung (Stufe 1–7).

    - Danach werden die Ergebnisse sichtbar gemacht und gemeinsam besprochen.

    ### 🎯 Ziel
    Am Ende habt ihr ein besseres Verständnis davon, wie Verantwortung und Entscheidungen im Team verteilt sind – und wo ihr vielleicht etwas anpassen wollt.
    """)

    if st.button("Loslegen"):
        st.session_state.intro_shown = True
        st.experimental_rerun()

# --- Spieler:innen-Login + Admin-Definition ---
elif not st.session_state.players:
    st.header("Spieler:innen anmelden")
    name = st.text_input("Name eingeben:")
    if st.button("Hinzufügen"):
        if name and name not in st.session_state.players:
            st.session_state.players.append(name)
            if not st.session_state.admin:
                st.session_state.admin = name  # Erste Person = Admin
    st.write("Angemeldete Spieler:innen:", ", ".join(st.session_state.players))
    if st.session_state.admin:
        st.write(f"**Admin:** {st.session_state.admin}")
    if st.button("Starten", disabled=(len(st.session_state.players) < 1)):
        st.experimental_rerun()

# --- Spielrunde ---
else:
    st.sidebar.write(f"**Admin:** {st.session_state.admin}")
    is_admin = st.sidebar.text_input("Admin-Check (Name eingeben):") == st.session_state.admin

    if not st.session_state.current_question and is_admin:
        category = random.choice(list(delegation_questions.keys()))
        question = random.choice(delegation_questions[category])
        st.session_state.current_question = (category, question)
        st.session_state.votes = {}

    if st.session_state.current_question:
        category, question = st.session_state.current_question
        st.subheader(f"Kategorie: {category}")
        st.write(f"**Frage:** {question}")

        for player in st.session_state.players:
            if player not in st.session_state.votes:
                vote = st.selectbox(f"{player}, wähle deine Stufe (1–7):", list(range(1, 8)), key=f"vote_{player}")
                if st.button(f"Bestätigen ({player})", key=f"confirm_{player}"):
                    st.session_state.votes[player] = vote
                    st.experimental_rerun()

        if len(st.session_state.votes) == len(st.session_state.players) and is_admin:
            st.success("Alle Stimmen abgegeben! Ergebnisse freigeben?")
            if st.button("Aufdecken (Admin)"):
                votes = list(st.session_state.votes.values())
                avg = sum(votes) / len(votes)
                stdev = (sum((x - avg) ** 2 for x in votes) / len(votes)) ** 0.5
                consensus = len(set(votes)) == 1

                st.write("### Ergebnisse")
                for player, vote in st.session_state.votes.items():
                    st.write(f"{player}: Stufe {vote}")
                st.write(f"Durchschnittliche Stufe: **{avg:.2f}**")
                st.write(f"Standardabweichung: **{stdev:.2f}**")
                st.write(f"Konsens erreicht? **{'Ja' if consensus else 'Nein'}**")

                # Diagramm
                fig, ax = plt.subplots()
                counts = pd.Series(votes).value_counts().sort_index()
                ax.bar(counts.index, counts.values)
                ax.set_xlabel('Delegationsstufe')
                ax.set_ylabel('Anzahl Stimmen')
                st.pyplot(fig)

                # Log speichern
                st.session_state.round_log.append({
                    'category': category,
                    'question': question,
                    'votes': st.session_state.votes.copy(),
                    'average': avg,
                    'stdev': stdev,
                    'consensus': consensus
                })

                if st.button("Nächste Runde"):
                    st.session_state.current_question = None
                    st.session_state.votes = {}
                    st.experimental_rerun()

                if st.button("Neustart"):
                    st.session_state.players = []
                    st.session_state.admin = None
                    st.session_state.current_question = None
                    st.session_state.votes = {}
                    st.session_state.round_log = []
                    st.session_state.intro_shown = False
                    st.experimental_rerun()

# --- Export-Button ---
if st.session_state.round_log and is_admin:
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