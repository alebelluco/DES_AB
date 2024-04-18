import streamlit as st
import simpy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly_express as px
import math
from des import des

st.set_page_config(page_title="Isola 3 AD", layout='wide')
my_cmap = plt.get_cmap("Reds")
st.title("Isola 3")
st.subheader(':red[Linea AD]', divider='grey')

tab_input, tab_risultati, tab_gantt = st.tabs(['Input','Risultati','Gantt'])

st.sidebar.header("Isola 3 AD")


with tab_input:

    env = simpy.Environment()
    operatore1 = simpy.PriorityResource(env, capacity=1)
    operatore2 = simpy.PriorityResource(env, capacity=1)

    raw_partenza = st.sidebar.number_input('Inserire WIP iniziale', step=1)
    wip = {'raw':raw_partenza, 'lavorato1707':200, 'lavorato1308':0, 'finito':0 } 

    col1, col2, col3 = st.columns([1,1,2])
    n = st.sidebar.number_input('Digitare il numero di macchine',step=1)

    while n is None:
        st.stop()

    machines = []
    # Caricamento dati----------------------------------------------------------------------
    for i in range (n):
        path = st.sidebar.file_uploader(f'Caricare il file di input della macchina {i+1}')
        if path is not None:
            st.subheader(f'Macchina {i+1}', divider='red')
            df=pd.read_excel(path)
            df_ciclo = df[['Ciclo macchina','Unnamed: 1']].dropna()
            df_ciclo = df_ciclo.rename(columns={'Unnamed: 1':'Valore'})
            df_frequenza = df[['Attività in frequenza','Unnamed: 4','Unnamed: 5','Unnamed: 6']].dropna()
            df_frequenza=df_frequenza[1:]
            df_frequenza = df_frequenza.rename(columns={'Attività in frequenza':'Nome attività',
                                                        'Unnamed: 4':'Periodo',
                                                        'Unnamed: 5':'Tempo ciclo',
                                                        'Unnamed: 6':'Operatore'})
            df_utensili = df[['Tabella utensili','Unnamed: 9','Unnamed: 10','Unnamed: 11']].dropna()     
            df_utensili = df_utensili[1:]
            df_utensili = df_utensili.rename(columns={'Unnamed: 9': 'Vita utensile [pezzi]',
                                                    'Unnamed: 10':'Tempo sostituzione [min]',
                                                    'Unnamed: 11':'Tempo correzione + ricontrollo [min]' })
            
            
            df_cq = df_frequenza[[('Controllo' in text) and ('Turno' not in text) and ('turno' not in text) for text in df_frequenza['Nome attività']]] #------------------------top class
            df_cq.reset_index(drop=True)

            df_turno = df_frequenza[[('Controllo' in text) and (('Turno' in text) or ('turno' in text)) for text in df_frequenza['Nome attività']]]
            df_turno.reset_index(drop=True)

    #info  cambio  utensili       
            freq_eq = 40
            df_utensili['new']=(df_utensili['Tempo sostituzione [min]']+df_utensili['Tempo correzione + ricontrollo [min]'])*freq_eq/df_utensili['Vita utensile [pezzi]']
    #*** frequenza eq       
            t_eq = df_utensili.new.sum()
            df_utensili = df_utensili.drop('new',axis=1)

        
            # recupero info cq

            for j in range(5):
                try:
                    t=df_cq.iloc[j,2]
                    f=df_cq.iloc[j,1]
                    o=df_cq.iloc[j,3]
                    globals()[f't{j+1}']=t
                    globals()[f'f{j+1}']=f
                    globals()[f'op_cq{j+1}']=o
                except:
                    globals()[f't{j+1}']=None
                    globals()[f'f{j+1}']=None
                    globals()[f'op_cq{j+1}']=None

            # recupero info controlli 1 a turno        

            for j in range(3):
                try:
                    turno_t=df_turno.iloc[j,2]  
                    ot=df_turno.iloc[j,3]
                    globals()[f'turno_t{j+1}']=turno_t 
                    globals()[f'op_ct{j+1}']=ot
                except:
                    globals()[f'turno_t{j+1}']=None
                    globals()[f'op_ct{j+1}']=None

            # recupero info correzione

            try:
                pos = df_frequenza[['Correzione' in text for text in df_frequenza[ 'Nome attività'] ]].index[0]
                periodo_cor = df_frequenza.loc[pos, 'Periodo']
                durata_cor = df_frequenza.loc[pos, 'Tempo ciclo']
                op_corr = df_frequenza.loc[pos, 'Operatore']
            except:
                periodo_cor = None
                durata_cor = None
                op_corr = None

            # recupero info SAP

            try:
                pos = df_frequenza[['SAP' in text for text in df_frequenza[ 'Nome attività'] ]].index[0]
                periodo_SAP = df_frequenza.loc[pos, 'Periodo']
                durata_SAP = df_frequenza.loc[pos, 'Tempo ciclo']
                op_sap = df_frequenza.loc[pos, 'Operatore']
            except:
                periodo_SAP = None
                durata_SAP = None
                op_sap = None

            # recupero info part_in

            try:
                pos = df_frequenza[['Prelievo' in text for text in df_frequenza[ 'Nome attività'] ]].index[0]
                periodo_part_in = df_frequenza.loc[pos, 'Periodo']
                durata_part_in = df_frequenza.loc[pos, 'Tempo ciclo']
                op_in = df_frequenza.loc[pos, 'Operatore']
            except:
                periodo_part_in = None
                durata_part_in = None
                op_in = None
            
            # recupero info part_out

            try:
                pos = df_frequenza[['TT' in text for text in df_frequenza[ 'Nome attività'] ]].index[0]
                periodo_part_out = df_frequenza.loc[pos, 'Periodo']
                durata_part_out = df_frequenza.loc[pos, 'Tempo ciclo']
                op_out = df_frequenza.loc[pos, 'Operatore']

            except:
                periodo_part_out = None
                durata_part_out = None
                op_out = None

    # creazione istanza della classe Machine

            macchina = des.Machine_wip(env,
                            wip,
                            df_ciclo.loc[8,'Valore'], 
                            df_ciclo.loc[9,'Valore'],
                            df_ciclo.loc[1,'Valore'],
                            df_ciclo.loc[2,'Valore'],
                            df_ciclo.loc[3,'Valore'],
                            df_ciclo.loc[4,'Valore'],
                            df_ciclo.loc[5,'Valore'],
                            df_ciclo.loc[6,'Valore'],
                            df_ciclo.loc[7,'Valore'],
                            i*10, freq_eq, t_eq, 
                            operatore1,operatore2,
                            i, f1, t1, op_cq1,
                            i,f2,t2, op_cq2,
                            i,f3,t3, op_cq3,
                            i,f4,t4, op_cq4,
                            i,f5,t5, op_cq5,
                            i, turno_t1, op_ct1,
                            i*5, turno_t2, op_ct2,
                            i*8, turno_t3, op_ct3,
                            durata_cor, periodo_cor, op_corr,
                            durata_SAP, periodo_SAP, op_sap,
                            durata_part_in, periodo_part_in, op_in,
                            durata_part_out, periodo_part_out, op_out)
        
            machines.append(macchina)
    
            col1, col2, col3 = st.columns([1,2,1])
                        
            with col1:
                st.write('Parametri macchina')
                st.dataframe(df_ciclo, width=1000, height=250)
            with col2:
                st.write('Attività in frequenza')
                st.dataframe(df_frequenza, width=1000, height=250)
            with col3:
                st.write('Tabella vita utensili')
                st.dataframe(df_utensili, width=1500, height=250)
                st.write('Il cambio utensile richiede {:0.2f} minuti ogni 40 pezzi'.format(t_eq))
    #---------------------------------------------------------------------------------------

