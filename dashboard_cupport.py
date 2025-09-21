import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import random
from plotly.subplots import make_subplots

# Configuración de la página para tablet
st.set_page_config(
    page_title="Sistema Integral de Gestión - SecureFleet Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para diseño moderno y futurista
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .alert-critical {
        background: rgba(255, 59, 48, 0.2);
        border-left: 4px solid #FF3B30;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .alert-warning {
        background: rgba(255, 204, 0, 0.2);
        border-left: 4px solid #FFCC00;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .alert-info {
        background: rgba(0, 122, 255, 0.2);
        border-left: 4px solid #007AFF;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Función para generar datos simulados
@st.cache_data
def generate_mock_data():
    np.random.seed(42)
    
    # Datos de flota
    vehicles = pd.DataFrame({
        'vehicle_id': [f'VH-{i:03d}' for i in range(1, 16)],
        'tipo': np.random.choice(['Blindado A', 'Blindado B', 'Camioneta'], 15),
        'estado': np.random.choice(['Activo', 'En Ruta', 'Mantenimiento', 'Disponible'], 15, p=[0.4, 0.3, 0.1, 0.2]),
        'km_dia': np.random.uniform(150, 350, 15),
        'consumo_litros': np.random.uniform(20, 60, 15),
        'eficiencia': np.random.uniform(0.75, 0.95, 15),
        'ultima_parada': [datetime.now() - timedelta(minutes=np.random.randint(5, 120)) for _ in range(15)],
        'lat': np.random.uniform(-12.08, -11.95, 15),
        'lon': np.random.uniform(-77.08, -76.95, 15),
        'ruta_cumplimiento': np.random.uniform(0.80, 1.0, 15)
    })
    
    # Datos de supervisores
    supervisores = pd.DataFrame({
        'supervisor_id': [f'SUP-{i:03d}' for i in range(1, 11)],
        'nombre': [f'Supervisor {i}' for i in range(1, 11)],
        'clientes_asignados': np.random.randint(5, 15, 10),
        'visitas_completadas': np.random.randint(3, 12, 10),
        'cumplimiento': np.random.uniform(0.70, 1.0, 10),
        'riesgo_score': np.random.uniform(0, 30, 10)
    })
    
    # Datos de RRHH
    guardias = pd.DataFrame({
        'guardia_id': [f'GRD-{i:04d}' for i in range(1, 51)],
        'nombre': [f'Guardia {i}' for i in range(1, 51)],
        'turno': np.random.choice(['Mañana', 'Tarde', 'Noche'], 50),
        'asistencia_real': np.random.choice(['Presente', 'Ausente', 'Tardanza'], 50, p=[0.8, 0.1, 0.1]),
        'horas_extra': np.random.randint(0, 20, 50),
        'salario_base': np.random.uniform(1500, 3000, 50),
        'alertas_nomina': np.random.choice(['Sin alertas', 'Pago duplicado', 'Inconsistencia'], 50, p=[0.8, 0.1, 0.1])
    })
    
    # Histórico para gráficos de tendencia
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    historico = pd.DataFrame({
        'fecha': dates,
        'km_total': np.cumsum(np.random.uniform(3000, 5000, 30)),
        'consumo_total': np.cumsum(np.random.uniform(400, 800, 30)),
        'incidentes': np.random.poisson(2, 30),
        'eficiencia_promedio': np.random.uniform(0.75, 0.95, 30)
    })
    
    # Alertas en tiempo real
    alertas = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(minutes=i*5) for i in range(20)],
        'tipo': np.random.choice(['Crítica', 'Advertencia', 'Información'], 20, p=[0.2, 0.4, 0.4]),
        'categoria': np.random.choice(['Flota', 'Supervisión', 'RRHH', 'Seguridad'], 20),
        'mensaje': [
            'Exceso de consumo detectado en VH-005',
            'Parada no autorizada - VH-008',
            'Supervisor SUP-003 no cumplió visitas',
            'Alerta de nómina: pago duplicado GRD-0015',
            'Mantenimiento urgente requerido VH-012',
            'Ruta optimizada disponible para VH-007',
            'Ausentismo superior al 15% en turno noche',
            'Cliente prioritario sin supervisión',
            'Vehículo VH-003 fuera de ruta',
            'Reemplazo necesario para GRD-0032',
            'KPI de eficiencia bajo umbral crítico',
            'Nuevo incidente reportado - Zona Norte',
            'Actualización de seguridad disponible',
            'Supervisor SUP-007 excede meta',
            'Combustible bajo en VH-011',
            'Alerta de velocidad VH-009',
            'Cambio de turno sin cobertura',
            'Cliente VIP solicita supervisión',
            'Mantenimiento preventivo programado',
            'Sistema de rastreo actualizado'
        ][:20]
    })
    
    return vehicles, supervisores, guardias, historico, alertas

