# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 13:43:16 2019

@author: Lucas
"""
import os
import argparse
import pandas as pd
import numpy as np
import copy
import math
from catsim.irt import icc_hpc

#from catsim import plot

parser = argparse.ArgumentParser(description = 'Ferramenta para analise dos datasets via TRI')

parser.add_argument('-dir', action = 'store', dest = 'dir',
                    default = 'output', required = False,
                    help = 'Nome do diretório onde estão as pastas dos datasets (Ex: output)')
parser.add_argument('-limit_dif', action = 'store', dest = 'limit_dif', required = False, type=float,
                    default = 1,help = 'Valor minimo para um item ser dificil (Ex: 1)')
parser.add_argument('-limit_dis', action = 'store', dest = 'limit_dis', required = False, type=float,
                    default = 0.75,help = 'Valor minimo para um item ser discriminativo (Ex: 0.75)')
parser.add_argument('-limit_adv', action = 'store', dest = 'limit_adv', required = False, type=float,
                    default = 0.2,help = 'Valor minimo para um item ser de facil adivinhacao (Ex: 0.2)')
parser.add_argument('-plotDataHist', action = 'store', dest = 'plotDataHist', required = False, 
                    help = 'Plota o histograma de um parametro de um dataset (Ex: nome_dataset,Dificuldade)')
parser.add_argument('-plotAllHist', action = 'store_true', dest = 'plotAllHist', required = False,
                    default = False, help = 'Plota todos os histogramas de cada dataset')
parser.add_argument('-bins', action = 'store', dest = 'bins', required = False, type=int,
                    help = 'Define o numero de bins do(s) histograma(s) gerados (Ex: 10)')
parser.add_argument('-plotDataCCC', action = 'store', dest = 'plotDataCCC', required = False, 
                    help = 'Plota as CCCs de um parametro de um dataset (Ex: nome_dataset,Dificuldade)')
parser.add_argument('-plotAllCCC', action = 'store_true', dest = 'plotAllCCC', required = False,
                    default = False, help = 'Plota todos as CCCs de cada dataset')
parser.add_argument('-scoreData', action = 'store', dest = 'scoreData', required = False, 
                    help = 'Calcula o score de todos os classificadores para um dataset (Ex: nome_dataset)')
parser.add_argument('-scoreAll', action = 'store_true', dest = 'scoreAll', required = False,
                    default = False, help = 'Calcula o score de todos os classificadores para todos os datasets')
parser.add_argument('-save', action = 'store_true', dest = 'save', required = False,
                    default = False, help = 'Salva os graficos mostrados na tela')

arguments = parser.parse_args()


global out
global limit_dif
global limit_dis
global limit_adv
out  = '/'+arguments.dir
limit_dif = arguments.limit_dif
limit_dis = arguments.limit_dis
limit_adv = arguments.limit_adv

def saveFile(lis,cols,path,name):
    df_media = pd.DataFrame(lis, columns = cols)
    df_media.to_csv(r''+path+name,index=0)

def compare_score(score1,score2):
    if score1 > score2:
        return 1
    if score1 < score2:
        return 0
    if score1 == score2:
        return 0.5

def calcDif(dict_tmp,dataset):
    
    dis = [i for i in list(dict_tmp[dataset]['Discriminacao']) if i[1] > 0]
    itens = [i[0]-1 for i in dis]
    dif_ord = sorted(list(dict_tmp[dataset]['Dificuldade']), key=lambda tup: tup[1])
    listap = [i for i in dif_ord if i[0]-1 in itens]
    
    return dif_ord,listap

def plotAll(dict_tmp, bins = None, save = False):
    
    parameters = ['Discriminacao','Dificuldade','Adivinhacao']
    for dataset in list(dict_tmp.keys()):
        for param in parameters:
            plothist(dict_tmp,param,dataset,bins = bins,save = save)
    
    if save:
        print('\nTodos os histogramas foram salvos \o/\n')

def plothist(dict_tmp,parameter,dataset,bins = None,save = False,out = out):
    from matplotlib import pyplot as plt
    
    lista = [i[1] for i in dict_tmp[dataset][parameter]]
    
    if bins == None:
        bins = round(1 +3.322*math.log10(len(lista)))#Regra de Sturge
    #bins = np.linspace(math.ceil(min(lista)),math.floor(max(lista)),bins)
    #print(bins)
    plt.xlim([min(lista), max(lista)])
    
    plt.hist(lista, bins=bins, alpha=0.75)
    plt.title(dataset+' - Histograma - '+parameter)
    plt.xlabel(parameter)
    plt.ylabel('Frequencia')
    
    if save:
        plt.savefig(os.getcwd()+out+'/'+dataset+'/'+parameter+'_hist.png',dpi=200)
        plt.close()
    else:
        plt.show()

def freqParam(irt_dict_tmp):
    tmp_dict = copy.deepcopy(irt_dict_tmp)
    for key in list(irt_dict_tmp.keys()):
        countdis = 0
        countdif = 0
        countges = 0
        for i in irt_dict_tmp[key]['Discriminacao']:
            if i[1] > limit_dis:
                countdis += 1
        for i in irt_dict_tmp[key]['Dificuldade']:
            if i[1] > limit_dif:
                countdif += 1
        for i in irt_dict_tmp[key]['Adivinhacao']:
            if i[1] > limit_adv:
                countges += 1
        tmp_dict[key]['Discriminacao'] = countdis/len(irt_dict_tmp[key]['Discriminacao'])
        tmp_dict[key]['Dificuldade'] = countdif/len(irt_dict_tmp[key]['Dificuldade'])
        tmp_dict[key]['Adivinhacao'] = countges/len(irt_dict_tmp[key]['Adivinhacao'])
        
    return tmp_dict

def verificaParametros(irt_dict):
    #lista = list(irt_dict.keys())
    parameters_dict = {}
    
    for key in list(irt_dict.keys()):
        tam = [i+1 for i in range(len(irt_dict[key]))]
        d = {}
        d['Discriminacao'] = list(zip(tam,irt_dict[key][:,0]))
        d['Dificuldade'] = list(zip(tam,irt_dict[key][:,1]))
        d['Adivinhacao']= list(zip(tam,irt_dict[key][:,2]))
        
        parameters_dict[key] = d
    
    return parameters_dict

def printFreq(tmp_dict, save = False):
    dis = []
    dif = []
    ges = []
    name = list(tmp_dict.keys())
    
    for n in name:
        dis.append((n,tmp_dict[n]['Discriminacao']))
        dif.append((n,tmp_dict[n]['Dificuldade']))
        ges.append((n,tmp_dict[n]['Adivinhacao']))
        
    dis.sort(key=lambda tup: tup[1], reverse=True)
    dif.sort(key=lambda tup: tup[1], reverse=True)
    ges.sort(key=lambda tup: tup[1], reverse=True)
    
    lista = [dis, dif, ges]
    name = ['Discriminacao','Dificuldade','Advinhacao']
    if save:
        file = open(r''+os.getcwd()+'/'+'IRT_param_freq.txt','w')
        for i in range(len(name)):
            file.write('Porcentagem de itens com valores altos do parametro '+name[i]+'\n')
            file.write('Dataset \t\t\t\t Percentual de itens\n')
            for p in lista[i]:
                file.write('{:40} {:10.0%}'.format(p[0],p[1])+'\n')
            file.write('-'*60+'\n')
        file.close() 
        print("As frequencias dos parametros de item foram salvas \o/\n")
    else:
        for i in range(len(name)):
            print('Porcentagem de itens com valores altos do parametro',name[i])
            print('Dataset \t\t\t\t Percentual de itens\n')
            for p in lista[i]:
                print('{:40} {:10.0%}'.format(p[0],p[1]))
            print('-'*60)
        

def thetaClfEstimate(dict_tmp,irt_dict,irt_resp_dict,dataset,parameter,list_theta, bins = None,save = False, out = out):
    from catsim.estimation import HillClimbingEstimator

    names = str(list_theta[dataset].keys).split()[6:]
    names = [names[i] for i in range(0,len(names),2)]
    tmp = {}
        
    for t in range(len(names)):
        
        itens = []
        item_resp = []
        if parameter == 'Dificuldade':
#            #Separa as instâncias com discriminacao maior que zero
#            dis = [i for i in list(dict_tmp[dataset]['Discriminacao']) if i[1] > 0]
#            
#            itens = [i[0]-1 for i in dis]
#            #Cria o vetor booleano de respostas
#            item_resp_tmp = [True if i == 1 else False for i in irt_resp_dict[dataset][t]]
#            item_resp = [item_resp_tmp[i] for i in itens]
#            
#            ###############
            dif_ord,listap = calcDif(dict_tmp,dataset)
            #print(dif_ord)
            itens = [i[0]-1 for i in dif_ord]
#            item_resp = [item_resp_tmp[i] for i in itens]
            #itens = [i for i in range(len(irt_dict[dataset]))]
            item_resp_tmp = [True if i == 1 else False for i in irt_resp_dict[dataset][t]]
            item_resp = [item_resp_tmp[i] for i in itens]
            
        elif parameter == 'Discriminacao':
            itens = [i for i in range(len(irt_dict[dataset]))]
            item_resp = [True if i == 1 else False for i in irt_resp_dict[dataset][t]]
            
        elif parameter == 'Adivinhacao':
            itens = [i for i in range(len(irt_dict[dataset]))]
            item_resp = [True if i == 1 else False for i in irt_resp_dict[dataset][t]]
            #raise ValueError("Os parametros permetidos sao Dificuldade e Descriminacaos")
        
        #print(itens)
        e_theta=list_theta[dataset].to_numpy()[t][0]
        #print(e_theta)
        qtd = len(itens)//10
        #print('qtd ',qtd)
        #print(itens)
        #a = input('TEste')
        for i in range(10):
        #Calcula o novo theta com base na acuracia de cada classificador
            items=irt_dict[dataset]
            adm_items= itens[:qtd]
            #print(items)
            itens = itens[qtd:]#Corte
            r_vector=item_resp[:qtd]
            item_resp = item_resp[qtd:]#Corte
            #e_theta=list_theta[dataset].to_numpy()[t][0]
            new_theta = HillClimbingEstimator().estimate(items=items, 
                                             administered_items= adm_items, 
                                             response_vector=r_vector, 
                                             est_theta=e_theta)
            e_theta = new_theta
        
        #list_new_theta.append(new_theta)
        
        tmp[names[t]] = new_theta
        #print(names[t])
   
    if save:
        df = pd.DataFrame(list(tmp.items()),index=tmp.keys(), columns=['Clf','Theta'])
        df.to_csv(os.getcwd()+out+'/'+dataset+'/'+'theta_list.csv',index=0)
    
    return tmp
        #dict_theta[dataset] = tmp

def thetaAllClfEstimate(dict_tmp, irt_dict, irt_resp_dict, list_theta, param = ['Dificuldade','Discriminacao', 'Adivinhacao'], save = False):
    dict_theta = {}
    for dataset in list(dict_tmp.keys()):
        p = {}
        for parameter in param:
            p[parameter] = thetaClfEstimate(dict_tmp,irt_dict,irt_resp_dict,dataset,parameter,list_theta,save = save)
        dict_theta[dataset] = p
        
    if save:
        print('Todos os valores de Theta foram salvos \o/')
        
    return dict_theta
        
def CalcICC(dict_theta,irt_dict):
    icc_dict = {}
    for dataset in list(dict_theta.keys()):
        p = {}
        for parameter in list(dict_theta[dataset].keys()):
            tmp = {}
            for clf in list(dict_theta[dataset][parameter].keys()):
                t = dict_theta[dataset][parameter][clf]
                tmp[clf] = list(icc_hpc(t,irt_dict[dataset]))
                p[parameter] = tmp
                
        icc_dict[dataset] = p
        
    return icc_dict

def calcPro(icc_dict,dict_tmp,dataset,save = False):
    dif_ord,listap = calcDif(dict_tmp,dataset)
    itens = [i[0]-1 for i in listap]
    score_total = []
    score_pos = []
    clfs = list(icc_dict[dataset]['Dificuldade'].keys())
    
    for clf in clfs:
        #score_total[clf] = sum(icc_dict[dataset]['Dificuldade'][clf])
        score_total.append(sum(icc_dict[dataset]['Dificuldade'][clf]))
        lista = [icc_dict[dataset]['Dificuldade'][clf][i] for i in itens]
        #score_pos[clf] = sum(lista)
        score_pos.append(sum(lista))
    
    l_score_total = list(zip(clfs,score_total))
    l_score_pos = list(zip(clfs,score_pos))
    
    l_score_total.sort(key=lambda tup: tup[1])
    l_score_pos.sort(key=lambda tup: tup[1])
    #print(l_score_total)
    
    import matplotlib.pyplot as plt
    eager = ['otimo','SVM', 'MLPClassifier','DecisionTreeClassifier()','GaussianNB', 'BernoulliNB']
    ensemble = ['RandomForestClassifier(3_estimators)', 'RandomForestClassifier(5_estimators)', 'RandomForestClassifier']
    lazy = ['KNeighborsClassifier(2)', 'KNeighborsClassifier(3)', 'KNeighborsClassifier(5)', 'KNeighborsClassifier(8)','rand1', 'rand2', 'rand3', 'majoritario', 'minoritario', 'pessimo']
    
    key = [1,1,1]
    for clfscore in l_score_total:    
        if clfscore[0] in eager:
            if key[0]:
                key[0] = 0
                plt.plot(clfscore[1], clfscore[0], 'ro',color='deepskyblue',label='eager')
            else:
                plt.plot(clfscore[1], clfscore[0], 'ro',color='deepskyblue')
            #plt.legend(plt, ['eager'])
        if clfscore[0] in ensemble:
            if key[1]:
                key[1] = 0
                plt.plot(clfscore[1], clfscore[0], 'ro',color='gold',label='ensemble')
            else:
                plt.plot(clfscore[1], clfscore[0], 'ro',color='gold')
        if clfscore[0] in lazy:
            if key[2]:
                key[2] = 0
                plt.plot(clfscore[1], clfscore[0], 'ro',color='orangered',label='lazy')
            else:
                plt.plot(clfscore[1], clfscore[0], 'ro',color='orangered')
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),ncol=3, fancybox=True)
    plt.grid(axis='y',linestyle='--')
    plt.xlabel('score')
    #plt.show()
    
    if save:
        cols = ['Clf','Score']
        saveFile(l_score_total,cols,os.getcwd()+out+'/'+dataset+'/','score_total.csv')
        saveFile(l_score_pos,cols,os.getcwd()+out+'/'+dataset+'/','score_disPositivo.csv')
        plt.savefig(os.getcwd()+out+'/'+dataset+'/'+dataset+'_score.png',dpi=200, bbox_inches='tight')
        plt.close()
    else:
        print('\nScores dos classificadores para o dataset:',dataset,'\n')
        print('Score total dos classificadores:\n')
        for i in range(len(clfs)):
            print('{:40} {:10}'.format(l_score_total[i][0],l_score_total[i][1]))
        #print('-'*60)
        plt.savefig(os.getcwd()+out+'/'+dataset+'/'+parameter+'_CCC.png',dpi=200, bbox_inches='tight')
        plt.close()
        print('\nScore com discriminacao positiva:\n')
        for i in range(len(clfs)):
            print('{:40} {:10}'.format(l_score_pos[i][0],l_score_pos[i][1]))
        print('-'*60)
        plt.show()
    #return score_total,score_pos
            
def calcAllPro(icc_dict,dict_tmp,save = False):
    datasets = list(icc_dict.keys())
    
    for dataset in datasets:
         calcPro(icc_dict,dict_tmp,dataset,save = save)
         
    if save:
        print('\nOs scores dos classificadores para todos os datasets foram salvos \o/\n')
    
def plotCCC(icc_dict,dict_tmp,dataset,parameter,save = False,out = out):
    from matplotlib import pyplot as plt
    
    listap = []
    if parameter == 'Dificuldade':
        # dis = [i for i in list(dict_tmp[dataset]['Discriminacao']) if i[1] > 0]
        # itens = [i[0]-1 for i in dis]
        # dif_ord = sorted(list(dict_tmp[dataset][parameter]), key=lambda tup: tup[1])
        # listap = [i for i in dif_ord if i[0]-1 in itens]
        dif_ord,listap = calcDif(dict_tmp,dataset)
        
    elif parameter == 'Discriminacao':
        listap = sorted(list(dict_tmp[dataset]['Discriminacao']), key=lambda tup: tup[1])
        
    elif parameter == 'Adivinhacao':
        listap = sorted(list(dict_tmp[dataset]['Adivinhacao']), key=lambda tup: tup[1])
        #raise ValueError("Os parametros permetidos sao Dificuldade e Descriminacaos")
    #print(listap)    
    list_index = [i[0]-1 for i in listap]
    tmp = {}
    clfs = list(icc_dict[dataset][parameter].keys())
    for clf in clfs:
        lista = []
        for i in list_index:
            lista.append(list(icc_dict[dataset][parameter][clf])[i])
        tmp[clf] = lista
    #dif_dict = tmp
    x = [i[1] for i in listap]
    plt.figure()
    plt.title(dataset)
    plt.xlabel(parameter)
    plt.ylabel('P(\u03B8)')
    clfs = ['GaussianNB','KNeighborsClassifier(8)', 'DecisionTreeClassifier()', 'RandomForestClassifier', 'SVM', 'MLPClassifier', 'rand1']
    #clfs = ['otimo','pessimo']
    for clf in clfs[:12]:
        plt.plot(x, list(tmp[clf]), label=clf, alpha=0.8, linewidth = 1)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    if save:
        plt.savefig(os.getcwd()+out+'/'+dataset+'/'+parameter+'_CCC.png',dpi=200, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plotAllCCC(icc_dict,dict_tmp,save = False):
  
    
    for dataset in list(icc_dict.keys()):
        for parameter in list(icc_dict[dataset].keys()):
            plotCCC(icc_dict,dict_tmp,dataset,parameter,save = save)
            
    if save:
        print('\nTodos as CCCs foram salvas \o/\n')


#Proficiencia inicial de cada metodo
list_theta = {}      
#Lista todos os diretorios de datasets da pasta output
list_dir = os.listdir(os.getcwd()+out)
#Pega todos os arquivos contendo os valores para o IRT
irt_dict = {}
irt_resp_dict = {}
for path in list_dir:
    
    theta = pd.read_csv(os.getcwd()+out+'/'+path+'/'+path+'_final.csv',index_col=0)
    list_theta[path] = theta
    irt_parameters = pd.read_csv(os.getcwd()+out+'/'+path+'/irt_item_param.csv',index_col=0).to_numpy()
    res_vector = pd.read_csv(os.getcwd()+out+'/'+path+'/'+path+'.csv').to_numpy()
    col = np.ones((len(irt_parameters), 1))    
    new_irt = np.append(irt_parameters, col, axis = 1)
    irt_dict[path] = new_irt
    irt_resp_dict[path] = res_vector

dict_tmp = verificaParametros(irt_dict)
tmp_freq = freqParam(dict_tmp)
printFreq(tmp_freq,save = arguments.save)

if arguments.plotDataHist != None:
    dataset,parameter = arguments.plotDataHist.split(',')
    plothist(dict_tmp,parameter,dataset,bins = arguments.bins,save = arguments.save)
    
if arguments.plotAllHist:
    plotAll(dict_tmp, bins = arguments.bins, save = arguments.save)
    
if arguments.plotDataCCC != None:
    dataset,parameter = arguments.plotDataCCC.split(',')
    dict_theta = {}
    p = {}
    p[parameter] = thetaClfEstimate(dict_tmp,irt_dict,irt_resp_dict,dataset,parameter,list_theta,save = arguments.save)
    dict_theta[dataset] = p
    icc_dict = CalcICC(dict_theta,irt_dict)
    plotCCC(icc_dict,dict_tmp,dataset,parameter,save = arguments.save)
    
if arguments.plotAllCCC:
    dict_theta = thetaAllClfEstimate(dict_tmp,irt_dict,irt_resp_dict,list_theta,save = arguments.save)
    icc_dict = CalcICC(dict_theta,irt_dict)
    plotAllCCC(icc_dict,dict_tmp,save = arguments.save)

if arguments.scoreData != None:
    dataset = arguments.scoreData
    dict_theta = {}
    p = {}
    p['Dificuldade'] = thetaClfEstimate(dict_tmp,irt_dict,irt_resp_dict,dataset,'Dificuldade',list_theta,save = arguments.save)
    dict_theta[dataset] = p
    icc_dict = CalcICC(dict_theta,irt_dict)
    calcPro(icc_dict,dict_tmp,dataset,save = arguments.save)
    
if arguments.scoreAll:
    dict_theta = thetaAllClfEstimate(dict_tmp,irt_dict,irt_resp_dict,list_theta,param = ['Dificuldade'],save = arguments.save)
    icc_dict = CalcICC(dict_theta,irt_dict)
    calcAllPro(icc_dict,dict_tmp,save = arguments.save)
