public class Screen extends Parts {
   private int size;
   
   public Screen(String serialNumberGiven, String manufacturerGiven, String colourGiven, int sizeGiven) {
      super(serialNumberGiven, manufacturerGiven, colourGiven);
      size = sizeGiven;
   }
   
   public int getSize() {
      return size;
   }
   
   public String toString() {
      return "Screen: " + getSerialNumber() + ", " + getColour() + ", " + getManufacturer() + ", " + getSize();
   }
}