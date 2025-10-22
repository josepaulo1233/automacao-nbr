import pandas as pd
import numpy as np

#######################################################################################

def horas_ocupadas(df, tipo):
    
    if tipo == 'dorm':
        horas_ocup = 3650
        horainf = 22
        horasup = 7
        tipo_filter ='DORM|SUITE'
        
    elif tipo == 'sala':
        horas_ocup = 2920
        horainf = 14
        horasup = 21
        tipo_filter = tipo.upper()
        
    elif tipo == 'studio':
        horas_ocup = 3650 + 2920
        horainf = 14
        horasup = 7
        tipo_filter = tipo.upper()
    
    if len(df.filter(regex=tipo_filter).columns) != 0:
    
        dff = df.copy()

        ocups = []
        for hora in dff.index:
            
            if tipo == 'dorm' or tipo == 'studio' or tipo == 'suite':

                if hora.hour >= horainf or hora.hour <= horasup:
                    ocup = 1
                else:
                    ocup = 0

            if tipo == 'sala':

                if hora.hour >= horainf and hora.hour <= horasup:
                    ocup = 1
                else:
                    ocup = 0
                    
            ocups.append(ocup)

        dff.loc[:, 'horas_ocupadas'] = ocups
        dff_hrs_ocups = dff[dff['horas_ocupadas'] == 1]
        
        if len(dff_hrs_ocups) != horas_ocup:
            
            print('O valor de horas ocupadas esta errado')
            
            return
        
        else:
        
            return dff_hrs_ocups
    
    else:
        
        return None
    
#######################################################################################
    
def calc_phft_t0min_t0max_index(df, tbulbo):

    if df is not None:
    
        if tbulbo <= 25:
            
            interinf = 18
            intersup = 26
            
        if tbulbo > 25 and tbulbo <= 27:
            
            interinf = -100
            intersup = 28
            
        if tbulbo > 27:   
            
            interinf = -100
            intersup = 30
        
        dff = df.copy()
        
        len_dff = len(dff)
        
        for coluna in dff.columns[1:-1]:
            
            t0max = dff[coluna].max()
            t0min = dff[coluna].min()
            
            check = []
            
            for temp in dff[coluna]:
                
                if temp > interinf and temp < intersup:

                    check.append(1) 

            dff.loc['PHFT', coluna] = (np.sum(check)/len_dff)*100
            dff.loc['TOMAX', coluna] = t0max
            dff.loc['TOMIN', coluna] = t0min
            
        dff.dropna(axis=1, inplace=True)
            
        return dff   
    
    else:

        return None
    
#######################################################################################

