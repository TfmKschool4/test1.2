import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# Configuración de página
# -----------------------------
st.set_page_config(
    page_title="Credit Risk Scoring",
    page_icon="💳",
    layout="wide"
)

# -----------------------------
# Sidebar - Navegación
# -----------------------------
st.sidebar.title("📊 Credit Risk Scoring")

page = st.sidebar.radio(
    "Navegación",
    ["🏢 Sobre Nosotros", "👤 Scoring individual", "👥 Scoring múltiple"]
)

st.sidebar.divider()
st.sidebar.caption("Soluciones inteligentes de decisión financiera")

# -----------------------------
# Función dummy de scoring
# -----------------------------
def dummy_pd_score(data: dict) -> float:
    income = float(data.get("AMT_INCOME_TOTAL", 0) or 0)
    credit = float(data.get("AMT_CREDIT", 0) or 0)
    years_work = float(data.get("YEARS_ACTUAL_WORK", 0) or 0)

    ratio = credit / (income + 1e-6)
    pd_ = 0.15 + 0.10 * min(ratio, 10) - 0.01 * min(years_work, 30)
    return float(np.clip(pd_, 0.01, 0.95))


def pd_to_score(pd, base_score=600, pdo=50):
    odds = (1 - pd) / pd
    factor = pdo / np.log(2)
    offset = base_score - factor * np.log(20)
    return float(offset + factor * np.log(odds))

# -----------------------------
# Página: Sobre Nosotros
# -----------------------------
if page == "🏢 Sobre Nosotros":
    st.title("Sobre Nosotros")

    st.markdown("""
Somos una empresa especializada en **analítica avanzada y soluciones de decisión financiera basadas en datos**. 
Nuestro objetivo es ayudar a entidades financieras y organizaciones a **evaluar el riesgo crediticio de forma precisa, 
transparente y eficiente**, apoyándonos en técnicas modernas de *Machine Learning* y *Data Science*.

Nuestra plataforma de **Credit Scoring** analiza múltiples variables financieras, laborales y demográficas para estimar la 
**probabilidad de impago** de un solicitante y generar recomendaciones objetivas que apoyen la toma de decisiones. 
El sistema está diseñado para integrarse fácilmente en procesos de evaluación existentes, ofreciendo resultados rápidos, 
escalables y consistentes.

Creemos en el uso responsable de la tecnología para impulsar **decisiones financieras más justas, sostenibles y basadas en evidencia**, 
reduciendo la incertidumbre y mejorando la gestión del riesgo.
""")

    st.info("La tecnología al servicio de decisiones financieras más inteligentes y eficientes.")

# -----------------------------
# Página: Scoring individual
# -----------------------------
elif page == "👤 Scoring individual":
    st.title("Formulario del préstamo (1 persona)")

    SK_ID_CURR = st.text_input("ID del solicitante")
    NAME = st.text_input("Nombre del solicitante")

    AGES = st.slider("Edad:", 18, 100, 30)
    AGE_BINS = pd.cut([AGES], bins=[18, 34, 43, 54, 100], labels=[1, 2, 3, 4])[0]

    GENDER = st.selectbox("Género:", ["Masculino", "Femenino"])
    CODE_GENDER = "M" if GENDER == "Masculino" else "F"

    CNT_CHILDREN = st.selectbox("Número de hijos:", [0, 1, 2, 3, "4 o más"])
    CNT_CHILDREN = 4 if CNT_CHILDREN == "4 o más" else CNT_CHILDREN

    NAME_EDUCATION_TYPE = st.selectbox(
        "Nivel de estudios:",
        ["Lower secondary", "Secondary / secondary special", "Incomplete higher", "Higher education", "Academic degree"]
    )

    AMT_INCOME_TOTAL = st.number_input("Ingresos anuales", min_value=0.0, step=100.0)
    AMT_CREDIT = st.number_input("Crédito solicitado", min_value=0.0, step=100.0)
    YEARS_ACTUAL_WORK = st.number_input("Años en el trabajo actual", min_value=0.0, step=0.5)

    st.divider()

    if st.button("Procesar solicitud", use_container_width=True):
        data = {
            "AMT_INCOME_TOTAL": AMT_INCOME_TOTAL,
            "AMT_CREDIT": AMT_CREDIT,
            "YEARS_ACTUAL_WORK": YEARS_ACTUAL_WORK
        }

        pd_score = dummy_pd_score(data)
        score = pd_to_score(pd_score)

        st.subheader("Resultado del análisis")
        c1, c2, c3 = st.columns(3)

        c1.metric("PD", f"{pd_score:.2%}")
        c2.metric("Score", f"{score:.0f}")
        c3.metric("Decisión", "❌ Riesgo alto" if pd_score >= 0.5 else "✅ Riesgo bajo")

        if pd_score < 0.2:
            st.success("Aprobación recomendada")
        elif pd_score < 0.4:
            st.warning("Revisión manual recomendada")
        else:
            st.error("Rechazo recomendado")

# -----------------------------
# Página: Scoring múltiple
# -----------------------------
elif page == "👥 Scoring múltiple":
    st.title("Carga múltiple de solicitudes")

    cols = [
        "SK_ID_CURR", "NAME", "AGE", "AMT_INCOME_TOTAL",
        "AMT_CREDIT", "YEARS_ACTUAL_WORK"
    ]

    n = st.number_input("Número de solicitantes", 2, 200, 5)
    df = pd.DataFrame([{c: None for c in cols} for _ in range(n)])
    edited = st.data_editor(df, use_container_width=True)

    if st.button("Procesar solicitudes", use_container_width=True):
        out = edited.copy()

        out["PD"] = out.apply(
            lambda r: dummy_pd_score(r),
            axis=1
        )
        out["SCORE"] = out["PD"].apply(pd_to_score)
        out["DECISION"] = out["PD"].apply(
            lambda p: "❌ Riesgo alto" if p >= 0.5 else "✅ Riesgo bajo"
        )

        st.subheader("Resultados")
        st.dataframe(out, use_container_width=True)

        st.download_button(
            "Descargar CSV",
            data=out.to_csv(index=False).encode("utf-8"),
            file_name="resultados_scoring.csv",
            mime="text/csv"
        )
