import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Radar de Vida", layout="wide", page_icon="🧭")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .metric-container {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center; border: 1px solid #f0f0f0;
    }
    .metric-label { font-size: 0.9rem; color: #666; margin-bottom: 5px; font-weight: 500;}
    .metric-value { font-size: 1.8rem; font-weight: bold; }
    .color-verde { color: #2E8B57; } .color-azul { color: #56CCF2; }
    .color-rojo { color: #D32F2F; } .color-alerta { color: #D68910; } .color-negro { color: #333333; }
    .progress-wrapper { display: flex; align-items: center; margin-top: 10px; margin-bottom: 20px; font-family: monospace; font-weight: bold; color: #555; }
    .progress-container { width: 100%; background-color: #e0e0e0; border-radius: 25px; margin: 0 10px; height: 20px; overflow: hidden; }
    .progress-bar { height: 100%; background-color: #2E8B57; text-align: right; line-height: 20px; color: white; padding-right: 10px; border-radius: 25px; transition: width 0.5s ease-in-out; }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Calibración")
    
    with st.expander("1. Biografía", expanded=True):
        fecha_nacimiento = st.date_input("Nacimiento", date(1997, 10, 7))
        genero = st.selectbox("Perfil Biológico", ["Hombre", "Mujer"])
        nivel_educativo = st.selectbox("Nivel Educativo", ["Bachillerato", "Licenciatura", "Maestría", "Doctorado"], index=2)
        esperanza_base = 72.3 if genero == "Hombre" else 77.8
        esperanza_vida = st.slider("Esperanza de Vida", 60, 100, int(esperanza_base))

    with st.expander("2. Finanzas (Mensual)", expanded=True):
        ingreso_mensual = st.number_input("Ingreso Neto", value=0, step=1000)
        gastos_mensuales = st.number_input("Gastos Fijos", value=0, step=1000)
        st.markdown("---")
        patrimonio_fisico = st.number_input("Activos Físicos (Casa, Auto)", value=0, step=10000)
        ahorro_liquido = st.number_input("Liquidez (Ahorro/Inversiones)", value=0, step=5000)
        deuda_total = st.number_input("Deuda Total", value=0, step=5000)

    with st.expander("3. Tiempo Semanal (Realista)", expanded=True):
        horas_trabajo = st.slider("Trabajo", 0, 80, 40)
        horas_transporte = st.slider("Transporte", 0, 30, 10)
        horas_bio = st.slider("Mantenimiento (Comer/Aseo/Casa)", 0, 50, 21, help="Horas dedicadas a comer, bañarse, limpiar, cocinar. Promedio: 3h diarias = 21h sem.")

    st.caption("v9.0 - Ultimate Dashboard")

# --- CÁLCULOS ---
hoy = date.today()
edad_anios = (hoy - fecha_nacimiento).days / 365.25
semanas_vividas = int((hoy - fecha_nacimiento).days / 7)
semanas_restantes = int(esperanza_vida * 52) - semanas_vividas
pct_vida = (semanas_vividas / int(esperanza_vida * 52)) * 100

patrimonio_neto = (patrimonio_fisico + ahorro_liquido) - deuda_total
meses_reserva = ahorro_liquido / gastos_mensuales if gastos_mensuales > 0 else 0

# Cálculo Ahorro %
ahorro_mensual = ingreso_mensual - gastos_mensuales
tasa_ahorro = (ahorro_mensual / ingreso_mensual * 100) if ingreso_mensual > 0 else 0

# --- HEADER (MÉTRICAS) ---
st.markdown("## 🧭 Radar de Vida")

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(f'<div class="metric-container"><div class="metric-label">Edad Actual</div><div class="metric-value color-negro">{edad_anios:.1f} años</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-container"><div class="metric-label">Progreso Vital</div><div class="metric-value color-verde">{pct_vida:.1f}%</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="metric-container"><div class="metric-label">Semanas Restantes</div><div class="metric-value color-azul">{semanas_restantes:,}</div></div>', unsafe_allow_html=True)
with c4:
    c_pat = "color-verde" if patrimonio_neto > 0 else "color-rojo"
    st.markdown(f'<div class="metric-container"><div class="metric-label">Patrimonio Neto</div><div class="metric-value {c_pat}">${patrimonio_neto/1000:,.0f}k</div><div style="font-size:0.7rem; color:#888;">Activos - Deuda</div></div>', unsafe_allow_html=True)
with c5:
    if meses_reserva < 3: c_run="color-rojo"; t_run="Alerta"
    elif meses_reserva < 6: c_run="color-alerta"; t_run="Estable"
    else: c_run="color-verde"; t_run="Blindado"
    st.markdown(f'<div class="metric-container"><div class="metric-label">Reserva (Runway)</div><div class="metric-value {c_run}">{meses_reserva:.1f} Meses</div><div style="font-size:0.7rem; color:#666;">{t_run}</div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="progress-wrapper"><span>0 años</span><div class="progress-container"><div class="progress-bar" style="width: {pct_vida}%;"></div></div><span>{int(esperanza_vida)} años</span></div>', unsafe_allow_html=True)

# --- WAFFLE CHART (MAPA DE VIDA) ---
with st.container():
    years = list(range(int(esperanza_vida)))
    weeks = list(range(1, 53))
    z_data, custom_data = [], []
    for y in years:
        row_z, row_c = [], []
        for w in weeks:
            wg = (y * 52) + w
            if wg < semanas_vividas: val, est = 0.6, "Vivido"
            elif wg == semanas_vividas: val, est = 0.9, "HOY"
            else: val, est = 0.1, "Futuro"
            row_z.append(val)
            row_c.append(f"Edad: {y} | Semana: {w}")
        z_data.append(row_z)
        custom_data.append(row_c)
    fig = go.Figure(data=go.Heatmap(z=z_data, x=weeks, y=years, customdata=custom_data, hovertemplate='%{customdata}<extra></extra>', colorscale=[[0.0, '#F4F6F7'], [0.2, '#F4F6F7'], [0.2001, '#E67E22'], [0.8, '#E67E22'], [0.8001, '#F1C40F'], [1.0, '#F1C40F']], showscale=False, xgap=1, ygap=1))
    fig.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0), yaxis=dict(autorange="reversed", showgrid=False, title="Edad"), xaxis=dict(showgrid=False, showticklabels=False))
    st.plotly_chart(fig, use_container_width=True)

# --- ANÁLISIS FINANCIERO (DOS CASCADAS) ---
st.divider()
st.markdown("### 💰 Arquitectura Financiera")
col_fin_1, col_fin_2 = st.columns(2)

with col_fin_1:
    # CASCADA 1: ESTRUCTURA DE RIQUEZA (STOCK)
    fig_w1 = go.Figure(go.Waterfall(
        name = "Wealth", orientation = "v",
        measure = ["relative", "relative", "relative", "total"],
        x = ["Activos Físicos", "Ahorro Líquido", "Deuda (-)", "Patrimonio Neto"],
        text = [f"${patrimonio_fisico/1000:.0f}k", f"${ahorro_liquido/1000:.0f}k", f"-${deuda_total/1000:.0f}k", f"${patrimonio_neto/1000:.0f}k"],
        y = [patrimonio_fisico, ahorro_liquido, -deuda_total, patrimonio_neto],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        decreasing = {"marker":{"color":"#D32F2F"}}, increasing = {"marker":{"color":"#2E8B57"}}, totals = {"marker":{"color":"#1F618D"}}
    ))
    fig_w1.update_layout(title="1. Tu Riqueza (Stock)", showlegend=False, height=350)
    st.plotly_chart(fig_w1, use_container_width=True)

with col_fin_2:
    # CASCADA 2: FLUJO DE EFECTIVO (FLOW)
    fig_w2 = go.Figure(go.Waterfall(
        name = "Flow", orientation = "v",
        measure = ["relative", "relative", "total"],
        x = ["Ingreso Neto", "Gastos Fijos (-)", "Ahorro Mensual"],
        text = [f"${ingreso_mensual/1000:.1f}k", f"-${gastos_mensuales/1000:.1f}k", f"${ahorro_mensual/1000:.1f}k"],
        y = [ingreso_mensual, -gastos_mensuales, ahorro_mensual],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        decreasing = {"marker":{"color":"#D32F2F"}}, increasing = {"marker":{"color":"#2E8B57"}}, totals = {"marker":{"color":"#1F618D"}}
    ))
    fig_w2.update_layout(title="2. Tu Motor de Crecimiento (Flow)", showlegend=False, height=350)
    st.plotly_chart(fig_w2, use_container_width=True)

# --- COMPARATIVA RADAR ---
st.divider()
st.markdown("### 🆚 Tú vs. El Estándar (La Verdad Incómoda)")

# Cálculos Radar
horas_totales = 168 
horas_sueno = 56 
horas_ocupadas = horas_trabajo + horas_transporte + horas_bio
horas_libres_tu = max(0, horas_totales - horas_sueno - horas_ocupadas)

txt_tu = [f"${ingreso_mensual:,.0f}", f"${patrimonio_neto:,.0f}", f"{horas_libres_tu}h/sem (Real)", f"{nivel_educativo}", f"{tasa_ahorro:.1f}%"]
txt_mx = ["~$12,000", "~$200,000", "~31h/sem", "Licenciatura", "~5%"]

s_ing = min((ingreso_mensual / 30000) * 100, 100)
s_pat = min((patrimonio_neto / 1000000) * 100, 100)
s_tim = min((horas_libres_tu / 50) * 100, 100)
s_edu = {"Bachillerato": 40, "Licenciatura": 65, "Maestría": 90, "Doctorado": 100}.get(nivel_educativo, 50)
s_aho = min((tasa_ahorro / 30) * 100, 100)

cat = ['Ingresos', 'Patrimonio', 'Tiempo Libre', 'Educación', '% Ahorro']
fig_r = go.Figure()
fig_r.add_trace(go.Scatterpolar(r=[40, 20, 60, 60, 20], theta=cat, fill='toself', name='Promedio MX', line_color='#BDC3C7', hovertext=txt_mx, hovertemplate="<b>%{theta}</b><br>MX: %{hovertext}<extra></extra>"))
fig_r.add_trace(go.Scatterpolar(r=[s_ing, s_pat, s_tim, s_edu, s_aho], theta=cat, fill='toself', name='Tú', line_color='#2E8B57', hovertext=txt_tu, hovertemplate="<b>%{theta}</b><br>Tú: %{hovertext}<extra></extra>"))
fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=450, margin=dict(t=30, b=20))
st.plotly_chart(fig_r, use_container_width=True)

# --- FUENTES Y METODOLOGÍA (RESTITUIDO) ---
with st.expander("📚 Fuentes de Datos y Metodología (Transparencia)"):
    st.markdown("""
    * **Esperanza de Vida:** Basado en proyecciones CONAPO 2024 para México (Hombres: ~72, Mujeres: ~78). Ajustado por supervivencia infantil.
    * **Ingreso y Patrimonio:** Comparativas basadas en deciles de la **ENIGH (INEGI)** y reportes de riqueza global (Credit Suisse).
    * **Tiempo Laboral:** Basado en promedios **OCDE** para México (2,255 horas anuales, el más alto de la organización).
    * **Eficiencia (Ahorro):** Se considera "Saludable" un ahorro del 20-30% del ingreso neto. El promedio nacional estimado es <5%.
    * **Reserva (Runway):** Cálculo de liquidez estricta: `(Ahorro + Inversión Líquida) / Gastos Mensuales`. No considera activos ilíquidos como casas o autos.
    """)

st.markdown("""<br><div style="text-align: center; color: #808080; font-size: 0.8rem; border-top: 1px solid #eee; padding-top: 20px;">Desarrollado por <strong>Jesus Osmar Gutierrez Fernandez</strong> con Python & Streamlit 🐍</div>""", unsafe_allow_html=True)