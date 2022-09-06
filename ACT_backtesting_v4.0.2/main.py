#%%

import matplotlib.pyplot as plt
import pyupbit


coin_type = "KRW-ETC"
data_num = 10000

print("data loading")
df = pyupbit.get_ohlcv(coin_type,interval = 'minute5' ,count = data_num)
df = df.reset_index()
print("done!\n\n\n")





print("setting variable")


df['sell_price'] = ''
df['buy_bool'] = ''
df['sell_bool'] = ''
df['ror'] = ''
df['buy_coin_num'] = ''
df['cell_revenue'] = ''
df['all_cell_revenue'] = ''
df['sell_count'] = ''
df['buy_count'] = ''
df['cut_sell_num'] = ''
df['tick'] = ''
df['tick_num'] = ''
df["avg_value"] = ''
df["limit"] = ''
df["total ror"] = ''

coin_sell_list = [0,0,0,0,0]
coin_buy_list = [0,0,0,0,0]
coin_buy_num = [0,0,0,0,0]

limit = 1
# cell_revenue = [900000,200000,200000,200000,0]
cell_revenue = [800000,800000,800000,800000,800000]
cell_state = ['nomal','nomal','nomal','nomal','nomal']
fund = sum(cell_revenue)
start_money = sum(cell_revenue)
b_all_cell_revenue_ = sum(cell_revenue)

buy_count = 0
sell_count = 0
c_buy_count = 0
c_sell_count = 0
tick = 0
end_tick = 0
tick_end_price = 0
avg_value = 0
have_coin_num = 0
circulation = False
minimum_close_low_price = 1
cut_sell = False
cut_sell_2 = False
cut_sell_num = 0
tick_stack_num = 0
total_ror = 0

max_tick_stack_num = 6


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

    

    max_list = []
    min_list = []
    for j in range(20,0,-1):
        max_list.append(df.at[i - j ,"high"])
        min_list.append(df.at[i - j ,"low"])
    c_mm = max(max_list) - min(min_list)
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



def mid_value(ll):
    return sum(ll) / len(ll)



def get_WMA_list(df, loop_num, length, num):
    a = 0
    WMA_value_list = []
    for i in range(num, 0, -1):
        for j in range(length, 0, -1):
            a += df[loop_num - j - i]
        WMA_value_list.append(a / length)
        a = 0
    return WMA_value_list
    
    



print("main simulation start...")
print(df)

#================================================
fig = plt.figure(figsize=(200,20)) # 캔버스 생성
fig.set_facecolor('white') # 캔버스 색상 설정
ax = fig.add_subplot() # 그림 뼈대(프레임) 생성
 
ax.plot(df['index'],df['close']) # 선그래프 생성
#================================================

ct = max(df['close'])
cl = min(df['close'])
for i in range(2,len(df['index'])):
    buy_bool = False
    if coin_buy_list[4] != 0:
        circulation = True
