import plotly.graph_objects as go


def render_gauge(fake_prob: float, prediction: str) -> go.Figure:
    """
    Render a clean professional gauge chart showing authenticity probability.
    fake_prob: 0.0 = definitely real, 1.0 = definitely fake
    """
    real_prob = 1.0 - fake_prob
    display_value = round(real_prob * 100, 1)

    if fake_prob >= 0.75:
        color = "#dc2626"       # red — high confidence fake
        label = "High Risk"
    elif fake_prob >= 0.5:
        color = "#f97316"       # orange — likely fake
        label = "Likely Fake"
    elif fake_prob >= 0.25:
        color = "#eab308"       # yellow — uncertain
        label = "Uncertain"
    else:
        color = "#16a34a"       # green — likely real
        label = "Likely Authentic"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=display_value,
        number={
            "suffix": "%",
            "font": {"size": 48, "color": "#18181b", "family": "Inter, sans-serif"},
        },
        title={
            "text": f"Authenticity Score<br><span style='font-size:14px;color:#71717a'>{label}</span>",
            "font": {"size": 16, "color": "#18181b", "family": "Inter, sans-serif"},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#e4e4e7",
                "tickfont": {"size": 11, "color": "#71717a"},
            },
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 25],   "color": "#fef2f2"},
                {"range": [25, 50],  "color": "#fff7ed"},
                {"range": [50, 75],  "color": "#fefce8"},
                {"range": [75, 100], "color": "#f0fdf4"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.75,
                "value": display_value,
            },
        },
    ))

    fig.update_layout(
        height=280,
        margin={"t": 60, "b": 20, "l": 30, "r": 30},
        paper_bgcolor="white",
        font={"family": "Inter, sans-serif"},
    )

    return fig


def render_probability_bars(fake_prob: float, real_prob: float) -> go.Figure:
    """Horizontal bar chart showing FAKE vs REAL probability breakdown."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=["REAL", "FAKE"],
        x=[round(real_prob * 100, 1), round(fake_prob * 100, 1)],
        orientation="h",
        marker_color=["#16a34a", "#dc2626"],
        text=[f"{round(real_prob * 100, 1)}%", f"{round(fake_prob * 100, 1)}%"],
        textposition="inside",
        textfont={"color": "white", "size": 13, "family": "Inter, sans-serif"},
    ))

    fig.update_layout(
        height=120,
        margin={"t": 10, "b": 10, "l": 10, "r": 10},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis={"range": [0, 100], "showgrid": False, "showticklabels": False},
        yaxis={"showgrid": False},
        showlegend=False,
        font={"family": "Inter, sans-serif", "color": "#18181b"},
    )

    return fig
