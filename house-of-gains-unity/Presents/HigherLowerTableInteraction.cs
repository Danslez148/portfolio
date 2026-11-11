// Higher Lower Interaction

using UnityEngine;
using HouseOfGains.Economy;
using HouseOfGains.Dealers;
using HouseOfGains.MiniGames;
using HouseOfGains.UI;

namespace HouseOfGains.World
{
    public class HigherLowerTableInteraction : MonoBehaviour
    {
        [Header("Setup")]
        [SerializeField] private GameObject HigherLowerUIPrefab;

        [SerializeField] private GameObject interactPrompt;

        [Header("Interaction")]
        public float interactRange = 3f;

        private Transform playerTransform;
        private bool sessionActive;
        private GameObject uiInstance;
        private HigherLowerGame game;

        private void Start()
        {
            GameObject player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                playerTransform = player.transform;
            }
        }

        private void Update()
        {
            if (playerTransform == null) return;

            float dist = Vector2.Distance(transform.position, playerTransform.position);
            bool inRange = dist <= interactRange && !sessionActive;

            if (interactPrompt != null)
            {
                interactPrompt.SetActive(inRange);
            }

            if (inRange && Input.GetKeyDown(KeyCode.E))
            {
                if (EconomyManager.Instance.TrySpendToken())
                {
                    Debug.Log("[HigherLowerTable] Token spent! Starting session...");
                    if (interactPrompt != null) interactPrompt.SetActive(false);
                    StartSession();
                }
                else
                {
                    Debug.Log("[HigherLowerTable] Not enough Round Tokens!");
                }
            }
        }

        private void StartSession()
        {
            sessionActive = true;

            GameController.Instance.SetPlayerCanMove(false);

            uiInstance = Instantiate(HigherLowerUIPrefab);

            HigherLowerUI ui = uiInstance.GetComponent<HigherLowerUI>();
            game = uiInstance.AddComponent<HigherLowerGame>();

            DealerConfig config = ScriptableObject.CreateInstance<DealerConfig>();
            DealerModifier dealer = new DealerModifier(config);

            game.Inject(EconomyManager.Instance, dealer);
            ui.Initialise(game, EconomyManager.Instance);

            game.OnGameEnded += EndSession;
        }

        private void EndSession()
        {
            sessionActive = false;

            GameController.Instance.SetPlayerCanMove(true);

            if (uiInstance) Destroy(uiInstance);
        }
    }
}