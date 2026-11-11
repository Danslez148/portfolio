using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using HouseOfGains.MiniGames;
using HouseOfGains.Economy;

namespace HouseOfGains.UI
{
    public class RouletteUI : MonoBehaviour
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

        [Header("Game Panel")]
        [SerializeField] private Button RedButton;
        [SerializeField] private Button BlackButton;
        [SerializeField] private Button OddButton;
        [SerializeField] private Button EvenButton;
        [SerializeField] private Button Dozen1Button;
        [SerializeField] private Button Dozen2Button;
        [SerializeField] private Button Dozen3Button;
        [SerializeField] private Button SpinButton;
        [SerializeField] private Image ColourBox;
        [SerializeField] private TextMeshProUGUI SpunNumberText;
        [SerializeField] private List<Button> NumberButtons;

        [Header("Result Panel")]
        [SerializeField] private TextMeshProUGUI ResultText;
        [SerializeField] private TextMeshProUGUI ResultTitleText;
        [SerializeField] private TextMeshProUGUI PayoutText;
        [SerializeField] private Button ContinueButton;

        [Header("Colors")]
        [SerializeField] private Color RedColor;
        [SerializeField] private Color BlackColor;
        [SerializeField] private Color GreenColor;

        private RouletteGame game;
        private EconomyManager economy;

        private int minBet;
        private int maxBet;
        private object currentChoice;

        public void Initialise(RouletteGame rouletteGame, EconomyManager economyManager)
        {
            game = rouletteGame;
            economy = economyManager;

            economy.OnChipsChanged += UpdateChipDisplay;
            UpdateChipDisplay(economy.Chips);

            ConfirmBetButton.onClick.AddListener(OnConfirmBet);
            ContinueButton.onClick.AddListener(OnContinue);
            SpinButton.onClick.AddListener(OnSpin);

            RedButton.onClick.AddListener(() => OnChooseBet(RouletteGame.BetType.Red));
            BlackButton.onClick.AddListener(() => OnChooseBet(RouletteGame.BetType.Black));
            OddButton.onClick.AddListener(() => OnChooseBet(RouletteGame.BetType.Odd));
            EvenButton.onClick.AddListener(() => OnChooseBet(RouletteGame.BetType.Even));

            Dozen1Button.onClick.AddListener(() => OnChooseBet(RouletteGame.BetType.Dozen1));
            Dozen2Button.onClick.AddListener(() => OnChooseBet(RouletteGame.BetType.Dozen2));
            Dozen3Button.onClick.AddListener(() => OnChooseBet(RouletteGame.BetType.Dozen3));

            for (int i = 0; i < NumberButtons.Count; i++)
            {
                int number = i; // 0..36
                NumberButtons[i].onClick.AddListener(() => OnChooseBet(number));
            }

            BetSlider.onValueChanged.AddListener(OnSliderChanged);
            BetInputField.onEndEdit.AddListener(OnBetInputChanged);

            currentChoice = null;
            HighlightSelection();

            SetupBettingPanel();
        }

        private void SetupBettingPanel()
        {
            minBet = economy.MinimumBuyIn;
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
            if (!int.TryParse(BetInputField.text, out int bet)) return;
            bet = Mathf.Clamp(bet, minBet, maxBet);

            if (!economy.ValidateBet(bet))
            {
                BuyInWarningText.text = "Not enough chips!";
                return;
            }

            game.InitialiseGame();
            game.PlaceBet(bet);

            EnableBetTypeButtons(true);
            SpinButton.interactable = false;

            ShowPanel(GamePanel);
        }

        private void OnChooseBet(object choice)
        {
            if (!game.IsActive()) return;

            currentChoice = choice;
            HighlightSelection();
            SpinButton.interactable = true;

            // Assign to game
            if (choice is int number)
                game.SetBetNumber(number);
            else if (choice is RouletteGame.BetType type)
            {
                switch (type)
                {
                    case RouletteGame.BetType.Red:
                    case RouletteGame.BetType.Black:
                        game.SetBetTypeRedBlack(type);
                        break;
                    case RouletteGame.BetType.Odd:
                    case RouletteGame.BetType.Even:
                        game.SetBetTypeOddEven(type);
                        break;
                    case RouletteGame.BetType.Dozen1:
                    case RouletteGame.BetType.Dozen2:
                    case RouletteGame.BetType.Dozen3:
                        game.SetBetTypeDozen(type);
                        break;
                }
            }
        }

        private void HighlightSelection()
        {
            RedButton.image.color = BlackButton.image.color = OddButton.image.color =
                EvenButton.image.color = Dozen1Button.image.color = Dozen2Button.image.color =
                Dozen3Button.image.color = Color.white;
            foreach (var btn in NumberButtons) btn.image.color = Color.white;

            if (currentChoice is int number) NumberButtons[number].image.color = Color.yellow;
            else if (currentChoice is RouletteGame.BetType type)
            {
                switch (type)
                {
                    case RouletteGame.BetType.Red: RedButton.image.color = Color.yellow; break;
                    case RouletteGame.BetType.Black: BlackButton.image.color = Color.yellow; break;
                    case RouletteGame.BetType.Odd: OddButton.image.color = Color.yellow; break;
                    case RouletteGame.BetType.Even: EvenButton.image.color = Color.yellow; break;
                    case RouletteGame.BetType.Dozen1: Dozen1Button.image.color = Color.yellow; break;
                    case RouletteGame.BetType.Dozen2: Dozen2Button.image.color = Color.yellow; break;
                    case RouletteGame.BetType.Dozen3: Dozen3Button.image.color = Color.yellow; break;
                }
            }
        }

        private void OnSpin()
        {
            SpinButton.interactable = false;
            EnableBetTypeButtons(false);
            StartCoroutine(SpinAnimation());
        }

        private IEnumerator SpinAnimation()
        {
            int cycles = 30;
            int spunNumber = 0;
            bool isRed = false;

            for (int i = 0; i < cycles; i++)
            {
                spunNumber = Random.Range(0, 37);
                isRed = spunNumber != 0 && game.IsRed(spunNumber);

                SpunNumberText.text = spunNumber.ToString();
                ColourBox.color = spunNumber == 0 ? GreenColor : isRed ? RedColor : BlackColor;

                yield return new WaitForSeconds(0.03f + i * 0.002f);
            }

            game.Spin();

            bool playerWon = game.CheckPlayerWin();
            spunNumber = game.GetLastSpunNumber();
            int payout = game.GetPayout();

            if (payout > 0)
            {
                economy.AddChips(payout);
            }

            ResultText.text = playerWon ? "YOU WON!" : "YOU LOST!";
            SpunNumberText.text = spunNumber.ToString();

            yield return new WaitForSeconds(0.5f);

            ResultTitleText.text = playerWon ? "Victory!" : "Defeat!";

            //int netChange = playerWon ? payout : -game.GetCurrentBet();

            PayoutText.text = $"Payout: {payout}";
            ShowPanel(ResultPanel);
        }

        private void OnContinue()
        {
            game.EndGame();

            BettingPanel.SetActive(false);
            GamePanel.SetActive(false);
            ResultPanel.SetActive(false);
        }       

        private void EnableBetTypeButtons(bool enable)
        {
            RedButton.interactable = BlackButton.interactable = OddButton.interactable =
                EvenButton.interactable = Dozen1Button.interactable = Dozen2Button.interactable =
                Dozen3Button.interactable = enable;

            foreach (var btn in NumberButtons) btn.interactable = enable;
        }

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