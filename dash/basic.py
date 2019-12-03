import dash
import dash_core_components as dcc
import dash_html_components as html

colors = {'background': '#111111',
          'text': '#7FDBFF'}

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1('WoW beau Dashboard Wow', style={'textAlign': 'center',
                                             'color': colors['text']}),
    dcc.Graph(id='example',
              figure={'data': [
                  {'x': [1, 2, 3], 'y':[4, 5, 6], 'type':'bar', 'name':'SF'}
              ],
                  'layout': {'title': 'Wow Bravo beau Dashboard',
                             'plot_bgcolor': colors['background'],
                             'paper_bgcolor': colors['text'],
                             'font': {'color': colors['text']}
                             }
              }
              )
],
                      style={'backgroundColor': colors['background']})

# Don't use the same ones than for the website
PORT = 8080

if __name__ == '__main__':
    app.run_server(port=PORT)
