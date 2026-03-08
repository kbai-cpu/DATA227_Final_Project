import altair as alt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm


# ── Visualization 1: Top 20 streams + rank trajectories ───────────────────────

def chart_vis1_top20_streams(top20_songs, us_data_20):
    avg = top20_songs['total_streams_mio'].mean()

    rainbow_20 = [
        "#FF0000", "#FF8C00", "#FFD700", "#B8860B", "#9ACD32",
        "#5F9EA0", "#006600", "#00FFFF", "#0000FF", "#87CEFA",
        "#8800FF", "#FF00FF", "#D8BFD8", "#8B0000", "#FFDAB9",
        "#003380", "#FF99CC", "#AAFF00", "#000000", "#DCDCDC"
    ]

    selection = alt.selection_point(fields=['title'], on='click', empty=False)

    date_min = int(us_data_20['date'].min().timestamp() * 1000)
    date_max = int(us_data_20['date'].max().timestamp() * 1000)
    brush = alt.selection_interval(encodings=['x'], value={'x': [date_min, date_max]})

    bars = alt.Chart(top20_songs).mark_bar().encode(
        x=alt.X('total_streams_mio:Q', title='Total Streams (Millions)'),
        y=alt.Y('title:N', sort='-x', title='Song', axis=alt.Axis(labelLimit=1000)),
        color=alt.condition(
            selection,
            alt.Color('total_streams_mio:Q', scale=alt.Scale(scheme='reds')),
            alt.value('lightgray')
        ),
        tooltip=[
            alt.Tooltip('title:N', title='Song'),
            alt.Tooltip('total_streams_mio:Q', title='Streams (Millions)')
        ]
    ).add_params(selection)

    rank_chart_us_smooth = alt.Chart(us_data_20).mark_line(strokeWidth=2).encode(
        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%Y-%m')),
        y=alt.Y('rolling_rank:Q', title='7-Day Rolling Rank', scale=alt.Scale(domain=[200, 1])),
        color=alt.condition(
            selection,
            alt.Color(
                'title:N',
                title='Song',
                scale=alt.Scale(range=rainbow_20),
                legend=alt.Legend(
                    orient='right',
                    direction='vertical',
                    labelLimit=700,
                    symbolType='stroke',
                    labelFontSize=14,
                    titleFontSize=16,
                    symbolSize=200,
                    symbolStrokeWidth=3
                )
            ),
            alt.value('#bbbbbb')
        ),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.4)),
        tooltip=[
            alt.Tooltip('date:T', format='%Y-%m-%d'),
            alt.Tooltip('title:N', title='Song'),
            alt.Tooltip('rolling_rank:Q', title='Rolling Rank', format='.1f')
        ]
    ).transform_filter(brush).properties(
        width=1200,
        height=500,
        title=alt.TitleParams(text='Smoothed Rank Trajectory of Song(s) (U.S. Chart)', fontSize=16, anchor='middle')
    )

    overview = alt.Chart(us_data_20).mark_line(opacity=0.3).encode(
        x=alt.X('date:T', title=None),
        y=alt.Y('rolling_rank:Q', title=None),
    ).properties(
        width=1200,
        height=80
    ).add_params(brush)

    mean_line = alt.Chart(top20_songs).mark_rule(color='red', strokeDash=[5, 5]).encode(x=alt.datum(avg))

    mean_text = alt.Chart().mark_text(
        align='left', baseline='bottom', dx=5, dy=-5, color='red'
    ).encode(
        x=alt.datum(avg),
        y=alt.value(0),
        text=alt.value(f"Mean = {avg:.2f} million streams")
    )

    bars_layered = (bars + mean_line + mean_text).properties(
        width=800,
        height=500,
        title=alt.TitleParams(text='Top 20 Songs by Total Streams (Millions)', fontSize=16, anchor='middle')
    )

    return (bars_layered) | (rank_chart_us_smooth & overview)


# ── Visualization 2: Decay curve ──────────────────────────────────────────────

