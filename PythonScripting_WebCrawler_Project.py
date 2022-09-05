import re
import urllib
import urllib.request
from urllib.parse import urljoin
import networkx as nx
import matplotlib.pyplot as plt
import time
import subprocess
from bs4 import BeautifulSoup
import tldextract
from datetime import datetime

absolute_links = []                                                          #List of all the complete links to crawl
visited_sublinks = set()                                                     #List of all the visited weblinks
visited_edges = set()                                                        #List of web links mapping pair
file_save_location = 'C:\\Users\\KCP\\Desktop\\Web_Crawler\\'                #File Directory Path to save the web page


downloaded_files = set()                                                     #Complete File Path of the downloaded files
G = nx.Graph()                                                               #Intialize Graph
#start_link ='http://amitakashikar.blogspot.com/'
#default_link='https://www.oslomet.no/alumni'
default_link = 'https://www.ebs-consulting.no/'
#initial_link='www.ebs-consulting.no'
initial_link ='www.ebs-consulting.no'
#start_link = 'https://www.ebs-consulting.no/produkter'
initial_domain=' '


def extract_weblinks(web_content,initial_domain):
    weblink_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)              #Regular Expression to extract all the web links on the web page
    sublinks = re.findall(weblink_regex, web_content)                                       #Find all the web links in the web page
    web_links = set()
    for link in sublinks:
        if link.startswith('/'):
            complete_link = urljoin(start_link, link)
            extract = tldextract.extract(complete_link)
            if extract.domain == initial_domain:
                web_links.add(link)
            else:
                print("The weblink is not in the same domain as the initial website link")

        else:
            complete_link=link
            extract = tldextract.extract(complete_link)
            if extract.domain == initial_domain:
                web_links.add(link)
            else:
                print("The weblink is not in the same domain as the initial website link")

    return web_links

def get_save_webcontent(web_link):
    response = urllib.request.urlopen(web_link)
    webpage_source = response.read()
    web_content = webpage_source.decode()
    mod_link = web_link.replace('http://', '')                                                  #To generate the name of the webpage file to be downloaded
    mod_link = mod_link.replace('https://', '')
    mod_link = mod_link.replace('/', '.')
    mod_link = mod_link.replace('www.', '')

    if mod_link.endswith('.'):
        file_path = file_save_location + mod_link + 'html'                                 #Generate the whole directory location path for the web page to be saved
    else:
        file_path = file_save_location + mod_link + '.html'

    print (file_path)
    downloaded_files.add(file_path)
    try:
        #file = open(file_path, 'r')
        #file_content = file.read()
        #file_content = file.readlines()
        #if file_content != web_content:                                                    #Check if the downloaded file content is different than the web page content

        file = codecs.open(location, 'r', encoding="utf-8")
        file_content = file.readlines()
        content = ''
        for item in file_content:
            content = content + item

        if content != webpage_source:                                               #Check if the downloaded file content is different than the web page content
            print ("file contents not same")
            urllib.request.urlretrieve(web_link, file_path)                         #Save the changed website content in the directory folder
            downloaded_files.add(file_path)
            return web_content
        else:
            downloaded_files.add(file_path)
            return web_content
    except:
        urllib.request.urlretrieve(web_link, file_path)                               #Download the web page if it is not downloaded
        return web_content

def add_nodes(webpage):
    G.add_node(webpage)                                                               #Adding the webpage link as the node to the Network Graph G
    return

def add_edges(node1, node2):
    G.add_edge(node1, node2)                        #Adding the webpage link as the node to the Network Graph G
    return


def ping_latency(web_link):
    p = subprocess.Popen('ping ' + web_link, stdout=subprocess.PIPE)
    now=datetime.now()
    while(True):
        now=datetime.now()
        print ("Ping latency results at ",now)
        print(p.communicate()[0])
        time.sleep(600)                                                                     #Wait for 10 minutes before pinging again
        p = subprocess.Popen('ping ' + web_link, stdout=subprocess.PIPE)
        if p.poll() == 0:                                                                      #If Web site is not up
            break
    return

def word_search(input_word,total_count_of_word):
    for file_path in downloaded_files:
        file = open(file_path, 'r')
        #file = open(file_path, encoding="utf8")                                #Open th file in different encoding formats
        #file = open(file_path, encoding="utf8")
        #file = open(file_path, encoding="latin-1")

        file_data = file.read()
        soup = BeautifulSoup(file_data, "html.parser")
        paragraph_list = [p.get_text() for p in soup.find_all("p", text=True)]  #List commprehension to find the paragraph list in webpages
        for paragraph in paragraph_list:
            words = paragraph.split()
            count = words.count(input_word)
            total_count_of_word = total_count_of_word + count
    return total_count_of_word

def web_crawl(web_link, count,initial_domain):

    try:
        visited_sublinks.add(web_link)                              # adding the visited weblinks to the Visited Set
        web_content = get_save_webcontent(web_link)                      # Returns the web content of the url link
        web_sublinks = (extract_weblinks(web_content,initial_domain))
    except:
        print ("Some issue encountered in %s " %(web_link))
        return

    for link in web_sublinks:
        if link.startswith('/'):                                 # to check the start of the sub links
            complete_link = urljoin(start_link, link)
            absolute_links.append(complete_link)
        else:
            absolute_links.append(link)

    for sub_link in absolute_links:
        if sub_link not in visited_sublinks:
            visited_edges.add((web_link,sub_link,count))

    for sub_link in absolute_links:
        if sub_link not in visited_sublinks:
            if count>=8:
                break
            else:
                count+=1
                web_crawl(sub_link, count,initial_domain)


#start_link =input("Enter the website link to crawl")


#Default link as  default_link='https://www.oslomet.no/alumni'
ext = tldextract.extract(default_link)                                                #Extracting the domain of the start_link
initial_domain = ext.domain
web_crawl(default_link, 0, initial_domain)
node_number=1
for weblink in visited_sublinks:
    add_nodes(weblink)

for entry in visited_edges:
    add_edges(entry[0], entry[1])

print ("The nodes in the Network Graph are as follows")
print (G.nodes())
print ("The edges in the Network Graph are as follows")
print (G.edges())
labels=dict()
for i,node in enumerate(G.nodes()):
    labels[node]=i
#nx.draw_networkx_labels(G,pos,labels,font_size=10)
nx.draw(G,labels=labels, with_labels=True,node_color='yellow',arrows=True)

plt.title('Network Graph')
plt.savefig("web_crawler_graph.png")                                        # save as png
plt.show(G)  # display
word=input("Enter the word to search in the paragraphs of the web pages")
number=word_search(word,0)
print ("The count of the words found in the paragraphs of downloaded webpages are " + str(number))
ping_latency(initial_link)                                                     #Initial_link is the deault website link required in www format which is www.oslomet.no