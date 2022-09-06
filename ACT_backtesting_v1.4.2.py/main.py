#%%

from re import T
from matplotlib.pyplot import close
import pyupbit
import yaml
import pandas as pd


coin_type = "KRW-XRP"


print("data loading")
df = pyupbit.get_ohlcv(coin_type,interval = 'minute5' ,count = 30000)
df = df.reset_index()
print("done!\n\n\n")





print("setting variable")


df['sell_price'] = 0.0
df['buy_bool'] = ''
df['sell_bool'] = ''
df['ror'] = 1.0
df['buy_coin_num'] = 0.0
df['cell_revenue'] = 0.0
df['all_cell_revenue'] = 0.0
df['sell_count'] = 0.0
df['tick'] = 0
df['tick_num'] = ""
df["avg_value"] = 0.0
df["limit"] = 0.0

coin_sell_list = [0,0,0,0,0]
coin_buy_list = [0,0,0,0,0]
coin_buy_num = [0,0,0,0,0]

limit = 5
cell_revenue = [900000,200000,200000,200000,0]
# cell_revenue = [300000,300000,300000,300000,300000]
all_cell_revenue = 0.0

buy_count = 0
sell_count = 0
tick = 0
tick_end_price = 0
avg_value = 0
have_coin_num = 0
tick_continue_count = 0
print("done!\n\n\n")


print("define setting...")
def insert_order(order_type,data):
    if order_type == 'sell':
        for i in range(0,len(coin_sell_list)):
            if coin_sell_list[i] == 0:
                coin_sell_list[i] = float(data)
                return None
    elif order_type == 'buy':
        for i in range(0,len(coin_buy_list)):
            if coin_buy_list[i] == 0:
                coin_buy_list[i] = float(data)
                return None

def remove_order(index_loc):
    coin_sell_list[index_loc] = 0
    coin_buy_list[index_loc] = 0
    coin_buy_num[index_loc] = 0
print("done!\n\n\n")


def limit_check(df, i, responsiveness):
    
    #df = pyupbit.get_ohlcv(coin_type,interval = 'minute5' ,count = 30)
    #df = df.reset_index()

    
    
    close_list = []
    for j in range(20,0,-1):
        close_list.append(df.at[i - j ,"close"])
    c_mm = max(close_list) - min(close_list)
    return (c_mm / responsiveness)


def get_asking_price(now_price):
        """호가단위 게산"""
        if now_price < 0.1:
            return 0.0001
        elif now_price < 1:
            return 0.001
        elif now_price < 10:
            return 0.01
        elif now_price< 100:
            return 0.1
        elif now_price < 1000:
            return 1
        elif now_price < 10000:
            return 5
        elif now_price < 100000:
            return 10
        elif now_price < 500000:
            return 50
        elif now_price < 1000000:
            return 100
        elif now_price < 2000000:
            return 500
        else:
            return 1000







