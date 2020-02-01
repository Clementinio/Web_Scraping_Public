Priority = {"https://datos.gov.co/":27.5,"https://datos.gov.co":27.5,"https://www.dane.gov.co":15,\
"https://www.dane.gov.co/":15, "https://www.who.int":5, "https://www.who.int/":5,\
"https://www.sdgindex.org":2.5,"https://www.sdgindex.org/":2.5,"Others":50}

from pathlib import Path
from pathlib import PosixPath
from warnings import simplefilter
from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import Progressbar
from tkinter import filedialog
from tkinter import StringVar
from tkinter.messagebox import *
import time
import sys
import ctypes
from multiprocessing import Pool
import multiprocessing as mp
import os
import gc
from threading import Thread

import pip

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except:
    install("requests")
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import urllib
    import urllib.request
except:
    install("urllib")
    import urllib
    import urllib.request

try:
    from bs4 import BeautifulSoup
except:
    install("bs4")
    from bs4 import BeautifulSoup

try:
    import pandas as pd
except:
    install("pandas")
    import pandas as pd

try:
    import numpy as np
except:
    install("numpy")
    import numpy as np

try:
    import itertools
except:
    install("itertools")
    import itertools

try:
    import pycountry as ps
except:
    install("pycountry")
    import pycountry as ps

def Country_Latin_America_Caribbean():
    countries = list(ps.countries)
    for i in range(len(countries)):
        st = str(countries[i])
        st = st.replace("Country(",'{"')
        st = st.replace("='",'\":\"')
        st = st.replace('="','":"')
        st = st.replace('", ','", "')
        st = st.replace("', ",'", "')
        st = st.replace("\")","\"}")
        st = st.replace("')","\"}")
        countries[i] = eval(st)

    countries = pd.DataFrame(countries)

    codes = countries[["name","alpha_3"]]

    Lat_Ame_Car = ['Brazil','Mexico','Colombia','Argentina','Peru','Venezuela, Bolivarian Republic of','Chile','Guatemala','Ecuador','Bolivia, Plurinational State of','Cuba','Haiti','Dominican Republic','Honduras','Paraguay','Nicaragua','El Salvador','Costa Rica','Panama','Uruguay','Jamaica','Trinidad and Tobago','Guyana','Suriname','Belize','Bahamas','Barbados','Saint Lucia','Grenada','Saint Vincent and the Grenadines','Antigua and Barbuda','Dominica','Saint Kitts and Nevis']
    return countries[np.array([dec for dec in [(value in Lat_Ame_Car) for value in countries["name"]]])].reset_index(drop=True)

countries_L_C = Country_Latin_America_Caribbean()   #Countries in Latin america and Caribbean with their codes
global Key_Words


