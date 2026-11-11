using System;
using UnityEngine;

namespace HouseOfGains.Economy
{
    public class EconomyManager : MonoBehaviour
    {
        public static EconomyManager Instance { get; private set; }

        [Header("Current Floor Stats")]
        public int Chips = 1000;
        public int RoundTokens = 6; // Floor 1 starts with 6 tokens
        public int FloorChipThreshold = 2500; // Amount needed to use elevator
        public int MinimumBuyIn = 50;

        // Events to tell the UI to update
        public event Action<int> OnChipsChanged;
        public event Action<int> OnTokensChanged;

        private void Awake()
        {
            if (Instance == null) { Instance = this; }
            else { Destroy(gameObject); }
        }

        public int GetBuyIn() => MinimumBuyIn;

        public bool ValidateBet(int amount)
        {
            return amount >= MinimumBuyIn && amount <= Chips;
        }

        public void AddChips(int amount)
        {
            Chips += amount;
            OnChipsChanged?.Invoke(Chips);
            CheckWinLossCondition();
        }

        public void RemoveChips(int amount)
        {
            Chips -= amount;
            OnChipsChanged?.Invoke(Chips);
            CheckWinLossCondition();
        }

        public bool TrySpendToken()
        {
            if (RoundTokens > 0)
            {
                RoundTokens--;
                OnTokensChanged?.Invoke(RoundTokens);

                // NEW: Check if spending this token doomed the player!
                CheckWinLossCondition();

                return true;
            }
            return false;
        }

        public bool HasMetThreshold()
        {
            return Chips >= FloorChipThreshold;
        }
        // --- Legacy Aliases to fix compiler errors ---

        public void DeductBet(int amount)
        {
            RemoveChips(amount);
        }

        public void ApplyPayout(int amount)
        {
            AddChips(amount);
        }

        public void StartNewRun()
        {
            Chips = 1000; // Reset to starting amount
            RoundTokens = 6; // Reset to floor 1 tokens

            // Update the UI
            OnChipsChanged?.Invoke(Chips);
            OnTokensChanged?.Invoke(RoundTokens);
        }

        // --- UPDATED: Win/Loss Triggers ---
        public void CheckWinLossCondition()
        {
            // Condition 1: Lost all chips
            if (Chips <= 0)
            {
                GameController.Instance.TriggerGameOver("Bankrupt! You lost all your chips.");
            }
            // Condition 2: Out of tokens AND haven't met the escape threshold
            else if (RoundTokens <= 0 && !HasMetThreshold())
            {
                GameController.Instance.TriggerGameOver("Out of time! You don't have enough chips to take the elevator.");
            }
        }

        // --- UPDATED: Floor Scaling & Carry-Over Logic ---
        public void SetupFloorRules(int floorNumber)
        {
            int tokensToAdd = 0;

            // GDD specifies exact tokens per floor
            switch (floorNumber)
            {
                case 1: tokensToAdd = 6; FloorChipThreshold = 2500; MinimumBuyIn = 50; break;
                case 2: tokensToAdd = 5; FloorChipThreshold = 5000; MinimumBuyIn = 100; break;
                case 3: tokensToAdd = 4; FloorChipThreshold = 10000; MinimumBuyIn = 250; break;
                case 4: tokensToAdd = 3; FloorChipThreshold = 25000; MinimumBuyIn = 500; break;
                case 5: tokensToAdd = 0; FloorChipThreshold = 999999; MinimumBuyIn = 1000; break; // Boss Floor!
            }

            // On Floor 1, we set the baseline. On later floors, we ADD to their leftovers!
            if (floorNumber == 1)
            {
                RoundTokens = tokensToAdd;
            }
            else
            {
                RoundTokens += tokensToAdd;
            }

            // Tell the UI to update the token visual
            OnTokensChanged?.Invoke(RoundTokens);
        }

        
    }
}