# Cargar datos
vehicles, supervisores, guardias, historico, alertas = generate_mock_data()

# Header principal
st.markdown("<h1 style='text-align: center; color: #ffffff; font-size: 2.5em; margin-bottom: 30px;'>🛡️ SecureFleet Pro - Centro de Control Integral</h1>", unsafe_allow_html=True)

# Panel de alertas en tiempo real (parte superior)
with st.container():
    st.markdown("<h2>🚨 Centro de Alertas en Tiempo Real</h2>", unsafe_allow_html=True)
    
    alert_cols = st.columns([1, 3])
    with alert_cols[0]:
        criticas = alertas[alertas['tipo'] == 'Crítica'].shape[0]
        advertencias = alertas[alertas['tipo'] == 'Advertencia'].shape[0]
        info = alertas[alertas['tipo'] == 'Información'].shape[0]
        
        fig_alerts = go.Figure(data=[
            go.Bar(x=['Críticas', 'Advertencias', 'Info'], 
                   y=[criticas, advertencias, info],
                   marker_color=['#FF3B30', '#FFCC00', '#007AFF'])
        ])
        fig_alerts.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_alerts, use_container_width=True)
    
    with alert_cols[1]:
        alert_container = st.container()
        with alert_container:
            for _, alert in alertas.head(5).iterrows():
                alert_class = {
                    'Crítica': 'alert-critical',
                    'Advertencia': 'alert-warning',
                    'Información': 'alert-info'
                }[alert['tipo']]
                
                st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>{alert['tipo']} - {alert['categoria']}</strong><br>
                        {alert['mensaje']}<br>
                        <small>{alert['timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                """, unsafe_allow_html=True)

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📊 Tablero Flota", "👥 Supervisión", "💼 RRHH", "🎯 Panel de Decisiones"])

# TAB 1: TABLERO FLOTA
with tab1:
    st.markdown("<h2>🚗 Control de Flota en Tiempo Real</h2>", unsafe_allow_html=True)
    
    # Filtros
    col_filters = st.columns(4)
    with col_filters[0]:
        vehicle_filter = st.selectbox("Filtrar Vehículo", ['Todos'] + vehicles['vehicle_id'].tolist())
    with col_filters[1]:
        estado_filter = st.selectbox("Estado", ['Todos'] + vehicles['estado'].unique().tolist())
    
    # KPIs principales
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        total_km = vehicles['km_dia'].sum()
        st.metric("KM Recorridos Hoy", f"{total_km:,.0f}", "+12.3%")
    with kpi_cols[1]:
        eficiencia_avg = vehicles['eficiencia'].mean()
        st.metric("Eficiencia Promedio", f"{eficiencia_avg:.1%}", "-2.1%")
    with kpi_cols[2]:
        consumo_total = vehicles['consumo_litros'].sum()
        st.metric("Consumo Total (L)", f"{consumo_total:,.0f}", "+5.7%")
    with kpi_cols[3]:
        cumplimiento = vehicles['ruta_cumplimiento'].mean()
        st.metric("Cumplimiento Rutas", f"{cumplimiento:.1%}", "+3.2%")
    
    # Mapa y gráficos
    map_col, charts_col = st.columns([1, 1])
    
    with map_col:
        st.markdown("### 🗺️ Mapa de Flota en Tiempo Real")
        
        # Crear mapa con Folium
        m = folium.Map(location=[-12.0464, -77.0428], zoom_start=11)
        
        for _, vehicle in vehicles.iterrows():
            color = 'green' if vehicle['estado'] == 'Activo' else 'orange' if vehicle['estado'] == 'En Ruta' else 'red'
            folium.CircleMarker(
                [vehicle['lat'], vehicle['lon']],
                radius=8,
                popup=f"{vehicle['vehicle_id']} - {vehicle['estado']}",
                color=color,
                fill=True,
                fillColor=color
            ).add_to(m)
        
        folium_static(m, height=400)
    
    with charts_col:
        # Gráfico de eficiencia por vehículo
        st.markdown("### 📈 Análisis de Rendimiento")
        
        fig_efficiency = px.bar(
            vehicles.head(10),
            x='vehicle_id',
            y='eficiencia',
            color='eficiencia',
            color_continuous_scale='RdYlGn',
            title="Eficiencia por Vehículo"
        )
        fig_efficiency.update_layout(
            height=200,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # Tendencia histórica
        fig_trend = px.line(
            historico,
            x='fecha',
            y='eficiencia_promedio',
            title="Tendencia de Eficiencia (30 días)"
        )
        fig_trend.update_layout(
            height=200,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Tabla de vehículos con alertas
    st.markdown("### ⚠️ Vehículos con Alertas Activas")
    
    vehicles_alert = vehicles[vehicles['eficiencia'] < 0.85].copy()
    vehicles_alert['alerta'] = vehicles_alert['eficiencia'].apply(
        lambda x: '🔴 Crítico' if x < 0.8 else '🟡 Advertencia'
    )
    
    if not vehicles_alert.empty:
        st.dataframe(
            vehicles_alert[['vehicle_id', 'tipo', 'estado', 'eficiencia', 'alerta']],
            use_container_width=True,
            hide_index=True
        )

# TAB 2: SUPERVISIÓN
with tab2:
    st.markdown("<h2>👥 Panel de Supervisión</h2>", unsafe_allow_html=True)
    
    # KPIs de supervisión
    sup_kpi_cols = st.columns(4)
    with sup_kpi_cols[0]:
        total_visitas = supervisores['visitas_completadas'].sum()
        st.metric("Visitas Completadas", total_visitas, "+8")
    with sup_kpi_cols[1]:
        cumplimiento_sup = supervisores['cumplimiento'].mean()
        st.metric("Cumplimiento Global", f"{cumplimiento_sup:.1%}", "+5.2%")
    with sup_kpi_cols[2]:
        clientes_total = supervisores['clientes_asignados'].sum()
        st.metric("Clientes Activos", clientes_total, "+3")
    with sup_kpi_cols[3]:
        riesgo_promedio = supervisores['riesgo_score'].mean()
        st.metric("Score de Riesgo", f"{riesgo_promedio:.1f}", "-2.3")
    
    # Visualizaciones de supervisión
    sup_cols = st.columns(2)
    
    with sup_cols[0]:
        # Mapa de calor de cumplimiento
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=supervisores['cumplimiento'].values.reshape(2, 5),
            x=[f'Zona {i}' for i in range(1, 6)],
            y=['Turno AM', 'Turno PM'],
            colorscale='RdYlGn',
            text=supervisores['cumplimiento'].values.reshape(2, 5),
            texttemplate='%{text:.0%}',
            textfont={"size": 12},
        ))
        fig_heatmap.update_layout(
            title="Mapa de Calor - Cumplimiento por Zona",
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with sup_cols[1]:
        # Gráfico de radar para supervisores top
        categories = ['Visitas', 'Cumplimiento', 'Clientes', 'Eficiencia', 'Puntualidad']
        
        fig_radar = go.Figure()
        
        for i in range(3):
            supervisor = supervisores.iloc[i]
            values = [
                supervisor['visitas_completadas'] / 15 * 100,
                supervisor['cumplimiento'] * 100,
                supervisor['clientes_asignados'] / 15 * 100,
                np.random.uniform(70, 95),
                np.random.uniform(80, 100)
            ]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=supervisor['nombre']
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Desempeño Top 3 Supervisores",
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Tabla de supervisores con métricas
    st.markdown("### 📊 Detalle de Supervisores")
    supervisores_display = supervisores.copy()
    supervisores_display['estado'] = supervisores_display['cumplimiento'].apply(
        lambda x: '✅ Óptimo' if x > 0.9 else '⚠️ Revisar' if x > 0.75 else '❌ Crítico'
    )
    st.dataframe(
        supervisores_display[['supervisor_id', 'nombre', 'clientes_asignados', 'visitas_completadas', 'cumplimiento', 'estado']],
        use_container_width=True,
        hide_index=True
    )

# TAB 3: RRHH
with tab3:
    st.markdown("<h2>💼 Gestión de Recursos Humanos</h2>", unsafe_allow_html=True)
    
    # KPIs de RRHH
    rrhh_kpi_cols = st.columns(4)
    with rrhh_kpi_cols[0]:
        asistencia = (guardias['asistencia_real'] == 'Presente').sum() / len(guardias)
        st.metric("Asistencia", f"{asistencia:.1%}", "-3.2%")
    with rrhh_kpi_cols[1]:
        horas_extra_total = guardias['horas_extra'].sum()
        st.metric("Horas Extra", f"{horas_extra_total:,}", "+127")
    with rrhh_kpi_cols[2]:
        alertas_nomina = (guardias['alertas_nomina'] != 'Sin alertas').sum()
        st.metric("Alertas Nómina", alertas_nomina, "+2")
    with rrhh_kpi_cols[3]:
        cobertura = 0.92
        st.metric("Cobertura Personal", f"{cobertura:.1%}", "-1.5%")
    
    rrhh_cols = st.columns(2)
    
    with rrhh_cols[0]:
        # Distribución de asistencia
        fig_asistencia = px.pie(
            guardias['asistencia_real'].value_counts().reset_index(),
            values='count',
            names='asistencia_real',
            title="Distribución de Asistencia",
            color_discrete_map={
                'Presente': '#00C851',
                'Ausente': '#ff4444',
                'Tardanza': '#ffbb33'
            }
        )
        fig_asistencia.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_asistencia, use_container_width=True)
    
    with rrhh_cols[1]:
        # Predicción de ausentismo
        dates_future = pd.date_range(start=datetime.now(), periods=7, freq='D')
        ausentismo_pred = pd.DataFrame({
            'fecha': dates_future,
            'prediccion': np.random.uniform(0.08, 0.20, 7),
            'historico': np.random.uniform(0.10, 0.15, 7)
        })
        
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(
            x=ausentismo_pred['fecha'],
            y=ausentismo_pred['prediccion'],
            mode='lines+markers',
            name='Predicción',
            line=dict(color='#FF6B6B', width=3)
        ))
        fig_pred.add_trace(go.Scatter(
            x=ausentismo_pred['fecha'],
            y=ausentismo_pred['historico'],
            mode='lines',
            name='Promedio Histórico',
            line=dict(color='#4ECDC4', dash='dash')
        ))
        fig_pred.update_layout(
            title="Predicción de Ausentismo (7 días)",
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            font=dict(color='white'),
            yaxis=dict(tickformat='.0%')
        )
        st.plotly_chart(fig_pred, use_container_width=True)
    
    # Análisis de nómina
    st.markdown("### 💰 Análisis de Nómina y Alertas")
    
    nomina_cols = st.columns(3)
    with nomina_cols[0]:
        nomina_total = guardias['salario_base'].sum()
        st.info(f"**Nómina Total:** ${nomina_total:,.0f}")
    with nomina_cols[1]:
        pagos_duplicados = (guardias['alertas_nomina'] == 'Pago duplicado').sum()
        st.warning(f"**Pagos Duplicados:** {pagos_duplicados}")
    with nomina_cols[2]:
        inconsistencias = (guardias['alertas_nomina'] == 'Inconsistencia').sum()
        st.error(f"**Inconsistencias:** {inconsistencias}")
    
    # Tabla de guardias con alertas
    guardias_alerta = guardias[guardias['alertas_nomina'] != 'Sin alertas']
    if not guardias_alerta.empty:
        st.markdown("#### ⚠️ Personal con Alertas Activas")
        st.dataframe(
            guardias_alerta[['guardia_id', 'nombre', 'turno', 'asistencia_real', 'alertas_nomina']],
            use_container_width=True,
            hide_index=True
        )

# TAB 4: PANEL DE DECISIONES
with tab4:
    st.markdown("<h2>🎯 Panel de Decisiones Ejecutivas</h2>", unsafe_allow_html=True)
    
    # Resumen ejecutivo
    st.markdown("### 📈 Resumen Ejecutivo")
    
    exec_cols = st.columns(3)
    
    with exec_cols[0]:
        st.markdown("""
        <div class="metric-card">
            <h4>🚗 Flota</h4>
            <ul>
                <li>3 vehículos requieren mantenimiento urgente</li>
                <li>Eficiencia 8% por debajo del objetivo</li>
                <li>Oportunidad: Optimizar rutas zona norte</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with exec_cols[1]:
        st.markdown("""
        <div class="metric-card">
            <h4>👥 Supervisión</h4>
            <ul>
                <li>2 clientes prioritarios sin cobertura</li>
                <li>Supervisor SUP-003 bajo rendimiento crítico</li>
                <li>Acción: Reasignar clientes VIP</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with exec_cols[2]:
        st.markdown("""
        <div class="metric-card">
            <h4>💼 RRHH</h4>
            <ul>
                <li>Ausentismo proyectado 18% próxima semana</li>
                <li>5 alertas de nómina pendientes</li>
                <li>Recomendación: Activar plan de contingencia</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Matriz de decisiones
    st.markdown("### 🎮 Matriz de Decisiones Críticas")
    
    decisiones = pd.DataFrame({
        'Área': ['Flota', 'Supervisión', 'RRHH', 'Seguridad'],
        'Impacto': [85, 72, 68, 91],
        'Urgencia': [78, 85, 62, 95],
        'Riesgo': [65, 58, 45, 88],
        'Acción Recomendada': [
            'Mantenimiento preventivo inmediato VH-005, VH-008',
            'Reasignar supervisor a cliente prioritario',
            'Activar personal de respaldo turno noche',
            'Actualización de protocolos de seguridad'
        ]
    })
    
    fig_bubble = px.scatter(
        decisiones,
        x='Urgencia',
        y='Impacto',
        size='Riesgo',
        color='Área',
        hover_data=['Acción Recomendada'],
        title="Matriz Impacto vs Urgencia",
        size_max=60
    )
    fig_bubble.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.1)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Proyecciones y tendencias
    st.markdown("### 📊 Proyecciones y Tendencias Clave")
    
    proj_cols = st.columns(2)
    
    with proj_cols[0]:
        # Proyección de costos
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        costos_actual = [420, 435, 445, 460, 475, 490]
        costos_proyectado = [420, 430, 425, 430, 435, 440]
        
        fig_costos = go.Figure()
        fig_costos.add_trace(go.Scatter(
            x=months, y=costos_actual,
            mode='lines+markers',
            name='Tendencia Actual',
            line=dict(color='#ff4444', width=3)
        ))
        fig_costos.add_trace(go.Scatter(
            x=months, y=costos_proyectado,
            mode='lines+markers',
            name='Con Optimización',
            line=dict(color='#00C851', width=3, dash='dash')
        ))
        fig_costos.update_layout(
            title="Proyección de Costos Operativos (Miles $)",
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.1)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_costos, use_container_width=True)
    
    with proj_cols[1]:
        # Score de riesgo integrado
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = 72,
            title = {'text': "Score de Riesgo Integrado"},
            delta = {'reference': 65},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#ffbb33"},
                'steps': [
                    {'range': [0, 50], 'color': "#00C851"},
                    {'range': [50, 75], 'color': "#ffbb33"},
                    {'range': [75, 100], 'color': "#ff4444"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Recomendaciones automatizadas
    st.markdown("### 🤖 Recomendaciones Automatizadas")
    
    recomendaciones = [
        {"prioridad": "🔴 ALTA", "accion": "Implementar rotación de personal en turno noche para reducir ausentismo", "impacto": "+15% cobertura"},
        {"prioridad": "🟡 MEDIA", "accion": "Optimizar rutas en zona norte basado en patrones de tráfico", "ahorro": "$8,500/mes"},
        {"prioridad": "🟡 MEDIA", "accion": "Capacitación urgente para supervisores con bajo desempeño", "mejora": "+22% cumplimiento"},
        {"prioridad": "🟢 BAJA", "accion": "Actualizar sistema de rastreo GPS en flota antigua", "beneficio": "Precisión +40%"}
    ]
    
    for rec in recomendaciones:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"**{rec['prioridad']}**")
        with col2:
            st.markdown(rec['accion'])
        with col3:
            if 'impacto' in rec:
                st.success(rec['impacto'])
            elif 'ahorro' in rec:
                st.info(rec['ahorro'])
            elif 'mejora' in rec:
                st.warning(rec['mejora'])
            else:
                st.info(rec['beneficio'])

# Footer con indicadores de estado
st.markdown("---")
footer_cols = st.columns(4)
with footer_cols[0]:
    st.success("🟢 Sistema Operativo")
with footer_cols[1]:
    st.info(f"🔄 Última actualización: {datetime.now().strftime('%H:%M:%S')}")
with footer_cols[2]:
    st.warning("📡 15 dispositivos conectados")
with footer_cols[3]:
    st.info("📊 Datos en tiempo real")