def Url(url,attr=None,tag='a',source="https://datos.gov.co"):
    if source == "https://datos.gov.co" or source == "https://datos.gov.co/":
        try :
            response = requests.get(url,verify = False)
            if response.status_code != 200:
                return([])
        except :
            return([])
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        out = list(soup.findAll(tag,attrs=attr))
        out = [link["href"] for link in out if "href" in link.attrs.keys()]
        out.sort()
        out = list(url for url,_ in itertools.groupby(out))
        return(out)
    elif source == "https://www.who.int" or source == "https://www.who.int/":
        Links_1 = ["http://apps.who.int/gho/data/node.country.country-"+country_code+"?lang=es" for country_code in countries_L_C["alpha_3"]]
        Links_2 = ["https://www.who.int/countries/"+country_code.casefold()+"/es/" for country_code in countries_L_C["alpha_3"]]
        Links_3 = ["https://extranet.who.int/sree/Reports?op=Replet&amp&name=/WHO_HQ_Reports/G2/PROD/EXT/TBCountryProfile&amp&ISO2="+country_code+"&amp&outtype=html&amp&LAN=ES" for country_code in countries_L_C["alpha_2"]]
        Links_4 = ["http://apps.who.int/nutrition/landscape/report.aspx?iso="+country_code.casefold() for country_code in countries_L_C["alpha_3"]]
        return ([Links_1,Links_2,Links_3,Links_4])

    elif source == "https://www.dane.gov.co" or source == "https://www.dane.gov.co/":
        result = []
        try:
            re =requests.get('https://sitios.dane.gov.co/anda-index/',verify=False)
            te = re.text
        except:
            return []
        soup = BeautifulSoup(te,"html.parser")
        elt = soup.findAll("a")
        out = [url["href"] for url in elt if "href" in url.attrs if url["href"]!="" and url["href"][0]!="#"]
        out.sort()
        out = list(url for url,_ in itertools.groupby(out))
        for url in out:
            url = url.split("/")
            if url[-1]=="":
                del url[-1]

            try:
                eval(url[-1])
                try:
                    eval(url[-2])
                    re =requests.get("/".join(url),verify=False)
                    te = re.text
                    soup = BeautifulSoup(te,"html.parser")
                    elt = soup.findAll("a")
                    ou = [ur["href"] for ur in elt if "href" in ur.attrs if (ur["href"].split("/")[-1]=="get_microdata" or ur["href"].split("/")[-2]=="get_microdata") or (ur["href"].split("/")[-1]=="study-description" or ur["href"].split("/")[-2]=="study-description")]
                    for link in ou:
                        if link not in result:
                            link = link.split("/")
                            if link[-1]=="":
                                del link[-1]
                            u = "/".join(link[:-1])
                            result.append(u)
                except:
                    u = "/".join(url)
                    result.append(u)
            except:
                if url[-1]=="get_microdata"  or url[-1]=="study-description":
                    u = "/".join(url[:-1])
                    result.append(u)
        return result

    elif source=="https://www.sdgindex.org" or source=="https://www.sdgindex.org/":
        try:
            response = requests.get(url,verify=False)
            if response.status_code!=200:
                return []
        except:
            return []
        text = response.text
        soup = BeautifulSoup(text,"html.parser")
        elts = soup.findAll('h3',attrs={"class":"teaser-title"})
        links = [ source+c["href"] for c in [h3.find('a') for h3 in elts] if "href" in c.attrs]
        links.insert(0,source)
        return (links)

def Download_Link(url,typo):
    if typo == 1:
        try:
            re = requests.get(url,verify=False)
            te=re.text
            sp = BeautifulSoup(te,"html.parser")
            url = sp.findAll('iframe',attrs={"id":"content_iframe"})[0]["src"].replace("../","http://apps.who.int/gho/")
            re = requests.get(url,verify=False)
            te=re.text
            sp = BeautifulSoup(te,"html.parser")
            out = sp.findAll('script')[0].text
            out = out[out.find("function iframe_set_downloads"):]
            ind1 = out.find("http")
            ind2 = out.find('"',ind+1)
            url = out[ind1 : ind2]
            re = requests.get(url,verify=False)
            te = re.text
            sp = BeautifulSoup(te,"html.parser")
            url = sp.findAll('a',attrs = {"title":"Basic data table with the row and column headers compressed to single cells"})[0]["href"].replace("../","https://apps.who.int/gho/athena/data/")
            return (url)
        except:
            return None
    elif typo == 2:
        try:
            re = requests.get(url,verify=False)
            te=re.text
            sp = BeautifulSoup(te,"html.parser")
            url = sp.findAll('a',attrs={"class":"link_media","target":"_blank"})
            if len(url)>0:
                return url[-1]["href"]
            return None
        except:
            return None

    else:
        return None

def downloadable(source,link):
    if "http" not in link:
        link = source+"/"+link
    url = link.split("/")
    while "" in url:
        url.remove("")
    del url[0]
    if len(url)>1:
        if "." in url[-1]:
            url = url[-1].split(".")
            if url[-1].casefold() in ['pdf','xlsx','dta']:
                return 1
            return 0
    return 0

