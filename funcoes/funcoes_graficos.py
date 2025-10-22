import plotly.graph_objects as go
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

####################################################################################################################################################################

# def plot_resultado_minimo(res_nv_minimo, coluna):

#     if coluna == '90%PHFT REFERENCIA':
#         y = 'PHFT REAL'
#         yaxis_title = 'PHFT %'
#         name = '90%PHFT REF'
#     elif coluna == 'TOMAX REF + ΔTOMAX':
#         y = 'TOMAX REAL'
#         yaxis_title = 'TEMPERATURA OPERATIVA (°C)'
#         name = 'TOMAX REF + ΔTOMAX'
#     elif coluna == 'TOMIN REF - ΔTOMIN':
#         y = 'TOMIN REAL'
#         yaxis_title = 'TEMPERATURA OPERATIVA (°C)'
#         name = 'TOMIN REF - ΔTOMIN'

#     fig = go.Figure()

#     fig.add_trace(
#             go.Scatter(
#                 x=res_nv_minimo['Unidades'],
#                 y=res_nv_minimo[coluna], # '90%PHFT REFERENCIA'
#                 marker = dict(color='darkorange'),
#                 mode = "lines+markers",
#                 name=name,
#                 line=dict(color='darkorange')
#             ))

#     fig.add_trace(
#             go.Bar(
#                 x=res_nv_minimo['Unidades'],
#                 y=res_nv_minimo[y],
#                 name=y,
#                 marker_color = 'lightblue'
#             ))

#     fig.update_layout(
#         hovermode="x unified",
#         yaxis_title=yaxis_title,
#         xaxis_title='Unidades',
#         font_family='Poppins',
#         template='plotly_white',
#         xaxis=dict(
#             tickmode='array',
#             tickvals=res_nv_minimo['Unidades'],
#             tickangle=90
#         ),
#         hoverlabel=dict(font_size=15)
#     )

#     return fig

# ####################################################################################################################################################################

def plot_resultado_minimo(res_nv_minimo, coluna):

    if coluna == '90%PHFT REFERENCIA':
        y = 'PHFT REAL'
        yaxis_title = 'PHFT %'
        name = '90%PHFT REF'
        # Condição: PHFT REAL > 90%PHFT REFERENCIA
        bar_colors = [
            'red' if real < ref else 'lightblue'
            for real, ref in zip(res_nv_minimo[y], res_nv_minimo[coluna])
        ]
    elif coluna == 'TOMAX REF + ΔTOMAX':
        y = 'TOMAX REAL'
        yaxis_title = 'TEMPERATURA OPERATIVA (°C)'
        name = 'TOMAX REF + ΔTOMAX'
        # Condição: TOMAX REAL > TOMAX REF + ΔTOMAX
        bar_colors = [
            'red' if real > ref else 'lightblue'
            for real, ref in zip(res_nv_minimo[y], res_nv_minimo[coluna])
        ]
    elif coluna == 'TOMIN REF - ΔTOMIN':
        y = 'TOMIN REAL'
        yaxis_title = 'TEMPERATURA OPERATIVA (°C)'
        name = 'TOMIN REF - ΔTOMIN'
        # Condição: TOMIN REAL < TOMIN REF - ΔTOMIN
        bar_colors = [
            'red' if real < ref else 'lightblue'
            for real, ref in zip(res_nv_minimo[y], res_nv_minimo[coluna])
        ]
    else:
        y = ''
        yaxis_title = ''
        name = ''
        bar_colors = 'lightblue'

    fig = go.Figure()

    # Linha de referência
    fig.add_trace(
        go.Scatter(
            x=res_nv_minimo['Unidades'],
            y=res_nv_minimo[coluna],
            marker=dict(color='darkorange'),
            mode="lines+markers",
            name=name,
            line=dict(color='darkorange')
        )
    )

    # Barras
    fig.add_trace(
        go.Bar(
            x=res_nv_minimo['Unidades'],
            y=res_nv_minimo[y],
            name=y,
            marker_color=bar_colors
        )
    )

    fig.update_layout(
        hovermode="x unified",
        yaxis_title=yaxis_title,
        xaxis_title='Unidades',
        font_family='Poppins',
        template='plotly_white',
        xaxis=dict(
            tickmode='array',
            tickvals=res_nv_minimo['Unidades'],
            tickangle=90
        ),
        hoverlabel=dict(font_size=15)
    )

    return fig

####################################################################################################################################################################

def plot_resultado_inter_sup(res_nv_inter_sup):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
                x=res_nv_inter_sup['Unidades'].values,
                y=res_nv_inter_sup['RED CGTT MIN SUPERIROR'].values,
                marker = dict(color = 'green'),
                mode = "lines+markers",
                name='RED CGTT MIN SUPERIROR',
                line=dict(color='green')
            ))

    fig.add_trace(
            go.Scatter(
                x=res_nv_inter_sup['Unidades'].values,
                y=res_nv_inter_sup['RED CGTT MIN INTERMEDIARIO'].values,
                marker = dict(color = 'rgb(255, 192, 0)'),
                mode = "lines+markers",
                name='RED CGTT MIN INTERMEDIARIO',
                line=dict(color='rgb(255, 192, 0)')
            ))

    fig.add_trace(
            go.Bar(
                x=res_nv_inter_sup['Unidades'].values,
                y=res_nv_inter_sup['REDUCAO CARGA TERMICA TOTAL'].values,
                name='REDUCAO CARGA TERMICA TOTAL',
                marker_color = 'lightblue'
            ))
    
    fig.update_layout(
        hovermode="x unified",
        yaxis_title='Redução da carga térmica total (%)',
        xaxis_title='Unidades',
        font_family='Poppins',
        template='plotly_white',
        xaxis=dict(
            tickmode='array',
            tickvals=res_nv_inter_sup['Unidades'],
            tickangle=90
        ),
        hoverlabel=dict(font_size=15)
    )

    return fig

