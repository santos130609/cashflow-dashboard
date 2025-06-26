
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Análisis de Flujo de Caja", layout="wide")
st.title("📊 Análisis Interactivo de Flujo de Caja")

uploaded_file = st.file_uploader("📥 Sube aquí tu CSV de movimientos bancarios", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';', on_bad_lines='skip')
        df.columns = ['Fecha_Proceso', 'Fecha_Valor', 'Codigo', 'Concepto', 'Observaciones', 'Oficina', 'Importe', 'Saldo', 'Remesa']
        df['Fecha_Valor'] = pd.to_datetime(df['Fecha_Valor'], dayfirst=True, errors='coerce')
        df['Importe'] = pd.to_numeric(df['Importe'], errors='coerce')
        df.dropna(subset=['Fecha_Valor', 'Importe'], inplace=True)

        # Cálculos
        df['Tipo'] = df['Importe'].apply(lambda x: 'Ingreso' if x > 0 else 'Gasto')
        df['Mes'] = df['Fecha_Valor'].dt.to_period('M')
        resumen = df.groupby(['Mes', 'Tipo'])['Importe'].sum().unstack(fill_value=0)
        resumen['Flujo_Neto'] = resumen.get('Ingreso', 0) + resumen.get('Gasto', 0)
        resumen.index = resumen.index.to_timestamp()

        # KPIs
        ingreso_total = df[df['Importe'] > 0]['Importe'].sum()
        gasto_total = df[df['Importe'] < 0]['Importe'].sum()
        flujo_neto = ingreso_total + gasto_total
        transacciones = df.shape[0]
        ingreso_medio_diario = df.groupby(df['Fecha_Valor'].dt.date)['Importe'].sum().mean()
        ticket_medio = df[df['Importe'] > 0]['Importe'].mean()
        mes_max_ingreso = resumen['Ingreso'].idxmax().strftime('%B %Y')
        mes_max_gasto = resumen['Gasto'].idxmin().strftime('%B %Y')

        st.markdown("### 🧮 KPIs Generales")
        col1, col2, col3 = st.columns(3)
        col1.metric("Ingreso Total", f"{ingreso_total:,.2f} €")
        col2.metric("Gasto Total", f"{gasto_total:,.2f} €")
        col3.metric("Flujo Neto", f"{flujo_neto:,.2f} €")

        col4, col5, col6 = st.columns(3)
        col4.metric("Ticket Medio", f"{ticket_medio:,.2f} €")
        col5.metric("Ingreso Medio Diario", f"{ingreso_medio_diario:,.2f} €")
        col6.metric("Transacciones", f"{transacciones}")

        col7, col8 = st.columns(2)
        col7.markdown(f"📈 **Mes con más ingresos:** {mes_max_ingreso}")
        col8.markdown(f"📉 **Mes con más gastos:** {mes_max_gasto}")

        st.markdown("### 📆 Análisis Mensual de Flujo de Caja")
        fig, ax = plt.subplots(figsize=(12, 5))
        resumen[['Ingreso', 'Gasto']].plot(kind='bar', stacked=False, ax=ax)
        ax.plot(resumen.index, resumen['Flujo_Neto'], color='purple', marker='o', label='Flujo Neto')
        ax.set_ylabel("€")
        ax.set_title("Ingresos, Gastos y Flujo Neto por Mes")
        ax.legend()
        st.pyplot(fig)

        with st.expander("📋 Ver datos detallados"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar el análisis.")
