public class Box extends Parts {
   private int memory;
   
   public Box(String serialNumberGiven, String manufacturerGiven, String colourGiven, int memoryGiven) {
      super(serialNumberGiven, manufacturerGiven, colourGiven);
      memory = memoryGiven;
   }
   
   public int getMemory() {
      return memory;
   }
   
   public String toString() {
      return "Box: " + super.toString() + ", " + getMemory();
   }
}