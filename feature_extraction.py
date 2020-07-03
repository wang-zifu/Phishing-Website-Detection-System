# -*- coding: utf-8 -*-
"""featureExtraction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10u-Vg2vGdWpIFWQfuCln-eY8f836p0lk
"""

# !pip install python-whois

# 1  legitimate
# -1 phishing
# 0 suspicious
from tldextract import extract
import whois
import re
import requests
import ipaddress
from bs4 import BeautifulSoup
import time
import urllib.request
import socket
from googlesearch import search
from dateutil.parser import parse as date_parse
from datetime import time
#

#calculate number of months:
def diff_month(d1,d2):
    return ((d1[:4] - d2[:4])*12 + d1[4:6]-d2[4:6] )     


def generate_url_dataset(url):
    dataset=[]
    #Convert the  given url in the standard format
    if not re.match(r"^https?",url):
        url="https://"+url
        

    
    #stores the response of given url
    try:
        response= requests.get(url)
        soup= BeautifulSoup(response.text,'html.parser')
    except:
        response=""
        soup= -999



    #Find the domain of the  url
    domain= re.findall(r"://([^/]+)/?",url)[0]
    if(re.match(r"^www.",domain)):
        domain= domain.replace("www.","")

    
    #Request all the info about domain
    try:
        whois_response =whois.whois(domain)
  
    except:
        whois_response=""
    
    rank_checker_response= requests.post("https://www.checkpagerank.net/index.php",{
        "name":domain
    })


    #extract global rank of the website
    try:
        global_rank = int(re.findall(r"Global Rank: ([0-9]+)",rank_checker_response.text)[0])
    except:
        global_rank = -1


    #1.having ip_address
    try:
        ipaddress.ip_address(url)
        dataset.append(-1)
    except:
        dataset.append(1)
    
    
    
    #2.Url_length
    if len(url)<54:
        dataset.append(1)
    elif len(url)>=54 and len(url)<=75:
        dataset.append(0)
    else:
        dataset.append(-1)



    #3.check if url is shortend 
    match= re.search('bit\.ly|goo\.gl|shorte\.st|go21\.ink|x\.co|ow\.ly|t\.co|tinyrl|tr\.im|is\.gd|cli\.gs|'
                    'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|sniurl\.com'
                    'short\.to|Budurl\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us'
                    'doiop\.com|short\.ie|kl\.am|wp\.me|rubyul\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in'
                    'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im'
                    'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|youIs\.org'
                    'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.in|link\.zip\.net',url)
    if(match):
        dataset.append(-1)
    else:
        dataset.append(1)

    #4. having "@" symbol
    if(re.search(r'@',url)):
        dataset.append(-1)

    else:
        dataset.append(1)


    #5. Double slash redirecting
    list=[x.start(0) for x in re.finditer("//",url)]
    if list[len(list)-1]>6:
        dataset.append(-1)
    else:
        dataset.append(1)

    
    #6.Prefix-Sufix
    subDomain, domain, suffix = extract(url)
    if(domain.count('-')):
        dataset.append(-1)
    else:
        dataset.append(1)


    #7. having sub-domain:
    
    subDomain, domain, suffix = extract(url)
    if(subDomain.count('.')==0):
        dataset.append(1)

    elif(subDomain.count('.')==1):
        dataset.append(0)

    else:
        dataset.append(-1)



    #8.SSLfinal_score:
    try:
    #check wheather contains https       
        if(re.search('^https',url)):
            usehttps = 1
        else:
            usehttps = 0
        #getting the certificate issuer to later compare with trusted issuer 
        #getting host name
        subDomain, domain, suffix = extract(url)
        host_name = domain + "." + suffix
        context = ssl.create_default_context()
        sct = context.wrap_socket(socket.socket(), server_hostname = host_name)
        sct.connect((host_name, 443))
        certificate = sct.getpeercert()
        issuer = dict(x[0] for x in certificate['issuer'])
        certificate_Auth = str(issuer['commonName'])
        certificate_Auth = certificate_Auth.split()
        if(certificate_Auth[0] == "Network" or certificate_Auth == "Deutsche"):
            certificate_Auth = certificate_Auth[0] + " " + certificate_Auth[1]
        else:
            certificate_Auth = certificate_Auth[0] 
        trusted_Auth = ['Comodo','Symantec','GoDaddy','GlobalSign','DigiCert','StartCom','Entrust','Verizon','Trustwave','Unizeto','Buypass','QuoVadis','Deutsche Telekom','Network Solutions','SwissSign','IdenTrust','Secom','TWCA','GeoTrust','Thawte','Doster','VeriSign']        
        
        #getting age of certificate
        startingDate = str(certificate['notBefore'])
        endingDate = str(certificate['notAfter'])
        startingYear = int(startingDate.split()[3])
        endingYear = int(endingDate.split()[3])
        Age_of_certificate = endingYear-startingYear
        
        #checking final conditions
        if((usehttps==1) and (certificate_Auth in trusted_Auth) and (Age_of_certificate>=1) ):
            dataset.append(1) #legitimate
        elif((usehttps==1) and (certificate_Auth not in trusted_Auth)):
            dataset.append(0) #suspicious
        else:
            dataset.append(-1) #phishing
        
    except Exception as e:
        dataset.append(-1)

    #------------------------------------------------------false----------------------------------------------------------    
    #9.Domain- Registration length
    try:
        try:
            registration_length=0
            expiration_date= whois_response.expiration_date[0].strftime('%Y%m%d')
            today= datetime.now()
            today= today.strftime('%Y%m%d')
            registration_length= abs((int(expiration_date[:4]) - int(today[:4])))
            
            if(registration_length<=1):
                dataset.append(-1)

            else:
                dataset.append(1)
        except:
            dataset.append(-1)
    except:
            print('err')
            dataset.append(-1)

    #-------------------------------------------------------------------------------------------------------------------------


    #10.Fevicon
    i=0
    if soup==-999:
        dataset.append(-1)
    else:
        try:
            for head in soup.find_all('head'):
                for head.link in soup.find_all('link',href=True):
                    i=i+1
                    dots=[x.start(0) for x in re.finditer('\.',head.link['href'])]
                    if url in head.link['href'] or len(dots)==1 or domain in head.link['href']:
                        dataset.append(1)
                        
                        raise StopIteration
                    else:
                        dataset.append(-1)
                        raise StopIteration
            if(i==0):
                dataset.append(-1)
        except StopIteration:
            pass            
    

    #11. Port
    try:
        port=domain.split(':')[1]
        if port:
            dataset.append(-1)
            
            
        else:
            dataset.append(1)
            

    except:
        dataset.append(1)


    #12.HTTPS_token
    if re.findall(r"^https//",url):
        dataset.append(1)
    else:
        dataset.append(-1)

    #13. Request_url
    success=0
    i=0
    if soup==-999:
        dataset.append(-1)
    else:
        for img in soup.find_all('img',src=True):
            dots=[x.start(0) for x in re.finditer('\.',img['src'])]
            if url in img['src'] or domain in img['src'] or len(dots)==1:
                success=success+1
            i=i+1

        for audio in soup.find_all('audio',src=True):
            dots=[x.start(0) for x in re.finditer('\.',audio['src'])]
            if url in audio['src'] or domain in audio['src'] or len(dots)==1:
                success=success+1
            i=i+1
        
        for embd in soup.find_all('embd',src=True):
            dots=[x.start(0) for x in re.finditer('\.',embd['src'])]
            if url in embd['src'] or domain in embd['src'] or len(dots)==1:
                success=success+1
            i=i+1
        
        for iframe in soup.find_all('iframe',src=True):
            dots=[x.start(0) for x in re.finditer('\.',iframe['src'])]
            if url in iframe['src'] or domain in iframe['src'] or len(dots)==1:
                success=success+1
            i=i+1
        
        try:
            percentage= success/float(i)*100
            if percentage<22.0:
                dataset.append(1)
            elif ((percentage>=22.0 ) and (percentage<61.0)):
                dataset.append(0)
            else:
                dataset.append(-1)
        
        except:
            dataset.append(1)



    #14.Url_of_anchor
    percentage=0
    i=0
    unsafe=0
    if soup==-999:
        dataset.append(-1)
    else:
        for a in soup.find_all('a',href=True):
            if "#" in a['href'] or "javascript" in a['href'].lower() or "mailto" in  a["href"].lower() or not (url in a['href'] or domain in a['href']):
                unsafe=unsafe+1
            i=i+1
        
        try:
            percentage= unsafe/float(i)*100
            if percentage<31.0:
                dataset.append(1)
            elif ((percentage>=31.0 ) and (percentage<67.0)):
                dataset.append(0)
            else:
                dataset.append(-1)
            
        except:
            dataset.append(1)
        


    #15.links_in_tags
    success=0
    i=0
    if soup==-999:
        dataset.append(-1)
        dataset.append(-1)

    else:
        for link in soup.find_all('link',src=True):
            dots=[x.start(0) for x in re.finditer('\.',link['src'])]
            if url in link['src'] or domain in link['src'] or len(dots)==1:
                success=success+1
            i=i+1

        for script in soup.find_all('script',src=True):
            dots=[x.start(0) for x in re.finditer('\.',script['src'])]
            if url in script['src'] or domain in script['src'] or len(dots)==1:
                success=success+1
            i=i+1
        
        try:
            
            percentage= success/float(i)*100
            if percentage<17.0:
                dataset.append(1)

            elif ((percentage>=17.0 ) and (percentage<81.0)):
                dataset.append(0)   
        
            else:
                dataset.append(-1)
        
        except:
            dataset.append(1)

    
    
        #16.SFH
        x=0
        for form in soup.find_all("form",action=True):
            x=x+1
            if form['action']=="" or form['action']=="about:blank":
                dataset.appaend(-1)
                break
            elif url not in form['action'] and domain not in form['action']:
                dataset.append(0)

                break  
            else:
                dataset.append(1)
                
                break
        if(x==0):
            dataset.append(0)



    #17. submiting to email
    if response=="":
        dataset.append(-1)
        
    else:
        if re.findall(r'[mail\(\)|mailto:?]',response.text):
            dataset.append(1)

        else:
            dataset.append(-1)

             
    #18. Abnormal url
    if response=="":
        dataset.append(-1)
    
    else:
        if response.text=="":
            dataset.append(1)

        else:
            dataset.append(-1)



    #19.Redirects

    if response=="":
        dataset.append(-1)
    
    else:
        if len(response.history)<=1:
            dataset.append(-1)
        elif len(response.history)<=4:
            dataset.append(0)
        else:
            dataset.append(1)




    #20. Mouseovers

    if response=="":
        dataset.append(-1)
    else:
        if re.findall(r"<script>.+onmouseover.+</scipt>",response.text):
            dataset.append(1)
        else:
            dataset.append(-1)
    

    #21.RightClick disable
            
    if response=="":
        dataset.append(-1)
    else:
        if re.findall(r"event.button ?== ?2",response.text):
            dataset.append(1)
        else:
            dataset.append(-1)


    #22. popup window
    if response=="":
        dataset.append(-1)
    else:
        if re.findall(r"alert\(",response.text):
            dataset.append(1)
        else:
            dataset.append(-1)


    #23. Iframe
    if response=="":
        dataset.append(-1)
    else:
        if re.findall(r"[<iframe>|<frameBorder>]",response.text):
            dataset.append(1)
        else:
            dataset.append(-1)

    #24. age_of_domain
    if response=="":
        dataset.append(-1)

    else:
        try:
            registration_date=whois_response.creation_date[0].strftime('%Y%m%d')
            expiration_date= whois_response.expiration_date[0].strftime('%Y%m%d')
            diff_month=(int(expiration_date[:4]) - int(registration_date[:4]))*12 + int(expiration_date[4:6])-int(registration_date[4:6])
            if diff_month<=6:
                dateset.append(-1)
            else:
                dataset.append(1)
                
        except:
                dataset.append(1)


    #25. DNS record
    dns=1
    try:
        d=whois.whois(domain)
    except:
        dns=-1
    if dns==-1:
        dataset.append(-1)

    else:
        if registration_length <= 1:
            dataset.append(-1)
        else:
            dataset.append(1) 


    #26. web-traffic
    try:
        rank=BeautifulSoup(urllib.request.urlopen("https://data.alexa.com/data?cli=10&dat=s&url="+ url).read(),"xml").find("REACH")['RANK']
        rank= int(rank)
        if( rank< 100000):
            dataset.append(1)
        else:
            dataset.append(0)

    except TypeError:
        dataset.append(-1)


    #27. page rank
    try:
        if global_rank>0 and global_rank<100000:
            dataset.append(1)
        else:
            dataset.append(-1)
            
    except:
        dataset.append(1)
        

    #28. google_index
    site= search(url, 5)
    if site:
        dataset.append(1)
    else:
        dataset.append(-1)

    #29. links_pointing_to_them
    if response=="":
        dataset.append(-1)

    else:
        number_of_links= len(re.findall(r"<a href=",response.text))
        if number_of_links==0:
            dataset.append(1)
        elif number_of_links<=2:
            dataset.append(0)
        else:
            dataset.append(-1)

    #30. statical_report
    url_match=re.search('at\.ua|usa\.cc|baltazarpresentes\.com\.br|pe\.hu|esy\.es|hol\.es|sweedy\.com|myjino\.ru|96\.lt|ow\.ly',url)
    try:
        ip_address= socket.gethostbyname(domain)
        ip_match=re.search('46\.112\.61\.108|213\.174\.157\.151|121\.50\.168\.88|192\.185\.217\.116|78\.46\.211\.158|181\.174\.165\.13'
                           '|46\.242\.145\.103|121\.50\.168\.40|83\.125\.22\.219|46\.242\.145\.98|107\.151\.148\.44|107\.151\.148\.107'
                           '|64\.70\.19\.203|199\.184\.144\.27|107\.151\.148\.108|107\.151\.148\.109|119\.28\.52\.61|54\.83\.43\.69|'
                           '52\.69\.166\.231|216\.58\.192\.225|118\.184\.25\.86|67\.208\.74\.71|23\.253\.126\.58|104\.239\.157\.210|'
                           '175\.126\.123\.219|141\.8\.224\.221|10\.10\.10\.10|43\.229\.108\.32|103\.232\.215\.140|69\.172\.201\.153|'
                           '216\.218\.185\.162|54\.225\.104\.146|103\.243\.24\.98|199\.59\.243\.120|31\.170\.160\.61|213\.19\.128\.77|'
                           '62\.113\.226\.131|208\.100\.26\.234|195\.16\.127\.102|195\.16\.127\.157|34\.196\.13\.28|103\.224\.212\.222|'
                           '172\.217\.4\.225|54\.72\.9\.51|192\.64\.147\.141|198\.200\.56\.183|23\.253\.164\.103|52\.48\.191\.26|'
                           '52\.214\.197\.72|87\.98\.255\.18|209\.99\.17\.27|216\.38\.62\.18|104\.130\.124\.96|47\.89\.58\.141|78\.46\.211\.158|'
                           '54\.86\.225\.156|54\.82\.156\.19|37\.157\.192\.102|204\.11\.56\.48|110\.34\.231\.42',ip_address)
        if(url_match):
            dataset.append(-1)
        elif ip_match:
            dataset.append(-1)
        else:
            dataset.append(1)
    except:
        dataset.append(0)
        # print("connection problem.check your internet connection!")
    
    return dataset