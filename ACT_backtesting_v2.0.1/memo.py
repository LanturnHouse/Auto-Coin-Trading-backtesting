#%%

import pyupbit
from fbprophet import Prophet


# 시간: ds
# 종가: y
# OHLCV(open: 당일시가, high: 고가, low: 저가, close: 종가, volume: 거래량)
print('데이터 가져오는중...')
df = pyupbit.get_ohlcv('KRW-XRP',interval = 'minute1' ,count = 1000)
#df = pyupbit.get_ohlcv('KRW-BTC', count = 60)
df = df.reset_index()
df['ds'] = df['index']
df['y'] = df['close']

data = df[['ds','y']][:-10]
print('Done!')



print('---------------------')
print('모델 만드는중...')
model = Prophet(changepoint_prior_scale=0.5,
                weekly_seasonality=20,
                daily_seasonality=20,
                seasonality_mode='multiplicative')
model.add_seasonality(name='monthly', period=60, fourier_order=5)
model.fit(data)
print('Done!')



print('---------------------')
print('예측중...')
future = model.make_future_dataframe(periods=20, freq = 'min')
forecst = model.predict(future)
forecst['now_price'] = df[['y']][-10:]
print('Done!')


print(type(forecst))

fig = model.plot(forecst)
forecst_ = forecst[-30:]
fig2 = forecst_.plot(xlabel = "ds", y = ['yhat', 'yhat_lower', 'yhat_upper', 'now_price'])



#sell_order = 0.0
#buy_order = 0.0


#fee = 0.05
df['now_price'] = df['open']
df['yhat'] = forecst['yhat']
df['yhat_upper'] = forecst['yhat_upper']
df['yhat_lower'] = forecst['yhat_lower']
df['range'] = (forecst['yhat_upper'] - df['now_price']) / 2
df['yhat_sell_price'] = df['now_price'] + df['range'].shift(1)
df['sell_price'] = 0.0
df['buy_bool'] = ''
df['sell_bool'] = ''
df['ror'] = 1.0
df['buy_coin_num'] = 0.0
df['cell_revenue'] = 0.0
df['all_cell_revenue'] = 0.0
df['sell_count'] = 0.0
# df['hqr'] = 1.0



'''
df['cell_0_ror'] = 1.0
df['cell_1_ror'] = 1.0
df['cell_2_ror'] = 1.0
df['cell_3_ror'] = 1.0
df['cell_4_ror'] = 1.0
df['cell_5_ror'] = 1.0
df['cell_6_ror'] = 1.0
df['cell_7_ror'] = 1.0
df['cell_8_ror'] = 1.0
df['cell_9_ror'] = 1.0



df['cell_0_hqr'] = 1.0
df['cell_1_hqr'] = 1.0
df['cell_2_hqr'] = 1.0
df['cell_3_hqr'] = 1.0
df['cell_4_hqr'] = 1.0
df['cell_5_hqr'] = 1.0
df['cell_6_hqr'] = 1.0
df['cell_7_hqr'] = 1.0
df['cell_8_hqr'] = 1.0
df['cell_9_hqr'] = 1.0
'''



# 리스트 del을 하게 될 경우 index 10 에 있던게 index 9로 넘어가게 되어서 배열이 끊기게됨
# 따라서 아래처럼 처음부터 10개의 index를 만들어 준 뒤 0을 다른 값으로 교체하고,
# del을 사용하는것이 아닌 해당 index를 0으로 바꾸는 형식으로 해야됨.
coin_sell_list = [0,0,0,0,0]
coin_buy_list = [0,0,0,0,0]
coin_buy_num = [0,0,0,0,0]


limit = 5
cell_revenue = {
    0: 30000,
    1: 30000,
    2: 30000,
    3: 30000,
    4: 30000,
}
all_cell_revenue = 0.0




# df[hqr]을 cell_1_hqr,cell_2_hqr···cell_10_hqr 까지 나누어서
# cell당 수익률을 계산한 뒤에 최종 수익률을 계속하는 방식으로 수정 필요.


def insert_order(order_type,data):
    if order_type == 'sell':
        for i in range(0,len(coin_sell_list)):
            if coin_sell_list[i] == 0:
                coin_sell_list[i] = data
                return None
    elif order_type == 'buy':
        for i in range(0,len(coin_buy_list)):
            if coin_buy_list[i] == 0:
                coin_buy_list[i] = data
                return None



