// Number guessing game using Number Utils
// Daniel Schlesinger
// SCHDAN066
// 22/09/23

public class CowsAndBulls {
   public final static int NUM_DIGITS = 4;
   public final static int MAX_VALUE = 9876;
   public final static int MIN_VALUE = 1234;
   public final static int MAX_GUESSES = 10;
   private int mysteryNumber;
   private int guesses = MAX_GUESSES;
   private Result guess = new Result(0, 0);
   boolean givenUp;
   
   public CowsAndBulls(int seed) {
      mysteryNumber = 0;
      NumberPicker random = new NumberPicker(seed, 1, 9);
      int[] digits = new int[NUM_DIGITS];
      boolean[] usedDigits = new boolean[10];
      for (int i=0; i<NUM_DIGITS; i++) {
         int newDigit = random.nextInt();
         while (usedDigits[newDigit] == true) {
            newDigit = random.nextInt();
         }
         digits[i] = newDigit;
      }
      for (int k=0; k<NUM_DIGITS; k++) {
         mysteryNumber = mysteryNumber*10 + digits[k];
      }
   }
   
   public int guessesRemaining() {
      return guesses;
   }
   
   public Result guess(int guessNumber) {
      guesses--;
      int bulls = NumberUtils.countMatches(guessNumber, mysteryNumber);
      int cows = NumberUtils.countIntersect(guessNumber, mysteryNumber) - bulls;
      Result guessResult = new Result(cows, bulls);
      guess = guessResult;
      return guessResult;
   }
   
   public int giveUp() {
      givenUp = true;
      return mysteryNumber;
   }
   
   public boolean gameOver() {
      return (guess.isCorrect() || (guesses == 0) || givenUp);
   }
}