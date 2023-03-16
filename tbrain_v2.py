import time
import pandas as pd
import numpy as np
from sklearn.externals import joblib 
last_name = pd.read_csv('last_name_CH.csv')

def model2(input):
    def name_len(x):
        return len(x)
    model = joblib.load('RFmodel2')
    feature = joblib.load('feature')
  # 取input的人名以及人名的位置
    name_id = input[input['word_pos']=='PERSON']
  # 只留百家姓
    name_id['name_last'] = name_id['word'].str.slice(start = 0, stop= 1)
    def name_last_test(x):
        res = x in list(last_name['name'])
        return res
    name_id = name_id[list(map(name_last_test,name_id['name_last']))]
  # 處理記者
    first_word = list(input['word'][:15])
    last_word = list(input['word'][-15:])
    first = '記者' in first_word or '報導' in first_word or '編輯' in first_word
    last = '記者' in last_word or '報導' in last_word or '編輯' in last_word
    def loca_test(x):
        res = x <=15
        res2 = x >= (len(input)-15)
        res3 = not ((res and first) or (res2 and last))
        return res3
    name_id = name_id[list(map(loca_test,name_id['word_loca']))]
  # 只猜三字
    name_id['name_len'] = list(map(name_len,name_id['word']))
    name_id = name_id[name_id['name_len']>2]
    name_id = name_id[['word','word_loca']].rename(columns = {'word_loca':'name_loca','word' : 'name'})
    name_id['news_ID'] = 1
  # 取出在keyword中的row
    def test(x):
        res = x in feature
        return res
    df1 = input[list(map(test,input['word']))][['word','word_loca']]
    df1['news_ID'] = 1
  # 算位置的權重
    df2 = pd.merge(df1,name_id,how = 'right',on = 'news_ID')
    df2['pos'] = (1+(abs(df2['name_loca']-df2['word_loca'])))
    df2['relat_pos'] = np.log(1/(df2['pos']/len(df2)))
    group_agg = df2.groupby(['name','word'])['relat_pos'].agg('max')
    df3 = pd.DataFrame(group_agg).reset_index()
    df4 = pd.pivot_table(df3,index='name',columns='word',values='relat_pos').reset_index()
  # 補齊沒有抽到的feature
    input_feature = list(df4.columns)
    ignore_col = list(set(feature) - set(input_feature))
    empty_df = pd.DataFrame(columns = ignore_col)
    empty_df[:] = 0
# 餵進model的DataFrame
    rf_df = pd.concat([df4,empty_df],axis = 1)
    rf_df = rf_df.fillna(0)
# output 
    res = model.predict(rf_df[feature])
    ans_list = []
    for i in range(len(res)):
        if res[i] ==1:
            ans_list.append(rf_df['name'][i])
    return ans_list

tf_idf_keyword = pd.read_csv('tf_idf_keyword.csv')

def keyword_test(x):
    res = x in list(tf_idf_keyword['word'])
    return res
def model1(input):
    if sum(list(map(keyword_test,test_df['word']))) > 0:
        return model2(input)
    else:
        ans_list = []
        return ans_list