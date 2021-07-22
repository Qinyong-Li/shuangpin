from os import error
from typing import List
from xpinyin import Pinyin
import matplotlib.pyplot as plt
import numpy as np
import json
import math

shengmu_list=['zh','ch','sh','b','p','m','f','d','t','n','l','g','k','h','j','q','x','r','z','c','s','y','w']
yunmu_list=['ang' ,'eng','ing','ong','ai' ,'ei','ui' ,'ao', 'ou', 'iu' ,'ie' ,'ve', 'er', 'an' ,'en' ,'in', 'un' ,'vn','a','o','e','i','u','v']

def input_article():
    frequency={}
    phrase={}

    # init dict
    for i in range(26):
        ch=chr(ord('a')+i)
        frequency[ch]=0

    for x in shengmu_list+yunmu_list:
        phrase[x]=0

    p=Pinyin()
    with open('./file/input.txt') as file:
        with open('./output/pinyin.txt','w') as out:
            lines=file.readlines()
            text_length=0
            for line  in lines:
                pinyin_str=p.get_pinyin(line,splitter="")
                text_length=text_length+len(line)
                for ch in pinyin_str:
                    index=ord(ch)-ord('a')
                    if 0<=index<26:
                        frequency[ch]=frequency[ch]+1
                
                for ch in line:
                    if '\u4e00' <= ch <= '\u9fff':
                        pinyin_ch=p.get_pinyin(ch)

                        for shengmu in shengmu_list:
                            if pinyin_ch.startswith(shengmu):
                                pinyin_ch=pinyin_ch[len(shengmu):]
                                phrase[shengmu]=phrase[shengmu]+1
                                break
                        
                        while pinyin_ch!="":
                            for yunmu in yunmu_list:
                                if pinyin_ch.startswith(yunmu):
                                    pinyin_ch=pinyin_ch[len(yunmu):]
                                    phrase[yunmu]=phrase[yunmu]+1
                                    break

    with open('./output/phrase.txt','w') as out:
        for key in sorted(phrase.keys()):
            out.write(key+":"+str(phrase[key])+'\n')
    
    return frequency,phrase

def generate_phicture():
    frequency,phrase=input_article()
    y_origin=[]
    y_phrase=[]
    keys=frequency.keys()
    for key in keys:
        y_origin.append(frequency[key])
    
    plt.figure(num=1,figsize=(12,5))
    plt.bar(x=keys,height=y_origin,label='origin',color='steelblue',alpha=0.8)
    plt.title("figure1-3 Keystoke frequency",y=-0.15)
    for x,y in zip(keys,y_origin):
        plt.text(x,y+10,str(y),ha='center',va='bottom')
    plt.savefig('./img/origin.png')

    keys=phrase.keys()
    keys=sorted(keys)
    for key in keys:
        y_phrase.append(phrase[key])

    plt.figure(num=2,figsize=(15,6))
    plt.bar(x=keys,height=y_phrase,label='phrase',color='indianred',alpha=0.8)
    plt.title("figure1-4 Pinyin phrase",y=-0.15)
    for x,y in zip(keys,y_phrase):
        plt.text(x,y+10,str(y),ha='center',va='bottom')
    plt.savefig('./img/phrase.png')

def statics():
    frequency,phrase=input_article()
    with open('./file/statics.txt','w') as out:
        keys=frequency.keys()
        is_writed=True
        for key in keys:
            out.write(key+"|"+str(frequency[key])+"|"+str(phrase[key])+"|"+str(frequency[key]-phrase[key])+"|")
            if not is_writed:
                out.write('\n')
            is_writed=not is_writed

    with open('./file/multi_ch.txt','w') as out:
        key1=phrase.keys()
        key2=frequency.keys()
        for key in sorted(key1-key2):
            out.write(key+":"+str(phrase[key])+"\n")

def return_difference():
    with open('./config/keys.json') as file:
        data_json=json.load(file)
        frequecy,phrase=input_article()
        res=0
        for key in data_json['left']:
            res=res+phrase[key]
        for key in data_json['right']:
            res=res-phrase[key]
        return res

