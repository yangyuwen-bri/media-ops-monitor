import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config for a professional management console
st.set_page_config(
    page_title="新华运营 · 全平台内容资产管理系统",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- OPERATIONAL DESIGN SYSTEM ---
PLATFORM_COLORS = {
    '今日头条': '#C21807',  # Deep Red
    '微博': '#FBB03B',     # Amber
    '微信': '#07C160',     # Green
    '小红书': '#FF2442',    # Vibrant Red-Pink
    'B站': '#00A1D6',     # Bilibili Blue
    'APP': '#02559E',
    '其他': '#94a3b8'
}

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>
    .stApp {{
        background-color: #f1f5f9;
        font-family: 'Noto Sans SC', sans-serif;
    }}
    
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }}

    /* Global Header */
    .ops-header {{
        background: #ffffff;
        padding: 1rem 2rem;
        border-bottom: 2px solid #02559e;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .ops-title {{
        color: #02559e;
        font-weight: 800;
        font-size: 1.25rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .ops-badge {{
        background: #e0f2fe;
        color: #0369a1;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
    }}

    /* Data Cards */
    .metric-container {{
        background: #ffffff;
        border-left: 4px solid #02559e;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    .metric-sub {{ color: #64748b; font-size: 0.75rem; margin-bottom: 2px; font-weight: 500; }}
    .metric-main {{ color: #0f172a; font-size: 1.5rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; }}

    /* Chart Containers */
    .chart-card {{
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }}
    .chart-header {{
        font-size: 1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
    }}

    /* Tables */
    .stDataFrame {{ border-radius: 8px; overflow: hidden; }}

    /* Unified Section Title */
    .ops-section-title {{
        color: #0f172a;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 3rem 0 2rem 0;
        display: flex;
        align-items: center;
        gap: 15px;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
    }}
    .ops-section-title::before {{
        content: "";
        display: inline-block;
        width: 8px;
        height: 28px;
        background: #02559e;
        border-radius: 4px;
    }}
</style>
""", unsafe_allow_html=True)

def load_data(file):
    try:
        df = pd.read_excel(file)
        # Force numeric types
        for col in ['阅读数', '点赞数', '评论数', '转发数']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        if '发布时间' in df.columns:
            df['发布时间'] = pd.to_datetime(df['发布时间'])
            df['日期'] = df['发布时间'].dt.date
            
        return df
    except Exception as e:
        st.error(f"加载出错: {e}")
        return None

def main():
    # Sidebar Filters
    with st.sidebar:
        st.markdown("### 🛠️ 运营过滤控制")
        uploaded_file = st.file_uploader("导入原始监测报表", type=["xlsx"])
    
    # Header logic
    st.markdown("""
        <div class="ops-header">
            <div class="ops-title">📊 新华社矩阵运营驾驶舱 <span class="ops-badge">Live Ops</span></div>
            <div style="color: #64748b; font-size: 0.8rem;">数据更新：""" + datetime.now().strftime("%Y-%m-%d %H:%M") + """</div>
        </div>
    """, unsafe_allow_html=True)

    if uploaded_file is None:
        sample_path = "信源监测_Updated.xlsx"
        try:
            df = load_data(sample_path)
        except:
            st.warning("请上传报表进行分析")
            return
    else:
        df = load_data(uploaded_file)

    if df is not None:
        # Sidebar dynamic filters
        platforms = df['发布平台'].unique().tolist()
        with st.sidebar:
            st.markdown("### 🎯 监测对象")
            selected_platforms = st.multiselect("选择观察平台", platforms, default=platforms)
            st.markdown("---")

        # Filtered data
        f_df = df[df['发布平台'].isin(selected_platforms)]

        # Dynamic Insight Calculation (placed after filtering)
        if not f_df.empty:
            with st.sidebar:
                # Calculate interaction density (Total Interactions / Article Count)
                insight_df = f_df.groupby('发布平台')[['点赞数', '评论数', '转发数']].sum()
                insight_df['total_int'] = insight_df.sum(axis=1)
                insight_df['count'] = f_df['发布平台'].value_counts()
                insight_df['density'] = insight_df['total_int'] / insight_df['count']
                
                if not insight_df.empty:
                    best_plat = insight_df['density'].idxmax()
                    best_val = insight_df['density'].max()
                    
                    st.markdown("### 💡 智能运营建议")
                    st.info(f"**{best_plat}** 当前表现最佳！\n\n篇均互动达到 **{int(best_val)}** 次。建议维持当前发布频率，并尝试将该平台的高赞内容分发至其他渠道。")

        # --- TIER 1: TOTAL PIPELINE ---
        st.markdown('<div class="ops-section-title">🚀 核心流水监测 (Matrix Totals)</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1:
            st.markdown(f'<div class="metric-container"><div class="metric-sub">监测覆盖篇数</div><div class="metric-main">{len(f_df):,}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-container"><div class="metric-sub">全网累计触达</div><div class="metric-main">{int(f_df["阅读数"].sum()):,}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-container"><div class="metric-sub">社交互动总量</div><div class="metric-main">{int(f_df["点赞数"].sum()+f_df["评论数"].sum()+f_df["转发数"].sum()):,}</div></div>', unsafe_allow_html=True)
        with c4:
            avg_int = (f_df['点赞数'].sum() / len(f_df)) if len(f_df) > 0 else 0
            st.markdown(f'<div class="metric-container"><div class="metric-sub">篇均互动(点赞)</div><div class="metric-main">{avg_int:.1f}</div></div>', unsafe_allow_html=True)
        with c5:
            platforms_count = f_df['发布平台'].nunique()
            st.markdown(f'<div class="metric-container"><div class="metric-sub">活跃监测渠道</div><div class="metric-main">{platforms_count}</div></div>', unsafe_allow_html=True)

        # --- TIER 2: BENCHMARKING ---
        st.markdown('<div class="ops-section-title">⚖️ 发布节奏与权重分配 (Benchmarking)</div>', unsafe_allow_html=True)
        col_bench1, col_bench2 = st.columns([1, 2])

        with col_bench1:
            st.markdown('<div class="chart-card"><div class="chart-header">各平台分发篇数占比</div>', unsafe_allow_html=True)
            p_vol = f_df['发布平台'].value_counts().reset_index()
            p_vol.columns = ['平台', '篇数']
            
            # Calculate total for center text
            total_vol = p_vol['篇数'].sum()
            
            fig_vol = px.pie(p_vol, values='篇数', names='平台', hole=0.7,
                             color='平台', color_discrete_map=PLATFORM_COLORS)
            fig_vol.update_layout(
                showlegend=False,
                margin=dict(l=60, r=60, t=60, b=60),
                height=320,
                annotations=[dict(text=f'<span style="font-size:32px; font-weight:bold; color:#0f172a">{total_vol}</span><br><span style="font-size:14px; color:#64748b">总篇数</span>', 
                                x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            fig_vol.update_traces(textposition='outside', textinfo='percent+label', textfont_size=11,
                                 hovertemplate='%{label}: %{value}篇<extra></extra>')
            st.plotly_chart(fig_vol, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_bench2:
            st.markdown('<div class="chart-card"><div class="chart-header">分平台日均生产节奏</div>', unsafe_allow_html=True)
            daily_p = f_df.groupby(['日期', '发布平台']).size().reset_index(name='篇数')
            fig_daily = px.line(daily_p, x='日期', y='篇数', color='发布平台', 
                               line_shape='spline', color_discrete_map=PLATFORM_COLORS)
            fig_daily.update_layout(
                margin=dict(l=0,r=0,t=20,b=0), 
                plot_bgcolor='white', 
                hovermode='x',
                height=320,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=''),
                xaxis=dict(tickformat='%m月%d日', tickmode='auto', nticks=10)
            )
            fig_daily.update_traces(mode='lines+markers', hovertemplate='%{y}篇<extra></extra>')
            st.plotly_chart(fig_daily, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- TIER 3: INTERACTION DETAIL ---
        st.markdown('<div class="ops-section-title">📊 平台传播效率深度对标 (Efficiency)</div>', unsafe_allow_html=True)
        col_eff1, col_eff2 = st.columns(2)

        with col_eff1:
            st.markdown('<div class="chart-card"><div class="chart-header">全网阅读量/触达规模对比</div>', unsafe_allow_html=True)
            read_comp = f_df.groupby('发布平台')['阅读数'].sum().reset_index()
            fig_read = px.bar(read_comp, x='发布平台', y='阅读数', color='发布平台', color_discrete_map=PLATFORM_COLORS)
            fig_read.update_layout(showlegend=False, plot_bgcolor='white')
            fig_read.update_traces(hovertemplate='%{y}<extra></extra>')
            st.plotly_chart(fig_read, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_eff2:
            st.markdown('<div class="chart-card"><div class="chart-header">各大平台社交声量构成 (互动类型)</div>', unsafe_allow_html=True)
            int_comp = f_df.groupby('发布平台')[['点赞数', '评论数', '转发数']].sum().reset_index()
            fig_int = px.bar(int_comp, x='发布平台', y=['点赞数', '评论数', '转发数'], barmode='group',
                            color_discrete_map={'点赞数': '#3b82f6', '评论数': '#8b5cf6', '转发数': '#ec4899'})
            fig_int.update_layout(
                plot_bgcolor='white', 
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title_text=''),
                yaxis_title='互动量',
                hovermode='closest'
            )
            # Clean hover template: removes the secondary box and formats numbers
            fig_int.update_traces(hovertemplate='%{y:.0f}<extra></extra>')
            
            st.plotly_chart(fig_int, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- TIER 4: CONTENT AUDIT ---
        st.markdown('<div class="ops-section-title">🏆 运营绩效审计与优质内容池 (Audit)</div>', unsafe_allow_html=True)
        
        # 4.1 Local Platform Filter
        audit_platforms = ["全平台"] + selected_platforms
        selected_audit_plat = st.radio("审计范围筛选:", audit_platforms, horizontal=True, label_visibility="collapsed")

        # 4.2 Data Preparation & CSI Calculation
        audit_df = f_df.copy()
        if selected_audit_plat != "全平台":
            audit_df = audit_df[audit_df['发布平台'] == selected_audit_plat]
            
        # CSI Algorithm: Likes*1 + Comments*2 + Shares*3
        audit_df['raw_csi'] = audit_df['点赞数'] + audit_df['评论数']*2 + audit_df['转发数']*3
        
        # Standardization (0-100 Scale)
        max_csi = audit_df['raw_csi'].max()
        if max_csi > 0:
            audit_df['传播指数'] = (audit_df['raw_csi'] / max_csi) * 100
        else:
            audit_df['传播指数'] = 0
            
        tab1, tab2 = st.tabs(["🔥 优质传播热度榜 (CSI Top 20)", "💬 评论活跃榜 Top 20"])
        
        with tab1:
            # Sort by CSI Index
            top_csi = audit_df.nlargest(20, '传播指数')[['标题', '发布平台', '传播指数', '点赞数', '评论数', '转发数', '发布时间']]
            # Format float to 1 decimal place
            st.dataframe(
                top_csi.style.format({'传播指数': '{:.1f}'}), 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "传播指数": st.column_config.ProgressColumn(
                        "传播指数 (CSI)",
                        help="基于点赞、评论、转发加权计算的归一化指数 (0-100)",
                        format="%.1f",
                        min_value=0,
                        max_value=100,
                    )
                }
            )
        
        with tab2:
            top_comments = audit_df.nlargest(20, '评论数')[['标题', '发布平台', '评论数', '点赞数', '发布时间']]
            st.dataframe(top_comments, use_container_width=True, hide_index=True)

        # --- TIER 5: SENTIMENT ---
        if '情感属性' in f_df.columns:
            st.markdown('<div class="ops-section-title">⚡ 全矩阵运营舆情及情感分布态势 (Sentiment Matrix)</div>', unsafe_allow_html=True)
            
            p_sent_list = f_df['发布平台'].unique().tolist()
            # Batch in 4 columns for a cleaner macro-integrated look
            for i in range(0, len(p_sent_list), 4):
                batch = p_sent_list[i:i+4]
                cols = st.columns(4)
                for j, plat in enumerate(batch):
                    with cols[j]:
                        plat_df = f_df[f_df['发布平台'] == plat]
                        sent_counts = plat_df['情感属性'].value_counts().reset_index()
                        sent_counts.columns = ['情感', '数量']
                        
                        fig_plat_sent = px.pie(sent_counts, values='数量', names='情感', hole=0.85,
                                              color='情感', color_discrete_map={'正面': '#10b981', '中性': '#94a3b8', '负面': '#ef4444'})
                        
                        fig_plat_sent.update_layout(
                            showlegend=False,
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=180,
                            annotations=[dict(text=f'<span style="font-size:14px; color:#1e293b; font-weight:700">{plat}</span>', 
                                            x=0.5, y=0.5, showarrow=False)]
                        )
                        fig_plat_sent.update_traces(
                            textinfo='none', 
                            hoverinfo='label+percent',
                            marker=dict(line=dict(color='#f1f5f9', width=3))
                        )
                        st.plotly_chart(fig_plat_sent, use_container_width=True, key=f"sent_v6_{plat}", config={'displayModeBar': False})

if __name__ == "__main__":
    main()