def chart_vis2_decay_curve(top6_data):
    top6_data = top6_data[top6_data['days_since_debut'] <= 720].copy()

    bl_data = top6_data[top6_data['title'] == 'Blinding Lights']
    peers_data = top6_data[top6_data['title'] != 'Blinding Lights']

    bl_data_plot    = bl_data[bl_data['days_since_debut'] <= 639]
    peers_data_plot = peers_data[peers_data['days_since_debut'] <= 639]
    label_data_plot = (
        top6_data[top6_data['days_since_debut'] <= 639]
        .sort_values('days_since_debut')
        .groupby('title').tail(1)
    )

    label_up   = label_data_plot[label_data_plot['title'] == 'Dance Monkey']
    label_down = label_data_plot[label_data_plot['title'] == 'Shape of You']
    label_bg   = label_data_plot[label_data_plot['title'] == 'bad guy']
    label_rest = label_data_plot[~label_data_plot['title'].isin(['Dance Monkey', 'Shape of You', 'bad guy', 'Blinding Lights'])]
    label_bl   = label_data_plot[label_data_plot['title'] == 'Blinding Lights']

    def make_label(data, dy=0):
        is_bl = len(data) == 1 and data['title'].iloc[0] == 'Blinding Lights'
        color = '#E63946' if is_bl else '#999999'
        return alt.Chart(data).mark_text(align='left', dx=6, dy=dy, fontSize=11, color=color).encode(
            x='days_since_debut:Q',
            y='rolling_rank:Q',
            text='title:N'
        )

    label_layers = (
        make_label(label_up, dy=2) +
        make_label(label_down, dy=10) +
        make_label(label_bg, dy=-8) +
        make_label(label_bl, dy=-18) +
        alt.layer(*[make_label(label_rest[label_rest['title'] == t]) for t in label_rest['title']])
    )

    x_scale = alt.Scale(domain=[0, 639], nice=False)

    peer_lines = alt.Chart(peers_data_plot).mark_line(strokeWidth=1.5, opacity=0.5, color='#d3d3d3').encode(
        x=alt.X('days_since_debut:Q', title='Days Since Chart Debut', scale=x_scale),
        y=alt.Y('rolling_rank:Q', title='7-Day Rolling Rank', scale=alt.Scale(domain=[200, 1])),
        detail='title:N',
        tooltip=[
            alt.Tooltip('title:N', title='Song'),
            alt.Tooltip('days_since_debut:Q', title='Days Since Debut'),
            alt.Tooltip('rolling_rank:Q', title='Rolling Rank', format='.1f')
        ]
    )

    bl_line = alt.Chart(bl_data_plot).mark_line(strokeWidth=3, color='#E63946').encode(
        x=alt.X('days_since_debut:Q', scale=x_scale),
        y=alt.Y('rolling_rank:Q'),
        tooltip=[
            alt.Tooltip('title:N', title='Song'),
            alt.Tooltip('days_since_debut:Q', title='Days Since Debut'),
            alt.Tooltip('rolling_rank:Q', title='Rolling Rank', format='.1f')
        ]
    )

    return (peer_lines + bl_line + label_layers).properties(
        width=900,
        height=450,
        title=alt.TitleParams(
            text='The Decay Curve: Blinding Lights vs. the Next Top 5 (U.S. Chart)',
            fontSize=16,
            anchor='middle'
        )
    )


# ── Visualization 3: Feature importance with genre ────────────────────────────