prodotti_finiti = st.sidebar.number_input('Macchine con output proodotto finito', step=1)

with tab_risultati:

    st.subheader('Simulazione', divider='red')

    turni = st.number_input('Digitare la durata della simulazione [turni]',step=1)

    if not turni:
        st.stop()
    st.divider()

    if turni != 0:
        stop=turni*440
        env.run(until=stop)

        for macchina in machines:
            #st.write('Macchina: {} | Codice: {} | Output per turno: {:0.0f} | Ta_isola5: {:0.2f} | Ta_isola4: {:0.2f} '.format(macchina.name, macchina.part, macchina.parts_made/turni, (turni*450)/macchina.parts_made/(3), (turni*450)/macchina.parts_made/(2)))
            st.write(':red[Macchina: {}]'.format(macchina.name))
            st.write('Codice: _{}_   | Output per turno: :red[{:0.0f}] | Ta:{:0.2f} '.format(macchina.part, macchina.parts_made/turni, 450/(macchina.parts_made/turni)/prodotti_finiti))#-------------

        saturazione_1 = 0
        saturazione_2 = 0

#*** saturazione operatore
        for machine in machines:
            
            try:
                saturazione_1 += machine.link[machine.link_op['operatore1']][0]/(4.5*turni)
        
            except:
                saturazione_1 += 0        
            try:
                saturazione_2 += machine.link[machine.link_op['operatore2']][0]/(4.5*turni)
            except:
                saturazione_2 += 0

        st.divider()

        st.subheader('Saturazione OP1: {:0.2f}%'.format(saturazione_1))
        
        if saturazione_2 != 0:
            st.subheader('Saturazione OP2: {:0.2f}%'.format(saturazione_2))

        st.divider()

