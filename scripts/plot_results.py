# %%
import altair as alt

import pandas as pd

df = pd.DataFrame.from_records(
    [
        {
            "conversion": "conversion",
            "tool": "pint",
            "time": 0.009694466943333327,
        },
        {
            "conversion": "conversion",
            "tool": "numericalunits",
            "time": 0.007906144310000005,
        },
        {
            "conversion": "conversion",
            "tool": "astropy",
            "time": 0.002235003480000005,
        },
        {
            "conversion": "conversion",
            "tool": "baseline",
            "time": 0.0004628404633333331,
        },
        {
            "conversion": "conversion",
            "tool": "quantities",
            "time": 0.0009585077666666571,
        },
        {
            "conversion": "conversion",
            "tool": "impunity",
            "time": 0.0006788837766666663,
        },
        {
            "conversion": "correct units",
            "tool": "impunity",
            "time": 0.00047280649666666525,
        },
        {
            "conversion": "correct units",
            "tool": "pint",
            "time": 0.008505804886666676,
        },
        {
            "conversion": "correct units",
            "tool": "baseline",
            "time": 0.0004589818400000019,
        },
        {
            "conversion": "correct units",
            "tool": "astropy",
            "time": 0.0022376610100000014,
        },
        {
            "conversion": "correct units",
            "tool": "quantities",
            "time": 0.0009541793033333342,
        },
        {
            "conversion": "correct units",
            "tool": "numericalunits",
            "time": 0.007808712183333338,
        },
    ]
)

# %%

chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        alt.Row(
            "tool",
            sort=[
                # "baseline",
                "impunity",
                "quantities",
                "astropy",
                "numericalunits",
                "pint",
            ],
            title=None,
        ),
        alt.Y("conversion", title=None),
        alt.Color("conversion", legend=None),
        alt.X(
            "scale:Q",
            # axis=alt.Axis(title="Computation time (in ms)"),
            title="Computation time (ratio to baseline)",
            scale=alt.Scale(nice=True),
        ),
    )
    .properties(width=600)
    .configure_header(
        labelOrient="top",
        labelAnchor="start",
        labelFont="Inconsolata",
        labelFontSize=14,
    )
    .configure_axis(
        labelFontSize=14,
        titleFontSize=16,
        titleAnchor="start",
    )
    .transform_calculate(
        milliseconds="datum.time * 1000",
        scale="datum.time / 0.0004628404633333331",
    )
    .transform_filter("datum.tool != 'baseline'")
)
chart
# %%