def gera_df_final(df, pavimentacao):

    #df = pd.read_csv(file)

    df.index = pd.date_range(start='1/1/2000 01:00:00', end='12/31/2000', freq='h') 
    df_dorm = df.filter(regex='DORM|Drybulb|SUITE')
    df_sala = df.filter(regex='SALA|Drybulb')
    df_studio = df.filter(regex='STUDIO|Drybulb')
    temp_bulboseco_anual_mean = df['Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)'].mean()

    df_dorm_ocup = horas_ocupadas(df_dorm, 'dorm')
    df_sala_ocup = horas_ocupadas(df_sala, 'sala')   
    df_studio_ocup = horas_ocupadas(df_studio, 'studio') 

    sala = calc_phft_t0min_t0max_index(df_sala_ocup,  temp_bulboseco_anual_mean)
    dorm = calc_phft_t0min_t0max_index(df_dorm_ocup, temp_bulboseco_anual_mean)
    studio = calc_phft_t0min_t0max_index(df_studio_ocup, temp_bulboseco_anual_mean)

    dfs = []

    for dataframes in sala, dorm, studio:
        # print(dataframes)
        if dataframes is not None:
            dfs.append(dataframes[-3:])

    df_concat = pd.concat(dfs, axis=1)
    
    if pavimentacao == 'unifamiliar':

        ambientes = [x.split(':')[1] for x in df_concat.columns]
        unidades = [x.split('X')[0] if 'X' in x.upper() else x.split(':')[0] for x in df_concat.columns] #[x.split(':')[0] for x in df_concat.columns]

    if pavimentacao == 'multifamiliar':

        unidades = [x.split(':')[0] + x.split(':')[1].split('X')[0] + x.split(':')[1].split('X')[1] for x in df_concat.columns]
        ambientes = [x.split(':')[1].split('X')[-1] for x in df_concat.columns]

    df_concat = df_concat.T
    df_concat['ambientes'] = ambientes
    df_concat['Unidades'] = unidades
    df_concat.reset_index(inplace=True)
    df_concat = df_concat[df_concat.columns[1:]]
    
    phft_medio = df_concat.groupby(['Unidades'])['PHFT'].mean()
    t0max_max = df_concat.groupby(['Unidades'])['TOMAX'].max()
    t0min_min = df_concat.groupby(['Unidades'])['TOMIN'].min()
    index_values = pd.DataFrame(pd.concat([phft_medio, t0max_max, t0min_min], axis=1))
        
    # Agrupando por ambiente
    phft_medio_amb = df_concat.groupby(['ambientes', 'Unidades'])['PHFT'].mean()
    t0max_max_amb = df_concat.groupby(['ambientes', 'Unidades'])['TOMAX'].max()
    t0min_min_amb = df_concat.groupby(['ambientes', 'Unidades'])['TOMIN'].min()
    index_values_amb = pd.DataFrame(pd.concat([phft_medio_amb, t0max_max_amb, t0min_min_amb], axis=1))

    return index_values, index_values_amb

#######################################################################################

def deltatmax(df, df_tipologia, df_pavimento):

    for index, valor, pavimento in zip(df.index, df_tipologia, df_pavimento):

        valor = valor.upper()

        if valor == 'UNIFAMILIAR':

            df.loc[index, 'ΔTOMAX'] = 2 

        elif valor == 'MULTIFAMILIAR' and pavimento == 'COBERTURA':

            df.loc[index, 'ΔTOMAX'] = 2 

        else:

            df.loc[index, 'ΔTOMAX'] = 1


#         if valor == 'UNIFAMILIAR' or valor == 'MULTIFAMILIAR NA COBERTURA' or valor == 'COBERTURA':

#             df.loc[index, 'ΔTOMAX'] = 2 
        
#         else:

#            df.loc[index, 'ΔTOMAX'] = 1

    return

#######################################################################################

def deltatmin(df, df_zona):

    for index, valor in zip(df.index, df_zona):
        
        if int(valor) <= 4 :

            df.loc[index ,'ΔTOMIN'] = 1
        
        else:

            df.loc[index ,'ΔTOMIN'] = 0   

    return

#######################################################################################

def criterio_tomax(df, df_real_tomax, df_ref_tomax, df_deltatmax):

    for index, valor_real, valor_ref, deltatmax in zip(df.index, df_real_tomax,  df_ref_tomax, df_deltatmax):

        if valor_real <= valor_ref + deltatmax:

            df.loc[index, 'CRITERIO TOMAX'] = 'ATENDE'
        
        else:

            df.loc[index, 'CRITERIO TOMAX'] = 'NAO ATENDE'

    return

#######################################################################################

def criterio_tomin(df, df_real_tomin, df_ref_tomin, df_deltatmin):

    for index, valor_real, valor_ref, deltatmin in zip(df.index, df_real_tomin, df_ref_tomin, df_deltatmin):

        if deltatmin == 0:

            df.loc[index, 'CRITERIO TOMIN'] = 'NAO HÁ'

        else:
            
            if valor_real >= valor_ref - deltatmin:

                df.loc[index, 'CRITERIO TOMIN'] = 'ATENDE'
            
            else:

                df.loc[index, 'CRITERIO TOMIN'] = 'NAO ATENDE'

    return