# Costruzione dataframe per Gantt-------------------------------------------------------------------------------------------------------------------------------------------

    incluso = ['Controllo','controllo','CONTROLLO',
            'Trasporto','trasporto','TRASPORTO',
            #'Correzione','correzione','CORREZIONE',
            'Prelievo','prelievo','PRELIEVO',
            'Sap','SAP','sap']

    escluso = ['Pronto','pronto','PRONTO',
            'Correzione','correzione','CORREZIONE',
            ]

    filtro_fine = ['Fine','fine','FINE']

    # ciclo su n macchine-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    log_macchine = []
    log_operatori = []

    prog = 1
    for macchina in machines:
        frame = pd.DataFrame([item.split("|", 3) for item in macchina.log])
        frame = frame.rename(columns={0:"Minuto",1:"Macchina",2:"Descrizione", 3:"Part"})   
        frame.Minuto = frame.Minuto.astype(float)

        # macchine

        frame_prod = frame[(frame['Descrizione'] == ' Inizio carico-scarico ') | (frame['Descrizione'] == ' Avvio macchina ') | (frame['Descrizione'] == ' Fine ciclo ')]
        frame_prod['Durata'] = frame_prod.Minuto.shift(-1) - frame_prod.Minuto
        frame_prod = frame_prod.replace({' Inizio carico-scarico ':'Carico-Scarico', ' Avvio macchina ':'Machining', ' Fine ciclo ':'Attesa operatore'})
        frame_prod['C{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Carico-Scarico',frame_prod.Durata,0)
        frame_prod['M{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Machining',frame_prod.Durata,0)
        frame_prod['A{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Attesa operatore',frame_prod.Durata,0)

        # operatori
        try:
            frame_op = frame[[(any(check in desc for check in incluso) and (all(check not in desc for check in escluso))) for desc in frame.Descrizione]]
            frame_op['Durata'] = frame_op.Minuto.shift(-1) - frame_op.Minuto
            frame_op = frame_op[[(all(check not in desc for check in filtro_fine)) for desc in frame_op.Descrizione]]
            frame_op['Descrizione'] = frame_op['Descrizione'].str[8:]
            frame_op['Macchina'] = macchina.name
            frame_op['operatore1'] = np.where(frame_op.Part == ' operatore1', frame_op.Durata, 0)
            frame_op['operatore2'] = np.where(frame_op.Part == ' operatore2', frame_op.Durata, 0)
            frame_op['Label'] = frame_op.Macchina + " | " + frame_op.Descrizione 
            
            log_operatori.append(frame_op)

        except:
            pass
        
        log_macchine.append(frame_prod)
        
        prog += 1