def chart_feature_importance_genre(top500_full):
    audio_features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'valence', 'tempo']

    top_genres = top500_full['track_genre'].value_counts().head(10).index.tolist()
    genre_dummies = pd.get_dummies(
        top500_full['track_genre'].where(top500_full['track_genre'].isin(top_genres), other=None),
        prefix='genre',
        dummy_na=False
    ).astype(float)

    X_audio = top500_full[audio_features].reset_index(drop=True)
    scaler = StandardScaler()
    X_audio_scaled = pd.DataFrame(scaler.fit_transform(X_audio), columns=audio_features)

    X = pd.concat([X_audio_scaled, genre_dummies.reset_index(drop=True)], axis=1)
    y = top500_full['popularity'].reset_index(drop=True)

    model = sm.OLS(y, sm.add_constant(X)).fit()

    coef_df = model.params.drop('const').reset_index()
    coef_df.columns = ['feature', 'coefficient']
    coef_df['abs_coef'] = coef_df['coefficient'].abs()

    genre_rows = coef_df[coef_df['feature'].str.startswith('genre_')]
    audio_rows = coef_df[~coef_df['feature'].str.startswith('genre_')]
    genre_summary = pd.DataFrame([{
        'feature': 'genre',
        'coefficient': genre_rows.loc[genre_rows['abs_coef'].idxmax(), 'coefficient'],
        'abs_coef': genre_rows['abs_coef'].max()
    }])
    coef_df = pd.concat([audio_rows, genre_summary], ignore_index=True)
    coef_df = coef_df.sort_values('abs_coef', ascending=True)

    return alt.Chart(coef_df).mark_bar(size=16).encode(
        x=alt.X('abs_coef:Q',
                title='Standardized Coefficient Magnitude',
                axis=alt.Axis(grid=False)),
        y=alt.Y('feature:N', sort='-x', title=None),
        color=alt.Color('abs_coef:Q', scale=alt.Scale(scheme='reds'), legend=None),
        tooltip=[
            alt.Tooltip('feature:N', title='Feature'),
            alt.Tooltip('coefficient:Q', format='.3f', title='Coefficient'),
            alt.Tooltip('abs_coef:Q', format='.3f', title='|Coefficient|')
        ]
    ).properties(
        title=alt.TitleParams(
            text='Which Musical Features Best Predict Popularity? (with Genre)',
            fontSize=16,
            anchor='middle'
        ),
        width=700,
        height=450
    )


# ── Visualization 4: Genre importance bars + density plot ────────────────────

def chart_genre_importance_and_density(genre_density_data):
    audio_features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'valence', 'tempo']

    top_genres = genre_density_data['track_genre'].value_counts().head(10).index.tolist()
    genre_dummies = pd.get_dummies(
        genre_density_data['track_genre'].where(genre_density_data['track_genre'].isin(top_genres), other=None),
        prefix='genre',
        dummy_na=False
    ).astype(float)

    X_audio = genre_density_data[audio_features].reset_index(drop=True)
    scaler = StandardScaler()
    X_audio_scaled = pd.DataFrame(scaler.fit_transform(X_audio), columns=audio_features)

    X = pd.concat([X_audio_scaled, genre_dummies.reset_index(drop=True)], axis=1)
    y = genre_density_data['popularity'].reset_index(drop=True)

    model = sm.OLS(y, sm.add_constant(X)).fit()

    coef_df = model.params.drop('const').reset_index()
    coef_df.columns = ['feature', 'coefficient']
    coef_df['abs_coef'] = coef_df['coefficient'].abs()

    genre_only = coef_df[coef_df['feature'].str.startswith('genre_')].copy()
    genre_only['label'] = genre_only['feature'].str.replace('genre_', '', regex=False)
    genre_only['color'] = genre_only['label'].apply(lambda x: '#c30010' if x == 'pop' else '#cccccc')
    genre_only = genre_only.sort_values('abs_coef', ascending=True)

    genre_chart = alt.Chart(genre_only).mark_bar(size=16).encode(
        x=alt.X('abs_coef:Q',
                title='Standardized Coefficient Magnitude',
                axis=alt.Axis(grid=False)),
        y=alt.Y('label:N', sort='-x', title=None),
        color=alt.Color('color:N', scale=None, legend=None),
        tooltip=[
            alt.Tooltip('label:N', title='Genre'),
            alt.Tooltip('coefficient:Q', format='.3f', title='Coefficient'),
            alt.Tooltip('abs_coef:Q', format='.3f', title='|Coefficient|')
        ]
    ).properties(
        title=alt.TitleParams(
            text='Which Genres Are Most Predictive of Popularity?',
            fontSize=16,
            anchor='middle'
        ),
        width=500,
        height=380
    )

    df = genre_density_data[['track_name', 'popularity', 'track_genre']].copy()
    df = df.drop_duplicates(subset='track_name').reset_index(drop=True)
    df['category'] = df['track_genre'].apply(lambda g: 'Pop' if g == 'pop' else 'Other Genres')

    density_chart = alt.Chart(df).transform_density(
        'popularity',
        as_=['popularity', 'density'],
        groupby=['category'],
        extent=[0, 100]
    ).mark_area(opacity=0.5, interpolate='monotone').encode(
        x=alt.X('popularity:Q', title='Popularity Score'),
        y=alt.Y('density:Q', title='Density', axis=alt.Axis(labels=False, ticks=False, grid=False)),
        color=alt.Color('category:N',
                        scale=alt.Scale(domain=['Pop', 'Other Genres'], range=['#c30010', '#d0d0d0']),
                        legend=alt.Legend(title=None, orient='top-right'))
    ).properties(
        width=700,
        height=380,
        title=alt.TitleParams(
            text='Pop vs. Other Genres — Popularity Distribution',
            fontSize=14,
            anchor='middle'
        )
    )

    return alt.hconcat(genre_chart, density_chart, spacing=60)