def Check_File(content_page):
    global Key_Words
    content_page = content_page.casefold()
    decision = 0
    SDGs     = []
    for sdg in range(len(Key_Words)):
        for key in Key_Words[sdg]:
            if key.casefold() == "Tecnologías de la Información y las Comunicaciones".casefold():
                if content_page.count(key.casefold()) != content_page.count("Ministerio de Tecnologías de la Información y las Comunicaciones".casefold()):
                    SDGs.append(sdg+1)
                    break
                continue
            if key.casefold() in content_page:
                SDGs.append(sdg+1)
                break
    decision = int(len(SDGs)>0)
    return(decision,SDGs)

def Verify(url,source = "https://datos.gov.co",typo=1):
    if source == "https://datos.gov.co" or source == "https://datos.gov.co/":
        try :
            response = requests.get(url,verify = False)
            if response.status_code != 200:
                return([0])
        except :
            return([0])
        
        text = response.text
        if '"data":"Ver datos"' not in text:
            Useful,SDGs = Check_File(text)
            if Useful == 1:
                soup = BeautifulSoup(text,"html.parser")
                Author = soup.findAll("a",attrs = {"class":"aboutAuthorName"})
                download_Link = soup.findAll("a",attrs={"rel":"external","class":"subscribe"})
                if len(Author)!=0:
                    try:
                        return(Useful,url,SDGs,Author[0].text,download_Link[0]["href"].replace(".rss",".csv")[2:])
                    except:
                        return(Useful,url,SDGs,Author[0].text,"None")
                
                el = soup.findAll('script',attrs={"id":"visualization-canvas-initial-state"})
                if len(el)==0:
                    try:
                        return(Useful,url,SDGs,"None",download_Link[0]["href"].replace(".rss",".csv")[2:])
                    except:
                        return(Useful,url,SDGs,"None","None")

                x = el[0].text.find("parentViewPath: ")+len("parentViewPath: ")
                y = el[0].text.find('"',x+1)
                link = "datos.gov.co"+el[0].text[x+1:y]
                return(Verify(link))
            return([0])
        return (Verify(url+"/data"))

    elif source == "https://www.who.int" or source == "https://www.who.int/":
        try :
            response = requests.get(url,verify = False)
            if response.status_code != 200:
                return([0])
        except :
            return([0])
        
        text = response.text
        Useful,SDGs = Check_File(text)
        if Useful == 1:
            soup = BeautifulSoup(text,"html.parser")
            Author = "World Health Observatory"
            download_Link = Download_Link(url,typo)
            return (Useful,url,SDGs,Author,download_Link)
        return([0])
    elif source == "https://www.dane.gov.co" or source == "https://www.dane.gov.co/":
        try :
            response = requests.get(url,verify = False)
            if response.status_code != 200:
                return([0])
        except :
            return([0])
    
        text = response.text
        Useful,SDGs = Check_File(text)
        if Useful == 1:
            soup = BeautifulSoup(text,"html.parser")
            Author = ""
            temp = soup.findAll('tr',attrs={"valign":"top"})
            for elt in temp:
                if "Productor(es)" in str(elt):
                    temp = str(elt)
                    break
            temp = BeautifulSoup(temp,"html.parser").findAll('td')
            for elt in temp:
                if "Productor(es)" not in str(elt):
                    Author = elt.text.strip()
                    break
            download_Link = [url+"/export"]
            try :
                response = requests.get(url+"/get_microdata",verify = False)
                if response.status_code != 200:
                    return(Useful,url,SDGs,Author,download_Link)
            except :
                return(Useful,url,SDGs,Author,download_Link)
            text = response.text
            soup = BeautifulSoup(text,"html.parser")
            temp = soup.findAll('input',attrs={"type":"image"})
            for cd in temp:
                try:    
                    cd = cd["onclick"]
                    ht = cd.rindex("http")
                    cd = cd[ht:]
                    download_Link.append(cd[:cd.index(" ')")])
                except:
                    pass
            return (Useful,url,SDGs,Author,download_Link)
        return([0])
    elif source=="https://www.sdgindex.org" or source=="https://www.sdgindex.org/":
        try:
            response = requests.get(url,verify=False)
            if response.status_code!=200:
                return([0])
        except:
            return([0])

        text = response.text
        soup = BeautifulSoup(text,"html.parser")
        elts = soup.findAll('a')
        links = [elt["href"] for elt in elts if "href" in elt.attrs if elt["href"][0]!="#" and elt["href"]!="/" if downloadable(url,elt["href"])]
        if len(links)==0:
            links=[""]
        return(1,url,list(np.arange(1,18)),"SDG Index",links)

