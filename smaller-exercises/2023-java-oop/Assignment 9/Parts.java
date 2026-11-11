public class Parts {
   private String serialNumber;
   private String manufacturer;
   private String colour;
   
   public Parts(String serialNumberGiven, String manufacturerGiven, String colourGiven) {
      serialNumber = serialNumberGiven;
      manufacturer = manufacturerGiven;
      colour = colourGiven;
   }
   
   public String getSerialNumber() {
      return serialNumber;
   }
   
   public String getManufacturer() {
      return manufacturer;
   }
   
   public String getColour() {
      return colour;
   }
   
   public String toString() {
      return serialNumber + ", " + manufacturer + ", " + colour;
   }
}