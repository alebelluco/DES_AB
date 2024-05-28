# Aggiornato 16/05/2024
# Class machine isola 2: per visualizzare sul gantt il carico-scarico è stato aggiunto l'operatore a log_macchina sull'inizio caricamento nella funzionee working



import pandas as pd
import simpy
import math

def CQ(macchina, env, operatore, tcq, nome):
    while True:
        macchina.log.append('{:0.1f} | {} | Pezzo pronto per {}'.format(env.now, macchina.name, nome ))          
        yield env.timeout(0.1) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tcq) 
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now-tcq, macchina.name, nome, op ))
            macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now, macchina.name, nome, op ))
            
            macchina.link[operatore][0] += tcq

            #op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log_op.append('{:0.1f}_{} | cq_macchina {} | + {} minuti'.format(env.now,op, macchina.name, tcq ))
            macchina.sat.append(tcq)             
        break   

def CQ_T(macchina, env, operatore, tcq, offset, nome): #a differenza del controllo a frequenza, qui l'offset ritarda il controllo per non farlo cadere per forza ad inizio turno
    while True:
        macchina.log.append('{:0.1f} | {} | Pezzo pronto per {}'.format(env.now, macchina.name, nome ))          
        yield env.timeout(offset) # ritardo a partire da cambio turno
        macchina.link[operatore][0] += tcq
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tcq)
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now-tcq, macchina.name, nome, op ))
            #st.write('{:0.1f} | {} | Inizio {}'.format(env.now-tcq, macchina.name, nome ))
            #st.write(macchina.sat_op)
            macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now, macchina.name, nome, op ))
            
            macchina.link[operatore][0] += tcq
            #st.write(macchina.sat_op)                       
        break   

def CQ_T_macchina_funzionante(macchina, env, operatore, tcq, offset, nome): #a differenza del controllo a frequenza, qui l'offset ritarda il controllo per non farlo cadere per forza ad inizio turno
    while True:
        macchina.log.append('{:0.1f} | {} | Pezzo pronto per {}'.format(env.now, macchina.name, nome ))          
        yield env.timeout(offset) # ritardo a partire da cambio turno
        macchina.link[operatore][0] += tcq
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            # Qui c'è la modifica che simula il controllo a macchina funzionante: carica ugualmente la saturazione ma non ferma la macchina
            yield env.timeout(0)
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now, macchina.name, nome, op ))
            #st.write('{:0.1f} | {} | Inizio {}'.format(env.now-tcq, macchina.name, nome ))
            #st.write(macchina.sat_op)
            macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now + tcq, macchina.name, nome, op ))
            
            macchina.link[operatore][0] += tcq
            #st.write(macchina.sat_op)                       
        break   

def CQ_cassetto(macchina, env, operatore,robot, tcq, nome):
    while True:
        macchina.log.append('{:0.1f} | {} | Pezzo pronto per {}'.format(env.now, macchina.name, nome ))          
        yield env.timeout(0.1) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with robot.request(priority=1) as req:
            yield req
            ripartenza = False
            with operatore.request(priority=1)as req1:
                yield req1 # blocco la risorsa
                #yield req
                #yield env.timeout(1)

                yield env.timeout(tcq) 

                op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
                robot =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(robot)]
                macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now-tcq, macchina.name, nome, op ))
                macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now, macchina.name, nome, op ))

                macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now-tcq, macchina.name, nome, robot ))
                macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now, macchina.name, nome, robot ))
                
                macchina.link[operatore][0] += tcq

                #op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
                macchina.log_op.append('{:0.1f}_{} | cq_macchina {} | + {} minuti'.format(env.now,op, macchina.name, tcq ))
                macchina.sat.append(tcq)             
        break   

def Correzione(macchina, env, operatore, tc_corr):
    while True:               
        yield env.timeout(0) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=1) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tc_corr) 
            #print('{} | correzione fatta'.format(env.now))
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-tc_corr, macchina.name, op))
            macchina.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, macchina.name, op))
            
            macchina.link[operatore][0] += tc_corr
        
        break

