public class Accessory extends Parts {
   public Accessory(String serialNumberGiven, String manufacturerGiven, String colourGiven) {
      super(serialNumberGiven, manufacturerGiven, colourGiven);
   }
   
   public String toString() {
      return "Accessories: " + super.toString();
   }
}