def Datos_gov_co1(i):
    Urls = Url(url="https://datos.gov.co/browse?sortBy=newest&utf8=✓&page="+str(i),attr={"class":"browse2-result-name-link"})
    out= []
    while Urls:
        link = Urls.pop(0)
        Res = Verify(link)
        if Res[0]==1:
            out.append(Res[1:])
    return(out)

def Datos_gov_co2(i):
    Urls = Url(url="https://datos.gov.co/browse?limitTo=charts&page="+str(i),attr={"class":"browse2-result-name-link"})
    out= []
    while Urls:
        link = Urls.pop(0)
        Res = Verify(link)
        if Res[0]==1:
            out.append(Res[1:])
    return(out)

def World_Health_Organization(link_t):
    source = "https://www.who.int"
    Res = Verify(url = link_t[0], source = source, typo = link_t[1])
    if Res[0]==1:
        return(Res[1:])

def Dane_Colombia(link):
    source = "https://www.dane.gov.co"
    Res = Verify(url = link, source = source)
    if Res[0]==1:
        return(Res[1:])

def SDG_Index(link):
    source = "https://www.sdgindex.org"
    Res = Verify(url = link, source = source)
    if Res[0]==1:
        return(Res[1:])


class GUI:
    def __init__(self,window):
        self.window = window
        self.window.title("CEPEI SCRAPING APP --- By Ing. Clement A. Hounkpevi")
        self.window.geometry('700x500')
        self.Initialise()
        self.Url = Url
        self.Datos_gov_co1 = Datos_gov_co1
        self.Datos_gov_co2 = Datos_gov_co2
        self.World_Health_Organization = World_Health_Organization
        self.Dane_Colombia = Dane_Colombia
        self.SDG_Index = SDG_Index

    def Initialise(self):
        self.delete_children()
        self.directory = ""
        self.butonFile1=Button(self.window, text="SELECT SDGs KEY WORDS", command=self.SelectFile,font=("Helvetica", 16))
        self.butonFile2=Button(self.window, text="ENTER THE LINKS",command=self.Links,font=("Helvetica", 16))
        self.butonFile3=Button(self.window, text="Enter",command=self.Start,font=("Helvetica", 16))
        self.butonFile4=Button(self.window, text="Finish",command=self.Finish,font=("Helvetica", 16))
        self.w1 = Label(self.window, text="KEY WORDS UPLOADED", font=("Helvetica", 22))
        self.w2 = Label(self.window, text="Select the Links (Multiple selection possible)\n-------------------------------------------------------------------------------------------------", font=("Helvetica", 16))
        self.w4 = Label(self.window, text="Data Scraping in Progess", font=("Helvetica", 22))
        self.w6 = Label(self.window, text="Do not close this app!", font=("Helvetica", 16),fg="red")
        self.progress = Progressbar(self.window, orient = HORIZONTAL,length = 100, mode = 'determinate')
        self.menubar = Menu(self.window)
        self.menubar.add_command(label="About", command=self.about)
        self.menubar.add_command(label="Close", command=self.window.quit)

        self.window.config(menu=self.menubar)
        self.butonFile1.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.Error = ""

    def delete_children (self) :
        _list = self.window.winfo_children()

        for item in _list :
            if item.winfo_children() :
                item.winfo_children().destroy()
            item.destroy()

    def execute(self):
        self.window.mainloop()

    def SelectFile(self):
        cpu = mp.cpu_count()
        if cpu<4:
            showerror("Error","You computer is not good enough!\nPlease find a computer of NUMBER OF CUP equals at least 4")
            return
        showwarning("warning","This app will need your whole memory to execute!\nDo not try to open or execute other things when it is running\n\nPress OK to Continue")
        file = filedialog.askopenfilename()
        tab=str(file).split("/")
        tab[-1]=""
        for di in tab:
            self.directory+="/"+di
        if "." not in str(file):
            return
        self.Procced_data(file)

    def create_btn(self, mode): 
        cmd = lambda: self.list.config(selectmode=mode) 
        return Button(self.window, command=cmd, text=mode.capitalize()) 
    
    def Correct_URL(self,url):
        if (url[0:4]=="http" or url[0:3]=="www"):
            return True
        return False
    def Start(self):
        try :
            if type(self.Error)!=str:
                self.Error.destroy()
                self.Error = ""

            selection = self.list.curselection() 
            self.URL = [self.list.get(i) for i in selection]

            if not self.URL:
                return

            if "Others" in self.URL:
                self.Links_others()

            else:
                self.Preprocess(self.URL)

        except Exception as e:
            return

    def Links_others(self):
        self.w2.destroy()
        self.list.destroy()
        self.xDefilB.destroy()
        self.yDefilB.destroy()
        for btn in self.btns:
            btn.destroy()

        self.butonFile3.destroy()
        self.butonFile3=Button(self.window, text="Enter",command=self.Start_Other,font=("Helvetica", 16))
        self.ENTRY = Entry(self.window,width=80)
        self.ENTRY.insert(0, "https://datos.gov.co/   https://www.who.int")
        self.w2 = Label(self.window, text="Enter the Links seperated by spaces and Press Enter\n-------------------------------------------------------------------------------------------------", font=("Helvetica", 16))
        self.w2.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.ENTRY.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.butonFile3.place(relx=0.75, rely=0.75, anchor=CENTER)

    def Start_Other(self):
        URL = []
        try :
            if type(self.Error)!=str:
                self.Error.destroy()
                self.Error = ""
            Str = str(self.ENTRY.get())
            URL = [elt for elt in Str.strip().split(" ") if elt!=""]
            if not URL:
                return
            for url in URL:
                if not self.Correct_URL(url):
                    self.Error = Label(self.window, text="incorrect urls! TRY AGAIN",font=("Helvetica", 14), fg ="red")
                    self.Error.place(relx=0.5, rely=0.80, anchor=CENTER)
                    showerror("Error","incorrect urls! TRY AGAIN")
                    return
        except Exception as e:
            return
        self.URL += URL
        self.URL.remove("Others")
        self.Preprocess(self.URL)


    def Links(self):
        self.links = []
        lma = 0
        for link in list(Priority.keys()):
            if link[-1]!="/":
                self.links.append(link)
                if len(link)>lma:
                    lma = len(link)
        self.MODES = [SINGLE, MULTIPLE]
        self.posi = [LEFT, RIGHT]
        self.xDefilB = Scrollbar(self.window, orient='horizontal')
        self.xDefilB.place(relx=0.55, rely=0.70, anchor=CENTER)
        self.yDefilB = Scrollbar(self.window, orient='vertical')
        self.yDefilB.place(relx=0.70, rely=0.5, anchor=CENTER)
        self.list = Listbox(self.window, width=lma, xscrollcommand=self.xDefilB.set, yscrollcommand=self.yDefilB.set)
        self.list.insert(0, *self.links)
        self.btns = [self.create_btn(m) for m in self.MODES]
        self.butonFile2.destroy()
        self.w1.destroy()
        self.w2.place(relx=0.5, rely=0.12, anchor=CENTER)

        self.list.place(relx=0.55, rely=0.5, anchor=CENTER)
        self.xDefilB['command'] = self.list.xview
        self.yDefilB['command'] = self.list.yview
        i = 0.2
        for btn in self.btns: 
            i += 0.2
            btn.place(relx=0.30, rely=i, anchor=CENTER)
        self.butonFile3.place(relx=0.75, rely=0.75, anchor=CENTER)

    def Finish(self):
        self.window.destroy()

    def about(self):
        showinfo(title="About this APP", message="This software is developed to extract data for SDGs in Latin America and Caribbean from some particular websites. It is on going project and needs to be completed by other web sites information.\n\nAuthor : Clement A. Hounkpevi")

    def Procced_data(self,file):
        global Key_Words
        try : 
            self.Key_Words,self.Units = self.KeyWords(file)
            Key_Words = self.Key_Words
            self.butonFile1.destroy()
            self.w1.place(relx=0.5, rely=0.40, anchor=CENTER)
            self.butonFile2.place(relx=0.5, rely=0.60, anchor=CENTER)
        except Exception as e:
            return

    def KeyWords(self,file):
        try:
            if type(self.Error)!=str:
                self.Error.destroy()
                self.Error = ""
            Key_words=pd.read_csv(file)

            Key_Words=[]
            Units=[]

            for i in range(len(Key_words)):
                Key_Words.append(Key_words["Palabras Clave"][i].split("; "))
                Units.append(Key_words["Unidades"][i].split(","))
            Key_words=0
            return (Key_Words,Units)
        except Exception as e:
            self.directory = ""
            self.Error = Label(self.window, text="Selected file incorrect!!!\n\nCheck the File again!",fg="red")
            self.Error.place(relx=0.5, rely=0.75, anchor=CENTER)
            showerror("Error","Selected file incorrect!!!\n\nCheck the File again!")
            return

    def Progress(self,URL):
        size = len(URL)
        out = [None]*size
        others = [url for url in URL if url not in list(Priority.keys())]
        for url in others:
        	Priority[url]=50/len(others)
        for i in range(size):
            out[i] = Priority[URL[i]]
        tot = sum(out)
        resum = 100 - tot
        for i in range(size):
            out[i] = out[i] + out[i]*resum/tot
        return (out)

    def init_pool(self,the_dict):
        self.Key_Words = the_dict

    def Preprocess(self,URL):
        prog = self.Progress(URL)
        try:            
            try:
                for btn in self.btns:
                    btn.destroy()
                self.w2.destroy()
                self.list.destroy()
                self.xDefilB.destroy()
                self.yDefilB.destroy()
                self.butonFile3.destroy()
            except:
                pass

            try:
                self.w2.destroy()
                self.ENTRY.destroy()
                self.butonFile3.destroy()
            except:
                pass    
            self.progress.place(relx=0.50, rely=0.45, anchor=CENTER)
            self.w4.place(relx=0.50, rely=0.25, anchor=CENTER)
            self.w6.place(relx=0.50, rely=0.35, anchor=CENTER)
            res = askokcancel("Confirm","Would you like to continue?")
            if res ==False:
                self.Initialise()
                self.execute()
                return
            self.progress['value'] = 0
            self.window.update_idletasks()
            time.sleep(0.01)
        except Exception as e:
            return
        Output =[]
        cpu = mp.cpu_count()
        cp = 0

        if cpu>=32:
            cp = int(200*cpu/8)

        if cpu>=12:
            cp = int(60*cpu/8)

        elif cpu>=8:
            cp = int(16*cpu/8)

        else:
            cp = cpu-1

        ind = -1
        for url in URL:
            ind+=1
            if url == "https://datos.gov.co" or url == "https://datos.gov.co/": 
                Set = range(1000)
                index = 0
                Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]
                while Subs:
                    p = Pool(len(Subs),initializer=self.init_pool, initargs=(self.Key_Words,))
                    for out in p.imap_unordered(self.Datos_gov_co1,Subs):
                        self.progress['value'] += prog[ind]*60/100/len(Set)
                        self.window.update_idletasks()
                        time.sleep(0.1)
                        Output += out
                    p.terminate()
                    gc.collect()
                    index += cp
                    Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]
                
                Set = range(859)
                index = 0
                Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]
                while Subs:
                    p = Pool(len(Subs),initializer=self.init_pool, initargs=(self.Key_Words,))
                    for out in p.imap_unordered(self.Datos_gov_co2,Subs):
                        self.progress['value'] += prog[ind]*40/100/len(Set)
                        self.window.update_idletasks()
                        time.sleep(0.1)
                        Output += out
                    p.terminate()
                    gc.collect()
                    index += cp
                    Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]

            elif url == "https://www.who.int" or url == "https://www.who.int/":
                Urls = self.Url(url="",source=url)
                self.progress['value'] += prog[ind]*10/100
                self.window.update_idletasks()
                time.sleep(0.1)
                i = 0
                Set = []
                while Urls:
                    links = Urls.pop(0)
                    i += 1
                    while links:
                        Set.append((links.pop(0),i))

                index = 0
                Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]
                while Subs:
                    p = Pool(len(Subs),initializer=self.init_pool, initargs=(self.Key_Words,))
                    for out in p.imap_unordered(self.World_Health_Organization,Subs):
                        self.progress['value'] += prog[ind]*90/100/len(Set)
                        self.window.update_idletasks()
                        time.sleep(0.1)
                        Output.append(out)
                    p.terminate()
                    gc.collect()
                    index += cp
                    Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]

            elif url == "https://www.dane.gov.co" or url == "https://www.dane.gov.co/":
                Urls = self.Url(url="",source=url)

                i = 0
                Set = Urls
                Urls = 0

                self.progress['value'] += prog[ind]*10/100
                self.window.update_idletasks()
                time.sleep(0.1)
                

                index = 0
                Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]
                while Subs:
                    p = Pool(len(Subs),initializer=self.init_pool, initargs=(self.Key_Words,))
                    for out in p.imap_unordered(self.Dane_Colombia,Subs):
                        if out == None:
                            self.progress['value'] += prog[ind]*90/100/len(Set)
                            self.window.update_idletasks()
                            time.sleep(0.1)
                            continue
                        dwl = out[3]
                        l = len(dwl)
                        while dwl:
                            self.progress['value'] += prog[ind]*90/100/len(Set)/l
                            self.window.update_idletasks()
                            time.sleep(0.1)
                            lol = dwl.pop()
                            Output.append((out[0],out[1],out[2],lol))
                    p.terminate()
                    gc.collect()
                    index += cp
                    Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]

            elif url == "https://www.sdgindex.org" or url == "https://www.sdgindex.org/":
                Urls = self.Url(url="https://www.sdgindex.org/reports/",source=url)

                i = 0
                Set = Urls
                Urls = 0

                self.progress['value'] += prog[ind]*20/100
                self.window.update_idletasks()
                time.sleep(0.1)
                

                index = 0
                Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]
                while Subs:
                    p = Pool(len(Subs),initializer=self.init_pool, initargs=(self.Key_Words,))
                    for out in p.imap_unordered(self.SDG_Index,Subs):
                        if out == None:
                            self.progress['value'] += prog[ind]*80/100/len(Set)
                            self.window.update_idletasks()
                            time.sleep(0.1)
                            continue
                        dwl = out[3]
                        l = len(dwl)
                        while dwl:
                            self.progress['value'] += prog[ind]*80/100/len(Set)/l
                            self.window.update_idletasks()
                            time.sleep(0.1)
                            lol = dwl.pop()
                            Output.append((out[0],out[1],out[2],lol))
                    p.terminate()
                    gc.collect()
                    index += cp
                    Subs = Set[index:(index+cp)*(index+cp<=len(Set))+len(Set)*(index+cp>len(Set))]

        name = "Data_Info.csv"
        i = 0
        files = os.listdir(self.directory)
        while name in files:
            i +=1
            name = "Data_Info("+str(i)+").csv"

        file = open(self.directory+name,"w")
        file.write("Link\tSDGs\tAuthor\tDownload_Link")
        while Output:
            t = Output.pop()
            if t!=None:
                file.write("\n"+str(t[0])+"\t"+str(t[1])+"\t"+str(t[2])+"\t"+str(t[3]))

        file.close()
        gc.collect()
        self.w3 = Label(self.window, text="END\n\nYou can see the output file in this directory\n\n("+self.directory+name+")",font=("Helvetica", 14))
        self.w3.place(relx=0.5, rely=0.65, anchor=CENTER)
        self.butonFile4.place(relx=0.85, rely=0.90, anchor=CENTER)


if __name__=="__main__":
    mp.freeze_support()
    window = Tk()
    gui = GUI(window)
    gui.execute()


