import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import numpy as np

app = dash.Dash(__name__)

# 3D 격자 셀 정의
cell_size = 1
min_xyz = -3
max_xyz = 3

x_range = range(min_xyz, max_xyz + 1)
y_range = range(min_xyz, max_xyz + 1)
z_range = range(0, max_xyz + 1)

# 정수 셀의 중심점을 생성
x, y, z = np.meshgrid(x_range, y_range, z_range, indexing='ij')
x, y, z = x.flatten(), y.flatten(), z.flatten()

fig = go.Figure()

# 정수 여부를 확인하는 함수
def is_integer(value):
    return value == int(value)

# x, y, z를 정수로 반올림하여 hovertext 생성
hovertext = [
    f"x: {round(xi)}, y: {round(yi)}, z: {round(zi)}" if is_integer(xi) and is_integer(yi) and is_integer(zi) else ""
    for xi, yi, zi in zip(x, y, z)
]

# 각 셀을 Scatter3d로 렌더링
fig.add_trace(go.Scatter3d(
    x=x, y=y, z=z,
    mode='markers',
    marker=dict(size=1, color='blue', opacity=0.3),
    name='Cells',
    showlegend=False
))


# 선의 범위 정의
line_length = 4
x_range = [-line_length, line_length]
y_range = [-line_length, line_length]
z_range = [0, line_length]

# 교차선 추가
fig.add_trace(go.Scatter3d(
    x=[0, 0], y=y_range, z=[0, 0],
    mode='lines',
    line=dict(color='green', width=5),
    name='x축',
    showlegend=False,
    hoverinfo='text',
    hovertext=hovertext,
))
fig.add_trace(go.Scatter3d(
    x=x_range, y=[0, 0], z=[0, 0],
    mode='lines',
    line=dict(color='blue', width=5),
    name='y축',
    showlegend=False,
    hoverinfo='text',
    hovertext=hovertext
))
fig.add_trace(go.Scatter3d(
    x=[0, 0], y=[0, 0], z=z_range,
    mode='lines',
    line=dict(color='red', width=5),
    name='z축',
    showlegend=False,
    hoverinfo='text',
    hovertext=hovertext
))

# 카메라 초기 시점 설정
initial_camera = dict(
    eye=dict(x=1.5, y=1.5, z=1.5),  # 카메라의 초기 위치
    up=dict(x=0, y=0, z=1),         # 위쪽 방향 벡터
    center=dict(x=0, y=0, z=0)      # 카메라가 바라보는 중심
)

# 3D 공간 축 설정 및 카메라 고정
fig.update_layout(
    scene=dict(
        xaxis=dict(
            range=[min_xyz, max_xyz],
            showbackground=False,
            showgrid=True,   
            zeroline=True,   
            showline=True,    
            tickmode='array',
            tickvals=list(range(min_xyz, max_xyz + 1)),
            ticktext=[str(i) for i in range(min_xyz, max_xyz + 1)]
        ),
        yaxis=dict(
            range=[min_xyz, max_xyz],
            showbackground=False,
            showgrid=True,
            zeroline=True,
            showline=True,
            tickmode='array',
            tickvals=list(range(min_xyz, max_xyz + 1)),
            ticktext=[str(i) for i in range(min_xyz, max_xyz + 1)]
        ),
        zaxis=dict(
            range=[0, max_xyz],
            showgrid=True,
            zeroline=True,
            showline=True,
            tickmode='array',
            tickvals=list(range(0, max_xyz + 1)),
            ticktext=[str(i) for i in range(0, max_xyz + 1)]
        ),
        camera=initial_camera
    ),
    uirevision='constant',
    margin=dict(l=0, r=0, b=0, t=0)
)

# Dash 레이아웃 정의
app.layout = html.Div([
    dcc.Graph(
        id='3d-plot',
        figure=fig,
        style={'height': '90vh', 'width': '90vw'}
    ),
    dcc.Store(id='highlighted-cells', data=[]),  # 강조된 셀을 저장하는 Store
    html.Div(id='output-div', style={'padding': '20px', 'fontSize': '18px'}),
    html.Div(
        id='highlighted-cells-list',
        style={'padding': '20px', 'fontSize': '16px', 'whiteSpace': 'pre-wrap'}
    )
])


highlighted_cells = []

