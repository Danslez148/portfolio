class Rectangle extends VectorObject {
   private int Length;
   private int Height;
   
   public Rectangle(int id, int x, int y, int Length, int Height) {
      super(id, x, y);
      this.Length = Length;
      this.Height = Height;
   }
   
   public void draw(char[][] matrix) {
      int lastX = x + Length - 1;
      int lastY = y + Height - 1;
      for (int i = x; i <= lastX; i++) {
         for (int j = y; j <= lastY; j++) {
            matrix[j][i] = '*';
         }
      }
   }
}