#     else:
#         circulation = False
    limit = get_asking_price(df.at[i, 'close'])
    # df["limit"][i] = limit
    if i > 20:
        # tick_value = limit_check(df, i, 10)
        tick_value = limit_check(df, i, 10)
        df["limit"][i] = tick_value
        print(tick_value)
        if tick_value <= limit * 2:
            tick_value =  limit * 2
    else:
        continue
    # tick_value =  10
    tick_value = round(tick_value)
    
    all_cell_revenue_ = sum(cell_revenue)
    df['tick_num'][i] = tick
    tick_start = False
    
    if df.at[i, 'close'] - df.at[i, 'low'] >= limit * minimum_close_low_price:
        if tick == 0 and df.at[i,'open'] - df.at[i,'close'] >= tick_value:
            if coin_buy_list[0] != 0:
                if df.at[i,'close'] <= avg_value:
                    tick += 1
                    tick_end_price = int(df.at[i,'close'])
                    df['tick'][i] = "tick start"
                    tick_stack_num += 1
                    tick_start = True
            else:
                tick += 1
                tick_end_price = int(df.at[i,'close'])
                df['tick'][i] = "tick start"
                tick_stack_num += 1
                tick_start = True
    
    
    
    
    
    # ver 1.0.1
    # 아래는 구매조건부의 코드입니다.
    if tick_start == False:
        # 틱을 너무 오랫동안 세는것을 방지하는 코드
        if tick_stack_num == max_tick_stack_num:
            tick = 0
            df["sell_price"][i] = 1
            df['tick'][i] = "reset"
        if tick != 0:
            tick_stack_num += 1
            if tick == 1:
                if mid_value([df.at[i - 1,'open'], df.at[i - 1,'close']]) - mid_value([df.at[i,'open'], df.at[i,'close']]) < tick_value:
                    tick = 0
                    df["sell_price"][i] = 1
                    df['tick'][i] = "reset"
                
            # D 아래꼬리를 얼마나 크게 그리냐에 대한 if
            if df.at[i, 'close'] - df.at[i, 'low'] >= limit * minimum_close_low_price:
                if tick_end_price - df.at[i,'close'] >= tick_value:
                    # CS 실험중인 코드 ( 한번에 크게 음봉이 떠야 틱 +1 )
                    if df.at[i - 2,'close'] - df.at[i,'close'] >= tick_value:
                        tick += 1
                        tick_end_price = float(df.at[i,'close'])
                        df['tick'][i] = "+= 1"
                    # CE
                else:
                    df['tick'][i] = "continue3"
            else:
                df['tick'][i] = "continue4"
                
            
            if df.at[i,'close'] - tick_end_price >= limit * 4 or (df.at[i-1,'open'] < df.at[i-1,'close'] and df.at[i,'open'] < df.at[i,'close'] and df.at[i,'close'] - df.at[i-1,'close'] > tick_value * 2) or (df.at[i - 1, "open"] > df.at[i - 1, "close"] and df.at[i - 1, "open"] < df.at[i, "close"]):
                tick = 0
                df['tick'][i] = "reset"
    

    
        if end_tick != tick:
            for j in range(0,len(cell_revenue)):
                if tick >= 3:
                    if coin_buy_list[j] == 0.0:
                        
                        buy_bool = True
                        raw_have_coin_num = sum(coin_buy_num)
                        coin_buy_num[j] = cell_revenue[j] / df['close'][i]
                        df['buy_coin_num'][i] = coin_buy_num[j]
                        have_coin_num = sum(coin_buy_num)
                        
                        insert_order('sell',df['close'][i] + 10)
                        insert_order('buy',df['close'][i])
                        
                        # avg = 0.0
                        # for b_order_ in range(0,len(coin_buy_list)):
                        #     if coin_buy_list[b_order_] != 0:
                        #         avg = avg + coin_buy_list[b_order_] * coin_buy_num[b_order_]
                        # avg_value =  avg / have_coin_num
                        # df["avg_value"][i] = avg_value
                        
                        for r in range(0,len(coin_buy_list)):
                            if coin_buy_list[r] != 0:
                                buy_count += 1
                                if cell_state[r] == "circulation":
                                    c_buy_count += 1
                                    cell_state[r] = "nomal"
                        avg_value = ((avg_value * raw_have_coin_num) + (df.at[i, 'close'] * coin_buy_num[j])) / have_coin_num
                        df["avg_value"][i] = avg_value
                                
                                
                        df['buy_bool'][i] = f"buy!{j}"
                        
                        plt.axvline(df.at[i, 'index'], color='red', linestyle='solid', linewidth=1)
                        
                        break
            end_tick = tick
    if buy_bool == True:
        continue
    
    # 판매
    sell_bool_ = ""
    sell_bool = False
    ll_1 = [mid_value([df["close"][i - 6],df["open"][i - 6]]),mid_value([df["close"][i - 5],df["open"][i - 5]]),
            mid_value([df["close"][i - 4],df["open"][i - 4]])]
    ll_2 = [mid_value([df["close"][i - 3],df["open"][i - 3]]),mid_value([df["close"][i - 2],df["open"][i - 2]]),
            mid_value([df["close"][i - 1],df["open"][i - 1]])]
    if df['close'][i] >= avg_value:
        
        a_all_cell_revenue = 0
        for y in range(0,5):
            if coin_buy_num[y] != 0:
                cell_revenue[y] = df['close'][i] * coin_buy_num[y]
                a_all_cell_revenue += cell_revenue[y]
            else:
                a_all_cell_revenue += cell_revenue[y]
        if b_all_cell_revenue_ < a_all_cell_revenue:
            if df['close'][i] - avg_value >= limit * 2:
                # if (df['open'][i - 1] > df['close'][i - 1]) and df['open'][i - 1] - df['close'][i] >= tick_value:
                # if mid_value(df.at[i - 3, 'open'], df.at[i - 3, 'close']) < mid_value(df.at[i - 2, 'open'], df.at[i - 2, 'close']) < mid_value(df.at[i - 1, 'open'], df.at[i - 1, 'close']) < mid_value(df.at[i, 'open'], df.at[i, 'close']):

                if ll_1[0] < ll_1[1] < ll_1[2]:
                    # if max(ll_2) - min(ll_2) >= tick_value:
                    if ll_2[2] > df.at[i, "close"] or ll_2[1] - ll_2[2] < tick_value: 
                        for k in range(0,len(cell_revenue)):
                            if coin_sell_list[k] != 0.0:
                                # 판매
                                cell_revenue[k] = df['close'][i] * coin_buy_num[k]
                                sell_bool_ += f'sell!{k}'
                                coin_sell_list[k] = 0
                                coin_buy_list[k] = 0
                                coin_buy_num[k] = 0
                                tick = 0
                                tick_end_price = 0
                                sell_count += 1
                                cut_sell = False
                                sell_bool = True
                                
                
            if sell_bool == True:
                ror = sum(cell_revenue) / b_all_cell_revenue_ * 100 - 100
                total_ror += ror
                df['ror'][i] = ror
                df["total ror"][i] = total_ror
                df['sell_bool'][i] = sell_bool_
                avg_value = 0
                b_all_cell_revenue_ = sum(cell_revenue)
                circulation = False
                cell_state = ['nomal','nomal','nomal','nomal','nomal']
                plt.axvline(df.at[i, 'index'], color='blue', linestyle='solid', linewidth=1)
                continue



    # 순환매
    print(df.at[i, 'index'])
    print(mid_value([df.at[i - 2, 'open'], df.at[i - 2, 'close']]))
    print(mid_value([df.at[i - 1, 'open'], df.at[i - 1, 'close']]))
    print(mid_value([df.at[i, 'open'], df.at[i, 'close']]))
    if mid_value([df.at[i - 2, 'open'], df.at[i - 2, 'close']]) < mid_value([df.at[i - 1, 'open'], df.at[i - 1, 'close']]) < mid_value([df.at[i, 'open'], df.at[i, 'close']]):
        print(True)
    

    if circulation:
        if coin_buy_list[0] != 0:
            for e in range(len(cell_revenue) - 1,len(cell_revenue) - 2,-1):
                # if coin_buy_list[e] <= avg_value:
                if coin_buy_list[e] != 0:
                    if coin_buy_list[e] <= df.at[i, "close"]:
                        
                        if mid_value([df.at[i - 2, 'open'], df.at[i - 2, 'close']]) < mid_value([df.at[i - 1, 'open'], df.at[i - 1, 'close']]) < mid_value([df.at[i, 'open'], df.at[i, 'close']]):

                            cell_revenue[e] = df['close'][i] * coin_buy_num[e]
                            df['sell_bool'][i] = f'순환 sell!{e}'

                            coin_sell_list[e] = 0
                            coin_buy_list[e] = 0
                            coin_buy_num[e] = 0
                            c_sell_count += 1
                            cell_state[e] = "circulation"
                            cut_sell = False

                            sell_bool = True
                            
                            plt.axvline(df.at[i, 'index'], color='gray', linestyle='solid', linewidth=1)
                            
                            break
        
    
            
    # ver 1.0.0
    sell_bool_ = ""
    cut_sell_bool = False
    if coin_buy_list[4] != 0:
        if ll_1[0] <= ll_1[1] <= ll_1[2] > ll_2[0] > ll_2[1] > ll_2[2]:
            if ll_2[0] - ll_2[2] > tick_value:
                # 한번 반등이 왔다가 다시 내려갈시 + 1 and
                if cut_sell == False:
                    cut_sell = True
                else:
                    for g in range(0,len(coin_buy_list)):
                        if coin_buy_list[g] != 0:
                            # 판매
                            cell_revenue[g] = df['close'][i] * coin_buy_num[g]
                            sell_bool_ += f'손절 sell{g}'

                            coin_sell_list[g] = 0
                            coin_buy_list[g] = 0
                            coin_buy_num[g] = 0
                            tick = 0
                            tick_end_price = 0
                            cut_sell_bool = True
                            cut_sell = False
                            cut_sell_num += 1
        

    if cut_sell_bool == True:
            ror = sum(cell_revenue) / b_all_cell_revenue_ * 100 - 100
            total_ror += ror
            df["total ror"][i] = total_ror
            df['ror'][i] = ror
            df['sell_bool'][i] = sell_bool_
            avg_value = 0
            b_all_cell_revenue_ = sum(cell_revenue)
            circulation = False
            cell_state = ['nomal','nomal','nomal','nomal','nomal']
            plt.axvline(df.at[i, 'index'], color='green', linestyle='solid', linewidth=1)
    
    
    