def Other(macchina, env, operatore, tc, attività):
    while True:               
        yield env.timeout(0) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tc) 
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | inizio {} | {}'.format(env.now-tc, macchina.name, attività, op))
            macchina.log.append('{:0.1f} | {} | fine {} | {}'.format(env.now, macchina.name, attività, op))
            
            macchina.link[operatore][0] += tc
        break   

def upload(df):
    '''
    Output:
    [0] = dic_gen \n
    [1] = dic_cq \n
    [2] = dic_other \n
    [3]= dic_turno

    '''
    info = df[df.Cat_dati == 'generale']
    dic_gen = dict(zip(info.Dato,info.Valore))

    cq = df[df.Cat_dati=='cq']
    dic_cq = {}
    for controllo in cq.Subcat_dati.unique():
        subdf = df[df.Subcat_dati == controllo]
        periodo = subdf[subdf.Dato=='periodo'].Valore.iloc[0]
        durata = subdf[subdf.Dato=='durata'].Valore.iloc[0]
        op = subdf[subdf.Dato=='op'].Valore.iloc[0]
        dic_cq[controllo]={'periodo':periodo,'durata':durata,'op':op}   

    other = df[df.Cat_dati=='other']
    dic_other = {}
    for oth in other.Subcat_dati.unique():
        subdf = df[df.Subcat_dati == oth]
        periodo = subdf[subdf.Dato=='periodo'].Valore.iloc[0]
        durata = subdf[subdf.Dato=='durata'].Valore.iloc[0]
        op = subdf[subdf.Dato=='op'].Valore.iloc[0]
        dic_other[oth]={'periodo':periodo,'durata':durata,'op':op}
    
    turno = df[df.Cat_dati=='turno']
    dic_turno  = {}
    for t in turno.Subcat_dati.unique():
        subdf = df[df.Subcat_dati == t]
        durata = subdf[subdf.Dato=='durata'].Valore.iloc[0]
        op = subdf[subdf.Dato=='op'].Valore.iloc[0]
        dic_turno[t]={'durata':durata,'op':op}


    return dic_gen, dic_cq, dic_other, dic_turno

def att_robot(macchina, env, operatore, tempo):
    while True:               
        yield env.timeout(0) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tempo) 

            # Ad ora non viene visualizzato niente sul gantt, nè sulla saturazione 


            #op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            #macchina.log.append('{:0.1f} | {} | inizio {} | {}'.format(env.now-tc, macchina.name, attività, op))
            #macchina.log.append('{:0.1f} | {} | fine {} | {}'.format(env.now, macchina.name, attività, op))
            
            #macchina.link[operatore][0] += tc
        break   

class Machine(object):
    
    def __init__(self, env, name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,                               
                ):
        
        self.env = env
        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        self.op_cambio_ut = self.link_op[op_cambio_ut]

        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        self.op_corr = self.link_op[op_corr]
        self.op_sap  = self.link_op[op_sap]
        self.op_in = self.link_op[op_in]
        self.op_out = self.link_op[op_out]

        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []


    def working(self): 
        while True:           
            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs+0.11)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico'.format(self.env.now-self.cs, self.name))  
                    self.link[self.op_conduttore][0] += self.cs + 0.11 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs ))
                    self.sat.append(self.cs)

                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq1, self.tempo_ciclo_cq1, 'controllo qualità_1'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if self.turno_now > self.turno:
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                #self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:    
                    with self.op_cambio_ut.request(priority=1) as req: 
                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | pezzo °{} | Inizio cambio utensile'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0

