using UnityEngine;
using HouseOfGains.MiniGames.Cards;

namespace HouseOfGains.MiniGames
{
    public class HigherLowerGame : BaseMiniGame
    {
        public enum GameState
        {
            WaitingForBet,
            Playing,
            Transitioning,
            RoundOver
        }

        public enum RoundResult { None, PlayerWin, PlayerLose }

        public GameState State { get; private set; }
        public RoundResult LastResult { get; private set; }

        private Deck deck;
        private Card currentCard;
        private Card nextCard;
        private int winStreak;

        public event System.Action OnStateChanged;
        public event System.Action<Card> OnCurrentCardRevealed;
        public event System.Action<Card> OnNextCardRevealed;

        protected override void OnInitialise()
        {
            deck = new Deck();
            currentCard = null;
            nextCard = null;
            winStreak = 0;

            IsCashingOut = false;

            State = GameState.WaitingForBet;
            LastResult = RoundResult.None;

            OnStateChanged?.Invoke();
        }

        protected override void OnBetPlaced(int amount)
        {
            currentCard = deck.Draw();
            OnCurrentCardRevealed?.Invoke(currentCard);

            State = GameState.Playing;
            OnStateChanged?.Invoke();
        }

        protected override void OnExecuteRound() { }
        protected override void OnResolveOutcome() { }
        protected override void OnEnd() { }

        public void Higher()
        {
            if (State != GameState.Playing) return;

            nextCard = deck.Draw();
            OnNextCardRevealed?.Invoke(nextCard);

            State = GameState.Transitioning;
            OnStateChanged?.Invoke();

            ResolveGuess(isHigherGuess: true);
        }

        public void Lower()
        {
            if (State != GameState.Playing) return;

            nextCard = deck.Draw();
            OnNextCardRevealed?.Invoke(nextCard);

            State = GameState.Transitioning;
            OnStateChanged?.Invoke();

            ResolveGuess(isHigherGuess: false);
        }

        private void ResolveGuess(bool isHigherGuess)
        {
            int current = currentCard.BlackjackValue();
            int next = nextCard.BlackjackValue();

            bool playerCorrect;

            if (next == current)
            {
                playerCorrect = true;
            }
            else
            {
                playerCorrect = isHigherGuess
                    ? next > current
                    : next < current;
            }

            ResolveRound(playerCorrect);
        }

        private void ResolveRound(bool playerCorrect)
        {
            State = GameState.Transitioning;
            OnStateChanged?.Invoke();

            if (playerCorrect)
            {
                winStreak++;
                LastResult = RoundResult.PlayerWin;

                int multiplier = 1 + winStreak;
                int payout = currentBet * multiplier;

                if (dealerModifier != null)
                    payout = dealerModifier.ModifyPayout(payout, currentBet);

                NotifyPayout(payout, true);
            }
            else
            {
                winStreak = 0;
                LastResult = RoundResult.PlayerLose;

                NotifyPayout(0, false);

                State = GameState.RoundOver;
                OnStateChanged?.Invoke();
            }
        }
        public bool IsCashingOut { get; private set; }
        public void Cashout()
        {
            IsCashingOut = true;
            LastResult = RoundResult.PlayerWin;
            NotifyPayout(pendingPayout, true);
            State = GameState.RoundOver;
            OnStateChanged?.Invoke();
        }

        public void AdvanceCard()
        {
            if (LastResult != RoundResult.PlayerWin) return;

            currentCard = nextCard;
            nextCard = null;

            OnCurrentCardRevealed?.Invoke(currentCard);

            State = GameState.Playing;
            OnStateChanged?.Invoke();
        }

        public int GetWinStreak() => winStreak;
        public Card GetCurrentCard() => currentCard;
        public Card GetNextCard() => nextCard;
    }
}