#######################################################################################

def criterio_phft(df, df_phft):

    for index, pfht in zip(df.index, df_phft):
        
        if pfht > 0:

            df.loc[index, 'CRITERIO PHFT'] = 'ATENDE'
        
        else:

            df.loc[index, 'CRITERIO PHFT'] = 'NAO ATENDE'

#######################################################################################

def atendimento_minimo(df, df_criterio_tomax, df_criterio_tomin, df_criterio_phft, df_zona):

    for index, criteirotmax, criteriotmin, criteriophft, zona in zip(df.index, df_criterio_tomax, df_criterio_tomin, df_criterio_phft, df_zona):
        
        if int(zona) <= 4: 

            if criteirotmax == criteriotmin == criteriophft == 'ATENDE':

                df.loc[index, 'ATENDIMENTO MINIMO'] = 'ATENDE O MINIMO'

            else: 

                df.loc[index, 'ATENDIMENTO MINIMO'] = 'NAO ATENDE O MINIMO'

        else:

            if criteirotmax == criteriophft == 'ATENDE':
        
                df.loc[index, 'ATENDIMENTO MINIMO'] = 'ATENDE O MINIMO'

            else: 

                df.loc[index, 'ATENDIMENTO MINIMO'] = 'NAO ATENDE O MINIMO'

    return 

#######################################################################################

def delta_phftmin(df, df_ref_phft, df_tipologia, df_pavimento):

    for index, valor, tipologia, tipologia_secundaria in zip(df.index, df_ref_phft, df_tipologia, df_pavimento):
        
        if valor >= 70:

            df.loc[index, 'ΔPHFTmin'] = 0

        else:

            if tipologia == 'UNIFAMILIAR':

                df.loc[index, 'ΔPHFTmin'] = 45 - 0.58 * valor

            if tipologia == 'MULTIFAMILIAR':

                if tipologia_secundaria == 'TERREO':

                    df.loc[index, 'ΔPHFTmin'] = 22 - 0.21 * valor

                if tipologia_secundaria == 'TIPO':
        
                    df.loc[index, 'ΔPHFTmin'] = 28 - 0.27 * valor

                if tipologia_secundaria == 'COBERTURA':
            
                    df.loc[index, 'ΔPHFTmin'] = 18 - 0.18 * valor

#######################################################################################

def atendimento_intermediario_delta_phft(df, df_delta_phft, df_delta_phftmin):

    for index, delta_phft, delta_phftmin in zip(df.index, df_delta_phft, df_delta_phftmin): 
        
        if delta_phft >= delta_phftmin:

            df.loc[index, 'CRITERIO PHFT INTERMEDIARIO'] = 'ATENDE'
        
        else:

            df.loc[index, 'CRITERIO PHFT INTERMEDIARIO'] = 'NAO ATENDE'

####################################################################################### 

