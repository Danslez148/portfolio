using System;
using System.Collections.Generic;
using UnityEngine;
using HouseOfGains.Economy;

namespace HouseOfGains.MiniGames
{
    public class RouletteGame : BaseMiniGame
    {
        public enum BetType
        {
            None,
            Red,
            Black,
            Odd,
            Even,
            Dozen1,
            Dozen2,
            Dozen3,
            Number
        }

        private BetType currentBetType = BetType.None;
        private int? chosenNumber;       // For number bets
        private int lastSpunNumber;
        private bool lastPlayerWon;

        private readonly HashSet<int> redNumbers = new HashSet<int>
        {
            1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
        };

        protected override void OnInitialise()
        {
            currentBetType = BetType.None;
            chosenNumber = null;
            lastSpunNumber = -1;
            lastPlayerWon = false;
        }

        protected override void OnBetPlaced(int amount)
        {
            currentBetType = BetType.None;
            chosenNumber = null;
        }

        public bool IsActive()
        {
            return gameActive;
        }

        protected override void OnExecuteRound() { }
        protected override void OnResolveOutcome() { }
        protected override void OnEnd() { }

        // --- Bet setters ---
        public void SetBetTypeRedBlack(BetType type)
        {
            if (type == BetType.Red || type == BetType.Black)
                currentBetType = type;
        }

        public void SetBetTypeOddEven(BetType type)
        {
            if (type == BetType.Odd || type == BetType.Even)
                currentBetType = type;
        }

        public void SetBetTypeDozen(BetType type)
        {
            if (type == BetType.Dozen1 || type == BetType.Dozen2 || type == BetType.Dozen3)
                currentBetType = type;
        }

        public void SetBetNumber(int number)
        {
            if (number < 0 || number > 36) return;
            currentBetType = BetType.Number;
            chosenNumber = number;
        }

        // --- Spin ---
        public void Spin()
        {
            lastSpunNumber = UnityEngine.Random.Range(0, 37);
            bool isRed = redNumbers.Contains(lastSpunNumber);

            lastPlayerWon = false;

            switch (currentBetType)
            {
                case BetType.Red: lastPlayerWon = isRed; break;
                case BetType.Black: lastPlayerWon = lastSpunNumber != 0 && !isRed; break;
                case BetType.Odd: lastPlayerWon = lastSpunNumber != 0 && lastSpunNumber % 2 == 1; break;
                case BetType.Even: lastPlayerWon = lastSpunNumber != 0 && lastSpunNumber % 2 == 0; break;
                case BetType.Dozen1: lastPlayerWon = lastSpunNumber >= 1 && lastSpunNumber <= 12; break;
                case BetType.Dozen2: lastPlayerWon = lastSpunNumber >= 13 && lastSpunNumber <= 24; break;
                case BetType.Dozen3: lastPlayerWon = lastSpunNumber >= 25 && lastSpunNumber <= 36; break;
                case BetType.Number: if (chosenNumber.HasValue) lastPlayerWon = lastSpunNumber == chosenNumber.Value; break;
            }

            int payout = lastPlayerWon ? currentBet * GetMultiplier() : 0;
            NotifyPayout(payout, lastPlayerWon);

            // Reset bet type for next round
            currentBetType = BetType.None;
            chosenNumber = null;
        }

        private int GetMultiplier()
        {
            switch (currentBetType)
            {
                case BetType.Red:
                case BetType.Black:
                case BetType.Odd:
                case BetType.Even:
                    return 2; // 1:1 payout
                case BetType.Dozen1:
                case BetType.Dozen2:
                case BetType.Dozen3:
                    return 3; // 2:1 payout
                case BetType.Number:
                    return 36; // Single number
                default:
                    return 0;
            }
        }
        public bool IsRed(int number) => redNumbers.Contains(number) && number != 0;

        public bool CheckPlayerWin() => lastPlayerWon;

        public int GetLastSpunNumber() => lastSpunNumber;
    }
}