import os

import re

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from io import open

def process_pdf(rsrcmgr, device, fp, pagenos=None, maxpages=2, password='', caching=True, check_extractable=True):
  interpreter = PDFPageInterpreter(rsrcmgr, device)
  for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,
              caching=caching, check_extractable=check_extractable):

       interpreter.process_page(page)
  return

def readPDF(pdffile):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr,retstr,laparams=laparams)

    process_pdf(rsrcmgr,device,pdffile)
    device.close()

    content = retstr.getvalue()
    retstr.close()

    return content

def handleData(filename):
    file = open('txt/' + filename, 'r', encoding='utf-8')

    while True:
        line = file.readline()
        if not line:
            file.close()
            break

        elif line.find("Load bearing anchor") > -1 or line.find("Torsion anchor") > -1 or line.find("Pins") > -1:
            # print(line)
            with open('result/' + filename, 'a', encoding='utf8') as f:
                f.write(line)


def abstract_extract(position):
    # 函数返回标题和摘要

    abstract_text = []
    keyword_text = []
    line_num = 0
    substr = "abstract".lower()
    substr0 = "keywords".lower()
    substr1 = "index term".lower()
    substr2 = "introduction".lower()
    flag = 0
    with open(position, "r", encoding='utf-8') as f:  # 打开文件
        lines = f.readlines()  # 读取文件中的一行

        # 提取标题
        (pdf_name, extension) = os.path.splitext(position)  # 分离后缀
        (filepath, title) = os.path.split(pdf_name)  # 分离文件目录和文件名
        abstract_text.append(title.strip('\n'))
        #abstract_text.append(lines[0].strip('\n'))

        # 提取摘要
        for line in lines:
            line = line.strip('\n')
            if line.lower().find(substr) != -1:  # if case-insensitive match
                if lines[line_num + 1].startswith('\n') == True:  # 如果下一行是空行，跳到第二行
                    line_num += 2
                else:  # 如果下一行不是空行，跳到下一行
                    line_num += 1

                flag = 1 #已经找到abstract，遍历后跳出
                # while lines[line_num].startswith('\n') == False | lines[line_num].startswith(' ') == False: # #判断是否是空行
                # 在出现keywords，index_term, introduction前截止
                while lines[line_num].lower().find(substr0) == -1 & lines[line_num].lower().find(substr1) == -1 & lines[
                    line_num].lower().find(substr2) == -1:
                    abstract_text.append(lines[line_num].strip('\n'))
                    line_num += 1
            if flag == 1:
                break
            line_num += 1
        f.close()

    abstract_text = ','.join(abstract_text)  # 转化为非数组类型, 以'，'分割
    abstract_text = abstract_text.replace('-,', '')
    return abstract_text

def keyword_extract(position):
    #函数返回keywords
    #提取以keyword开始的行

    keyword_text =[]
    line_num = 0
    substr = "keywords".lower()
    flag = 0
    with open(position, "r", encoding='utf-8') as f:  # 打开文件
        lines = f.readlines()  # 读取文件中的一行

        #提取keywords
        for line in lines:
            line = line.strip('\n')
            #if line.lower().find(substr) != -1: # if case-insensitive match
            if    line.lower().startswith(substr) == True: #line starts with "keywords"
                # if lines[line_num+1].startswith('\n') == True: #如果下一行是空行，跳到第二行
                #    line_num += 1
                flag = 1
                while lines[line_num].startswith('\n') == False: # #判断是否是空行
                    x = lines[line_num].split(":") #以"："为分割符分割一行
                    keyword_text.append(x[-1].strip('\n').lstrip()) #.lstrip()未删除每行前面的空行
                    #keyword_text.append(lines[line_num].strip('\n').lstrip())  # .lstrip()未删除每行前面的空行
                    line_num += 1

            if flag == 1:
               break
            line_num += 1
        f.close()
    keyword_text = ','.join(keyword_text)#转化为非数组类型
    #keyword_text.replace('-', '')
    keyword_text = keyword_text.replace('-,', '')
    return keyword_text


###################################
## Part 1： 把pdf文件提取到txt目录下
#获取目录下所有pdf文件
pdf_dir = '/Users/Peng/PycharmProjects/pythonProject/a/aa/212/2010 copy'
#pdfList = os.listdir(pdf_dir)