def gera_df_temperatura_e_cargatermica(df_temp, df_crg_term, pavimentacao):
    
    index_rage = pd.date_range(start='1/1/2000 01:00:00', end='12/31/2000', freq='h')
    
    # Temperatura 

    # df_temp = pd.read_csv(file_temperatura)

    # if len(df_temp) != 8760:
    
    #     return st.error(f'Não há o total de horas anuais no arquivo de temperatura. Esperado 8760 horas, recebido {len(df_temp)}')
    
    # else:

    df_temp.index = index_rage
    df_temp_dorm = df_temp.filter(regex='DORM|SUITE')
    df_temp_sala = df_temp.filter(regex='SALA')
    df_temp_studio = df_temp.filter(regex='STUDIO')
    
    df_temp_dorm_ocup = horas_ocupadas(df_temp_dorm, 'dorm')
    df_temp_sala_ocup = horas_ocupadas(df_temp_sala, 'sala')
    df_temp_studio_ocup = horas_ocupadas(df_temp_studio, 'studio')
    
    dfs_temp = []
    if df_temp_dorm_ocup is not None:
        df_temp_dorm_ocup = df_temp_dorm_ocup.loc[:, df_temp_dorm_ocup.columns != 'horas_ocupadas']
        dfs_temp.append(df_temp_dorm_ocup)
    
    if df_temp_sala_ocup is not None:
        df_temp_sala_ocup = df_temp_sala_ocup.loc[:, df_temp_sala_ocup.columns != 'horas_ocupadas']
        dfs_temp.append(df_temp_sala_ocup)
    
    if df_temp_studio_ocup is not None:
        df_temp_studio_ocup = df_temp_studio_ocup.loc[:, df_temp_studio_ocup.columns != 'horas_ocupadas']
        dfs_temp.append(df_temp_studio_ocup)

    # Carga termica
    
    # df_crg_term = pd.read_csv(file_carga_termica)

    # if len(df_crg_term) != 8760:
        
    #     return st.error(f'Não há o total de horas anuais no arquivo de carga térmica. Esperado 8760 horas, recebido {len(df_crg_term)}')    

    # else:

    df_crg_term.index = index_rage
    df_crg_term_dorm = df_crg_term.filter(regex='DORM|SUITE')
    df_crg_term_sala = df_crg_term.filter(regex='SALA')
    df_crg_term_studio = df_crg_term.filter(regex='STUDIO')
    
    df_crg_term_dorm_ocup = horas_ocupadas(df_crg_term_dorm, 'dorm')
    df_crg_term_sala_ocup = horas_ocupadas(df_crg_term_sala, 'sala')
    df_crg_term_studio_ocup = horas_ocupadas(df_crg_term_studio, 'studio')
    
    dfs_crg_term_resf = [] 
    dfs_crg_term_aqcm = [] 
    
    if df_crg_term_dorm_ocup is not None:
        df_crg_term_dorm_ocup = df_crg_term_dorm_ocup.loc[:, df_crg_term_dorm_ocup.columns != 'horas_ocupadas']
        df_crg_term_dorm_ocup_resf = df_crg_term_dorm_ocup.filter(regex='Cooling')
        df_crg_term_dorm_ocup_aqcm = df_crg_term_dorm_ocup.filter(regex='Heating')
        dfs_crg_term_resf.append(df_crg_term_dorm_ocup_resf)
        dfs_crg_term_aqcm.append(df_crg_term_dorm_ocup_aqcm)
    
    if df_crg_term_sala_ocup is not None:
        df_crg_term_sala_ocup = df_crg_term_sala_ocup.loc[:, df_crg_term_sala_ocup.columns != 'horas_ocupadas']
        df_crg_term_sala_ocup_resf = df_crg_term_sala_ocup.filter(regex='Cooling')
        df_crg_term_sala_ocup_aqcm = df_crg_term_sala_ocup.filter(regex='Heating')
        dfs_crg_term_resf.append(df_crg_term_sala_ocup_resf)
        dfs_crg_term_aqcm.append(df_crg_term_sala_ocup_aqcm)
    
    if df_crg_term_studio_ocup is not None:
        df_crg_term_studio_ocup = df_crg_term_studio_ocup.loc[:, df_crg_term_studio_ocup.columns != 'horas_ocupadas']
        df_crg_term_studio_ocup_resf = df_crg_term_studio_ocup.filter(regex='Cooling')
        df_crg_term_studio_ocup_aqcm = df_crg_term_studio_ocup.filter(regex='Heating')
        dfs_crg_term_resf.append(df_crg_term_studio_ocup_resf)
        dfs_crg_term_aqcm.append(df_crg_term_studio_ocup_aqcm)
        
    # checando as quantidades ...
    
    if df_temp_dorm_ocup is not None and df_crg_term_dorm_ocup is not None:
    
        if len(df_temp_dorm_ocup.columns)*2 != len(df_crg_term_dorm_ocup.columns):
            print('A quantidade de colunas do dormitório esta errada')
            return None

    if df_temp_dorm_ocup is not None and df_crg_term_dorm_ocup is not None:
    
        if len(df_temp_dorm_ocup.columns)*2 != len(df_crg_term_dorm_ocup.columns):
            print('A quantidade de colunas da sala esta errada')
            return None

    if df_crg_term_studio_ocup is not None and df_temp_studio_ocup is not None:
    
        if len(df_temp_studio_ocup.columns)*2 != len(df_crg_term_studio_ocup.columns):
            print('A quantidade de colunas do studio esta errada')
            return None
        
    # Considerando a carga termica certa na unidade ... 
                    
    for df_temperatura, df_carga_termica_rsf, df_carga_termica_aqcm in zip(dfs_temp, dfs_crg_term_resf, dfs_crg_term_aqcm):
        
        for col_temp in df_temperatura:
            
            valores_aquecimento = []
            valores_resfriamento = []
            
            nome_unidade = col_temp.split(':')
            nome_unidade = nome_unidade[0] + ':' + nome_unidade[1]
            coluna_resfriamento = nome_unidade + 'CARGA_CONSIDERADA_RESFRIAMENTO'
            coluna_aquecimento = nome_unidade + 'CARGA_CONSIDERADA_AQUECIMENTO'

            for val_temp, val_aqcm, val_resf in zip(df_temperatura.filter(regex=nome_unidade).values, df_carga_termica_aqcm.filter(regex=nome_unidade).values, df_carga_termica_rsf.filter(regex=nome_unidade).values):

                if val_temp[0] >= 18 and val_temp[0] <= 26:

                    valores_aquecimento.append(np.nan)
                    valores_resfriamento.append(np.nan)

                if val_temp[0] >= 26:

                    valores_aquecimento.append(np.nan)
                    valores_resfriamento.append(val_resf[0])

                if val_temp[0] <= 18:

                    valores_resfriamento.append(np.nan)
                    valores_aquecimento.append(val_aqcm[0])
                    
            df_temperatura.loc[:, coluna_resfriamento] = valores_resfriamento
            df_temperatura.loc[:, coluna_aquecimento] = valores_aquecimento
            
    
    # Somando as cargas de resfriamento e aquecimento por ambiente

    df_total = []
    
    for df in dfs_temp:
        
        dff = df.copy()
        dff = pd.DataFrame(dff.filter(regex='CARGA').sum())
        index = [x.split('CARGA')[0] for x in dff.index]
        index = list(dict.fromkeys(index))
        dff2 = pd.DataFrame()
        dff2.index = index
        dff2['SOMA_CARGA_RESFRIAMENTO'] = dff.T.filter(regex='RESFRIAMENTO').values[0]
        dff2['SOMA_CARGA_AQUECIMENTO'] = dff.T.filter(regex='AQUECIMENTO').values[0]
        
        df_total.append(dff2)
        
    # Agrupando e somando as cargas de resfriamento e aquecimento
    df_concat = pd.concat(df_total)

    if pavimentacao == 'unifamiliar':

        ambientes = [x.split(':')[1] for x in df_concat.index]
        unidades = [x.split('X')[0] if 'X' in x.upper() else x.split(':')[0] for x in df_concat.index] #[x.split(':')[0] for x in df_concat.index]

    if pavimentacao == 'multifamiliar':

        unidades = [x.split(':')[0] + x.split(':')[1].split('X')[0] + x.split(':')[1].split('X')[1] for x in df_concat.index]
        ambientes = [x.split(':')[1].split('X')[-1] for x in df_concat.index]        
    
    df_concat['ambientes'] = ambientes
    df_concat['Unidades'] = unidades

    # Por unidades
    soma_unidade_resfriamento = df_concat.groupby(['Unidades'])['SOMA_CARGA_RESFRIAMENTO'].sum()
    soma_unidade_aquecimento = df_concat.groupby(['Unidades'])['SOMA_CARGA_AQUECIMENTO'].sum()

    df_final = pd.DataFrame()
    df_final.index = soma_unidade_resfriamento.index
    df_final['SOMA CARGA RESFRIAMENTO'] = soma_unidade_resfriamento
    df_final['SOMA CARGA AQUECIMENTO'] = soma_unidade_aquecimento
    df_final['SOMA CARGA TOTAL'] = df_final.sum(axis=1)

    # Por ambientes
    soma_unidade_resfriamento_ambiente = df_concat.groupby(['ambientes', 'Unidades'])['SOMA_CARGA_RESFRIAMENTO'].sum()
    soma_unidade_aquecimento_ambiente = df_concat.groupby(['ambientes', 'Unidades'])['SOMA_CARGA_AQUECIMENTO'].sum()

    df_final_ambiente = pd.DataFrame()
    df_final_ambiente.index = soma_unidade_resfriamento_ambiente.index
    df_final_ambiente['SOMA CARGA RESFRIAMENTO'] = soma_unidade_resfriamento_ambiente
    df_final_ambiente['SOMA CARGA AQUECIMENTO'] = soma_unidade_aquecimento_ambiente
    df_final_ambiente['SOMA CARGA TOTAL'] = df_final_ambiente.sum(axis=1)        
        
    return df_final, df_final_ambiente

