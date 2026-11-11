// Collection of routines for working with integers
// SCHDAN066
// Daniel Schlesinger
// 22/09/2023

public class NumberUtils {
   private NumberUtils() {}
   
   public static int[] toArray(int number) {
      String numString = "" + number;
      int i = numString.length();
      int[] result = new int[i];
      for (int k = 0; k<i; k++) {
         result[k] = numString.charAt(k)-48;
      }
      return result;
   }
   
   public static int countMatches(int numberA, int numberB) {
      int count = 0;
      String numStringA = "" + numberA;
      String numStringB = "" + numberB;
      int i = numStringA.length();
      for (int k = 0; k<i; k++) {
        if (numStringA.charAt(k) == numStringB.charAt(k)) {
         count++;
        }
      }
      return count;
   }
   
   public static int countIntersect(int NumberA, int NumberB) {
      int count = 0;
      String numStringA = "" + NumberA;
      String numStringB = "" + NumberB;
      int i = numStringA.length();
      for (int k = 0; k<i; k++) {
         for (int n = 0; n<i; n++) {
            if (numStringA.charAt(k) == numStringB.charAt(n)) {
               count++;
            }
         }
      }
      return count; 
   }
}