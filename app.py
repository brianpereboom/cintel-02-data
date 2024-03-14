import pandas as pd
import plotly.express as px
import seaborn
from shiny.express import input, ui, render
from shinywidgets import render_plotly, render_altair
import altair as alt
from palmerpenguins import load_penguins
from vega_datasets import data

penguins_df = pd.DataFrame(load_penguins())

with ui.sidebar(open="open"):
    ui.h2("Sidebar")
    ui.input_selectize("selected_attribute", "Attribute", ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"])
    ui.input_numeric("plotly_bin_count", "Plotly Bins", 20)
    ui.input_slider("seaborn_bin_count", "Seaborn Bins", 1, 100, 20)
    ui.input_checkbox_group("selected_species_list", "Species", ["Adelie", "Gentoo", "Chinstrap"], selected=["Adelie"], inline=True)
    ui.hr()
    ui.a("GitHub", href="https://github.com/brianpereboom/cintel-02-data", target="_blank")

with ui.layout_columns():
    @render.data_frame
    def table():
        return render.DataTable(penguins_df)
        
    @render.data_frame
    def grid():
        return render.DataGrid(penguins_df)
        
with ui.layout_columns():
    
    @render_plotly
    def plotly_hist():
        return px.histogram(penguins_df, x=input.selected_attribute.get(),\
            nbins=input.plotly_bin_count.get())

    @render.plot()
    def seaborn_hist():
        return seaborn.histplot(penguins_df, x=input.selected_attribute.get(),\
            bins=input.seaborn_bin_count.get())

with ui.card(full_screen=True):

    ui.card_header("Plotly Scatterplot: Species")
    
    @render_plotly
    def plotly_scatterplot():
        return px.scatter(penguins_df, x="bill_length_mm", y="bill_depth_mm", color="species")

with ui.card(full_screen=True):

    ui.card_header("Altair Ridgeline Plot")
    
    @render_altair
    def altair_ridgeline():
        source = data.seattle_weather.url
        step = 20
        overlap = 0.1
        
        return (
            alt.Chart(source, height=step).transform_timeunit(
                Month='month(date)'
            ).transform_joinaggregate(
                mean_temp='mean(temp_max)', groupby=['Month']
            ).transform_bin(
                ['bin_max', 'bin_min'], 'temp_max'
            ).transform_aggregate(
                value='count()', groupby=['Month', 'mean_temp', 'bin_min', 'bin_max']
            ).mark_area(
                interpolate='monotone',
                fillOpacity=0.8,
                stroke='lightgray',
                strokeWidth=0.5
            ).encode(
                alt.X('bin_min:Q')
                    .title('Maximum Daily Temperature (C)')
                    .axis(None),
                alt.Y('value:Q')
                    .axis(None)
                    .scale(
                        range=[step, 0]
                    ),
                alt.Fill('mean_temp:Q')
                    .scale(domain=[30, 5], scheme='redyellowblue')
                    .legend(None),
                alt.Row(
                    'Month:T',
                    title=None,
                    header=alt.Header(labelAngle=0, labelAlign='left', format='%B')
                )
            )
        )