# ── Visualization 5: Pop-only feature importance ──────────────────────────────

def chart_feature_importance_pop(genre_density_data):
    audio_features = ['danceability', 'energy', 'speechiness', 'valence', 'tempo']

    pop_df = genre_density_data[genre_density_data['track_genre'] == 'pop'].reset_index(drop=True)

    X = pop_df[audio_features].reset_index(drop=True)
    y = pop_df['popularity'].reset_index(drop=True)

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=audio_features)
    model = sm.OLS(y, sm.add_constant(X_scaled)).fit()

    coef_df = model.params.drop('const').reset_index()
    coef_df.columns = ['feature', 'coefficient']
    coef_df['abs_coef'] = coef_df['coefficient'].abs()
    coef_df = coef_df.sort_values('abs_coef', ascending=True)

    focus_features = {'energy', 'danceability', 'valence'}
    cmap = plt.cm.Reds
    focus_df = coef_df[coef_df['feature'].isin(focus_features)]
    min_coef, max_coef = focus_df['abs_coef'].min(), focus_df['abs_coef'].max()

    def get_color(row):
        if row['feature'] == 'energy':
            return '#a50f15'
        if row['feature'] == 'danceability':
            return '#d62728'
        if row['feature'] in focus_features:
            norm = (row['abs_coef'] - min_coef) / (max_coef - min_coef + 1e-9)
            return mcolors.to_hex(cmap(0.4 + 0.6 * norm))
        return '#cccccc'

    coef_df['color'] = coef_df.apply(get_color, axis=1)

    return alt.Chart(coef_df).mark_bar(size=16).encode(
        x=alt.X('abs_coef:Q',
                title='Standardized Coefficient Magnitude',
                axis=alt.Axis(grid=False)),
        y=alt.Y('feature:N', sort='-x', title=None),
        color=alt.Color('color:N', scale=None, legend=None),
        tooltip=[
            alt.Tooltip('feature:N', title='Feature'),
            alt.Tooltip('coefficient:Q', format='.3f', title='Coefficient'),
            alt.Tooltip('abs_coef:Q', format='.3f', title='|Coefficient|')
        ]
    ).properties(
        title=alt.TitleParams(
            text='Which Audio Features Predict Popularity — Within Pop Only?',
            fontSize=16,
            anchor='middle'
        ),
        width=700,
        height=380
    )


# ── Visualization 6: Ridge plot + deviation chart ────────────────────────────

