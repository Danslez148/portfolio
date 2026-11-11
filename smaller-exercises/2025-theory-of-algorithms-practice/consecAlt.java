public class consecAlt {
   public static int[] numbers = {1, -3, 2, 4, -6, 2, 7, -5, -5, -2, -2};
   public static int maxLength = 1;
   public static void main(String[] args) {
      int currLength = 1;
      for (int i = 1; i<numbers.length; i++) {
         if ((numbers[i-1]>0&&numbers[i]<0) || (numbers[i-1]<0&&numbers[i]>0)) {
            currLength++;
         } else { 
            if (currLength > maxLength) { maxLength = currLength; }
            currLength = 1; 
         }
      }
      if (currLength > maxLength) { maxLength = currLength; }
      System.out.println(maxLength);
   }
}