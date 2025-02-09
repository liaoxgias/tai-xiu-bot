import random

def max_consecutive_length(arr):
    max_zeros = max_ones = 0
    count_zeros = count_ones = 0
    
    for num in arr:
        if num == 0:
            count_zeros += 1
            max_zeros = max(max_zeros, count_zeros)
            count_ones = 0
        else:
            count_ones += 1
            max_ones = max(max_ones, count_ones)
            count_zeros = 0
    
    return max(max_zeros, max_ones)

def simulate_game():
    balance = 35000
    bet = 10000
    target = 200000
    max_losing_streak = 0
    current_losing_streak = 0
    history = []
    history_money = []
    
    while balance > 0 and balance < target:
        result = random.choice([0, 1])  # 1 là thắng, 0 là thua
        history.append(result)
        
        if result == 1:
            balance += bet
            bet = 2000  # Reset cược về mức ban đầu
            current_losing_streak = 0
        else:
            balance -= bet
            current_losing_streak += 1
            max_losing_streak = max(max_losing_streak, current_losing_streak)
            if (current_losing_streak > 2):
                bet *= 2  # Nhân đôi số cược sau mỗi lần thua
            if bet > balance:  # Nếu cược vượt quá số dư, đặt cược tối đa có thể
                bet = balance
        history_money.append(balance)
    print(history_money)
    return max_losing_streak, history, balance

def main():
    win = 0
    lose = 0
    for (i) in range(0, 100):
        max_losing_streak, history, final_balance = simulate_game()
        if final_balance > 0:
            win += 1
        else:
            lose += 1
    
    print(f"Win: {win}, Lose: {lose}")

if __name__ == "__main__":
    main()