# 背包算法，尽可能平均分配组合键
def allocate():
    frequency,phrease=input_article()
    keys=sorted(phrease.keys()-frequency.keys())
    difference=return_difference()
    sum=abs(difference)
    values=[]
    for key in keys:
        values.append(phrease[key])
        sum=sum+phrease[key]
    values.append(abs(difference))
    if difference<0:
        keys.append('right')
    else:
        keys.append('left')
    
    top=int((sum+1)/2)
    dp=np.zeros((22,top),dtype=int)
    path=np.zeros((22,top),dtype=int)
    for j in range(values[0],top):
        dp[0][j]=values[0]
        path[0][j]=1

    for i in range(1,len(values)):
        for j in range(0,top):
            if j<values[i]:
                dp[i][j]=dp[i-1][j]
            else:
                if dp[i-1][j]>dp[i-1][j-values[i]]+values[i]:
                    dp[i][j]=dp[i-1][j]
                else:
                    dp[i][j]=dp[i-1][j-values[i]]+values[i]
                    path[i][j]=1

    j=top-1
    i=21
    res=[]
    while i>=0:
        if path[i][j]==1:
            res.append(keys[i])
            j=j-values[i]
            i=i-1
        else:
            i=i-1

    left=None
    right=None
    if 'left' in res:
        left=res
        right=list(set(keys).difference(set(res)))
        left.remove('left')
    elif 'right' in res:
        right=res
        left=list(set(keys).difference(set(res)))
        right.remove('right')
    elif values[21]=='right':
        left=res
        right=list(set(keys).difference(set(res)))
        right.remove('right')
    else:
        right=res
        left=list(set(keys).difference(set(res)))
        left.remove('left')
    return left,right

def define_phrase():
    left_phrase,right_phrase=allocate()
    left_key,right_key=[],[]
    left_weight,right_weight={},{}
    with open('./config/keys.json') as file:
        data_json=json.load(file)
        left_key,right_key=data_json['left'],data_json['right']
    with open('./config/weight.json') as file:
        data_json=json.load(file)
        for ch in left_key:
            left_weight[ch]=data_json[ch]
        for ch in right_key:
            right_weight[ch]=data_json[ch]
    left_phrase_dict,right_phrase_dict={},{}
    frequency,phrase_dict=input_article()
    for phrase in left_phrase:
        left_phrase_dict[phrase]=phrase_dict[phrase]
    for phrase in right_phrase:
        right_phrase_dict[phrase]=phrase_dict[phrase]
    left_weight = sorted( left_weight.items(),key = lambda x:x[1],reverse = False)
    right_weight = sorted( right_weight.items(),key = lambda x:x[1],reverse = False)
    left_phrase_dict=sorted( left_phrase_dict.items(),key = lambda x:x[1],reverse = True)
    right_phrase_dict=sorted( right_phrase_dict.items(),key = lambda x:x[1],reverse = True)

    res={}
    for i in range(len(left_phrase_dict)):
        res[left_phrase_dict[i][0]]=left_weight[i][0]
    for i in range(len(right_phrase_dict)):
        res[right_phrase_dict[i][0]]=right_weight[i][0]
    
    with open('./file/res.txt','w') as file:
        is_writed=False
        for key in res.keys():
            res[key]=res[key]
            file.write(key+"|;"+res[key]+"|")
            if is_writed:
                file.write("\n")
            is_writed=not is_writed
        
    return res