####################################################################################################################################################################

def plot_resultado_minimo_matplotlib(res_nv_minimo, coluna, filename, salvar_fig=True):
    
    if coluna == '90%PHFT REFERENCIA':
        y = 'PHFT REAL'
        yaxis_title = 'PHFT %'
        name = '90%PHFT REF'
        cores = ['lightblue' if real > ref else 'red'
                 for real, ref in zip(res_nv_minimo[y], res_nv_minimo[coluna])]

    elif coluna == 'TOMAX REF + ΔTOMAX':
        y = 'TOMAX REAL'
        yaxis_title = 'TEMPERATURA OPERATIVA (°C)'
        name = 'TOMAX REF + ΔTOMAX'
        cores = ['lightblue' if real <= ref else 'red'
                 for real, ref in zip(res_nv_minimo[y], res_nv_minimo[coluna])]

    elif coluna == 'TOMIN REF - ΔTOMIN':
        y = 'TOMIN REAL'
        yaxis_title = 'TEMPERATURA OPERATIVA (°C)'
        name = 'TOMIN REF - ΔTOMIN'
        cores = ['lightblue' if real >= ref else 'red'
                 for real, ref in zip(res_nv_minimo[y], res_nv_minimo[coluna])]
        
    elif coluna == 'ΔPHFTmin':
        y = 'ΔPHFT'
        yaxis_title = ''
        name = 'ΔPHFTmin'
        cores = ['lightblue' if real >= ref else 'red'
                 for real, ref in zip(res_nv_minimo[y], res_nv_minimo[coluna])]
        
    unidades = res_nv_minimo['Unidades']
    x = np.arange(len(unidades))

    fig, ax = plt.subplots(figsize=(25, 8))
    ax.bar(x, res_nv_minimo[y], color=cores, label=y, edgecolor='black')
    ax.plot(x, res_nv_minimo[coluna], color='#e76f51', marker='o', label=name)

    ax.set_ylabel(yaxis_title, fontsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.tick_params(axis='x', labelsize=12)
    ax.set_xlabel('Unidades', fontsize=12)
    ax.set_title(f'{name} x {y}', fontsize=18, loc='left', fontweight='bold')
    ax.set_xticks(x[::2])
    ax.set_xticklabels(unidades[::2], rotation=90)
    ax.legend(loc='lower left', ncols=2)
    # ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), borderaxespad=0.)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Inserção do logo
    try:
        logo_path = "assets/logo-mit.png"
        logo_img = mpimg.imread(logo_path)
        imagebox = OffsetImage(logo_img, zoom=0.115)
        ab = AnnotationBbox(imagebox, (1, 1), xycoords='axes fraction', frameon=False, box_alignment=(0.9, 1))
        ax.add_artist(ab)
    except FileNotFoundError:
        print(f"[AVISO] Logo não encontrado em: {logo_path}")

    if salvar_fig:
        os.makedirs("outputs", exist_ok=True)
        fig.savefig(f"outputs/{filename}.png", bbox_inches='tight')
        plt.close(fig)

    return

####################################################################################################################################################################

def plot_resultado_inter_sup_matplotlib(res_nv_inter_sup, filename, salvar_fig=True):
    
    unidades = res_nv_inter_sup['Unidades'].values
    x = np.arange(len(unidades))

    y1 = res_nv_inter_sup['RED CGTT MIN SUPERIROR'].values
    y2 = res_nv_inter_sup['RED CGTT MIN INTERMEDIARIO'].values
    y_bar = res_nv_inter_sup['REDUCAO CARGA TERMICA TOTAL'].values

    fig, ax = plt.subplots(figsize=(25, 8))

    # Barras
    ax.bar(x, y_bar, color='lightblue', label='REDUCAO CARGA TERMICA TOTAL', edgecolor='black')

    # Linhas
    ax.plot(x, y1, color='green', marker='o', label='RED CGTT MIN SUPERIROR')
    ax.plot(x, y2, color='orange', marker='o', label='RED CGTT MIN INTERMEDIARIO')

    ax.set_ylabel('Redução da carga térmica total (%)', fontsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.tick_params(axis='x', labelsize=12)
    ax.set_xlabel('Unidades', fontsize=12)
    ax.set_title('Redução da Carga Térmica - Intermediário e Superior', fontsize=18, loc='left', fontweight='bold')
    ax.set_xticks(x[::2])
    ax.set_xticklabels(unidades[::2], rotation=90)
    ax.legend(loc='lower left', ncols=2)
    # ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), borderaxespad=0.)
    ax.grid(True, linestyle='--', alpha=0.5)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Inserção do logo
    try:
        logo_path = "assets/logo-mit.png"
        logo_img = mpimg.imread(logo_path)
        imagebox = OffsetImage(logo_img, zoom=0.115)
        ab = AnnotationBbox(imagebox, (1, 1), xycoords='axes fraction', frameon=False, box_alignment=(0.9, 1))
        ax.add_artist(ab)
    except FileNotFoundError:
        print(f"[AVISO] Logo não encontrado em: {logo_path}")

    if salvar_fig:
        os.makedirs("outputs", exist_ok=True)
        fig.savefig(f"outputs/{filename}.png", bbox_inches='tight')
        plt.close(fig)

    return 

####################################################################################################################################################################
