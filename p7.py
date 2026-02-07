import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class IntradayMeanReversionAlgo:
    """
    Intraday Mean Reversion Algorithm for Nifty 50
    - Designed for algorithmic trading
    - 5% risk per trade with stop-loss
    - All positions closed before market close
    """
    
    def __init__(self, lookback=20, z_entry=2.0, z_exit=0.5, 
                 risk_per_trade=0.05, stop_loss_pct=0.02, target_pct=0.04):
        """
        Parameters:
        -----------
        lookback : int
            Rolling window for intraday calculations (20 periods for 5-min bars = 100 min)
        z_entry : float
            Z-score threshold for entry (default: 2.0)
        z_exit : float
            Z-score threshold for exit (default: 0.5)
        risk_per_trade : float
            Risk per trade as fraction of capital (default: 0.05 = 5%)
        stop_loss_pct : float
            Stop loss as percentage of entry price (default: 2%)
        target_pct : float
            Target profit as percentage of entry price (default: 4%)
        """
        self.lookback = lookback
        self.z_entry = z_entry
        self.z_exit = z_exit
        self.risk_per_trade = risk_per_trade
        self.stop_loss_pct = stop_loss_pct
        self.target_pct = target_pct
        
    def calculate_zscore(self, prices):
        """Calculate Z-Score: Z = (P_t - μ) / σ"""
        rolling_mean = prices.rolling(window=self.lookback).mean()
        rolling_std = prices.rolling(window=self.lookback).std()
        zscore = (prices - rolling_mean) / rolling_std
        return zscore, rolling_mean, rolling_std
    
    def calculate_position_size(self, capital, entry_price, stop_loss_price):
        """
        Calculate position size based on 5% risk per trade
        Risk = (Entry Price - Stop Loss Price) × Quantity
        Quantity = (Capital × Risk%) / (Entry - Stop Loss)
        """
        risk_amount = capital * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            return 0
        
        quantity = int(risk_amount / price_risk)
        
        # For Nifty options, adjust to lot size (50)
        lot_size = 50
        quantity = (quantity // lot_size) * lot_size
        
        return max(quantity, lot_size)  # Minimum 1 lot
    
    def is_market_hours(self, timestamp):
        """Check if timestamp is within market hours (9:15 AM - 3:30 PM IST)"""
        time = timestamp.time()
        market_open = pd.Timestamp('09:15:00').time()
        market_close = pd.Timestamp('15:30:00').time()
        return market_open <= time <= market_close
    
    def should_close_position(self, timestamp):
        """Force close all positions at 3:15 PM (15 min before close)"""
        time = timestamp.time()
        force_close_time = pd.Timestamp('15:15:00').time()
        return time >= force_close_time
    
    def generate_signals(self, data):
        """
        Generate intraday trading signals
        
        Parameters:
        -----------
        data : pd.DataFrame
            Must contain 'Close' column with intraday prices (5-min bars recommended)
        """
        df = data.copy()
        prices = df['Close']
        
        # Calculate Z-Score
        df['zscore'], df['rolling_mean'], df['rolling_std'] = self.calculate_zscore(prices)
        
        # Initialize columns
        df['signal'] = 0
        df['position'] = 0
        df['entry_price'] = np.nan
        df['stop_loss'] = np.nan
        df['target'] = np.nan
        df['quantity'] = 0
        df['exit_reason'] = ''
        
        return df
    
    def backtest_intraday(self, data, initial_capital=100000):
        """
        Backtest intraday strategy with 5% risk management
        """
        df = data.copy()
        prices = df['Close']
        
        # Calculate Z-Score
        df['zscore'], df['rolling_mean'], df['rolling_std'] = self.calculate_zscore(prices)
        
        # Track portfolio
        capital = initial_capital
        position = None
        trades = []
        daily_pnl = []
        
        current_date = None
        daily_capital_start = capital
        
        for i in range(self.lookback, len(df)):
            timestamp = df.index[i]
            price = df['Close'].iloc[i]
            z = df['zscore'].iloc[i]
            
            # Check if new trading day
            if current_date != timestamp.date():
                if current_date is not None and len(daily_pnl) > 0:
                    # End of previous day
                    if position is not None:
                        # Force close position at end of day
                        pnl = self._calculate_pnl(position, price)
                        capital += pnl
                        
                        trades.append({
                            'Entry Time': position['entry_time'],
                            'Exit Time': timestamp,
                            'Direction': position['direction'],
                            'Entry Price': position['entry_price'],
                            'Exit Price': price,
                            'Quantity': position['quantity'],
                            'Stop Loss': position['stop_loss'],
                            'Target': position['target'],
                            'P&L (INR)': pnl,
                            'Return (%)': (pnl / (position['entry_price'] * position['quantity'])) * 100,
                            'Exit Reason': 'EOD Force Close'
                        })
                        position = None
                
                current_date = timestamp.date()
                daily_capital_start = capital
            
            # Skip if outside market hours
            if not self.is_market_hours(timestamp):
                continue
            
            # Force close before market close
            if self.should_close_position(timestamp) and position is not None:
                pnl = self._calculate_pnl(position, price)
                capital += pnl
                
                trades.append({
                    'Entry Time': position['entry_time'],
                    'Exit Time': timestamp,
                    'Direction': position['direction'],
                    'Entry Price': position['entry_price'],
                    'Exit Price': price,
                    'Quantity': position['quantity'],
                    'Stop Loss': position['stop_loss'],
                    'Target': position['target'],
                    'P&L (INR)': pnl,
                    'Return (%)': (pnl / (position['entry_price'] * position['quantity'])) * 100,
                    'Exit Reason': 'Pre-Close Exit'
                })
                position = None
                continue
            
            # No position - Look for entry
            if position is None and not pd.isna(z):
                
                # LONG Entry
                if z < -self.z_entry:
                    stop_loss = price * (1 - self.stop_loss_pct)
                    target = price * (1 + self.target_pct)
                    quantity = self.calculate_position_size(capital, price, stop_loss)
                    
                    position = {
                        'entry_time': timestamp,
                        'entry_price': price,
                        'direction': 'LONG',
                        'quantity': quantity,
                        'stop_loss': stop_loss,
                        'target': target,
                        'entry_z': z
                    }
                
                # SHORT Entry
                elif z > self.z_entry:
                    stop_loss = price * (1 + self.stop_loss_pct)
                    target = price * (1 - self.target_pct)
                    quantity = self.calculate_position_size(capital, price, stop_loss)
                    
                    position = {
                        'entry_time': timestamp,
                        'entry_price': price,
                        'direction': 'SHORT',
                        'quantity': quantity,
                        'stop_loss': stop_loss,
                        'target': target,
                        'entry_z': z
                    }
            
            # Have position - Check exit conditions
            elif position is not None:
                exit_trade = False
                exit_reason = ''
                
                if position['direction'] == 'LONG':
                    # Stop Loss Hit
                    if price <= position['stop_loss']:
                        exit_trade = True
                        exit_reason = 'Stop Loss'
                    # Target Hit
                    elif price >= position['target']:
                        exit_trade = True
                        exit_reason = 'Target Reached'
                    # Mean Reversion Exit
                    elif z >= -self.z_exit:
                        exit_trade = True
                        exit_reason = 'Mean Reversion'
                
                else:  # SHORT
                    # Stop Loss Hit
                    if price >= position['stop_loss']:
                        exit_trade = True
                        exit_reason = 'Stop Loss'
                    # Target Hit
                    elif price <= position['target']:
                        exit_trade = True
                        exit_reason = 'Target Reached'
                    # Mean Reversion Exit
                    elif z <= self.z_exit:
                        exit_trade = True
                        exit_reason = 'Mean Reversion'
                
                if exit_trade:
                    pnl = self._calculate_pnl(position, price)
                    capital += pnl
                    
                    trades.append({
                        'Entry Time': position['entry_time'],
                        'Exit Time': timestamp,
                        'Direction': position['direction'],
                        'Entry Price': position['entry_price'],
                        'Exit Price': price,
                        'Quantity': position['quantity'],
                        'Stop Loss': position['stop_loss'],
                        'Target': position['target'],
                        'P&L (INR)': pnl,
                        'Return (%)': (pnl / (position['entry_price'] * position['quantity'])) * 100,
                        'Exit Reason': exit_reason
                    })
                    position = None
        
        # Calculate metrics
        trades_df = pd.DataFrame(trades)
        
        winning_trades = len(trades_df[trades_df['P&L (INR)'] > 0]) if len(trades_df) > 0 else 0
        losing_trades = len(trades_df[trades_df['P&L (INR)'] < 0]) if len(trades_df) > 0 else 0
        total_pnl = trades_df['P&L (INR)'].sum() if len(trades_df) > 0 else 0
        
        avg_win = trades_df[trades_df['P&L (INR)'] > 0]['P&L (INR)'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['P&L (INR)'] < 0]['P&L (INR)'].mean() if losing_trades > 0 else 0
        
        win_rate = (winning_trades / len(trades_df) * 100) if len(trades_df) > 0 else 0
        
        metrics = {
            'Initial Capital': initial_capital,
            'Final Capital': capital,
            'Total P&L': total_pnl,
            'Total Return (%)': ((capital - initial_capital) / initial_capital) * 100,
            'Total Trades': len(trades_df),
            'Winning Trades': winning_trades,
            'Losing Trades': losing_trades,
            'Win Rate (%)': win_rate,
            'Average Win': avg_win,
            'Average Loss': avg_loss,
            'Risk-Reward Ratio': abs(avg_win / avg_loss) if avg_loss != 0 else 0
        }
        
        return trades_df, metrics
    
    def _calculate_pnl(self, position, exit_price):
        """Calculate P&L for a position"""
        if position['direction'] == 'LONG':
            pnl = (exit_price - position['entry_price']) * position['quantity']
        else:  # SHORT
            pnl = (position['entry_price'] - exit_price) * position['quantity']
        return pnl


def generate_intraday_data(trading_days=20, bars_per_day=75):
    """
    Generate sample 5-minute intraday data
    75 bars per day = 6.25 hours × 60 min / 5 min
    (9:15 AM to 3:30 PM = 6 hours 15 minutes)
    """
    np.random.seed(42)
    
    all_data = []
    base_price = 18000
    
    for day in range(trading_days):
        date = datetime.now() - timedelta(days=trading_days - day)
        
        # Generate intraday bars
        current_price = base_price + np.random.randn() * 200
        
        for bar in range(bars_per_day):
            minutes = 9 * 60 + 15 + (bar * 5)  # Start at 9:15 AM
            hour = minutes // 60
            minute = minutes % 60
            
            timestamp = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Mean reverting price movement
            drift = 0.1 * (base_price - current_price)
            diffusion = 50 * np.random.randn()
            current_price += drift + diffusion
            
            all_data.append({
                'timestamp': timestamp,
                'Close': current_price
            })
    
    df = pd.DataFrame(all_data)
    df.set_index('timestamp', inplace=True)
    return df


if __name__ == "__main__":
    print("=" * 140)
    print(" " * 45 + "NIFTY 50 INTRADAY MEAN REVERSION ALGORITHM")
    print(" " * 50 + "5% Risk Per Trade | Stop Loss & Target")
    print("=" * 140)
    
    # Generate intraday data (5-min bars for 20 trading days)
    print("\n[1/3] Generating 5-minute intraday data (20 trading days)...")
    intraday_data = generate_intraday_data(trading_days=20, bars_per_day=75)
    
    print(f"Data Period: {intraday_data.index[0]} to {intraday_data.index[-1]}")
    print(f"Total Bars: {len(intraday_data)}")
    
    # Initialize algo
    initial_capital = 100000
    
    algo = IntradayMeanReversionAlgo(
        lookback=20,          # 20 bars = 100 minutes
        z_entry=2.0,          # Entry at 2 std dev
        z_exit=0.5,           # Exit when reverting to mean
        risk_per_trade=0.05,  # 5% risk per trade
        stop_loss_pct=0.02,   # 2% stop loss
        target_pct=0.04       # 4% target (2:1 risk-reward)
    )
    
    # Run backtest
    print("[2/3] Running intraday backtest with risk management...")
    trades, metrics = algo.backtest_intraday(intraday_data, initial_capital)
    
    print("[3/3] Analysis complete!\n")
    
    # Capital Summary
    print("=" * 140)
    print("CAPITAL SUMMARY")
    print("=" * 140)
    print(f"Initial Capital:        ₹{metrics['Initial Capital']:,.2f}")
    print(f"Final Capital:          ₹{metrics['Final Capital']:,.2f}")
    print(f"Total P&L:              ₹{metrics['Total P&L']:,.2f}")
    print(f"Total Return:           {metrics['Total Return (%)']:.2f}%")
    print("=" * 140)
    
    # Performance Metrics
    print("\nPERFORMANCE METRICS")
    print("-" * 140)
    print(f"Total Trades:           {metrics['Total Trades']}")
    print(f"Winning Trades:         {metrics['Winning Trades']}")
    print(f"Losing Trades:          {metrics['Losing Trades']}")
    print(f"Win Rate:               {metrics['Win Rate (%)']:.2f}%")
    print(f"Average Win:            ₹{metrics['Average Win']:,.2f}")
    print(f"Average Loss:           ₹{metrics['Average Loss']:,.2f}")
    print(f"Risk-Reward Ratio:      {metrics['Risk-Reward Ratio']:.2f}:1")
    print("-" * 140)
    
    # All Trades
    print("\n" + "=" * 140)
    print("ALL INTRADAY TRADES")
    print("=" * 140)
    
    if len(trades) > 0:
        print(f"{'#':<4} {'Entry Time':<20} {'Exit Time':<20} {'Dir':<6} {'Entry':<10} {'Exit':<10} "
              f"{'Qty':<6} {'SL':<10} {'Target':<10} {'P&L':<12} {'Return%':<10} {'Exit Reason':<18}")
        print("-" * 140)
        
        for idx, trade in trades.iterrows():
            entry_time = trade['Entry Time'].strftime('%Y-%m-%d %H:%M')
            exit_time = trade['Exit Time'].strftime('%Y-%m-%d %H:%M')
            direction = trade['Direction']
            entry_price = f"₹{trade['Entry Price']:,.0f}"
            exit_price = f"₹{trade['Exit Price']:,.0f}"
            qty = trade['Quantity']
            sl = f"₹{trade['Stop Loss']:,.0f}"
            target = f"₹{trade['Target']:,.0f}"
            pnl = f"₹{trade['P&L (INR)']:,.0f}"
            ret = f"{trade['Return (%)']:.2f}%"
            reason = trade['Exit Reason']
            
            print(f"{idx+1:<4} {entry_time:<20} {exit_time:<20} {direction:<6} {entry_price:<10} {exit_price:<10} "
                  f"{qty:<6} {sl:<10} {target:<10} {pnl:<12} {ret:<10} {reason:<18}")
        
        print("=" * 140)
    else:
        print("No trades executed.")
        print("=" * 140)
    
    # Strategy Rules
    print("\n" + "=" * 140)
    print("ALGORITHM RULES")
    print("=" * 140)
    print("Entry Conditions:")
    print("  • LONG:  Z-score < -2.0 (Price 2σ below mean)")
    print("  • SHORT: Z-score > +2.0 (Price 2σ above mean)")
    print("\nRisk Management:")
    print("  • Risk Per Trade: 5% of capital")
    print("  • Stop Loss: 2% from entry price")
    print("  • Target: 4% from entry price (Risk-Reward = 2:1)")
    print("  • Position Size: Auto-calculated based on 5% risk")
    print("  • Lot Size: 50 (Nifty options standard)")
    print("\nExit Conditions:")
    print("  • Stop Loss hit (2% loss)")
    print("  • Target reached (4% profit)")
    print("  • Mean reversion (Z-score returns toward 0)")
    print("  • Force close at 3:15 PM (all positions squared off)")
    print("\nTimeframe:")
    print("  • 5-minute bars")
    print("  • Lookback: 20 bars (100 minutes)")
    print("  • Market Hours: 9:15 AM - 3:30 PM IST")
    print("=" * 140)