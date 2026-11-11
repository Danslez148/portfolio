using System.Collections.Generic;
using UnityEngine;

namespace HouseOfGains.MiniGames.Cards
{
    public enum Suit  { Hearts, Diamonds, Clubs, Spades }
    //public enum Rank  { Two=2, Three, Four, Five, Six, Seven, Eight, Nine, Ten,
    //                    Jack=10, Queen=10, King=10, Ace=11 }

    [System.Serializable]
    public class Card
    {
        public Suit   suit;
        public int    rank;        // numeric rank 2-14 (14 = Ace)
        public string displayName; // e.g. "A♠", "K♥"
        public bool   faceDown;

        // Blackjack value: face cards = 10, Ace starts as 11
        public int BlackjackValue()
        {
            if (rank >= 10 && rank <= 13) return 10; // J, Q, K
            if (rank == 14)               return 11; // Ace (high by default)
            return rank;
        }

        public override string ToString() => faceDown ? "??" : displayName;
    }

    public class Deck
    {
        private List<Card> cards = new List<Card>();

        private static readonly string[] suitSymbols = { "♥", "♦", "♣", "♠" };
        private static readonly string[] rankNames    =
            { "", "", "2","3","4","5","6","7","8","9","10","J","Q","K","A" };

        public Deck(bool shuffle = true)
        {
            Build();
            if (shuffle) Shuffle();
        }

        private void Build()
        {
            cards.Clear();
            foreach (Suit s in System.Enum.GetValues(typeof(Suit)))
            {
                for (int r = 2; r <= 14; r++)
                {
                    cards.Add(new Card
                    {
                        suit        = s,
                        rank        = r,
                        displayName = rankNames[r] + suitSymbols[(int)s],
                        faceDown    = false
                    });
                }
            }
        }

        public void Shuffle()
        {
            for (int i = cards.Count - 1; i > 0; i--)
            {
                int j = Random.Range(0, i + 1);
                (cards[i], cards[j]) = (cards[j], cards[i]);
            }
        }

        public Card Draw()
        {
            if (cards.Count == 0) { Build(); Shuffle(); } // reshuffle if empty
            Card c = cards[0];
            cards.RemoveAt(0);
            return c;
        }

        public int Count => cards.Count;
    }
}
