import streamlit as st

st.set_page_config(
    page_title="DES",
    layout='wide'
)

st.sidebar.write("*Versione 1.0 | 18-04-2024*")

if st.sidebar.toggle('Più info'):
    st.sidebar.write(
        '''
:red[*Il tool di simulazione permette di calcolare:*]

- Output per turno da ogni macchina
- Tempo assegnato
- Saturazione operatori

:red[*Nella tab "Gantt" è visibile:*]

- Gantt collassato dei macchinari
- Gantt operatori

'''
    )

# HEADER---------------------------------------------------------------
sx,  cx, dx = st.columns([8,4,1])
with sx:
    st.title("Discrete Event Simulator")
    st.subheader(':red[Lavorazioni meccaniche]')
    
with dx:
    st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/Ducati_red_logo.png?raw=True')


if st.sidebar.toggle('Istruzioni'):
    with st.expander('Istruzioni generali'):
        st.write("Spiegazione utilizzo base dell'app")
    with st.expander('Preparazione file di input'):

        st.subheader('Esempio di compilazione file di input', divider ='red')

        st.write('Info macchina + attività in frequenza')
        
        st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/Ciclo_frequenza.png?raw=True')

        st.write('Tabella utensili')

        st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/Tab_utensili.png?raw=True')

    
    with st.expander('Impostazione parametri simulazione'):
        st.write('Argomento2')
    
    with st.expander('Lettura risultati'):
        st.write('Argomento3')


else:
    sx1, cx1 = st.columns([2,8])
    with cx1:
        st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/motore4.png?raw=True', width=800)