with tab_gantt:
# costruzione Gantt macchine
    
    tempo = st.slider('Impostare intervallo gantt', 0, stop,(0, 100))
    st.divider()
    intervallo = tempo[1] - tempo[0]
    gantt_op = pd.concat([logs for logs in log_operatori] )
    gantt_macchine = pd.concat([logs for logs in log_macchine])

    # qui deve essere filtrato il dataframe in base alla scelta
    gantt_macchine = gantt_macchine[(gantt_macchine.Minuto > tempo[0]) & (gantt_macchine.Minuto < tempo[1]) ]
    gantt_macchine = gantt_macchine.reset_index(drop=True)
    gantt_op = gantt_op[(gantt_op.Minuto > tempo[0]) & (gantt_op.Minuto < tempo[1]) ]
    gantt_op = gantt_op.sort_values(by=['Part','Minuto'])    

    unique = gantt_macchine.Macchina.unique()

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(20,5))
    y_pos = np.arange(0,len(gantt_macchine), step=1)

    for i in range(len(unique)):
        
        colonna = f'M{i+1}' 
        #ax.barh(i*2, gantt_macchine.Minuto, color='black')
        #ax.barh(y_pos, gantt_macchine[colonna], left=gantt_macchine.Minuto, color=my_cmap(60*i))  
        ax.barh(i*2, gantt_macchine[colonna], left=gantt_macchine.Minuto, color=my_cmap(60*i))  
        ax.text(tempo[0]-15, i*2+0.1, unique[i], fontsize=12, color=my_cmap(60*i))

    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.grid('on', linewidth=0.2)
    ax.tick_params(right=False, left=False, axis='y', color='r', length=16,grid_color='none')
    ax.tick_params(axis='x', color='black', length=4, direction='in', width=4,labelcolor='w', grid_color='grey',labelsize=10)
    ax.tick_params(axis='y', color='black', length=4, direction='in', width=4,labelcolor='w')
    plt.xticks(np.arange(tempo[0],tempo[1],step=(intervallo/10)))
    plt.yticks(np.arange(0,len(unique)*2 ,step=100))
    plt.xlim(tempo[0]-20,tempo[1]+20)

    # costruzione Gantt operatori

    fig2, ax2 = plt.subplots(figsize=(20,7))
    y_pos2 = np.arange(0,len(gantt_op), step=1)
    operatori = ['operatore1','operatore2']
    colori = {'operatore1': 'w', 'operatore2': 'red'}

    for operatore in operatori:
        ax2.barh(y_pos2, gantt_op.Minuto, color='black')
        ax2.barh(y_pos2, gantt_op[operatore], left=gantt_op.Minuto, color=colori[operatore])

    gantt_op['x_pos'] = gantt_op['Minuto'] + gantt_op['Durata'] + 1
    for i in range(len(gantt_op)):
        x_pos = gantt_op.x_pos.iloc[i]
        ax2.text(x_pos, i, gantt_op.Label.iloc[i], fontsize=10, fontname='Avenir')#backgroundcolor='black')

    ax2.text(tempo[0]-15, 2, 'Operatore1', fontsize=12)
    ax2.text(tempo[0]-15, len(gantt_op)/2 + 2, 'Operatore2', color='red', fontsize=12)

    ax2.invert_yaxis()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(True)
    ax2.grid('on', linewidth=0.2)
    ax2.tick_params(right=False, left=False, axis='y', color='r', length=16,grid_color='none')
    ax2.tick_params(axis='x', color='black', length=4, direction='in', width=4,labelcolor='w', grid_color='grey',labelsize=10)
    ax2.tick_params(axis='y', color='black', length=4, direction='in', width=4,labelcolor='w')
    plt.xticks(np.arange(tempo[0],tempo[1],step=(intervallo/10)))
    plt.yticks(np.arange(0,len(gantt_op),step=20))
    plt.xlim(tempo[0]-20,tempo[1]+20)

    st.subheader('Gantt macchine')
    st.pyplot(fig)

    st.subheader('Gantt operatori')
    st.pyplot(fig2)