####################################################################################### 

def reducao_carga_termica_minima_intermediaria(df, df_pft_ref, df_cgtt_area, df_tipologia, df_pavimentacao):

    for index, phft_ref, cgtt_area, tipologia, pavimentacao in zip(df.index, df_pft_ref, df_cgtt_area, df_tipologia, df_pavimentacao): 

        # print(index)
        # print(phft_ref)
        # print(cgtt_area)

        if phft_ref < 70:

            df.loc[index, 'RED CGTT MIN INTERMEDIARIO'] = 0

        if phft_ref >= 70 and cgtt_area < 100:

            if tipologia == 'UNIFAMILIAR':

                df.loc[index, 'RED CGTT MIN INTERMEDIARIO'] = 17

            if tipologia == 'MULTIFAMILIAR':

                if pavimentacao == 'TERREO' or pavimentacao == 'COBERTURA':

                    df.loc[index, 'RED CGTT MIN INTERMEDIARIO'] = 15

                if pavimentacao == 'TIPO':

                    df.loc[index, 'RED CGTT MIN INTERMEDIARIO'] = 22

    return

#######################################################################################

def reducao_carga_termica_minima_superior(df, df_cgtt_area, df_tipologia, df_pavimentacao):
    
    for index, cgtt_area, tipologia, pavimentacao in zip(df.index, df_cgtt_area, df_tipologia, df_pavimentacao): 

        if cgtt_area < 100:

            if tipologia == 'UNIFAMILIAR':

                df.loc[index, 'RED CGTT MIN SUPERIROR'] = 35

            if tipologia == 'MULTIFAMILIAR':

                if pavimentacao == 'TERREO' or pavimentacao == 'COBERTURA':

                    df.loc[index, 'RED CGTT MIN SUPERIROR'] = 30

                if pavimentacao == 'TIPO':

                    df.loc[index, 'RED CGTT MIN SUPERIROR'] = 45

        else:

            if tipologia == 'UNIFAMILIAR':
    
                df.loc[index, 'RED CGTT MIN SUPERIROR'] = 55

            if tipologia == 'MULTIFAMILIAR':

                if pavimentacao == 'TERREO' or pavimentacao == 'COBERTURA':

                    df.loc[index, 'RED CGTT MIN SUPERIROR'] = 40

                if pavimentacao == 'TIPO':

                    df.loc[index, 'RED CGTT MIN SUPERIROR'] = 55

    return
    
