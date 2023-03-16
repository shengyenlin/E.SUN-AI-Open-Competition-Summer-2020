# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import jsonify
import datetime
import hashlib
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from ckiptagger import WS, POS, NER
import time
ws = WS("./data", disable_cuda=False)
pos = POS("./data", disable_cuda=False)
ner = NER("./data", disable_cuda=False)


def ckip(text):
    x = time.time()
    text_comma = text.split('，')
    ws_comma = ws(text_comma)
    ws_news = [[ws_comma[i][j] for i in range(len(ws_comma)) for j in range(len(ws_comma[i]))]]
    pos_news = pos(ws_news)
    ner_news = ner(ws_news, pos_news)

    news_entity = []
    list_ner = sorted(ner_news[0])
    for i in ws_news[0]:
        news_entity.append('NONE_PERSON')
        for j in range(len(list_ner)):
            if i == list_ner[j][3] and list_ner[j][2] == 'PERSON':
                news_entity.pop()
                news_entity.append('PERSON')
            else:
                continue

    word_list = [ws_news[0][j] for j in range(len(ws_news[0]))]
    word_loca = []
    count = 0 
    for j in range(len(ws_news[0])):
        count += 1
        word_loca.append(count)

    data_final = {'word': word_list, 'word_pos': news_entity, 'word_loca': word_loca}
    df_final = DataFrame(data_final)
    y = time.time()
    print("斷詞階段共花了{}秒".format(y-x))
    return df_final

app = Flask(__name__)
####### PUT YOUR INFORMATION HERE #######
CAPTAIN_EMAIL = 'b06305030@g.ntu.edu.tw'          #
SALT = 'dragons666'                        #
#########################################

def generate_server_uuid(input_string):
    """ Create your own server_uuid
    @param input_string (str): information to be encoded as server_uuid
    @returns server_uuid (str): your unique server_uuid
    """
    s = hashlib.sha256()
    data = (input_string+SALT).encode("utf-8")
    s.update(data)
    server_uuid = s.hexdigest()
    return server_uuid

def predict(article):
    """ Predict your model result
    @param article (str): a news article
    @returns prediction (list): a list of name
    """
    f = open('test.txt', 'w')
    f.write(article)
    f.close()
    

    ticks = time.time()
    #ws_results = ws([article])
    #pos_results = pos([article])
    #ner_results = ner([article], pos_results)
    ckip_df = ckip(article)
    ckip_df.to_csv("ckip_df.csv", encoding = "utf-8")
    
    ticks2 = time.time()
    print("斷詞所花費時間: {}s".format(ticks2 - ticks))
    ####### PUT YOUR MODEL INFERENCING CODE HERE #######
    prediction = ['']
    #prediction = ws_results[0]
    
    
    ####################################################
    prediction = _check_datatype_to_list(prediction)
    return prediction

def _check_datatype_to_list(prediction):
    """ Check if your prediction is in list type or not. 
        And then convert your prediction to list type or raise error.
        
    @param prediction (list / numpy array / pandas DataFrame): your prediction
    @returns prediction (list): your prediction in list type
    """
    if isinstance(prediction, np.ndarray):
        _check_datatype_to_list(prediction.tolist())
    elif isinstance(prediction, pd.core.frame.DataFrame):
        _check_datatype_to_list(prediction.values)
    elif isinstance(prediction, list):
        return prediction
    raise ValueError('Prediction is not in list type.')

@app.route('/healthcheck', methods=['POST'])
def healthcheck():
    """ API for health check """
    data = request.get_json(force=True)  
    t = datetime.datetime.now()  
    ts = str(int(t.utcnow().timestamp()))
    server_uuid = generate_server_uuid(CAPTAIN_EMAIL+ts)
    server_timestamp = t.strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({'esun_uuid': data['esun_uuid'], 'server_uuid': server_uuid, 'captain_email': CAPTAIN_EMAIL, 'server_timestamp': server_timestamp})

@app.route('/inference', methods=['POST'])
def inference():
    """ API that return your model predictions when E.SUN calls this API """
    data = request.get_json(force=True)  
    esun_timestamp = data['esun_timestamp'] #自行取用
    
    t = datetime.datetime.now()  
    ts = str(int(t.utcnow().timestamp()))
    server_uuid = generate_server_uuid(CAPTAIN_EMAIL+ts)
    
    try:
        answer = predict(data['news'])
    except:
        raise ValueError('Model error.')        
    server_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({'esun_timestamp': data['esun_timestamp'], 'server_uuid': server_uuid, 'answer': answer, 'server_timestamp': server_timestamp, 'esun_uuid': data['esun_uuid']})

if __name__ == "__main__":    
    app.run(host='0.0.0.0', port=8080, debug=True)
