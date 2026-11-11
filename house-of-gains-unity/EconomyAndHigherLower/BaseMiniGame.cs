using UnityEngine;
using HouseOfGains.Economy;
using HouseOfGains.Dealers;

namespace HouseOfGains.MiniGames
{
   
    public abstract class BaseMiniGame : MonoBehaviour, IMiniGame
    {

        protected EconomyManager   economyManager;
        protected DealerModifier   dealerModifier;


        public int   currentBet;
        protected int   roundNumber;
        protected bool  gameActive;
        protected int   pendingPayout;


        public event System.Action<int>    OnPayoutCalculated;  
        public event System.Action<bool>   OnRoundResolved;    
        public event System.Action         OnGameEnded;


        public void Inject(EconomyManager economy, DealerModifier dealer)
        {
            economyManager = economy;
            dealerModifier = dealer;
        }


        public virtual void InitialiseGame()
        {
            roundNumber  = 0;
            currentBet   = 0;
            gameActive   = true;
            pendingPayout = 0;
            OnInitialise();
        }

        public virtual void PlaceBet(int amount)
        {
            if (!economyManager.ValidateBet(amount)) return;
            currentBet = amount;
            economyManager.DeductBet(amount);
            OnBetPlaced(amount);
        }

        public virtual void ExecuteRound()
        {
            if (!gameActive) return;
            roundNumber++;
            OnExecuteRound();
        }

        public virtual void ResolveOutcome()
        {
            OnResolveOutcome();
        }

        public virtual int GetPayout()
        {
            return pendingPayout;
        }

        public virtual void EndGame()
        {
            gameActive = false;
            economyManager.ApplyPayout(pendingPayout);
            OnGameEnded?.Invoke();
            OnEnd();
        }

        protected abstract void OnInitialise();
        protected abstract void OnBetPlaced(int amount);
        protected abstract void OnExecuteRound();
        protected abstract void OnResolveOutcome();
        protected abstract void OnEnd();


        protected void NotifyPayout(int amount, bool playerWon)
        {
            pendingPayout = amount;
            OnPayoutCalculated?.Invoke(amount);
            OnRoundResolved?.Invoke(playerWon);
        }
    }
}