def remove_order(order_type,index_loc):
    if order_type == 'sell':
        coin_sell_list[index_loc] = 0

    elif order_type == 'buy':
        coin_buy_list[index_loc] = 0

'''
def add_stack(loc,count):
    drop_down_stack[loc] = drop_down_stack[loc] + count

def reset_stack(loc):
    drop_down_stack[loc] = 0

def check_stack(loc):
    return drop_down_stack[loc]
'''


sell_count = 0
for i in range(0,len(df['ds'])):

    # 그래프가 상승일때만 구매를 하도록 하는 코드
    #=========================
    b_graph_value= df['yhat'][i]
    b_ = False
    for j in range(1,10):
        try:
            if b_graph_value < df['yhat'][i + j]:
                b_ = True
                b_graph_value = df['yhat'][i + j]
            else:
                b_ = False
        except:
            pass
    
    #=======================================
    #구매
    for d in range(0,5):
        if coin_buy_list[d] == 0.0:
            if b_:
                if df['now_price'][i] <= df['yhat_lower'][i]:
                    coin_buy_num[d] = cell_revenue[d] / df['now_price'][i]
                    df['buy_coin_num'][i] = coin_buy_num[d]
                    df['buy_bool'][i] = f'buy!{d}'
                    insert_order('sell',df['now_price'][i] + df['range'][i])
                    insert_order('buy',df['now_price'][i])

                    # coin_buy_list.append(df['now_price'][i])
                    # coin_sell_list.append(df['now_price'][i])

                    df['sell_price'][i] = f"{df['now_price'][i] + df['range'][i]} | {(df['now_price'][i] + df['range'][i]) * coin_buy_num[d]}"
                    break




    # 판매 
    for k in range(0,5):
        if coin_sell_list[k] != 0.0:
            s_graph_value= df['yhat'][i]
            s_ = False
            for p in range(1,10):
                try:
                    if s_graph_value > df['yhat'][i + p]:
                        s_ = True
                        s_graph_value = df['yhat'][i + p]
                    else:
                        s_ = False
                        break
                except:
                    pass
            
            if s_:
                if df['range'][i] >= 0:
                    df['ror'][i] = df['now_price'][i] / coin_buy_list[k]
                    cell_revenue[k] = (df['now_price'][i] + df['ror'][i]) * coin_buy_num[k] - 10
                    df['sell_bool'][i] = f'sell!{k}'

                    remove_order('sell',k)
                    remove_order('buy',k)

                    # del coin_buy_list[k]
                    # del coin_sell_list[k]
                    # coin_buy_list[k] = 0.0
                    # coin_sell_list[k] = 0.0
                    sell_count += 1
                    break
#         continue
# # 떡락 방지 손절 코드 (일정지점 이하로 떨어지면 손절)
#     #=============================
#     #'''
#     for p in range(0,5):
#         if coin_buy_list[p] != 0.0:
#             if df['now_price'][i] <= coin_buy_list[p] - limit:
#                 df['ror'][i] = df['now_price'][i] / coin_buy_list[p]
#                 cell_revenue[p] = (df['now_price'][i] + df['ror'][i]) * coin_buy_num[p] - 10
#                 df['sell_bool'][i] = f'손절sell!{p}'

#                 remove_order('sell',p)
#                 remove_order('buy',p)

#                 #del coin_buy_list[p]
#                 #del coin_sell_list[p]

#                 break
#         #'''
#     #=====================================


for l in cell_revenue:
    all_cell_revenue = all_cell_revenue + cell_revenue[l]

print(coin_buy_list)
print(coin_sell_list)
print(cell_revenue)
print(all_cell_revenue)

for w in range(0,len(cell_revenue)):
    df['cell_revenue'][w] = f'cell {w}: {cell_revenue[w]}'
df['all_cell_revenue'][0] = f'all cell: {all_cell_revenue}'
df['sell_count'][0] = sell_count
# df['hqr'] = df['ror'].cumprod()*100


df[['ds','now_price', 'yhat', 'buy_bool' ,'sell_bool','sell_price','ror','buy_coin_num','cell_revenue','all_cell_revenue']].to_excel('test1.xlsx')
# %%
