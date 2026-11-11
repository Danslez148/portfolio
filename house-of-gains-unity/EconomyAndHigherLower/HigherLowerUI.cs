using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using HouseOfGains.MiniGames;
using HouseOfGains.MiniGames.Cards;
using HouseOfGains.Economy;

namespace HouseOfGains.UI
{
    public class HigherLowerUI : MonoBehaviour
    {
        [Header("Panels")]
        [SerializeField] private GameObject BettingPanel;
        [SerializeField] private GameObject GamePanel;
        [SerializeField] private GameObject ResultPanel;

        [Header("Betting Panel")]
        [SerializeField] private TMP_InputField BetInputField;
        [SerializeField] private Slider BetSlider;
        [SerializeField] private Button ConfirmBetButton;
        [SerializeField] private TextMeshProUGUI BuyInWarningText;
        [SerializeField] private TextMeshProUGUI ChipTotalText;

        [Header("HUD")]
        [SerializeField] private TextMeshProUGUI WinStreakText;
        [SerializeField] private TextMeshProUGUI CurrentPayoutText;

        [Header("Card Display")]
        [SerializeField] private Image CurrentCardImage;
        [SerializeField] private TextMeshProUGUI CurrentCardLabel;
        [SerializeField] private Image NextCardImage;
        [SerializeField] private TextMeshProUGUI NextCardLabel;

        [Header("Action Buttons")]
        [SerializeField] private Button HigherButton;
        [SerializeField] private Button LowerButton;
        [SerializeField] private Button CashoutButton;

        [Header("Result Panel")]
        [SerializeField] private TextMeshProUGUI ResultTitleText;
        [SerializeField] private TextMeshProUGUI PayoutText;
        [SerializeField] private Button ContinueButton;

        private HigherLowerGame game;
        private EconomyManager economy;
        private int maxBet;
        private int minBet;

        public void Initialise(HigherLowerGame higherLowerGame, EconomyManager economyManager)
        {
            game = higherLowerGame;
            economy = economyManager;

            economy.OnChipsChanged += UpdateChipDisplay;
            UpdateChipDisplay(economy.Chips);

            game.OnStateChanged += HandleStateChanged;
            game.OnCurrentCardRevealed += HandleCurrentCardRevealed;
            game.OnNextCardRevealed += HandleNextCardRevealed;
            game.OnRoundResolved += HandleRoundResolved;
            game.OnPayoutCalculated += HandlePayoutCalculated;

            HigherButton.onClick.AddListener(OnHigher);
            LowerButton.onClick.AddListener(OnLower);
            CashoutButton.onClick.AddListener(OnCashout);
            ConfirmBetButton.onClick.AddListener(OnConfirmBet);
            ContinueButton.onClick.AddListener(OnContinue);

            BetSlider.onValueChanged.AddListener(OnSliderChanged);
            BetInputField.onEndEdit.AddListener(OnBetInputChanged);

            SetupBettingPanel();
        }

        private void SetupBettingPanel()
        {
            minBet = economy.GetBuyIn();
            maxBet = economy.Chips;

            BetSlider.minValue = minBet;
            BetSlider.maxValue = maxBet;
            BetSlider.value = minBet;
            BetInputField.text = minBet.ToString();

            BuyInWarningText.text = $"Minimum buy-in: {minBet} chips";
            ShowPanel(BettingPanel);
        }

        private void OnConfirmBet()
        {
            maxBet = economy.Chips;
            if (maxBet <= 0) maxBet = 9999;

            if (!int.TryParse(BetInputField.text, out int bet)) return;
            bet = Mathf.Clamp(bet, minBet, maxBet);

            if (!economy.ValidateBet(bet))
            {
                BuyInWarningText.text = "Not enough chips!";
                return;
            }

            game.InitialiseGame();
            game.PlaceBet(bet);

            ShowPanel(GamePanel);
        }

        private void HandleCurrentCardRevealed(Card card)
        {
            CurrentCardLabel.text = card.displayName;
        }

        private void HandleNextCardRevealed(Card card)
        {
            NextCardLabel.text = card.displayName;
        }

        private void HandleStateChanged()
        {
            bool playerTurn = game.State == HigherLowerGame.GameState.Playing;

            HigherButton.interactable = playerTurn;
            LowerButton.interactable = playerTurn;
            CashoutButton.interactable = playerTurn;

            if (playerTurn)
            {
                NextCardLabel.text = "";
            }
        }

        private void HandleRoundResolved(bool playerWon)
        {
            if (game.IsCashingOut)
            {
                StartCoroutine(ShowResultAfterDelay(0.8f));
                return;
            }
            if (playerWon)
            {
                StartCoroutine(AdvanceCardAfterDelay(0.8f));
            }
            else
            {
                StartCoroutine(ShowResultAfterDelay(0.8f));
            }
        }

        private void HandlePayoutCalculated(int payout)
        {
            CurrentPayoutText.text = $"Payout: {payout}";
            WinStreakText.text = $"Win Streak: {game.GetWinStreak()}";
        }

        private IEnumerator AdvanceCardAfterDelay(float delay)
        {
            yield return new WaitForSeconds(delay);
            NextCardLabel.text = "";
            game.AdvanceCard();
        }

        private IEnumerator ShowResultAfterDelay(float delay)
        {
            yield return new WaitForSeconds(delay);
            
            if (game.LastResult == HigherLowerGame.RoundResult.PlayerLose)
            {
                ResultTitleText.text = "YOU LOST";
                PayoutText.text = "- " + game.currentBet;
            }
            else
            {
                ResultTitleText.text = "CASHED OUT!";
                PayoutText.text = "+ " + game.GetPayout();
            }
            ShowPanel(ResultPanel);
        }

        private void OnHigher() => game.Higher();
        private void OnLower() => game.Lower();

        private void OnCashout()
        {
            ResultTitleText.text = "CASHED OUT!";
            game.Cashout();
        }

        private void OnContinue() => game.EndGame();

        private void UpdateChipDisplay(int chips)
        {
            ChipTotalText.text = $"Chips: {chips}";
        }

        private void ShowPanel(GameObject target)
        {
            BettingPanel.SetActive(target == BettingPanel);
            GamePanel.SetActive(target == GamePanel);
            ResultPanel.SetActive(target == ResultPanel);
        }

        private void OnDestroy()
        {
            if (economy != null)
                economy.OnChipsChanged -= UpdateChipDisplay;

            if (game != null)
            {
                game.OnStateChanged -= HandleStateChanged;
                game.OnCurrentCardRevealed -= HandleCurrentCardRevealed;
                game.OnNextCardRevealed -= HandleNextCardRevealed;

                game.OnRoundResolved -= HandleRoundResolved;
                game.OnPayoutCalculated -= HandlePayoutCalculated;
            }
}

        private void OnSliderChanged(float value)
        {
            BetInputField.text = Mathf.RoundToInt(value).ToString();
        }

        private void OnBetInputChanged(string value)
        {
            if (int.TryParse(value, out int bet))
            {
                bet = Mathf.Clamp(bet, minBet, maxBet);
                BetSlider.value = bet;
                BetInputField.text = bet.ToString();
            }
        }
    }
}