#######################################################################################

def criterio_cgt_intermediaria(df, df_red_total, df_cgt_min_intermediaria):

    for index, red_cg_total, cgt_min_inter in zip(df.index, df_red_total, df_cgt_min_intermediaria): 

        if red_cg_total >= cgt_min_inter:

            df.loc[index, 'CRITERIO CARGA TERMICA INTERMEDIARIA'] = 'ATENDE'

        else:

            df.loc[index, 'CRITERIO CARGA TERMICA INTERMEDIARIA'] = 'NAO ATENDE'

    return

#######################################################################################

def criterio_cgt_superior(df, df_red_total, df_cgt_min_superior):

    for index, red_cg_total, cgt_min_superior in zip(df.index, df_red_total, df_cgt_min_superior): 

        if red_cg_total >= cgt_min_superior:

            df.loc[index, 'CRITERIO CARGA TERMICA SUPERIOR'] = 'ATENDE'

        else:

            df.loc[index, 'CRITERIO CARGA TERMICA SUPERIOR'] = 'NAO ATENDE'

    return

#######################################################################################

def criterio_valor(df, df_zona, df_criterio_phft, df_criterio_tomax, df_criterio_tomin, df_criterio_phft_intermediario, df_criterio_red_carga_tt_intermediario, df_criterio_red_carga_tt_superior):

    for index, zona, criterio_phft, criterio_tomax, criterio_tomin, criterio_phft_intermediario, red_criterio_carga_tt_intermediario, red_criterio_carga_tt_superior in zip(df.index, df_zona,  df_criterio_phft, df_criterio_tomax, df_criterio_tomin, df_criterio_phft_intermediario, df_criterio_red_carga_tt_intermediario, df_criterio_red_carga_tt_superior): 

        if int(zona) <=4 :

            if criterio_tomax == 'ATENDE' and criterio_tomin == 'ATENDE' and criterio_phft == 'ATENDE' and criterio_phft_intermediario == 'ATENDE' and red_criterio_carga_tt_superior == 'ATENDE':

                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'SUPERIOR'
            
            elif criterio_tomax == 'ATENDE' and criterio_tomin == 'ATENDE' and criterio_phft == 'ATENDE' and criterio_phft_intermediario == 'ATENDE' and red_criterio_carga_tt_intermediario == 'ATENDE':
    
                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'INTERMEDIARIO'            

            elif criterio_tomax == 'ATENDE' and criterio_tomin == 'ATENDE' and criterio_phft == 'ATENDE' and criterio_phft_intermediario == 'ATENDE' and red_criterio_carga_tt_intermediario == 'ATENDE':
        
                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'INTERMEDIARIO'   

            elif criterio_tomax == 'ATENDE' and criterio_tomin == 'ATENDE' and criterio_phft == 'ATENDE':
            
                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'MINIMO'   

            else:

                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'NAO ATENDE'

        else:

            if criterio_tomax == 'ATENDE' and criterio_phft == 'ATENDE' and criterio_phft_intermediario == 'ATENDE' and red_criterio_carga_tt_superior == 'ATENDE':
    
                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'SUPERIOR'
            
            elif criterio_tomax == 'ATENDE' and criterio_phft == 'ATENDE' and criterio_phft_intermediario == 'ATENDE' and red_criterio_carga_tt_intermediario == 'ATENDE':
    
                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'INTERMEDIARIO'            

            elif criterio_tomax == 'ATENDE' and criterio_phft == 'ATENDE' and criterio_phft_intermediario == 'ATENDE' and red_criterio_carga_tt_intermediario == 'ATENDE':
        
                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'INTERMEDIARIO'   

            elif criterio_tomax == 'ATENDE' and criterio_phft == 'ATENDE':
            
                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'MINIMO'   

            else:

                df.loc[index, 'NÍVEL DE ATENDIMENTO'] = 'NAO ATENDE'

    return

#######################################################################################