class Machine_isola_2(object):

    # chiama la funzione CQ_T_macchina_funzionante anzichè CQ_T

    def __init__(self, env, name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,                               
                ):
        
        self.env = env
        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        self.op_cambio_ut = self.link_op[op_cambio_ut]

        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        self.op_corr = self.link_op[op_corr]
        self.op_sap  = self.link_op[op_sap]
        self.op_in = self.link_op[op_in]
        self.op_out = self.link_op[op_out]

        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []


    def working(self): 
        while True:           
            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs+0.11)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.11 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs))
                    self.sat.append(self.cs)

                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq1, self.tempo_ciclo_cq1, 'controllo qualità_1'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if self.turno_now > self.turno:
                self.env.process(CQ_T_macchina_funzionante(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                #self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                op_ut =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
                if self.count_utensile == self.periodo_cu:    
                    with self.op_cambio_ut.request(priority=1) as req: 
                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name,op_ut))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile | {}'.format(self.env.now, self.name,op_ut))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0

class Machine_wip(object):
    # Isola 3AD
    # Non presente la parte sul controllo 1 a turno

    def __init__(self, env,
                 # ------------ argomenti che differenziano Machine_wip da Machine
                 # Questa configurazione serve quando si hanno macchine in serie con wip intermedio
                 wip,
                 part_in,
                 part_out,
                 #-------------
                 name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,                               
                ):
        
        self.env = env

        self.wip = wip
        self.part_in = part_in
        self.part_out = part_out

        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        self.op_cambio_ut = self.link_op[op_cambio_ut]

        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        self.op_corr = self.link_op[op_corr]
        self.op_sap  = self.link_op[op_sap]
        self.op_in = self.link_op[op_in]
        self.op_out = self.link_op[op_out]

        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []


    def working(self): 
        while True:
            while not self.wip[self.part_in] >= self.batch: # se non c'è WIP aspetto
                yield self.env.timeout(0.01)     

            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs+0.27)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico'.format(self.env.now-self.cs, self.name))  
                    self.link[self.op_conduttore][0] += self.cs + 0.13 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs ))
                    self.sat.append(self.cs)

                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 

            self.wip[self.part_in] -= self.batch
            self.wip[self.part_out] += self.batch


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq1, self.tempo_ciclo_cq1, 'controllo qualità_1'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if (self.turno_now > self.turno) and (self.tempo_ct1):
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:    
                    with self.op_cambio_ut.request(priority=1) as req: 
                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | pezzo °{} | Inizio cambio utensile'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0

class Machine_robot(object):
    # Isola 3AD
    # Non presente la parte sul controllo 1 a turno

    def __init__(self, env,
                 # ------------ argomenti che differenziano Machine_wip da Machine
                 # Questa configurazione serve quando si hanno macchine in serie con wip intermedio
                 wip,
                 part_in,
                 part_out,
                 #-------------
                 name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,                               
                ):
        
        self.env = env

        self.wip = wip
        self.part_in = part_in
        self.part_out = part_out

        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'robot':operatore1,
                      'operatore1':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        self.op_cambio_ut = self.link_op[op_cambio_ut]

        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        self.op_corr = self.link_op[op_corr]
        self.op_sap  = self.link_op[op_sap]
        self.op_in = self.link_op[op_in]
        self.op_out = self.link_op[op_out]

        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []


    def working(self): 
        while True:
            while not self.wip[self.part_in] >= self.batch: # se non c'è WIP aspetto
                yield self.env.timeout(0.01)     

            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs)  #difica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico'.format(self.env.now-self.cs, self.name))  
                    self.link[self.op_conduttore][0] += self.cs + 0.13 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs ))
                    self.sat.append(self.cs)

            self.env.process(att_robot(self, self.env, self.op_conduttore, 10))
                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 

            self.wip[self.part_in] -= self.batch
            self.wip[self.part_out] += self.batch


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ_cassetto(self, self.env, self.op_cq1,self.op_conduttore, self.tempo_ciclo_cq1, 'controllo qualità_1'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if (self.turno_now > self.turno) and (self.tempo_ct1):
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:    
                    with self.op_cambio_ut.request(priority=1) as req: 
                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | pezzo °{} | Inizio cambio utensile'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0