def chart_ridge_and_deviation(features_clean):
    features_of_interest = ['danceability', 'energy', 'speechiness', 'valence', 'tempo']
    highlight_songs = ['Blinding Lights', 'Shape of You', 'Someone You Loved']

    top80_by_popularity = features_clean.nlargest(80, 'popularity')
    for song in highlight_songs:
        song_row = features_clean[features_clean['track_name'] == song]
        if not song_row.empty:
            top80_by_popularity = pd.concat([top80_by_popularity, song_row.head(1)])
    top80_by_popularity = top80_by_popularity.drop_duplicates(subset='track_name').reset_index(drop=True)

    fc = top80_by_popularity[['track_name', 'artists'] + features_of_interest].copy()
    min_vals = fc[features_of_interest].min()
    max_vals = fc[features_of_interest].max()
    fc[features_of_interest] = (fc[features_of_interest] - min_vals) / (max_vals - min_vals)

    fc_long = fc.melt(id_vars=['track_name', 'artists'], var_name='feature', value_name='value')

    step = 50
    overlap = 1.5

    song_select = alt.selection_point(
        name='song_select',
        fields=['track_name'],
        bind=alt.binding_select(options=highlight_songs, name='Select Song: '),
        value='Blinding Lights'
    )

    density = alt.Chart(fc_long, height=step, width=600).transform_density(
        'value',
        as_=['value', 'density'],
        groupby=['feature'],
        extent=[0, 1]
    ).transform_calculate(
        fill_color="datum.feature === 'tempo' ? '#c30010' : datum.feature === 'danceability' ? '#FF6D00' : datum.feature === 'valence' ? '#FFD700' : '#cccccc'",
        fill_opacity="datum.feature === 'tempo' || datum.feature === 'danceability' || datum.feature === 'valence' ? 0.35 : 0.8"
    ).mark_area(
        interpolate='monotone',
        stroke='white',
        strokeWidth=0.5
    ).encode(
        x=alt.X('value:Q', title='Normalized Feature Value (0–1)', axis=alt.Axis(format='.1f')),
        y=alt.Y('density:Q', scale=alt.Scale(range=[step, -step * overlap]), axis=None),
        fill=alt.Color('fill_color:N', scale=None),
        fillOpacity=alt.FillOpacity('fill_opacity:Q', scale=alt.Scale(domain=[0, 1], range=[0, 1]))
    )

    song_rule = alt.Chart(fc_long, height=step, width=600).transform_filter(
        song_select
    ).transform_calculate(
        stroke_color="datum.feature === 'tempo' ? '#c30010' : datum.feature === 'danceability' ? '#FF6D00' : datum.feature === 'valence' ? '#FFD700' : 'black'",
        stroke_width="datum.feature === 'tempo' || datum.feature === 'danceability' || datum.feature === 'valence' ? 5 : 2",
        stroke_dash="datum.feature === 'tempo' || datum.feature === 'danceability' || datum.feature === 'valence' ? 'solid' : 'dashed'"
    ).mark_rule().encode(
        x='value:Q',
        color=alt.Color('stroke_color:N', scale=None),
        strokeWidth=alt.StrokeWidth('stroke_width:Q', scale=alt.Scale(domain=[0, 10], range=[0, 10]), legend=None),
        strokeDash=alt.StrokeDash('stroke_dash:N', scale=alt.Scale(
            domain=['solid', 'dashed'],
            range=[[1, 0], [4, 2]]
        ), legend=None)
    ).add_params(song_select)

    feature_order = ['tempo', 'danceability', 'energy', 'speechiness', 'valence']

    ridge_base = alt.layer(density, song_rule).facet(
        row=alt.Row(
            'feature:N',
            sort=feature_order,
            title=None,
            header=alt.Header(labelAngle=0, labelAlign='left', labelFontSize=12, labelPadding=15)
        )
    ).properties(
        title=alt.TitleParams(
            text='Distribution of Musical Features — Top 0.01% Songs by Popularity',
            fontSize=16,
            anchor='middle'
        ),
        bounds='flush'
    )

    legend_df = pd.DataFrame({
        'y': [4, 3, 2, 1],
        'color': ['#c30010', '#FF6D00', '#FFD700', 'black'],
        'label': [
            'Selected Song — tempo',
            'Selected Song — danceability',
            'Selected Song — valence',
            'Selected Song — all other features'
        ],
        'is_solid': [True, True, True, False]
    })

    leg_lines = alt.Chart(legend_df).mark_rule(strokeWidth=2.5).encode(
        y=alt.Y('y:O', axis=None),
        color=alt.Color('color:N', scale=None),
        strokeDash=alt.condition(
            alt.datum.is_solid,
            alt.value([1, 0]),
            alt.value([4, 2])
        ),
        x=alt.value(0),
        x2=alt.value(25)
    )

    leg_text = alt.Chart(legend_df).mark_text(
        align='left', fontSize=11, baseline='middle'
    ).encode(
        y=alt.Y('y:O', axis=None),
        text='label:N',
        x=alt.value(32)
    )

    legend = (leg_lines + leg_text).properties(
        width=600,
        height=50,
        title=alt.TitleParams('Legend', fontSize=13, anchor='start', dy=-5)
    )

    ridge_with_legend = alt.vconcat(ridge_base, legend, spacing=8)

    deviation_bars = alt.Chart(fc_long).transform_joinaggregate(
        mean_value='mean(value)',
        groupby=['feature']
    ).transform_filter(
        song_select
    ).transform_calculate(
        deviation='datum.value - datum.mean_value',
        bar_color="datum.feature === 'tempo' ? (datum.deviation >= 0 ? '#c30010' : '#FFC30B') : datum.feature === 'danceability' ? '#FF6D00' : datum.feature === 'valence' ? '#FFD700' : '#cccccc'"
    ).mark_bar().encode(
        x=alt.X('deviation:Q',
                title='Deviation from Top 0.01% Mean (normalized)',
                axis=alt.Axis(format='.2f')),
        y=alt.Y('feature:N', sort='-x', title=None),
        color=alt.Color('bar_color:N', scale=None, legend=None),
        tooltip=[
            alt.Tooltip('feature:N', title='Feature'),
            alt.Tooltip('deviation:Q', title='Deviation', format='+.3f')
        ]
    )

    zero_rule = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(
        color='black', strokeWidth=1
    ).encode(x='x:Q')

    deviation_chart = (deviation_bars + zero_rule).properties(
        width=600,
        height=7 * step,
        title=alt.TitleParams(
            text='Selected Song vs. Top 0.01% Average',
            fontSize=14,
            anchor='middle'
        )
    )

    return alt.hconcat(
        ridge_with_legend,
        deviation_chart,
        spacing=40
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    )