def output_result():
    count={}
    frequency,phrase=input_article()
    res=define_phrase()
    for key in frequency.keys():
        count[key]=phrase[key]
    for key in res.keys():
        count[res[key]]=count[res[key]]+phrase[key]
    
    p=Pinyin()
    length=0
    # with open('./file/input.txt') as file:
    #     with open('./output/pinyin.txt','w') as out:
    #         lines=file.readlines()
    #         for line  in lines:                
    #             for ch in line:
    #                 if '\u4e00' <= ch <= '\u9fff':
    #                     pinyin_ch=p.get_pinyin(ch)

    #                     for shengmu in shengmu_list:
    #                         if pinyin_ch.startswith(shengmu):
    #                             pinyin_ch=pinyin_ch[len(shengmu):]
    #                             phrase[shengmu]=phrase[shengmu]+1
    #                             if len(shengmu)==1:
    #                                 out.write(shengmu)
    #                             else:
    #                                 out.write(res[shengmu])
    #                             length=length+1
    #                             break
                        
    #                     while pinyin_ch!="":
    #                         for yunmu in yunmu_list:
    #                             if pinyin_ch.startswith(yunmu):
    #                                 pinyin_ch=pinyin_ch[len(yunmu):]
    #                                 phrase[yunmu]=phrase[yunmu]+1
    #                                 if len(yunmu)==1:
    #                                     out.write(yunmu)
    #                                 else:
    #                                     out.write(res[yunmu])
    #                                 length=length+1
    #                                 break
    return count

def calculate_variance(values):
    av=sum(values)
    av=av/(len(values)*1000)

    res=0.0
    for v in values:
        res=res+(v/1000 -av)**2
    res=math.sqrt(res)
    return res

def calculate_total_keystroke(count):
    res={}
    with open('./config/error.json') as file:
        data_json=json.load(file)
        for key in count.keys():
            if key in data_json["top_key"]:
                res[key]=int(count[key]*(1+2*data_json["top_error"]))
            elif key in data_json["mid_key"]:
                res[key]=int(count[key]*(1+2*data_json["mid_error"]))
            else:
                res[key]=int(count[key]*(1+2*data_json["bottom_error"]))

    return res

def calculate_error_keystroke(count):
    res={}
    with open('./config/error.json') as file:
        data_json=json.load(file)
        for key in count.keys():
            if key in data_json["top_key"]:
                res[key]=int(count[key]*(data_json["top_error"]))
            elif key in data_json["mid_key"]:
                res[key]=int(count[key]*(data_json["mid_error"]))
            else:
                res[key]=int(count[key]*(data_json["bottom_error"]))

    return sum(res.values())

def output_res():
    frequency,x=input_article()
    new_data=output_result()
    total_origin=sum(calculate_total_keystroke(frequency).values())
    per_ch_origin=total_origin/19698
    delta_orgin=calculate_variance(frequency.values())
    error_origin=calculate_error_keystroke(frequency)/sum(frequency.values())*100
    total_new=sum(calculate_total_keystroke(new_data).values())
    per_ch_new=total_new/19698
    delta_new=calculate_variance(new_data.values())
    error_new=calculate_error_keystroke(new_data)/sum(new_data.values())*100

    plt.figure(figsize=(12,7))
    plt.bar([r"$\Delta$",r"$\eta$",r"$\xi$"],[delta_orgin,per_ch_origin,error_origin],label='origin',color='steelblue',alpha=0.8)
    plt.bar([r"$\Delta$",r"$\eta$",r"$\xi$"],[delta_new,per_ch_new,error_new],label='origin',color='indianred',alpha=0.8)
    for x,y in zip([r"$\Delta$",r"$\eta$",r"$\xi$"],[delta_new,per_ch_new,error_new]):
        plt.text(x,y+0.2,'%.2f' % y,ha='center',va='bottom')
    for x,y in zip([r"$\Delta$",r"$\eta$",r"$\xi$"],[delta_orgin,per_ch_origin,error_origin]):
        plt.text(x,y+0.2,'%.2f' % y,ha='center',va='bottom')
    plt.savefig('./img/compared.png')

    print("全拼编码")
    print("均衡指标:","%.2f"%delta_orgin)
    print("输入效率指标:","%.2f"%per_ch_origin)
    print("错误率(%):","%.2f"%error_origin)
    print("-------------------------------------------")
    print("双拼编码")
    print("均衡指标:","%.2f"%delta_new)
    print("输入效率指标:","%.2f"%per_ch_new)
    print("错误率(%):","%.2f"%error_new)

    
    
output_res()
    
    
