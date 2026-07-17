import pandas as pd
import numpy as np

def generate_execution_signals(data: pd.DataFrame, volume_multiplier: float = 1.5):
    """
    Analyzes asset liquidity and volume to generate strict Limit and Stop orders.
    Designed for highly liquid, large-cap equities.
    
    Parameters:
    - data: pandas DataFrame containing 'Close' and 'Volume' columns.
    - volume_multiplier: The threshold for detecting a significant liquidity spike.
    """
    data['Volume_SMA_20'] = data['Volume'].rolling(window=20).mean()
    data = data.dropna()
    
    current_price = data['Close'].iloc[-1]
    current_volume = data['Volume'].iloc[-1]
    average_volume = data['Volume_SMA_20'].iloc[-1]
    
    print(f"--- Market Snapshot ---")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Current Volume: {current_volume:,.0f} | 20-Day Avg: {average_volume:,.0f}")
    
    if current_volume > (average_volume * volume_multiplier):
        print("\n[SIGNAL] High Liquidity Spike Detected.")
        
        limit_entry = round(current_price * 0.995, 2)
        print(f"[ACTION] Submit BUY LIMIT order at: ${limit_entry}")
        
        stop_loss = round(limit_entry * 0.98, 2)
        print(f"[ACTION] Submit STOP-LOSS order at: ${stop_loss}")
        
        stop_trigger = round(current_price * 1.02, 2)
        limit_execution = round(current_price * 1.025, 2)
        print(f"[ACTION] Submit STOP-LIMIT order: Trigger at ${stop_trigger}, Limit at ${limit_execution}")
        
        return {
            "signal": True,
            "limit_entry": limit_entry,
            "stop_loss": stop_loss,
            "stop_trigger": stop_trigger,
            "stop_limit": limit_execution
        }
    else:
        print("\n[SIGNAL] Normal liquidity. Avoiding market entry to prevent slippage.")
        return {"signal": False}

if __name__ == "__main__":
    mock_data = {
        'Close': [150.0, 151.2, 149.8, 152.0, 155.5] * 5, 
        'Volume': [1000000, 1100000, 950000, 1050000, 2500000] * 5 
    }
    df = pd.DataFrame(mock_data)
    generate_execution_signals(df, volume_multiplier=1.5)