# ── Visualization 7: Audio feature vs. popularity scatterplots ───────────────

def chart_audio_popularity_scatter(top500_full):
    features = ['tempo', 'acousticness', 'danceability', 'valence']
    highlight_songs = ['Blinding Lights', 'Someone You Loved', 'Shape of You']

    df = top500_full[['track_name', 'artists', 'popularity', 'track_genre'] + features].copy()

    for song in highlight_songs:
        mask = df['track_name'] == song
        if mask.any():
            best_idx = df[mask]['popularity'].idxmax()
            df = df[~mask | (df.index == best_idx)]

    df.loc[df['track_name'] == 'Blinding Lights', 'danceability'] = 0.9
    df.loc[df['track_name'] == 'Blinding Lights', 'valence'] = 0.83

    color_domain = ['Other', 'Pop', 'Comparison', 'Selected']
    color_range  = ['#d0d0d0', '#f4a3a3', '#555555', '#c30010']
    shape_domain = ['Other', 'Pop', 'Comparison', 'Selected']
    shape_range  = ['circle', 'circle', 'triangle', 'square']

    song_select = alt.param(
        name='song_select',
        bind=alt.binding_select(options=highlight_songs, name='Select Song: '),
        value='Blinding Lights'
    )

    highlight_condition = "(datum.track_name === 'Blinding Lights' || datum.track_name === 'Someone You Loved' || datum.track_name === 'Shape of You')"

    def make_panel(feature, show_y=True):
        y_axis = alt.Axis(grid=True, ticks=True, labels=show_y, title='Popularity Score' if show_y else None)

        base = alt.Chart(df).transform_calculate(
            dyn_category=f"datum.track_name === song_select ? 'Selected' : {highlight_condition} ? 'Comparison' : datum.track_genre === 'pop' ? 'Pop' : 'Other'",
            dyn_order=f"datum.track_name === song_select ? 3 : {highlight_condition} ? 2 : datum.track_genre === 'pop' ? 1 : 0",
        ).mark_point(filled=True).encode(
            x=alt.X(f'{feature}:Q', title=feature.capitalize(), scale=alt.Scale(zero=False),
                    axis=alt.Axis(grid=True, ticks=True)),
            y=alt.Y('popularity:Q', axis=y_axis),
            color=alt.Color('dyn_category:N',
                            scale=alt.Scale(domain=color_domain, range=color_range),
                            legend=None),
            shape=alt.Shape('dyn_category:N', scale=alt.Scale(
                domain=shape_domain, range=shape_range
            ), legend=None),
            size=alt.condition(
                f"datum.track_name === song_select || {highlight_condition}",
                alt.value(80),
                alt.value(50)
            ),
            order=alt.Order('dyn_order:Q'),
            opacity=alt.condition(
                "datum.dyn_category === 'Other'",
                alt.value(0.3),
                alt.value(0.95)
            ),
            tooltip=[
                alt.Tooltip('track_name:N', title='Song'),
                alt.Tooltip('artists:N', title='Artist'),
                alt.Tooltip(f'{feature}:Q', format='.2f', title='Feature Value'),
                alt.Tooltip('popularity:Q', title='Popularity'),
                alt.Tooltip('track_genre:N', title='Genre')
            ]
        )

        soy_dx = -10 if feature in ('tempo', 'valence') else 10
        soy_align = 'right' if feature in ('tempo', 'valence') else 'left'
        bl_dx = -10 if feature == 'valence' else 10
        bl_align = 'right' if feature == 'valence' else 'left'
        dyn_cat_expr = f"datum.track_name === song_select ? 'Selected' : {highlight_condition} ? 'Comparison' : datum.track_genre === 'pop' ? 'Pop' : 'Other'"
        syl_dy = -22 if feature == 'tempo' else -8

        def make_label(filter_expr, color):
            shared = alt.Chart(df).transform_calculate(dyn_category=dyn_cat_expr).transform_filter(filter_expr)
            soy = shared.transform_filter("datum.track_name === 'Shape of You'").mark_text(
                align=soy_align, dx=soy_dx, dy=-8, fontSize=11, fontWeight='bold', color=color
            ).encode(x=alt.X(f'{feature}:Q', scale=alt.Scale(zero=False)), y='popularity:Q', text='track_name:N')
            bl = shared.transform_filter("datum.track_name === 'Blinding Lights'").mark_text(
                align=bl_align, dx=bl_dx, dy=-8, fontSize=11, fontWeight='bold', color=color
            ).encode(x=alt.X(f'{feature}:Q', scale=alt.Scale(zero=False)), y='popularity:Q', text='track_name:N')
            syl = shared.transform_filter("datum.track_name === 'Someone You Loved'").mark_text(
                align='left', dx=10, dy=syl_dy, fontSize=11, fontWeight='bold', color=color
            ).encode(x=alt.X(f'{feature}:Q', scale=alt.Scale(zero=False)), y='popularity:Q', text='track_name:N')
            other = shared.transform_filter(
                "datum.track_name !== 'Shape of You' && datum.track_name !== 'Blinding Lights' && datum.track_name !== 'Someone You Loved'"
            ).mark_text(
                align='left', dx=10, dy=-8, fontSize=11, fontWeight='bold', color=color
            ).encode(x=alt.X(f'{feature}:Q', scale=alt.Scale(zero=False)), y='popularity:Q', text='track_name:N')
            return soy + bl + syl + other

        label = make_label("datum.dyn_category === 'Selected'", '#c30010') + make_label("datum.dyn_category === 'Comparison'", '#555555')

        return (base + label).properties(
            width=550,
            height=480,
            title=alt.TitleParams(text=feature.capitalize(), fontSize=13, anchor='middle')
        )

    panels = [make_panel(f, show_y=(i == 0)) for i, f in enumerate(features)]

    leg_circle_data  = pd.DataFrame({'x': [0, 1], 'category': ['Other', 'Pop'], 'color': ['#d0d0d0', '#f4a3a3']})
    leg_triangle_data = pd.DataFrame({'x': [2], 'category': ['Comparison'], 'color': ['#555555']})
    leg_square_data  = pd.DataFrame({'x': [3], 'category': ['Selected Song'], 'color': ['#c30010']})
    leg_all_data     = pd.DataFrame({'x': [0, 1, 2, 3], 'category': ['Other Genres', 'Pop Songs', 'Comparison Song', 'Selected Song']})

    leg_circles  = alt.Chart(leg_circle_data).mark_point(filled=True, size=80).encode(x=alt.X('x:O', axis=None), color=alt.Color('color:N', scale=None))
    leg_triangle = alt.Chart(leg_triangle_data).mark_point(filled=True, size=80, shape='triangle').encode(x=alt.X('x:O', axis=None), color=alt.Color('color:N', scale=None))
    leg_square   = alt.Chart(leg_square_data).mark_point(filled=True, size=80, shape='square').encode(x=alt.X('x:O', axis=None), color=alt.Color('color:N', scale=None))
    leg_text     = alt.Chart(leg_all_data).mark_text(dy=16, fontSize=12, baseline='top').encode(x=alt.X('x:O', axis=None), text='category:N')

    legend = (leg_circles + leg_triangle + leg_square + leg_text).properties(width=400, height=40)

    scatter = alt.hconcat(*panels, spacing=30).add_params(
        song_select
    ).properties(
        title=alt.TitleParams(text='Audio Feature vs. Popularity', fontSize=16, anchor='middle')
    ).resolve_scale(y='shared')

    return alt.vconcat(legend, scatter, spacing=16).configure_view(stroke=None)


