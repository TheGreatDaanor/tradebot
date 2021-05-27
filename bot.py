import websocket, json, pprint, numpy, talib
from binance.client import Client 
from binance.enums import *

client = Client(config.API_KEY, config.API_SECRET,)

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 140
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.008

closes = []
in_position = False

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except  Exception as e:
        return False

    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes
    
    print('recieved message')
    print(message)
    json_message = json.loads(message)
    pprint.pprint(json_message)
    
    candle = json_message['k']
    
    is_candle_closed = candle ['x']
    candle = candle['c']
    
    if is_candle_closed:
        print('closed at {}'.format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsi calculated")
            print (rsi)
            last_rsi = rsi[-1]
            print("the current rsi {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Sell")
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("already sold")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("Position already taken")
                else:
                    print("BUY")
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()