from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import re
from dash.exceptions import PreventUpdate
import requests
import pandas as pd
import json
from requests.structures import CaseInsensitiveDict

index_app = Dash(__name__,
                     meta_tags=[{'name':'viewport',
                                 'content': 'width=device-width, initial-scale=1.0'}],
                     title="OA Tracker", update_title=None, external_stylesheets=[dbc.themes.BOOTSTRAP], url_base_pathname="/", suppress_callback_exceptions=True)

index_app.layout = html.Div([
    html.Div([
        dbc.Label("Enter an ORCID: ", style={'font-weight': 'bold', 'display':'inline-block'}),
        dbc.Input(id="orcid", placeholder="Use xxxx-xxxx-xxxx-xxxx format:", type='text', style={'marginLeft':'10px', 'height': '50px', 'width': '30%', 'display':'inline-block'}),
        dbc.Alert(id="alert", color="danger", style={'display': "None"}),
        html.Br(),
        dbc.Button("Search", id="search", style={'marginTop':'10px', 'margin': 'auto', 'display': 'flex'})
    ], style={'text-align': 'center', 'margin-left': 'auto', 'margin-right': 'auto'}),

    html.Div(id='results')
])

@index_app.callback(
    [Output("results", "children"), Output("alert", "children"), Output("alert", "style")],
    Input("search", "n_clicks"),
    State("orcid", "value")
    , prevent_initial_call=True)
def searchorcid(n, orcid):
    if(n is None):
        raise PreventUpdate
    else:

        chex = re.compile(r'\d{4}-\d{4}-\d{4}')
        if(chex.match(orcid)):
            orcid_org_web_address = "https://pub.orcid.org/v3.0/"
            orcid_org_link =  orcid_org_web_address + str(orcid)
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            resp2 = requests.get(orcid_org_link, headers=headers)
            data2 = resp2.json()#str(resp2.json())

            uri = data2['orcid-identifier']['uri']
            name = data2['person']['name']['given-names']['value']
            fam_name = data2['person']['name']['family-name']['value']
            visibility = data2['person']['name']['visibility']
            depart = data2['activities-summary']['educations']['affiliation-group'][0]['summaries'][0]['education-summary']['department-name']
            organization = data2['activities-summary']['educations']['affiliation-group'][0]['summaries'][0]['education-summary']['organization']['name']
            address = data2['activities-summary']['educations']['affiliation-group'][0]['summaries'][0]['education-summary']['organization']['address']['region']
            roletitle = data2['activities-summary']['educations']['affiliation-group'][0]['summaries'][0]['education-summary']['role-title']

            name = str(name) + " " + str(fam_name)
            data = [uri, name, roletitle, visibility, depart, organization, address]
            df = pd.DataFrame([data],
                              columns=['source-orcid', "Name", 'Role Title', "Visibility", "Department", "Organization", 'Address'])

            table = dbc.Table.from_dataframe(df, bordered=True)
                                             #style={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'})
            return table, "", {'display':'None'},

        else:
            msg = "Incorrect ORCID format"
            return "", msg, {'display':'block'},




if __name__ == "__main__":
    index_app.run_server()