#遍历文件夹下所有目录的pdf文件
pdfList=[]
for root, dirnames, filenames in os.walk(pdf_dir):
    for filename in filenames:
        if os.path.splitext(filename)[1][1:].strip().lower() == 'pdf':   #only get pdf
            pdfList.append(os.path.join(root, filename))

#提取所有pdf文件到txt目录下
mydict = {}
for li in pdfList:
    #pdffile = open(pdf_dir + '/' + li, "rb")
    key = li.split('/')[-1]
    if not key in mydict:

       pdffile = open(li, "rb")
       content = readPDF(pdffile)
       (filepath, filename) = os.path.split(li) #分离文件目录和文件名
       str = re.sub('.pdf', '.txt', filename)
       file1 = 'txt/' + str
       with open( file1, 'w', encoding='utf8') as f:
           f.write(content)

       mydict[key]=handleData(str)
       print("Extracting pdf content from {} pdf file...".format(key))

print("All {} PFD have been Extracted...".format(len(mydict)))

###################################
## Part 2： 从所有txt文件提取题目，摘要和关键词
txt_path = "/Users/Peng/PycharmProjects/pythonProject/a/txt"  #文件夹目录
files= os.listdir(txt_path) #得到文件夹下的所有文件名称
abstract_txts = []
abstract_dict = {}
keyword_txt = []
keyword_dict = {}
for file in files: #遍历文件夹
       key = file.split('/')[-1]
       position = txt_path + '/' + file  # 构造绝对路径
       #print(position)
       if not key in abstract_dict:

          if os.path.splitext(file)[1][1:].strip().lower() == 'txt':   # only txt file
             data = abstract_extract(position).replace('-,', '') #去掉换行符
             abstract_txts.append(data)
             abstract_dict[key] = data

             keyword_data = keyword_extract(position)
             keyword_txt.append(keyword_data)
             keyword_dict[key] = keyword_data

          #print("Extracting txt content from {} ...".format(file))

#提取题目和摘要
f = open("Extract_abstract.txt",'w')##读取label.txt文件，没有则创建，‘a’表示再次写入时不覆盖之前的内容
abstract_txts = '\n'.join(abstract_txts)#转化为非数组类型
f.write(abstract_txts)
f.write('\n') ##实现换行的功能
f.close()

print("All {} Titles and abstracts have been Extracted...".format(len(abstract_dict)))

#提取关键词
f = open("Extract_keyword.txt",'w')##读取label.txt文件，没有则创建，‘a’表示再次写入时不覆盖之前的内容
keyword_txt = '\n'.join(keyword_txt)#转化为非数组类型
f.write(keyword_txt)
f.write('\n') ##实现换行的功能
f.close()

#How many articles contain keywords
keyword_count = len(keyword_dict) - list(keyword_dict.values()).count('')
print("All {} keywords have been Extracted...".format(keyword_count))



##To be continue...
#把字典变成数据框
import pandas as pd
df = pd.DataFrame.from_dict(abstract_dict, orient='index').reset_index()
df.columns = ["path", "content"]

df1 = pd.DataFrame.from_dict(keyword_dict, orient='index').reset_index()
df1.columns = ["path", "keyword"]

my_df = pd.merge(left=df,right=df1, how='left', left_on='path', right_on='path')

#计算提取内容长度，有些文章可能提取失败，需要手动提取
my_df["content_length"] = my_df.content.apply(lambda x: len(x))
#df["keyword_info"] = df.keyword.apply
keyword_count = my_df[my_df.keyword != ''].count()["keyword"]


def listToString(s):
    # initialize an empty string
    str1 = " "

    # return string
    return (str1.join(s))

cc = ['Geeks11 2232', 'for', 'Geeks']
dd = ['Geeks', 'for2', 'Geeksdss 32', '222']
dd = ['Geeks', 'for2', 'Geeksdss 32', '222']

file1 = open('test111.txt', 'w', encoding='UTF-8')
cc = ', '.join(cc)

file1.write(cc)
file1.write('\n')

dd = ', '.join(dd)
file1.write(dd)
file1.write('\n')
file1.write(dd)