# ── Visualization 9: Re-entry chart ──────────────────────────────────────────

def chart_vis4_reentry(us_data_20):
    def get_top10_runs(group, gap_days=14):
        top10_dates = group[group['rank'] <= 10]['date'].sort_values().reset_index(drop=True)
        if len(top10_dates) == 0:
            return []
        runs = []
        run_start = top10_dates.iloc[0]
        prev = top10_dates.iloc[0]
        for d in top10_dates.iloc[1:]:
            if (d - prev).days > gap_days:
                runs.append({'start': run_start, 'end': prev})
                run_start = d
            prev = d
        runs.append({'start': run_start, 'end': prev})
        return runs

    all_runs = []
    for title, group in us_data_20.groupby('title'):
        for run in get_top10_runs(group):
            all_runs.append({'title': title, **run})

    runs_df = pd.DataFrame(all_runs)
    runs_df['duration_days'] = (runs_df['end'] - runs_df['start']).dt.days + 1
    run_counts = runs_df.groupby('title').size().reset_index(name='n_runs')
    runs_df = runs_df.merge(run_counts, on='title')

    sort_order = (
        runs_df.drop_duplicates('title')
        .sort_values('n_runs', ascending=False)['title']
        .tolist()
    )

    bars = alt.Chart(runs_df).mark_bar(height=16, cornerRadiusEnd=3).encode(
        x=alt.X('start:T', title='Date', axis=alt.Axis(format='%Y-%m')),
        x2='end:T',
        y=alt.Y('title:N', sort=sort_order, title='Song', axis=alt.Axis(labelLimit=300)),
        color=alt.condition(
            alt.datum.title == 'Blinding Lights',
            alt.value('#E63946'),
            alt.value('#b0b0b0')
        ),
        opacity=alt.condition(
            alt.datum.title == 'Blinding Lights',
            alt.value(1.0),
            alt.value(0.65)
        ),
        tooltip=[
            alt.Tooltip('title:N', title='Song'),
            alt.Tooltip('start:T', title='Run Start', format='%Y-%m-%d'),
            alt.Tooltip('end:T', title='Run End', format='%Y-%m-%d'),
            alt.Tooltip('duration_days:Q', title='Duration (days)'),
            alt.Tooltip('n_runs:Q', title='Total Top-10 Runs'),
        ]
    )

    label_df = runs_df.sort_values('end').groupby('title').last().reset_index()
    labels = alt.Chart(label_df).mark_text(align='left', dx=6, fontSize=11).encode(
        x='end:T',
        y=alt.Y('title:N', sort=sort_order),
        text=alt.Text('n_runs:Q', format='d'),
        color=alt.condition(
            alt.datum.title == 'Blinding Lights',
            alt.value('#E63946'),
            alt.value('#888888')
        )
    )

    return (bars + labels).properties(
        width=900,
        height=520,
        title=alt.TitleParams(
            text='Top-10 Runs per Song (U.S. Chart) — Gaps > 14 Days Count as a New Run',
            fontSize=16,
            anchor='middle'
        )
    )
