import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Delegation Poker", layout="centered")

st.title("Delegation Poker")
st.write(
    "Delegation Poker hilft Teams, Klarheit über Verantwortlichkeiten und Entscheidungsbefugnisse zu gewinnen. "
    "Alle stimmen ab, auf welcher Stufe sie die Delegation sehen."
)

# Beispiel-Fragenpool (kannst du beliebig erweitern)
fragen = [
    "Wer entscheidet über die Urlaubsplanung?",
    "Wer wählt neue Tools für das Team aus?",
    "Wer entscheidet über das Budget?",
    "Wer ist für die Zielvereinbarungen verantwortlich?",
]

if 'runde' not in st.session_state:
    st.session_state.runde = 0
if 'abstimmungen' not in st.session_state:
    st.session_state.abstimmungen = []

# Auswahl der aktuellen Frage
frage = fragen[st.session_state.runde % len(fragen)]
st.markdown(f"### Frage: {frage}")

# Eingabe der Teilnehmenden & Entscheidung
with st.form("abstimmung_form", clear_on_submit=True):
    name = st.text_input("Name")
    entscheidung = st.selectbox(
        "Wie möchtest du entscheiden?",
        options=[
            "1 – Ich entscheide allein",
            "2 – Ich entscheide mit Beratung",
            "3 – Wir entscheiden gemeinsam",
            "4 – Du entscheidest mit Beratung",
            "5 – Du entscheidest allein"
        ]
    )
    abgeschickt = st.form_submit_button("Abstimmen")

if abgeschickt and name:
    st.session_state.abstimmungen.append({
        "Name": name.strip(),
        "Entscheidung": entscheidung,
        "Frage": frage
    })

# Ergebnisse filtern: Nur die Abstimmungen zur aktuellen Frage
aktuelle_abstimmungen = [
    ab for ab in st.session_state.abstimmungen if ab["Frage"] == frage
]
if aktuelle_abstimmungen:
    st.markdown("## Ergebnisse")
    df = pd.DataFrame(aktuelle_abstimmungen)
    # Nur Name und Entscheidung anzeigen
    st.table(df[["Name", "Entscheidung"]])

    # Plotly: Entscheidung in limonengrün
    fig = px.bar(
        df,
        x="Name",
        y="Entscheidung",
        color_discrete_sequence=["#B7E778"],  # Limonengrün (Hexcode, kannst du weiter anpassen)
    )
    fig.update_traces(marker_line_width=1.5, marker_line_color="black")
    fig.update_layout(
        yaxis_title="Entscheidung",
        xaxis_title="Name",
        showlegend=False,
        plot_bgcolor="#f7f7fa"
    )
    st.plotly_chart(fig, use_container_width=True)

# Protokoll (nur für aktuelle Frage, kompakt)
st.markdown("---")
st.markdown("### Protokoll")
st.markdown(f"**Frage:** {frage}")
if aktuelle_abstimmungen:
    st.table(df[["Name", "Entscheidung"]].reset_index(drop=True))
else:
    st.info("Noch keine Abstimmungen für diese Frage eingetragen.")

# Navigation: Nächste Frage (falls gewünscht)
if st.button("Nächste Frage"):
    st.session_state.runde += 1