b_all_cell_revenue_ = 0
print("main simulation start...")
print(df)
for i in range(2,len(df['index'])):
    
    limit = get_asking_price(df.at[i, 'close'])
    df["limit"][i] = limit
    if i > 20:
        tick_value = limit_check(df, i, 10)
        print("limit check")
        print(tick_value)
        if tick_value <= limit * 2:
            tick_value = 2
    else:
        tick_value = 2
    tick_value = round(tick_value)
    df["avg_value"][i] = avg_value
    
    all_cell_revenue_ = sum(cell_revenue)
    df['tick_num'][i] = tick
    print(f"│  buy checking...")
    if (tick == 0 and ((df.at[i-1,'close'] - df.at[i,'close'] >= tick_value and df.at[i-1,'open'] - df.at[i-1,'close'] >= tick_value and df.at[i - 1,'close'] - df.at[i,'close'] >= tick_value) or
                            df.at[i,'open'] - df.at[i,'close'] >= tick_value * 2)):
        if coin_buy_list[0] != 0:
            if tick_end_price - df.at[i,'close'] >= tick_value:
                print('│  tick start')
                tick += 1
                tick_end_price = int(df.at[i,'close'])
                df['tick'][i] = "tick start"
                print(f'│  tick: {tick}')
                continue
        else:
            print('│  tick start')
            tick += 1
            tick_end_price = int(df.at[i,'close'])
            df['tick'][i] = "tick start"
            print(f'│  tick: {tick}')
            continue
    
    
    elif tick != 0:
        if tick_continue_count >= 5:
            df['tick'][i] = "reset type3"
            tick = 0
            tick_continue_count = 0
            continue
        
        if tick >= 3:
            if df.at[i,'close'] >= avg_value:
                tick = 0
                tick_continue_count = 0
                continue
            

            if (tick_end_price - df.at[i,'close'] >= tick_value and
                df.at[i-1,'open'] > df.at[i-1,'close'] and df.at[i,'open'] > df.at[i,'close']) or (df.at[i,'open'] - df.at[i,'close'] >= tick_value):
                    tick += 1
                    tick_end_price = float(df.at[i,'close'])
                    df['tick'][i] = "+= 1"
                    
            else:
                df['tick'][i] = "continue"
                tick_continue_count += 1
                continue
            
            
        else:
            if df.at[i,'close'] - tick_end_price >= limit * 4 or (df.at[i-1,'open'] < df.at[i-1,'close'] and df.at[i,'open'] < df.at[i,'close'] and df.at[i,'close'] - df.at[i-1,'close'] > tick_value * 2):
                tick = 0
                tick_continue_count = 0
                continue
    
            if tick_end_price - df.at[i,'close'] >= tick_value:
                tick += 1
                tick_end_price = float(df.at[i,'close'])
                df['tick'][i] = "+= 1"
            
            else:
                df['tick'][i] = "continue"
                tick_continue_count += 1
                continue
    
    buy_bool = False
    for j in range(0,5):
        if tick >= 3:
            if coin_buy_list[j] == 0.0:
                
                buy_bool = True
                print('│  buy True')
                coin_buy_num[j] = cell_revenue[j] / df['close'][i]
                df['buy_coin_num'][i] = coin_buy_num[j]
                have_coin_num = sum(coin_buy_num)
                
                insert_order('sell',df['close'][i] + 10)
                insert_order('buy',df['close'][i])
                
                avg = 0.0
                for b_order_ in range(0,len(coin_buy_list)):
                    if coin_buy_list[b_order_] != 0:
                        avg = avg + coin_buy_list[b_order_] * coin_buy_num[b_order_]
                avg_value =  avg / have_coin_num
                
                buy_count += 1
                df['buy_bool'][i] = f"buy!{j}"
                break
    if buy_bool == True:
        continue
    
    
    # 판매
    sell_bool_ = ""
    sell_bool = False
    if df['close'][i] >= avg_value:
        for k in range(0,5):
            if coin_sell_list[k] != 0.0:
                if df['close'][i] - avg_value >= tick_value * 2:
                    if (df['open'][i - 2] > df['close'][i - 2]) and df['close'][i - 2] - df['close'][i - 1] >= tick_value:
                
                        cell_revenue[k] = df['close'][i] * coin_buy_num[k]
                        
                        sell_bool_ += f'sell!{k}'


                        coin_sell_list[k] = 0
                        coin_buy_list[k] = 0
                        coin_buy_num[k] = 0

                        sell_count += 1
                        sell_bool = True
            
        if sell_bool == True:
            df['ror'][i] = sum(cell_revenue) / b_all_cell_revenue_ * 100 - 100
            df['sell_bool'][i] = sell_bool_
            avg_value = 0
            b_all_cell_revenue_ = sum(cell_revenue)
            continue
    '''
    if ((avg_value - df['close'][i]) >= limit * 10):
        for k in range(0,5):
            if coin_sell_list[k] != 0.0:
                cell_revenue[k] = df['close'][i] * coin_buy_num[k]
                
                sell_bool_ += f'c sell!{k}'

                coin_sell_list[k] = 0
                coin_buy_list[k] = 0
                coin_buy_num[k] = 0

                sell_count += 1
                sell_bool = True
        
        if sell_bool == True:
            df['ror'][i] = sum(cell_revenue) / b_all_cell_revenue_ * 100 - 100
            df['sell_bool'][i] = sell_bool_
            avg_value = 0
            b_all_cell_revenue_ = sum(cell_revenue)
            continue
    '''
    if coin_buy_list[0] != 0:
        for e in range(4,1,-1):
            if coin_buy_list[e] != 0:
                if df.at[i - 2, 'close'] < df.at[i - 1, 'close'] < df.at[i , 'close']:
                    
                    cell_revenue[e] = df['close'][i] * coin_buy_num[e]
                    
                    df['sell_bool'][i] = f'cut sell!{e}'


                    coin_sell_list[e] = 0
                    coin_buy_list[e] = 0
                    coin_buy_num[e] = 0

                    sell_count += 1
                    sell_bool = True

                    break

print(cell_revenue)
for l in cell_revenue:
    all_cell_revenue = all_cell_revenue + l

print(coin_buy_list)
print(coin_sell_list)
print(cell_revenue)
print(all_cell_revenue)

for w in range(0,len(cell_revenue)):
    df['cell_revenue'][w] = f'cell {w}: {cell_revenue[w]}'
df['all_cell_revenue'][0] = f'all cell: {all_cell_revenue}'
df['sell_count'][0] = sell_count
# df['hqr'] = df['ror'].cumprod()*100
df['ror'][0] = all_cell_revenue / 1500000 * 100 - 100

df[['index', 'close', 'tick', 'tick_num', 'avg_value', 'buy_bool' ,'sell_bool','sell_price','limit','ror','buy_coin_num','cell_revenue','all_cell_revenue']].to_excel('ACT_backtesting.xlsx')
        
# %%