print("\n\n")
print(cell_revenue)
all_cell_revenue = sum(cell_revenue)


print(coin_buy_list)
print(coin_sell_list)
print(cell_revenue)
print(all_cell_revenue)

for w in range(0,len(cell_revenue)):
    df['cell_revenue'][w] = f'cell {w}: {cell_revenue[w]}'
df['all_cell_revenue'][0] = f'all cell: {all_cell_revenue}'
df['sell_count'][0] = sell_count
df['buy_count'][0] = buy_count
df['cut_sell_num'][0] = cut_sell_num
# df['hqr'] = df['ror'].cumprod()*100
df['ror'][0] = all_cell_revenue / start_money * 100 - 100

df[['index', 'close', 'tick', 'tick_num', 'avg_value', 'buy_bool' ,'sell_bool','sell_price','limit','ror',"total ror",'buy_coin_num','cell_revenue','all_cell_revenue', "buy_count", "sell_count", "cut_sell_num"]].to_excel('ACT_backtesting.xlsx')



print("최종 결과")
print(f"├기간: {df['index'][0]} ~ {df['index'][i - 1]}")
print(f"├수익률: {df['ror'][0]}")
print(f"└최종 자금: {df['all_cell_revenue'][0]}")
print("\nnomal")
print(f"├구매횟수: {buy_count}")
print(f"└판매횟수: {sell_count}")
print("\ncirculation")
print(f"├순환 구매횟수: {c_buy_count}")
print(f"└순환 판매횟수: {c_sell_count}")
print("\ncutsell")
print(f"└손절 횟수: {cut_sell_num}")
print(cut_sell)




 
# plt.xticks(rotation=45) ## x축 눈금 라벨 설정 - 40도 회전
plt.title('backtesting V1.5.0',fontsize=20) ## 타이틀 설정
plt.show()

 # %%