@app.callback(
    [Output('3d-plot', 'figure'),
     Output('highlighted-cells', 'data'),
     Output('output-div', 'children'),
     Output('highlighted-cells-list', 'children')],
    [Input('3d-plot', 'clickData')],
    [State('highlighted-cells', 'data')]
)
def highlight_clicked_cell(clickData, highlighted_cells):

    if clickData is None:
        return fig, highlighted_cells, "쌓기나무를 쌓아보세요!", "강조된 셀: 없음"
    
    # 강조된 셀을 set으로 변환 (중복 방지)
    highlighted_cells = set(map(tuple, highlighted_cells))

    # 클릭 데이터로 좌표 추출
    point = clickData['points'][0]
    x, y, z = round(point['x']), round(point['y']), round(point['z'])

    # z가 0인 경우 무시
    if z == 0:
        return fig, list(highlighted_cells), f"클릭한 셀: ({x}, {y}, {z})는 클릭할 수 없습니다 (∵z=0).", f"강조된 셀: {highlighted_cells}"
    
    # z >= 2인 경우 아래 블럭 확인
    if z >= 2 and (x, y, z - 1) not in highlighted_cells:
        return fig, list(highlighted_cells), f"클릭한 셀: ({x}, {y}, {z}) (아래 블럭이 없습니다)", f"강조된 셀:\n{chr(10).join(map(str, highlighted_cells))}"
    
    clicked_cell = (x, y, z)

    # 이미 강조된 셀인지 확인
    if clicked_cell in highlighted_cells:
        return fig, list(highlighted_cells), f"클릭한 셀: {clicked_cell} (이미 강조됨)", f"강조된 셀:\n{chr(10).join(map(str, highlighted_cells))}"

    # 강조된 셀 추가
    highlighted_cells.add(clicked_cell)

    # 강조되는 영역 정의
    bottom = [(x - 1, y - 1, z - 1), (x, y - 1, z - 1), (x, y, z - 1), (x - 1, y, z - 1)]
    top = [(x - 1, y - 1, z), (x, y - 1, z), (x, y, z), (x - 1, y, z)]

    # 테두리를 그리는 선 추가
    def add_edges(points, fig, color):
        x_coords, y_coords, z_coords = zip(*points)
        fig.add_trace(go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode='lines',
            line=dict(color=color, width=3),
            showlegend=False,
            hoverinfo='text',
            hovertext=hovertext
        ))

    # 아래쪽 테두리
    add_edges(bottom, fig, '#B58F65')  

    # 위쪽 테두리
    add_edges(top, fig, '#B58F65')    

    # 옆면 테두리 추가
    for i in range(4):
        # 아래에서 위로 연결
        edge = [bottom[i], top[i]]  
        add_edges(edge, fig, '#B58F65')

    # 각 면의 네 개의 테두리도 추가
    add_edges([bottom[0], bottom[1], top[1], top[0]], fig, '#B58F65')  # 앞면
    add_edges([bottom[1], bottom[2], top[2], top[1]], fig, '#B58F65')  # 오른쪽
    add_edges([bottom[2], bottom[3], top[3], top[2]], fig, '#B58F65')  # 뒷면
    add_edges([bottom[3], bottom[0], top[0], top[3]], fig, '#B58F65')  # 왼쪽

    # x, y, z 좌표 리스트 생성
    x_coords = [p[0] for p in bottom + top]
    y_coords = [p[1] for p in bottom + top]
    z_coords = [p[2] for p in bottom + top]

    # 각 면을 구성하는 점들의 인덱스 정의
    faces = [
        # 아래면
        (0, 1, 2), (0, 2, 3),
        # 윗면
        (4, 5, 6), (4, 6, 7),
        # 옆면 1 (앞면)
        (0, 1, 5), (0, 5, 4),
        # 옆면 2 (오른쪽)
        (1, 2, 6), (1, 6, 5),
        # 옆면 3 (뒷면)
        (2, 3, 7), (2, 7, 6),
        # 옆면 4 (왼쪽)
        (3, 0, 4), (3, 4, 7)
    ]

    # i, j, k 리스트 생성
    i, j, k = zip(*faces)

    # Mesh3d 수정
    fig.add_trace(go.Mesh3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        i=i,
        j=j,
        k=k,
        opacity=1,  # 완전히 불투명
        facecolor=[
            '#DEC091', '#DEC091',  # 아래면
            '#DEC091', '#DEC091',  # 윗면
            '#DEC091', '#DEC091',  # 옆면 1 (앞면)
            '#DEC091', '#DEC091',  # 옆면 2 (오른쪽)
            '#DEC091', '#DEC091',  # 옆면 3 (뒷면)
            '#DEC091', '#DEC091'   # 옆면 4 (왼쪽)
        ],
        name='Selected Side',
        hoverinfo='text',
        hovertext=hovertext,
        showlegend=False
    ))

    # 강조된 셀 리스트 업데이트
    highlighted_cells_list = '\n'.join([str(cell) for cell in highlighted_cells])

    return fig, list(highlighted_cells), f"클릭한 셀: {clicked_cell}", f"강조된 셀:\n{highlighted_cells_list}"

if __name__ == '__main__':
    app.run_server(debug=True)